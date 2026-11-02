import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { HIDDEN_ROUTES, commandVisible, isHiddenRoute, visibleDestinations } from './product';
import { CallenLegalNotice } from './legal-notice';

describe('CallenVoice product scope', () => {
  it('keeps the dubbing workflow visible', () => {
    for (const route of ['/', '/dub', '/batch', '/projects', '/clone', '/personas', '/settings']) {
      expect(isHiddenRoute(route)).toBe(false);
    }
  });

  it('hides out-of-scope upstream sections and their sub-routes', () => {
    for (const route of HIDDEN_ROUTES) expect(isHiddenRoute(route)).toBe(true);
    expect(isHiddenRoute('/integrations/claude-code')).toBe(true);
    expect(isHiddenRoute('/pro/')).toBe(true);
    expect(isHiddenRoute('/settings/support')).toBe(true);
    expect(isHiddenRoute('/settings/models')).toBe(false);
    expect(isHiddenRoute('/promo')).toBe(false);
  });

  it('filters navigation entries by route', () => {
    const entries = [
      ['/dub', 'a'],
      ['/stories', 'b'],
      ['/batch', 'c'],
    ] as const;
    expect(visibleDestinations(entries).map((e) => e[0])).toEqual(['/dub', '/batch']);
  });
});

describe('command palette scope', () => {
  it('drops commands that open hidden sections', () => {
    for (const id of [
      'stories',
      'gallery',
      'transcriptions',
      'workflows',
      'calls',
      'design',
      'audiobook',
      'tools',
      'integrations',
      'pro',
    ]) {
      expect(commandVisible(id)).toBe(false);
    }
  });

  it('keeps dubbing commands and filters settings entries by route', () => {
    for (const id of [
      'home',
      'dub',
      'batch',
      'voices',
      'projects',
      'models',
      'settings',
      'theme',
    ]) {
      expect(commandVisible(id)).toBe(true);
    }
    expect(commandVisible('settings.support', '/settings/support')).toBe(false);
    expect(commandVisible('settings.models', '/settings/models')).toBe(true);
  });
});

describe('AGPL notice', () => {
  it('credits the upstream project and its licence', () => {
    render(<CallenLegalNotice />);
    const notice = screen.getByTestId('callen-legal-notice');
    expect(notice.textContent).toContain('VoiceStudio');
    expect(notice.textContent).toContain('Palash Debnath');
    expect(notice.textContent).toContain('AGPL-3.0');
    expect(screen.getByRole('link', { name: 'VoiceStudio' })).toHaveAttribute(
      'href',
      'https://github.com/debpalash/VoiceStudio',
    );
  });
});
