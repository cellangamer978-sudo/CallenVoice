# Third-party notices

CallenVoice includes or downloads the components below. Each keeps its own
licence. This list covers what CallenVoice **offers**; models excluded by the
whitelist (`backend/callen/catalog.py`) are not offered and are not listed.

Status: draft for Phase 2. The full per-package list (≈300 Python and ≈1,150
JavaScript packages) must be generated from `uv.lock` and `bun.lock` before the
first release, together with the FFmpeg/x264 notices for the PyAV wheels
(see `docs/licensing/pyav-15.1.0-audit.md`).

## Application code

| Component | Licence | Notes |
| --- | --- | --- |
| VoiceStudio (upstream of CallenVoice) | AGPL-3.0-only | © Palash Debnath and VoiceStudio contributors |
| OmniVoice Python package (`omnivoice/`) | Apache-2.0 | Code only; its CC-BY-NC weights are not offered |
| T3 Code shell components | MIT | `electron/T3CODE-LICENSE.txt` |
| pedalboard | GPL-3.0 | Compatible with AGPL distribution |
| phonemizer-fork, eSpeak NG | GPL-3.0 | Compatible with AGPL distribution |
| num2words, lameenc, soxr | LGPL | |
| Inter, Source Serif 4, IBM Plex Mono fonts | OFL-1.1 | |

## AI models offered (whitelist)

| Model | Use | Licence | Source |
| --- | --- | --- | --- |
| Whisper / faster-whisper (Systran conversions) | Transcription | MIT | huggingface.co/Systran |
| HTDemucs | Voice/music separation | MIT | github.com/facebookresearch/demucs |
| MOSS-TTS-Nano + MOSS Audio Tokenizer Nano | Voice cloning | Apache-2.0 | huggingface.co/OpenMOSS-Team |
| KittenTTS mini | Preset English voices | Apache-2.0 | huggingface.co/KittenML |
| Fun-CosyVoice3-0.5B-2512 | Voice cloning (16 GB / GPU) | Apache-2.0 | huggingface.co/FunAudioLLM |
| VoxCPM2 | Voice cloning (16 GB / GPU) | Apache-2.0 | huggingface.co/openbmb |
| Opus-MT | Translation | Apache-2.0 | huggingface.co/Helsinki-NLP |
| MADLAD-400 3B (CTranslate2) | Translation, high quality | Apache-2.0 | huggingface.co/santhosh/madlad400-3b-ct2 |
| AudioSeal | Watermark | MIT | github.com/facebookresearch/audioseal |

Pending review before release: Argos Translate language packages (no licence
declared in the package; kept temporarily until Opus-MT is integrated).
