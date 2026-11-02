# 0003 — Actualizaciones automáticas apagadas hasta tener canal propio

Fecha: 2026-11-02. Estado: aceptada.

**Problema:** el actualizador del original consulta las versiones de
`debpalash/VoiceStudio`. Sin cambios, una instalación de CallenVoice ofrecería
instalar VoiceStudio encima.

**Decisión:**
- `electron/src/main/callen/updates.ts` define el repositorio de versiones de
  CallenVoice (`CALLEN_UPDATE_REPO` o la variable `CALLENVOICE_UPDATE_REPO`, formato `owner/repo`).
- Mientras esté vacío, `distribution.ts` informa que las actualizaciones no están
  disponibles y el listado de versiones devuelve vacío.
- `electron-builder.config.mjs` escribe como canal un host `.invalid` (reservado, nunca
  resuelve) si no hay repositorio configurado.
- No se usa ningún nombre de cuenta inventado: si alguien lo registrara, podría
  enviar actualizaciones a nuestros clientes.

**Pendiente:** cuando exista el repositorio de versiones, completar `CALLEN_UPDATE_REPO`,
reemplazar en `updater.ts` las URLs de la API de versiones y probar una actualización
real entre dos versiones firmadas (Fase 4).
