"""Model and engine whitelist for CallenVoice.

Only components whose licence was read at the source and allows commercial
use are offered. Everything else stays in the code base (upstream merges) but
is hidden from listings, cannot be installed or selected, and is refused at
the moment an engine would load. See docs/callen/decisiones/0002-lista-blanca.md.
"""
from __future__ import annotations

import fnmatch
import os
import re

from services.model_acceptance import ModelLicenceNotAccepted

#: Text-to-speech engines that may be listed, installed, selected and run.
ALLOWED_TTS_ENGINES: frozenset[str] = frozenset({
    "moss-tts-nano",  # Apache-2.0 code + weights; fits 8 GB on CPU (Phase 1 benchmark)
    "kittentts",      # Apache-2.0; English preset voices, no cloning
    "cosyvoice",      # Apache-2.0; 16 GB RAM or GPU tier
    "voxcpm2",        # Apache-2.0; 16 GB RAM or GPU tier
})

#: Engine used when nothing (or something no longer allowed) is selected.
DEFAULT_TTS_ENGINE = "moss-tts-nano"

#: Translation engines that may be offered. v1 decision: local translation only,
#: so cloud services (Google, DeepL, Microsoft, Amazon, MyMemory) and the LLM
#: engine (which can call cloud APIs) are excluded, and so is NLLB (CC-BY-NC-4.0).
#: "opus" is the Opus-MT engine planned for Phase 3; "argos" stays only until it
#: lands (its language packages declare no licence).
ALLOWED_TRANSLATION_ENGINES: frozenset[str] = frozenset({"argos", "opus"})

#: Hugging Face repositories that may appear in the model manager. Patterns use
#: fnmatch syntax and are matched against the exact repo id.
ALLOWED_MODEL_REPOS: tuple[str, ...] = (
    # Speech recognition (MIT)
    "Systran/faster-whisper-*",
    "Systran/faster-distil-whisper-*",
    "deepdml/faster-whisper-large-v3-turbo-ct2",
    "openai/whisper-large-v3-turbo",
    "ggerganov/whisper.cpp",
    # Voice (Apache-2.0)
    "OpenMOSS-Team/MOSS-TTS-Nano*",
    "OpenMOSS-Team/MOSS-Audio-Tokenizer*",
    "KittenML/kitten-tts-*",
    "FunAudioLLM/Fun-CosyVoice3-0.5B-2512",
    "openbmb/VoxCPM2",
    # Translation (Apache-2.0)
    "Helsinki-NLP/opus-mt-*",
    "santhosh/madlad400-3b-ct2",
)


_REPO_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*")


#: Models the first-run setup downloads: the default voice engine's weights and
#: a small Whisper for transcription (both fit the 8 GB CPU tier).
REQUIRED_MODEL_REPOS: tuple[str, ...] = (
    "OpenMOSS-Team/MOSS-TTS-Nano-100M",
    "Systran/faster-whisper-small",
)


def _env_override_allows_all() -> bool:
    # Developer escape hatch for comparing against upstream engines locally.
    # Never set in release builds.
    return os.environ.get("CALLENVOICE_ALLOW_ALL_MODELS") == "1"


def url_import_allowed() -> bool:
    """Importing media from a URL (yt-dlp) is off in v1."""
    return _env_override_allows_all()


def upstream_demo_voice_allowed() -> bool:
    """The upstream "Demo Voice" (backend/assets/samples/demo_voice.wav) was
    rendered with OmniVoice (CC-BY-NC weights) and declares no licence, so it is
    not seeded. A CallenVoice demo voice needs a real speaker's signed consent."""
    return _env_override_allows_all()


def tts_engine_allowed(engine_id: str | None) -> bool:
    return _env_override_allows_all() or (engine_id or "") in ALLOWED_TTS_ENGINES


def translation_engine_allowed(engine_id: str | None) -> bool:
    return _env_override_allows_all() or (engine_id or "") in ALLOWED_TRANSLATION_ENGINES


def llm_provider_allowed(provider_id: str | None) -> bool:
    """Only LLM providers that run on the user's machine (Ollama, LM Studio).

    CallenVoice promises local processing: cloud providers and agent CLIs would
    send the user's transcripts to third parties and need their own API terms.
    """
    if _env_override_allows_all():
        return True
    from services import llm_providers  # lazy: keeps catalog import-light

    provider = llm_providers.get_provider(provider_id or "")
    return bool(provider and provider.local)


def model_repo_allowed(repo_id: str | None) -> bool:
    if _env_override_allows_all():
        return True
    rid = repo_id or ""
    # fnmatch's "*" also matches "/", so require a plain "owner/name" id first.
    if not _REPO_ID.fullmatch(rid):
        return False
    return any(fnmatch.fnmatchcase(rid, pattern) for pattern in ALLOWED_MODEL_REPOS)


class ModelNotOffered(ModelLicenceNotAccepted):
    """An engine or model that CallenVoice does not offer.

    Subclasses the upstream licence refusal so every existing handler already
    turns it into a typed 403 instead of a 500.
    """

    ERROR_CODE = "callen_model_not_offered"

    def __init__(self, kind: str, identifier: str):
        self.kind = kind
        self.identifier = identifier
        super().__init__([{"repo_id": identifier, "license": "not offered", "category": "excluded"}])
        self.args = (
            f"{identifier} is not available in CallenVoice: its licence does not allow "
            "commercial use or it is outside the product. Choose another engine.",
        )

    def __str__(self) -> str:  # the parent builds its own message; ours is clearer
        return self.args[0]

    def detail(self) -> dict:
        return {"code": self.ERROR_CODE, "message": str(self), "kind": self.kind, "id": self.identifier}


def ensure_tts_engine_allowed(engine_id: str | None) -> None:
    if not tts_engine_allowed(engine_id):
        raise ModelNotOffered("tts_engine", engine_id or "")


def resolve_tts_engine(engine_id: str | None) -> str:
    """The engine to use for a stored or default selection.

    A selection that is no longer offered (for example the upstream default
    OmniVoice) falls back to the CallenVoice default instead of failing.
    """
    return engine_id if tts_engine_allowed(engine_id) else DEFAULT_TTS_ENGINE


def apply_to_model_catalogue(models: list[dict]) -> list[dict]:
    """Adjust the upstream model catalogue (models.yaml) to the CallenVoice scope.

    Excluded models are never required or recommended; our default models are
    required, so first-run setup downloads them instead of OmniVoice.
    """
    if _env_override_allows_all():
        return models
    out = []
    for model in models:
        entry = dict(model)
        repo = entry.get("repo_id")
        if repo in REQUIRED_MODEL_REPOS:
            entry["required"] = True
        elif not model_repo_allowed(repo):
            entry["required"] = False
            entry["curated_on"] = []
        else:
            entry["required"] = False
        out.append(entry)
    return out
