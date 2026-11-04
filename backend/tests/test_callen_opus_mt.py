"""CallenVoice Opus-MT engine: routing and router wiring (no model download)."""
from fastapi.testclient import TestClient

from callen import opus_mt


def test_routes_direct_pivot_and_unsupported():
    assert opus_mt.route("en", "es-419") == [opus_mt.DIRECT_PAIRS[("en", "es")]]
    assert opus_mt.route("Spanish", "pt_BR") == [
        opus_mt.DIRECT_PAIRS[("es", "en")],
        opus_mt.DIRECT_PAIRS[("en", "pt")],
    ]
    assert opus_mt.route("es-AR", "es-MX") == []
    assert opus_mt.route("en", "fr") is None


def test_every_opus_repo_is_whitelisted():
    from callen import catalog

    for repo, _ in opus_mt.DIRECT_PAIRS.values():
        assert catalog.model_repo_allowed(repo)


def test_engine_is_registered_and_allowed():
    from callen import catalog
    from services import translation_engines

    assert translation_engines.get_engine("opus")["category"] == "offline"
    assert catalog.translation_engine_allowed("opus")


def _client():
    from fastapi import FastAPI

    from api.routers import dub_translate

    app = FastAPI()
    app.include_router(dub_translate.router)
    return TestClient(app)


def test_dub_translate_uses_opus(monkeypatch):
    calls = []

    def fake(texts, source, target):
        calls.append((tuple(texts), source, target))
        return [f"[{target}] {t}" for t in texts]

    monkeypatch.setattr(opus_mt, "translate", fake)
    r = _client().post("/dub/translate", json={
        "provider": "opus", "source_lang": "en", "target_lang": "es",
        "segments": [{"id": "a", "text": "Hi"}, {"id": "b", "text": " "}, {"id": "c", "text": "Bye"}],
    })
    assert r.status_code == 200, r.text
    assert [row["text"] for row in r.json()["translated"]] == ["[es] Hi", " ", "[es] Bye"]
    assert calls == [(("Hi", "Bye"), "en", "es")]


def test_dub_translate_rejects_unsupported_pair():
    r = _client().post("/dub/translate", json={
        "provider": "opus", "source_lang": "en", "target_lang": "fr",
        "segments": [{"id": "a", "text": "Hi"}],
    })
    assert r.status_code == 400
    assert r.json()["code"] == "unsupported_translation_language"


def test_seed_sets_opus_once_and_respects_user_choice(monkeypatch):
    from callen import catalog
    from core import prefs

    store = {}
    monkeypatch.setattr(prefs, "get", lambda key, default=None: store.get(key, default))
    monkeypatch.setattr(prefs, "set_", lambda key, value: store.__setitem__(key, value))
    catalog.seed_default_preferences()
    assert store["translation_backend"] == "opus"
    store["translation_backend"] = "argos"
    catalog.seed_default_preferences()
    assert store["translation_backend"] == "argos"
