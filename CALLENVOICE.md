# CallenVoice

CallenVoice is a desktop application for dubbing and localizing video with AI,
running locally on the user's computer.

## Modification notice (AGPL-3.0 §5)

CallenVoice is a **modified version of [VoiceStudio](https://github.com/debpalash/VoiceStudio)**,
Copyright 2024-present Palash Debnath and VoiceStudio contributors, licensed
under the GNU Affero General Public License, version 3 (AGPL-3.0-only).

- Based on upstream commit `1a29929cb` (tag `upstream-base-1a29929`).
- Modified from 2026-11-02 onwards. The full list of changed upstream files and
  the reason for each change is in [docs/callen/cambios-al-original.md](docs/callen/cambios-al-original.md).
- CallenVoice as a whole remains licensed under AGPL-3.0-only. The full text is
  in [LICENSE](LICENSE); the upstream notice is kept unchanged in
  [LICENSE-NOTICE.md](LICENSE-NOTICE.md).
- Every user who receives CallenVoice, or uses it over a network, is entitled to
  the complete corresponding source code of the exact version they received.
  The link is shown in the app under Settings → About.

"VoiceStudio" is the name of the upstream project and is used here only to
credit it. CallenVoice is not affiliated with or endorsed by the VoiceStudio
maintainers.

## Third-party components and models

Code dependencies and AI model weights keep their own licences. CallenVoice
only offers models on its whitelist (`backend/callen/catalog.py`), all of which
allow commercial use. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Where CallenVoice code lives

| Path | What |
| --- | --- |
| `backend/callen/` | Product layer: model whitelist and its HTTP filter |
| `electron/src/renderer/src/callen/` | Brand theme, product scope, legal notice |
| `electron/src/main/callen/` | Update feed (off until the first CallenVoice release is published) |
| `branding/` | Logo and artwork sources |
| `scripts/callen/` | Rebranding script (`--check` fails if the old name is visible) |
| `docs/callen/` | Decisions and the log of upstream files we changed |
