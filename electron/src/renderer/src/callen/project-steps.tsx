import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/utils';

/*
 * CallenVoice: the dubbing project's steps, shown above the Dub page so the user
 * always knows where the project is. The order follows the real pipeline of the
 * upstream page (transcription runs before the target language is chosen).
 * Purely presentational: it reads the session phase and changes no behaviour.
 * Strings live here (es/pt/en) so the upstream locale files stay untouched.
 */
export const PROJECT_STEPS = [
  'import',
  'process',
  'languages',
  'editor',
  'voices',
  'generate',
  'export',
] as const;
export type ProjectStep = (typeof PROJECT_STEPS)[number];

const COPY: Record<'es' | 'pt' | 'en', Record<ProjectStep | 'label', string>> = {
  es: {
    label: 'Pasos del proyecto',
    import: 'Importar',
    process: 'Procesar',
    languages: 'Idiomas',
    editor: 'Editor',
    voices: 'Voces',
    generate: 'Generar',
    export: 'Exportar',
  },
  pt: {
    label: 'Etapas do projeto',
    import: 'Importar',
    process: 'Processar',
    languages: 'Idiomas',
    editor: 'Editor',
    voices: 'Vozes',
    generate: 'Gerar',
    export: 'Exportar',
  },
  en: {
    label: 'Project steps',
    import: 'Import',
    process: 'Process',
    languages: 'Languages',
    editor: 'Editor',
    voices: 'Voices',
    generate: 'Generate',
    export: 'Export',
  },
};

/** Where each step lives on the Dub page (`data-callen-step` anchors). */
const STEP_ANCHOR: Record<ProjectStep, string> = {
  import: 'import',
  process: 'import',
  languages: 'languages',
  editor: 'editor',
  voices: 'voices',
  generate: 'generate',
  export: 'export',
};

/** Scrolls the Dub page to a step's section. Returns false when it isn't on screen. */
export function scrollToProjectStep(step: ProjectStep, root: ParentNode = document): boolean {
  const anchor = root.querySelector(`[data-callen-step="${STEP_ANCHOR[step]}"]`);
  // Anchors are `display: contents` wrappers, which have no box of their own.
  const target = anchor?.getAttribute('class')?.includes('contents')
    ? anchor.firstElementChild
    : anchor;
  if (!(target instanceof HTMLElement)) return false;
  target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  return true;
}

export interface StepInput {
  phase: string;
  jobId: string | null;
  segments: Array<{ translations?: Record<string, string> }>;
}

/** Index in PROJECT_STEPS of the step the project is currently on. */
export function currentStep(s: StepInput): number {
  const at = (step: ProjectStep) => PROJECT_STEPS.indexOf(step);
  switch (s.phase) {
    case 'preparing':
    case 'importing':
    case 'cleaning':
    case 'transcribing':
    case 'mirroring':
      return at('process');
    case 'translating':
      return at('languages');
    case 'generating':
      return at('generate');
    case 'done':
      return at('export');
    case 'editing': {
      const translated = s.segments.some((seg) => Object.keys(seg.translations ?? {}).length > 0);
      return at(translated ? 'editor' : 'languages');
    }
    default:
      return s.jobId ? at('process') : at('import');
  }
}

export function ProjectSteps({ onSelect, ...props }: StepInput & { onSelect?: (step: ProjectStep) => void }) {
  const { i18n } = useTranslation();
  const base = (i18n.language ?? 'en').toLowerCase().split('-')[0];
  const c = base === 'es' || base === 'pt' ? COPY[base] : COPY.en;
  const current = currentStep(props);
  return (
    <ol
      aria-label={c.label}
      data-testid="callen-project-steps"
      className="flex flex-wrap items-center gap-x-1 gap-y-1 text-xs"
    >
      {PROJECT_STEPS.map((step, i) => {
        const state = i < current ? 'done' : i === current ? 'current' : 'todo';
        return (
          <li
            key={step}
            data-state={state}
            aria-current={state === 'current' ? 'step' : undefined}
            className="flex items-center gap-1"
          >
            <span
              className={cn(
                'grid size-5 place-items-center rounded-full text-[11px] font-semibold',
                state === 'current' && 'bg-primary text-primary-foreground',
                state === 'done' && 'bg-primary/15 text-primary',
                state === 'todo' && 'bg-muted text-muted-foreground',
              )}
            >
              {i + 1}
            </span>
            {onSelect ? (
              <button
                type="button"
                onClick={() => onSelect(step)}
                className={cn(
                  'rounded px-0.5 hover:text-primary focus-visible:outline-2 focus-visible:outline-primary',
                  state === 'current' ? 'font-medium text-foreground' : 'text-muted-foreground',
                )}
              >
                {c[step]}
              </button>
            ) : (
              <span
                className={cn(
                  state === 'current' ? 'font-medium text-foreground' : 'text-muted-foreground',
                )}
              >
                {c[step]}
              </span>
            )}
            {i < PROJECT_STEPS.length - 1 && (
              <span aria-hidden="true" className="mx-1 h-px w-3 bg-border" />
            )}
          </li>
        );
      })}
    </ol>
  );
}
