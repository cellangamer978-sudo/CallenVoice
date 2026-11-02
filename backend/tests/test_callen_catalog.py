"""CallenVoice whitelist: catalog rules, engine resolution and the HTTP layer."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from callen import catalog
from callen.middleware import CallenCatalogMiddleware


@pytest.fixture(autouse=True)
def _whitelist_on(monkeypatch):
    # The shared conftest turns the whitelist off for upstream suites.
    monkeypatch.delenv("CALLENVOICE_ALLOW_ALL_MODELS", raising=False)


# ── catalog rules ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("engine", ["moss-tts-nano", "kittentts", "cosyvoice", "voxcpm2"])
def test_commercial_tts_engines_are_allowed(engine):
    assert catalog.tts_engine_allowed(engine)


@pytest.mark.parametrize(
    "engine",
    ["omnivoice", "omnivoice-subprocess", "omnivoice-gguf", "indextts2", "supertonic3",
     "mlx-audio", "gpt-sovits", "", None],
)
def test_non_commercial_or_unreviewed_tts_engines_are_refused(engine):
    assert not catalog.tts_engine_allowed(engine)


@pytest.mark.parametrize("repo", [
    "Systran/faster-whisper-small",
    "Systran/faster-whisper-large-v3",
    "OpenMOSS-Team/MOSS-TTS-Nano",
    "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano",
    "Helsinki-NLP/opus-mt-en-es",
    "santhosh/madlad400-3b-ct2",
])
def test_whitelisted_model_repos(repo):
    assert catalog.model_repo_allowed(repo)


@pytest.mark.parametrize("repo", [
    "k2-fsa/OmniVoice",
    "Serveurperso/OmniVoice-GGUF",
    "facebook/nllb-200-distilled-600M",
    "mlx-community/Llama-OuteTTS-1.0-1B-4bit",
    "IndexTeam/IndexTTS-2.5",
    "Systran/faster-whisper-small-evil/../x",
    "",
    None,
])
def test_excluded_model_repos(repo):
    assert not catalog.model_repo_allowed(repo)


def test_only_local_translation_engines_are_offered():
    for blocked in ("nllb", "google", "google-cloud", "deepl", "microsoft", "amazon",
                    "mymemory", "openai", "", None):
        assert not catalog.translation_engine_allowed(blocked)
    assert catalog.translation_engine_allowed("argos")
    assert catalog.translation_engine_allowed("opus")


def test_disallowed_selection_falls_back_to_the_default_engine():
    assert catalog.resolve_tts_engine("omnivoice") == catalog.DEFAULT_TTS_ENGINE
    assert catalog.resolve_tts_engine(None) == catalog.DEFAULT_TTS_ENGINE
    assert catalog.resolve_tts_engine("cosyvoice") == "cosyvoice"


def test_escape_hatch_allows_everything(monkeypatch):
    monkeypatch.setenv("CALLENVOICE_ALLOW_ALL_MODELS", "1")
    assert catalog.tts_engine_allowed("omnivoice")
    assert catalog.model_repo_allowed("k2-fsa/OmniVoice")


# ── engine resolution hooks in services.tts_backend ───────────────────────

def test_active_backend_never_resolves_to_an_excluded_engine(monkeypatch):
    from services import tts_backend

    monkeypatch.setenv("OMNIVOICE_TTS_BACKEND", "omnivoice")
    assert tts_backend.active_backend_id() == catalog.DEFAULT_TTS_ENGINE
    monkeypatch.setenv("OMNIVOICE_TTS_BACKEND", "kittentts")
    assert tts_backend.active_backend_id() == "kittentts"


def test_excluded_engine_is_refused_before_loading():
    from services import tts_backend
    from services.model_acceptance import ModelLicenceNotAccepted

    cls = tts_backend.get_backend_class("omnivoice")
    with pytest.raises(catalog.ModelNotOffered) as info:
        tts_backend.ensure_engine_licence(cls)
    # Existing upstream handlers catch the licence refusal and answer 403.
    assert isinstance(info.value, ModelLicenceNotAccepted)
    assert info.value.detail()["code"] == "callen_model_not_offered"


# ── HTTP layer ─────────────────────────────────────────────────────────────

def _stub_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(CallenCatalogMiddleware)
    calls = []

    @app.get("/engines/tts")
    def tts():
        return {"active": "omnivoice", "backends": [{"id": "omnivoice"}, {"id": "moss-tts-nano"},
                                                    {"id": "indextts2"}, {"id": "kittentts"}]}

    @app.get("/engines/translation")
    def translation():
        return {"active": "argos", "engines": [{"id": "argos"}, {"id": "nllb"}, {"id": "deepl"},
                                             {"id": "mymemory"}, {"id": "openai"}]}

    @app.get("/models")
    def models():
        return {"models": [{"repo_id": "k2-fsa/OmniVoice"}, {"repo_id": "Systran/faster-whisper-small"}]}

    @app.post("/engines/select")
    async def select(body: dict):
        calls.append(("select", body))
        return {"ok": True}

    @app.post("/engines/sidecar/{engine_id}/install")
    def install(engine_id: str):
        calls.append(("install", engine_id))
        return {"status": "started"}

    @app.post("/dub/ingest-url")
    async def ingest_url(body: dict):
        calls.append(("url", body))
        return {"job_id": "x"}

    @app.post("/models/install")
    async def model_install(body: dict):
        calls.append(("model", body))
        return {"status": "install_started"}

    app.state.calls = calls
    return app


@pytest.fixture()
def stub():
    app = _stub_app()
    return app, TestClient(app)


def test_listings_hide_excluded_components(stub):
    _, client = stub
    tts = client.get("/engines/tts").json()
    assert [b["id"] for b in tts["backends"]] == ["moss-tts-nano", "kittentts"]
    assert tts["active"] == "moss-tts-nano"
    tr = client.get("/engines/translation").json()
    assert [e["id"] for e in tr["engines"]] == ["argos"]
    models = client.get("/models").json()
    assert [m["repo_id"] for m in models["models"]] == ["Systran/faster-whisper-small"]


def test_excluded_install_and_select_are_refused_without_reaching_the_router(stub):
    app, client = stub
    r = client.post("/engines/sidecar/indextts2/install")
    assert r.status_code == 403 and r.json()["detail"]["code"] == "callen_model_not_offered"
    r = client.post("/engines/select", json={"family": "tts", "backend_id": "omnivoice"})
    assert r.status_code == 403
    r = client.post("/models/install", json={"repo_id": "k2-fsa/OmniVoice"})
    assert r.status_code == 403
    assert app.state.calls == []


def test_allowed_requests_pass_through_unchanged(stub):
    app, client = stub
    assert client.post("/engines/sidecar/moss-tts-nano/install").status_code == 200
    assert client.post("/engines/select", json={"family": "tts", "backend_id": "kittentts"}).status_code == 200
    assert client.post("/engines/select", json={"family": "asr", "backend_id": "whisperx"}).status_code == 200
    assert client.post("/models/install", json={"repo_id": "Helsinki-NLP/opus-mt-en-es"}).status_code == 200
    assert [c[0] for c in app.state.calls] == ["install", "select", "select", "model"]


# ── first-run setup catalogue ──────────────────────────────────────────────

def test_setup_requires_our_default_models_and_never_omnivoice():
    models = [
        {"repo_id": "k2-fsa/OmniVoice", "required": True, "curated_on": ["all"]},
        {"repo_id": "OpenMOSS-Team/MOSS-TTS-Nano-100M"},
        {"repo_id": "Systran/faster-whisper-small"},
        {"repo_id": "Systran/faster-whisper-large-v3", "required": True},
    ]
    out = {m["repo_id"]: m for m in catalog.apply_to_model_catalogue(models)}
    assert out["k2-fsa/OmniVoice"]["required"] is False
    assert out["k2-fsa/OmniVoice"]["curated_on"] == []
    assert out["OpenMOSS-Team/MOSS-TTS-Nano-100M"]["required"] is True
    assert out["Systran/faster-whisper-small"]["required"] is True
    assert out["Systran/faster-whisper-large-v3"]["required"] is False
    # The input list is not mutated (models.yaml stays the upstream source).
    assert models[0]["required"] is True


def test_every_required_model_is_whitelisted():
    for repo in catalog.REQUIRED_MODEL_REPOS:
        assert catalog.model_repo_allowed(repo)


def test_video_url_import_is_refused(stub):
    app, client = stub
    r = client.post("/dub/ingest-url", json={"url": "https://www.youtube.com/watch?v=x"})
    assert r.status_code == 403
    assert r.json()["detail"]["id"] == "url_import"
    assert app.state.calls == []


def test_upstream_demo_voice_is_not_seeded():
    # Rendered with OmniVoice (non-commercial weights); see catalog docstring.
    assert not catalog.upstream_demo_voice_allowed()


def test_allow_all_override_restores_upstream_demo(monkeypatch):
    monkeypatch.setenv("CALLENVOICE_ALLOW_ALL_MODELS", "1")
    assert catalog.upstream_demo_voice_allowed()
