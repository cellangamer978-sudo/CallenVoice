"""Opus-MT (Helsinki-NLP MarianMT) offline translation for CallenVoice.

Runs on CPU through `transformers`, which is already a core dependency, so it
adds no new package. Weights download from Hugging Face on first use into the
normal HF cache (whitelisted as ``Helsinki-NLP/opus-mt-*``).

Licences (checked on the model cards, 2026-11): opus-mt-en-es, opus-mt-es-en
and opus-mt-ROMANCE-en are Apache-2.0; opus-mt-tc-big-en-pt is CC-BY-4.0, which
requires attribution (see THIRD_PARTY_NOTICES.md).

Pairs without a direct model pivot through English (es → en → pt).
"""
from __future__ import annotations

import threading

#: (source, target) → (repo, target-language token or None)
DIRECT_PAIRS: dict[tuple[str, str], tuple[str, str | None]] = {
    ("en", "es"): ("Helsinki-NLP/opus-mt-en-es", None),
    ("es", "en"): ("Helsinki-NLP/opus-mt-es-en", None),
    ("en", "pt"): ("Helsinki-NLP/opus-mt-tc-big-en-pt", ">>por<<"),
    ("pt", "en"): ("Helsinki-NLP/opus-mt-ROMANCE-en", None),
}
SUPPORTED_LANGS = frozenset(code for pair in DIRECT_PAIRS for code in pair)
_BATCH = 8

_lock = threading.Lock()
_loaded: dict[str, tuple[object, object]] = {}


def base_lang(code: str | None) -> str:
    """'es-419' / 'pt_BR' / 'Spanish' → 'es' / 'pt' / 'es'."""
    value = (code or "").strip().lower().replace("_", "-")
    names = {"english": "en", "spanish": "es", "portuguese": "pt"}
    return names.get(value, value.split("-")[0])


def route(source: str, target: str) -> list[tuple[str, str | None]] | None:
    """Model chain for a pair, or None when Opus-MT cannot translate it."""
    src, tgt = base_lang(source), base_lang(target)
    if src == tgt:
        return []
    if (src, tgt) in DIRECT_PAIRS:
        return [DIRECT_PAIRS[(src, tgt)]]
    if (src, "en") in DIRECT_PAIRS and ("en", tgt) in DIRECT_PAIRS:
        return [DIRECT_PAIRS[(src, "en")], DIRECT_PAIRS[("en", tgt)]]
    return None


def _model(repo: str):
    with _lock:
        if repo not in _loaded:
            from transformers import MarianMTModel, MarianTokenizer

            tokenizer = MarianTokenizer.from_pretrained(repo)
            model = MarianMTModel.from_pretrained(repo)
            model.eval()
            _loaded[repo] = (tokenizer, model)
        return _loaded[repo]


def _run(repo: str, token: str | None, texts: list[str]) -> list[str]:
    import torch

    tokenizer, model = _model(repo)
    out: list[str] = []
    for i in range(0, len(texts), _BATCH):
        chunk = [f"{token} {t}" if token else t for t in texts[i : i + _BATCH]]
        batch = tokenizer(chunk, return_tensors="pt", padding=True, truncation=True)
        with torch.inference_mode():
            generated = model.generate(**batch, num_beams=4, max_new_tokens=256)
        out.extend(tokenizer.batch_decode(generated, skip_special_tokens=True))
    return out


def translate(texts: list[str], source: str, target: str) -> list[str]:
    chain = route(source, target)
    if chain is None:
        raise ValueError(f"Opus-MT has no model for {source} → {target}")
    for repo, token in chain:
        texts = _run(repo, token, texts)
    return texts


def unload() -> None:
    with _lock:
        _loaded.clear()
