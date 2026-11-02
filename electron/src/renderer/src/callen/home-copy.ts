/** Home headline for CallenVoice (es/pt/en), kept out of the upstream locales. */
const COPY = {
  es: {
    title: 'Dobla y localiza tus videos',
    subtitle:
      'Traduce, dobla con voces clonadas y exporta subtítulos, todo en tu computadora. Sin nube y sin cuentas.',
  },
  pt: {
    title: 'Duble e localize seus vídeos',
    subtitle:
      'Traduza, duble com vozes clonadas e exporte legendas, tudo no seu computador. Sem nuvem e sem contas.',
  },
  en: {
    title: 'Dub and localize your videos',
    subtitle:
      'Translate, dub with cloned voices and export subtitles, all on your computer. No cloud, no accounts.',
  },
} as const;

export function callenHomeCopy(language: string | undefined) {
  const base = (language ?? 'en').toLowerCase().split('-')[0];
  return base === 'es' || base === 'pt' ? COPY[base] : COPY.en;
}

/** Last setup step (dictation setup is out of the v1 scope). */
const READY_COPY = {
  es: 'Todo listo. Entra al estudio para crear tu primer proyecto de doblaje.',
  pt: 'Tudo pronto. Entre no estúdio para criar seu primeiro projeto de dublagem.',
  en: 'All set. Enter the studio to create your first dubbing project.',
} as const;

export function callenSetupReadyCopy(language: string | undefined): string {
  const base = (language ?? 'en').toLowerCase().split('-')[0];
  return base === 'es' || base === 'pt' ? READY_COPY[base] : READY_COPY.en;
}
