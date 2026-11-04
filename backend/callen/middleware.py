"""HTTP layer of the CallenVoice whitelist.

Filters the engine and model listings the UI reads, and refuses requests that
would install or select something CallenVoice does not offer. The upstream
routers stay untouched; this middleware wraps them.

Pure ASGI on purpose: every request outside the handful of paths below passes
straight through (no body buffering, no response wrapping), so streaming
endpoints, background tasks and upstream error handling behave exactly as
without the middleware.
"""
from __future__ import annotations

import json
import re

from callen import catalog

_SIDECAR_INSTALL = re.compile(r"^/engines/sidecar/([^/]+)/install$")
_TRANSLATION_INSTALL = re.compile(r"^/engines/translation/([^/]+)/install$")
_MODEL_INSTALL_PATHS = {"/models/install", "/models/install/prepare", "/models/licenses/accept"}
_LLM_PROVIDERS = "/api/settings/llm-providers"
_LLM_PROVIDER_ACTION = re.compile(r"^/api/settings/llm-providers/([^/]+)(?:/(connect|test))?$")
_BODY_CHECK_PATHS = {
    "/engines/select",
    "/engines/translation/select",
    _LLM_PROVIDERS + "/active",
    *_MODEL_INSTALL_PATHS,
}
_FILTERED_LISTINGS = {"/engines/tts", "/engines/translation", "/models", _LLM_PROVIDERS}


def _refusal(kind: str, identifier: str) -> tuple[int, bytes]:
    exc = catalog.ModelNotOffered(kind, identifier)
    return 403, json.dumps({"detail": exc.detail()}).encode()


def _check_path(path: str) -> tuple[int, bytes] | None:
    if path == "/dub/ingest-url" and not catalog.url_import_allowed():
        # v1: no import from video URLs (platform terms and copyright risk).
        return _refusal("feature", "url_import")
    m = _SIDECAR_INSTALL.match(path)
    if m and not catalog.tts_engine_allowed(m.group(1)):
        return _refusal("tts_engine", m.group(1))
    m = _TRANSLATION_INSTALL.match(path)
    if m and not catalog.translation_engine_allowed(m.group(1)):
        return _refusal("translation_engine", m.group(1))
    m = _LLM_PROVIDER_ACTION.match(path)
    if m and m.group(1) != "active" and not catalog.llm_provider_allowed(m.group(1)):
        return _refusal("llm_provider", m.group(1))
    return None


def _check_body(path: str, raw: bytes) -> tuple[int, bytes] | None:
    try:
        body = json.loads(raw or b"{}")
    except (ValueError, UnicodeDecodeError):
        return None  # let the router answer the malformed request itself
    if not isinstance(body, dict):
        return None
    if path == "/engines/select":
        if body.get("family") == "tts" and not catalog.tts_engine_allowed(body.get("backend_id")):
            return _refusal("tts_engine", str(body.get("backend_id") or ""))
    elif path == "/engines/translation/select":
        if not catalog.translation_engine_allowed(body.get("engine_id")):
            return _refusal("translation_engine", str(body.get("engine_id") or ""))
    elif path == _LLM_PROVIDERS + "/active":
        if not catalog.llm_provider_allowed(body.get("provider")):
            return _refusal("llm_provider", str(body.get("provider") or ""))
    elif path in _MODEL_INSTALL_PATHS:
        repo = body.get("repo_id")
        if repo and not catalog.model_repo_allowed(repo):
            return _refusal("model", str(repo))
    return None


def _filter_listing(path: str, data):
    if not isinstance(data, dict):
        return data
    if path == "/engines/tts" and isinstance(data.get("backends"), list):
        data["backends"] = [b for b in data["backends"] if catalog.tts_engine_allowed(b.get("id"))]
        data["active"] = catalog.resolve_tts_engine(data.get("active"))
    elif path == "/engines/translation" and isinstance(data.get("engines"), list):
        data["engines"] = [
            e for e in data["engines"] if catalog.translation_engine_allowed(e.get("id"))
        ]
    elif path == _LLM_PROVIDERS and isinstance(data.get("providers"), list):
        data["providers"] = [p for p in data["providers"] if catalog.llm_provider_allowed(p.get("id"))]
        if not catalog.llm_provider_allowed(data.get("active")):
            data["active"] = None
    elif path == "/models" and isinstance(data.get("models"), list):
        data["models"] = [m for m in data["models"] if catalog.model_repo_allowed(m.get("repo_id"))]
    return data


async def _send_json(send, status: int, body: bytes) -> None:
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [(b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode())],
    })
    await send({"type": "http.response.body", "body": body})


class CallenCatalogMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        path = scope.get("path", "")
        method = scope.get("method", "")

        if method in ("POST", "PUT"):
            refused = _check_path(path)
            if refused:
                return await _send_json(send, *refused)
            if path in _BODY_CHECK_PATHS:
                chunks, more = [], True
                while more:
                    message = await receive()
                    if message["type"] == "http.disconnect":
                        return
                    chunks.append(message.get("body", b""))
                    more = message.get("more_body", False)
                raw = b"".join(chunks)
                refused = _check_body(path, raw)
                if refused:
                    return await _send_json(send, *refused)
                replayed = False

                async def replay():
                    nonlocal replayed
                    if not replayed:
                        replayed = True
                        return {"type": "http.request", "body": raw, "more_body": False}
                    return await receive()

                return await self.app(scope, replay, send)

        if method == "GET" and path in _FILTERED_LISTINGS:
            start: dict | None = None
            chunks: list[bytes] = []

            async def capture(message):
                nonlocal start
                if message["type"] == "http.response.start":
                    start = message
                    return
                if message["type"] != "http.response.body" or start is None:
                    return await send(message)
                chunks.append(message.get("body", b""))
                if message.get("more_body", False):
                    return
                body = b"".join(chunks)
                headers = [(k, v) for k, v in start.get("headers", []) if k.lower() != b"content-length"]
                is_json = any(k.lower() == b"content-type" and b"json" in v for k, v in headers)
                if start.get("status") == 200 and is_json:
                    try:
                        body = json.dumps(_filter_listing(path, json.loads(body))).encode()
                    except ValueError:
                        pass
                headers.append((b"content-length", str(len(body)).encode()))
                await send({**start, "headers": headers})
                await send({"type": "http.response.body", "body": body})

            return await self.app(scope, receive, capture)

        return await self.app(scope, receive, send)
