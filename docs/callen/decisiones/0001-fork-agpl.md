# 0001 — Fork AGPL de VoiceStudio

Fecha: 2026-11-02. Estado: aceptada.

**Decisión:** CallenVoice es un fork de VoiceStudio distribuido bajo AGPL-3.0-only,
entregando el código fuente completo de cada versión a cada cliente.

**Por qué:** es la única vía que no requiere negociar con Yupcha Softwares (titular
del copyright, que vende una licencia comercial aparte). Permite cobrar por el
producto, el instalador, el soporte y los servicios.

**Consecuencias:**
- Cualquier cliente puede redistribuir el código; la diferenciación es el producto,
  la experiencia en español y el soporte, no el código.
- Las dependencias GPL (pedalboard, phonemizer, eSpeak NG, binarios FFmpeg con x264)
  son compatibles y no hace falta reemplazarlas.
- Se conservan todos los avisos del original; la app muestra que es una versión
  modificada y enlaza al código fuente (Configuración → Acerca de).
- Si más adelante se quiere cerrar el código: licencia comercial de Yupcha
  (hi@voicestudio.sh) y reemplazo de las dependencias GPL.
