# Cambios a archivos del original (VoiceStudio)

Base: commit `1a29929cb` (etiqueta `upstream-base-1a29929`). Cada archivo del
original que modificamos queda acá, con el motivo. Al mezclar una versión nueva
del original, revisar primero estos archivos.

## Cambio mecánico de nombre

`scripts/callen/rebrand.py` reemplaza la palabra suelta "VoiceStudio" por
"CallenVoice" en textos de `electron/src` y `backend` (unos 300 archivos, sobre
todo los 44 archivos de idiomas). No toca identificadores (`VoiceStudioBridge`),
el encabezado `X-VoiceStudio-CSRF`, claves internas en minúscula
(`voicestudio`), avisos de licencia ni la sección oculta de integraciones.
Después de cada mezcla con el original: `python scripts/callen/rebrand.py` y
luego `--check`, que falla si quedó algún texto visible con el nombre viejo.

## Cambios a mano

| Archivo | Cambio | Motivo |
| --- | --- | --- |
| `config/app.json` | `productName` CallenVoice, `appId` com.callenvoice.desktop | Identidad de la app, nombre del instalador y carpeta de datos propia |
| `config/distributions.mjs` | Texto de error con el nombre nuevo | Marca |
| `electron/package.json` | Descripción, autor; sin `homepage` | Marca. El nombre interno `voicestudio-electron` se mantiene: lo usan scripts de empaquetado y no se ve en Windows |
| `electron/electron-builder.config.mjs` | Canal de actualización desde `CALLENVOICE_UPDATE_REPO`; si falta, un host `.invalid` | Que ninguna compilación descargue versiones del original |
| `electron/src/main/distribution.ts` | Actualizaciones apagadas sin canal propio | Idem |
| `electron/src/main/updater.ts` | No lista versiones del original sin canal propio | Idem |
| `electron/src/main/reset-data.ts` | Reconoce la carpeta `callenvoice` | "Restablecer datos" debe reconocer nuestra carpeta |
| `electron/src/main/backend.ts` | Reconoce la carpeta `callenvoice` al elegir ubicación | Idem |
| `electron/src/renderer/src/main.tsx` | Importa `callen/brand.css` | Paleta negra y naranja |
| `electron/src/renderer/src/routes/index.ts` | Redirige rutas ocultas al inicio | Alcance v1: solo doblaje |
| `electron/src/renderer/src/components/app-shell/workspace-menu.tsx` | Filtra el menú con `visibleDestinations` | Idem |
| `electron/src/renderer/src/features/settings/settings-page.tsx` | Oculta Soporte (donaciones y Pro del original) | Idem |
| `electron/src/renderer/src/features/settings/diagnostics-settings.tsx` | Agrega el aviso de licencia y código fuente | AGPL-3.0 §5 y §13 |
| `electron/vite.config.ts` | Variable de entorno de prueba para el actualizador | Los tests del original suponen un canal configurado |
| `backend/main.py` | Registra `CallenCatalogMiddleware` | Lista blanca de modelos |
| `backend/services/tts_backend.py` | `active_backend_id` y `ensure_engine_licence` consultan la lista blanca | Ningún motor excluido puede cargarse |
| `conftest.py` | `CALLENVOICE_ALLOW_ALL_MODELS=1` para las suites del original | Siguen probando todos los motores; nuestros tests la desactivan |
| `electron/build/icons/*`, `electron/public/favicon.svg`, `electron/public/signal-field.webp`, `docs/logo.png` | Logo y fondo nuevos | Marca (fuentes en `branding/`) |
| `backend/services/model_catalogue.py` | `KNOWN_MODELS` pasa por `apply_to_model_catalogue` | El primer arranque pide MOSS-TTS-Nano y Whisper small, nunca OmniVoice |
| `electron/src/renderer/src/features/settings/performance-model-packs.ts` | Los paquetes de modelos usan MOSS-TTS-Nano en lugar de OmniVoice | Idem |
| `electron/src/renderer/src/features/home/home-page.tsx` | Título y descripción propios; solo destinos dentro del alcance; sin avatares de colaboradores ni enlace a voicestudio.sh | Marca y alcance |
| `electron/src/renderer/src/components/app-shell/support-shortcut.tsx` | Oculta "Obtener Pro" y la estrella de GitHub | Son del proyecto original |
| `electron/src/renderer/src/features/dub/dub-page.tsx` | Oculta el panel de demostración | Demos generadas con OmniVoice (no comercial) |
| `electron/src/renderer/src/features/dub/dub-source-panel.tsx`, `dub-source-row.tsx` | Sin importación por URL | Riesgo legal (términos de plataformas, copyright) |
| `electron/src/renderer/src/components/command-palette.tsx` | Filtra comandos y ajustes con `commandVisible` | La paleta no debe abrir secciones ocultas |
| `backend/main.py` (siembra de la voz demo) | Solo siembra la "Demo Voice" si `upstream_demo_voice_allowed()` | Generada con OmniVoice (no comercial), sin licencia declarada |
| `backend/core/analytics.py`, `electron/src/shared/utils/analytics.ts` | Sin clave de PostHog por defecto | La clave del original enviaba eventos a la cuenta del proyecto original; sin destino, la app no pregunta ni envía nada |
| `electron/src/renderer/src/features/dub/dub-translation-panel.tsx` | Oculta el traductor "Agent" (`ALLOW_AGENT_TRANSLATION`) | Decisión: solo traducción local; el agente puede usar servicios en la nube |
| `backend/api/routers/setup/models.py` | Textos de los presets de hardware describen MOSS-TTS-Nano | El cambio de nombre había dejado "CallenVoice (required)" donde iba el modelo OmniVoice; ya no nombran motores excluidos |
| `electron/src/shared/utils/errorDocsMap.ts`, `components/backend-gate.tsx`, `components/app-shell/voice-studio-agent.tsx`, `lib/expression.ts`, `features/settings/mcp-bindings-settings.tsx` | Enlaces pasan por `@shared/callen/repo` | Un solo lugar para la dirección del repositorio; sin repositorio publicado se ocultan descarga y clonado |
| `electron/tsconfig.web.json` | Incluye `src/shared/callen/repo.ts` | Lo exige el proyecto TypeScript |
| `electron/build/icons/*` | Regenerados con `scripts/callen/build_icons.mjs` (macOS con el margen de Apple, 824/1024) | El ícono de macOS llenaba todo el lienzo |
| `mobile/contract/strings.mobile.en.json`, tokens generados de `mobile/` | Sincronizados con los textos y colores nuevos | Las apps móviles no son parte del producto, pero sus tests comparan contra la interfaz de escritorio |
| `backend/config/model_licenses.json`, `docs/licensing/model-license-data.json` | Entrada de MADLAD-400 CT2 y datos regenerados | Candidato de traducción de la Fase 3 |
| `README.md` | Reemplazado por el README de CallenVoice (en español): qué hace, estado, requisitos, ejecución desde el código, licencia, créditos a VoiceStudio y uso responsable | Es la portada del repositorio público. El README del original sigue en el historial y en su repositorio; sus traducciones quedan sin cambios en `docs/readme/` |
| `pyproject.toml` | `Homepage`, `Repository`, `Documentation` y `Bug Tracker` apuntan a cellangamer978-sudo/CallenVoice; nuevo `Upstream Project` con el original | Enlace al código fuente (AGPL) y enlaces a la documentación del backend (`core/links.py` lee `Repository`) |
| `electron/src/shared/callen/repo.ts` | `CALLEN_REPO_URL` con nuestro repositorio; `CALLEN_HAS_RELEASES = false` mantiene ocultos los enlaces de descarga | Aún no hay versiones publicadas: un enlace a una página de descargas vacía no sirve |
| `electron/src/shared/utils/contactLinks.js` | `REPO_URL` de nuestro repositorio | Los botones "Reportar error" (pantalla de error del backend, detalles de un fallo, pantalla de error general) abrían reportes en el repositorio de VoiceStudio |
| `backend/core/db.py`, `backend/services/model_manager.py` | Los mensajes de error enlazan nuestros reportes vía `core.links` | Idem |
| `docs/install/agent.md`, `docs/migration/real-time-voice-cloning.md` | Anclas al README nuevo | Las secciones del README anterior ya no existen |
| `scripts/update_contributors.py` | Solo actualiza las traducciones de `docs/readme/` | El README nuevo no tiene la fila de avatares del original |

### Tests del original adaptados

| Archivo | Cambio |
| --- | --- |
| `electron/src/renderer/src/components/app-shell/workspace-menu.test.tsx` | Usa secciones visibles (Voces guardadas, Lotes, Proyectos) y verifica que las ocultas no aparecen |
| `electron/src/renderer/src/features/home/home-page.test.tsx` | Reescrito para el Inicio de CallenVoice |
| `electron/src/renderer/src/features/settings/model-packs.test.tsx`, `performance-model-packs.test.ts` | Modelo de voz por defecto: MOSS-TTS-Nano |
| `electron/src/shared/test/LanguageSwitchPrompt.test.jsx` | Expresión regular con el nombre nuevo |
| `tests/test_voicestudio_branding.py` | La nota de modificación debe acreditar a VoiceStudio (el test esperaba el nombre nuevo) |
| `tests/test_gitleaks_allowlist.py` | Lee la clave permitida de `.gitleaks.toml`: ya no está en el código, pero sigue en el historial heredado |
| `tests/test_no_committed_analytics_token.py`, `tests/test_analytics_lifecycle.py`, `tests/test_analytics_optin.py` | Prueban la decisión contraria a la del original (#1193): sin destino por defecto |
| `tests/test_model_license_workflow.py` | Cuentas de modelos y pines con la entrada de MADLAD-400 |
| `tests/test_agent_skill_discovery.py`, `tests/test_issue_fixes.py`, `tests/test_sponsors_lockstep.py`, `tests/test_readme_translations.py`, `tests/test_cla_workflow.py` | Exigían en el README contenido del original (instalar sus skills, su Discord, sus patrocinadores, sus traducciones, su CLA). Ahora verifican que el README de CallenVoice **no** lo promocione; las traducciones del original se siguen verificando |
| `tests/test_voicestudio_branding.py` | Logo del README desde `branding/logo.svg`; metadatos del paquete con nuestro repositorio y el original acreditado |
| `tests/test_db_migration_safety.py`, `tests/test_wedge_vs_slow_hardware_1416.py`, `electron/.../bugReport.test.js`, `errorDocsMap.test.ts`, `error-boundary.test.tsx`, `pipeline-failure.test.tsx`, `github-star.test.tsx`, `support-settings.test.tsx` | Esperan enlaces a nuestro repositorio |
| `electron/.../voice-studio-agent.test.tsx` | El comando de clonado usa nuestro repositorio |
| `backend/tests/test_ram_preflight_1618.py` | Con 16 GB recomendados, 12 GB ahora da advertencia; 16 GB (≈15,8 utilizables) pasa limpio |

## Pendiente antes de distribuir

- Al publicar la primera versión (Fase 5): `CALLEN_HAS_RELEASES = true` en `electron/src/shared/callen/repo.ts` y `CALLEN_UPDATE_REPO = 'cellangamer978-sudo/CallenVoice'` en `electron/src/main/callen/updates.ts`. Se activan juntos, cuando exista un instalador firmado que ofrecer.
- Textos del original fuera de la interfaz que todavía dicen VoiceStudio: `docs/` (incluye `docs/install/`, que describe el instalador por script de voicestudio.sh, que instala el original), `backend/config/models.yaml` (etiquetas de modelos ocultos), instaladores por script (`scripts/install*`).
- `.github/CONTRIBUTING.md` y la plantilla de pull request piden firmar el CLA del original. Hace falta una política de contribuciones propia antes de aceptar aportes de terceros.
- `electron/src/shared/pages/ContactPage.jsx` y `contactLinks.js` (correo, Discord, sitio web, licencia comercial) siguen con los datos del original; hoy solo se usan en secciones ocultas.
- Demos de audio y video del original (`backend/assets/samples`, `docs/media`): generadas con OmniVoice; ya no se muestran ni se siembran. Falta grabar una voz demo propia con consentimiento firmado.
- Configuración → Modelos → LLM sigue permitiendo cargar claves de servicios en la nube; revisar en la Fase 3 junto con el traductor Opus-MT.
- El motor MOSS-TTS-Nano necesita su entorno propio (≈5 GB) además de los pesos: hoy se instala desde Configuración → Modelos; en la Fase 4 viene en el instalador.

### Fase 2 — Inicio y textos
- `electron/src/renderer/src/features/home/home-page.tsx`: los íconos de acceso usan un único tono de marca (`bg-primary/10 text-primary`) en lugar de la paleta multicolor heredada.
- `electron/src/renderer/src/i18n/locales/es.json`: "vídeo" → "video" (forma latinoamericana). pt.json y gl.json no se tocan (allí "vídeo" es correcto).
- Nuevo `electron/src/renderer/src/callen/project-steps.tsx` (+ test): indicador de pasos del proyecto (Importar → Procesar → Idiomas → Editor → Voces → Generar → Exportar; el Inicio es el 8.º, fuera del proyecto). Solo lee `session.phase`; no cambia comportamiento. Orden ajustado al flujo real (la transcripción ocurre antes de elegir idioma), distinto del orden del plan de Fase 1.
- `electron/src/renderer/src/features/dub/dub-page.tsx`: inserta `<ProjectSteps>` bajo la cabecera. Sin otros cambios.
- `electron/src/renderer/src/callen/brand.css`: las tarjetas del Inicio usan `--callen-orange` como acento (antes azul/violeta/verde agua por destino). Override en nuestra capa; `home-page.css` sin tocar. Verificado con captura (Inicio y Doblaje, tema oscuro).
- `features/dub/dub-section.tsx`: `DubStepHeading` ya no muestra número (un punto naranja en su lugar) para no chocar con la barra de pasos; la prop `step` se conserva como `data-step`.
- `i18n/locales/es.json`: "cinemático" → "Cinemático"; "Cinematic"/"Autofit" sueltos en textos en español → "Cinemático"/"Ajuste automático"; "utiliza el LLM" → "usa un modelo de lenguaje".
- Barra de pasos navegable: `ProjectSteps` acepta `onSelect`; `scrollToProjectStep` lleva a la sección. `dub-page.tsx`: cinco paneles envueltos en `<div data-callen-step="…" className="contents">` (sin cambio de layout) y `data-callen-step="generate"` en el botón Generar. "Procesar" lleva al panel de carga. Tests unitarios; el desplazamiento real con un proyecto cargado no se verificó en pantalla.

### Fase 2 — Proveedores LLM solo locales
- `backend/callen/catalog.py`: `llm_provider_allowed()` → solo proveedores con `local=True` (Ollama, LM Studio). Justificación: la app promete procesamiento local ("sin nube"); los proveedores en la nube y las CLIs de agentes enviarían transcripciones a terceros. `CALLENVOICE_ALLOW_ALL_MODELS=1` los reactiva para desarrollo.
- `backend/callen/middleware.py`: filtra `GET /api/settings/llm-providers` y rechaza (403) `PUT /api/settings/llm-providers/{id}`, `POST …/{id}/connect|test` y `POST …/active` para proveedores no locales. Ahora también inspecciona PUT. Routers originales sin tocar.
- `backend/tests/test_callen_catalog.py`: 2 tests nuevos. Verificado contra el backend real: la lista devuelve solo `ollama` y `lmstudio`.
- Limitación conocida: el proveedor "custom" (endpoint OpenAI-compatible propio) queda bloqueado aunque apunte a localhost.
- `features/settings/settings-nav.tsx`: oculta el botón "Soporte" (donaciones al original), ya que `/settings/support` es una sección oculta.
- Lotes y Configuración: revisados con capturas; ya usaban la paleta negro/naranja, sin cambios de color.
