import { useTranslation } from 'react-i18next';
import { SOURCE_CODE_URL, UPSTREAM_PROJECT } from './product';

/*
 * AGPL-3.0 §5 and §13: a modified version must say it is modified, keep the
 * original copyright notice, and offer users its complete source code. This
 * notice is shown in Settings → About. Strings are kept here (es/pt/en) so the
 * upstream locale files stay untouched.
 */
const COPY = {
  es: {
    title: 'Licencia y código fuente',
    modified: 'CallenVoice es una versión modificada de',
    license: 'Se distribuye bajo la licencia',
    source: 'Código fuente completo de esta versión',
    pending: 'Enlace al código fuente pendiente de publicar.',
  },
  pt: {
    title: 'Licença e código-fonte',
    modified: 'CallenVoice é uma versão modificada de',
    license: 'Distribuído sob a licença',
    source: 'Código-fonte completo desta versão',
    pending: 'Link do código-fonte ainda não publicado.',
  },
  en: {
    title: 'License and source code',
    modified: 'CallenVoice is a modified version of',
    license: 'Distributed under the',
    source: 'Complete source code of this version',
    pending: 'Source code link not published yet.',
  },
} as const;

function copyFor(language: string | undefined) {
  const base = (language ?? 'en').toLowerCase().split('-')[0];
  return base === 'es' || base === 'pt' ? COPY[base] : COPY.en;
}

export function CallenLegalNotice() {
  const { i18n } = useTranslation();
  const c = copyFor(i18n.language);
  return (
    <div data-testid="callen-legal-notice" className="space-y-1 text-right text-xs">
      <p>
        {c.modified}{' '}
        <a href={UPSTREAM_PROJECT.url} target="_blank" rel="noreferrer" className="underline">
          {UPSTREAM_PROJECT.name}
        </a>
        . {UPSTREAM_PROJECT.copyright}.
      </p>
      <p>
        {c.license} {UPSTREAM_PROJECT.license}.
      </p>
      <p>
        {SOURCE_CODE_URL ? (
          <a href={SOURCE_CODE_URL} target="_blank" rel="noreferrer" className="underline">
            {c.source}
          </a>
        ) : (
          c.pending
        )}
      </p>
    </div>
  );
}

export function callenLegalTitle(language: string | undefined): string {
  return copyFor(language).title;
}
