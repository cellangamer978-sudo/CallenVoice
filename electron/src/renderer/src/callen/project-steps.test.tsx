import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { PROJECT_STEPS, ProjectSteps, currentStep } from './project-steps';

const at = (s: (typeof PROJECT_STEPS)[number]) => PROJECT_STEPS.indexOf(s);
const seg = (translations?: Record<string, string>) => ({ translations });

describe('currentStep', () => {
  it('maps every session phase to a project step', () => {
    expect(currentStep({ phase: 'idle', jobId: null, segments: [] })).toBe(at('import'));
    expect(currentStep({ phase: 'transcribing', jobId: 'j', segments: [] })).toBe(at('process'));
    expect(currentStep({ phase: 'editing', jobId: 'j', segments: [seg()] })).toBe(at('languages'));
    expect(currentStep({ phase: 'translating', jobId: 'j', segments: [seg()] })).toBe(
      at('languages'),
    );
    expect(currentStep({ phase: 'editing', jobId: 'j', segments: [seg({ es: 'hola' })] })).toBe(
      at('editor'),
    );
    expect(currentStep({ phase: 'generating', jobId: 'j', segments: [] })).toBe(at('generate'));
    expect(currentStep({ phase: 'done', jobId: 'j', segments: [] })).toBe(at('export'));
  });
});

describe('ProjectSteps', () => {
  it('marks the current step for assistive technology', () => {
    render(<ProjectSteps phase="generating" jobId="j" segments={[]} />);
    const current = screen.getByTestId('callen-project-steps').querySelector('[aria-current="step"]');
    expect(current?.getAttribute('data-state')).toBe('current');
    expect(screen.getAllByRole('listitem')).toHaveLength(PROJECT_STEPS.length);
  });
});

describe('step navigation', () => {
  it('calls onSelect with the clicked step', async () => {
    const { fireEvent } = await import('@testing-library/react');
    const picked: string[] = [];
    render(<ProjectSteps phase="idle" jobId={null} segments={[]} onSelect={(s) => picked.push(s)} />);
    fireEvent.click(screen.getByRole('button', { name: /Voices|Voces|Vozes/ }));
    expect(picked).toEqual(['voices']);
  });

  it('scrolls to the section inside a display:contents anchor', async () => {
    const { scrollToProjectStep } = await import('./project-steps');
    const root = document.createElement('div');
    root.innerHTML = '<div data-callen-step="import" class="contents"><section></section></div>';
    const section = root.querySelector('section') as HTMLElement;
    let scrolled = false;
    section.scrollIntoView = () => {
      scrolled = true;
    };
    expect(scrollToProjectStep('process', root)).toBe(true);
    expect(scrolled).toBe(true);
    expect(scrollToProjectStep('export', root)).toBe(false);
  });
});
