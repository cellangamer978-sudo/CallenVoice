"""Replace the user-visible product name VoiceStudio -> CallenVoice.

Only the standalone word is replaced (not identifiers such as VoiceStudioBridge,
not the X-VoiceStudio-CSRF header, not lowercase voicestudio URLs or IPC keys).
Copyright and attribution files are excluded on purpose: the AGPL notices of
the original project must stay intact.

Usage: python scripts/callen/rebrand.py [--check]
--check exits 1 if any replaceable occurrence remains (used by CI).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Not after "@" (e-mail), not before ".ext" (file names such as VoiceStudio.log).
WORD = re.compile(r"(?<![A-Za-z0-9_\-/.@])VoiceStudio(?![A-Za-z0-9_\-]|\.[a-z])")
NEW = "CallenVoice"
# Locale strings only: compounds ("VoiceStudio-Server") and folder paths
# ("~/VoiceStudio", "C:\\VoiceStudio") are user-visible there, while in code the
# same shapes are identifiers or URLs.
LOCALE_WORD = re.compile(r"(?:(?<![A-Za-z0-9_\-/.@])|(?<=~/)|(?<=\\))VoiceStudio(?=-[A-Za-z]|s(?![A-Za-z])|[^A-Za-z0-9_\-.]|\.(?![a-z])|$)")

INCLUDE = [
    ("electron/src", {".ts", ".tsx", ".js", ".jsx", ".mjs", ".json", ".html", ".css"}),
    ("electron/scripts", {".mjs", ".js", ".ts"}),
    ("backend", {".py"}),
]
# Files whose wording is about the upstream project itself, or that carry
# attribution we are required to keep.
EXCLUDE_PARTS = {"node_modules", "__pycache__", "migrations", "callen"}
EXCLUDE_FILES = {
    # The demo transcript must match the bundled audio; legacy names are migration keys.
    "backend/core/onboarding.py",
    "backend/core/engine_licenses.py",
    "backend/services/model_licenses.py",
    "electron/T3CODE-LICENSE.txt",
    # "VoiceStudio" there is the upstream gallery's author id in remote data.
    "electron/src/renderer/src/features/gallery/community-view.test.tsx",
    # Lists the (hidden) integration directory entry named after the upstream API.
    "electron/src/renderer/src/features/integrations/integrations-page.test.tsx",
}
# Hidden upstream features whose ids and tests are keyed on the upstream name.
EXCLUDE_DIRS = (
    # The integration directory derives its slugs from these names.
    "electron/src/shared/config/voice-ai-directory.js",
    "electron/src/shared/config/integration-catalog.js",
)


def candidates():
    for rel, exts in INCLUDE:
        for p in (ROOT / rel).rglob("*"):
            if not p.is_file() or p.suffix not in exts:
                continue
            if EXCLUDE_PARTS & set(p.parts):
                continue
            r = p.relative_to(ROOT).as_posix()
            if r in EXCLUDE_FILES or r.startswith(EXCLUDE_DIRS):
                continue
            yield p, r


def main(check: bool) -> int:
    changed = total = 0
    for p, r in candidates():
        text = p.read_text(encoding="utf-8")
        new, n = WORD.subn(NEW, text)
        if "/locales/" in r and r.endswith(".json"):
            new, n2 = LOCALE_WORD.subn(NEW, new)
            n += n2
        if n:
            total += n
            changed += 1
            if not check:
                p.write_text(new, encoding="utf-8")
    verb = "remaining" if check else "replaced"
    print(f"{total} occurrences {verb} in {changed} files")
    return 1 if (check and total) else 0


if __name__ == "__main__":
    sys.exit(main("--check" in sys.argv))
