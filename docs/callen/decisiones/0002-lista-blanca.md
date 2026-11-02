# 0002 — Lista blanca de modelos y motores

Fecha: 2026-11-02. Estado: aceptada.

**Decisión:** CallenVoice solo ofrece modelos y motores cuya licencia permite uso
comercial, leída en la fuente original. Están en `backend/callen/catalog.py`.

**Cómo se aplica (tres capas):**
1. `CallenCatalogMiddleware` filtra los listados (`/engines/tts`, `/engines/translation`,
   `/models`) y responde 403 `callen_model_not_offered` a instalaciones y selecciones
   fuera de la lista.
2. `services.tts_backend.ensure_engine_licence` rechaza un motor excluido antes de cargar
   pesos, aunque se pida por parámetro en `/generate` o `/dub/generate`.
3. `active_backend_id` cambia una selección excluida (incluido el valor por defecto del
   original, OmniVoice) por el motor por defecto de CallenVoice, MOSS-TTS-Nano.

**Excluidos destacados:** OmniVoice (CC-BY-NC), NLLB-200 (CC-BY-NC-4.0), OuteTTS
(CC-BY-NC-SA), IndexTTS-2.5 y Supertonic-3 (condiciones a trasladar al cliente),
traducción en la nube (decisión de producto: solo local).

**Pendiente:** Argos sigue permitido de forma transitoria hasta integrar Opus-MT
(Fase 3); sus paquetes no declaran licencia.

**Para desarrollo:** `CALLENVOICE_ALLOW_ALL_MODELS=1` desactiva la lista. Nunca en
una versión distribuida. Las suites de tests del original la usan para seguir probando
todos los motores; `backend/tests/test_callen_catalog.py` prueba la lista activa.
