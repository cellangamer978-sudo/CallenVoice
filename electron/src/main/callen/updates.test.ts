import { describe, expect, it } from 'vitest';
import { callenUpdateRepo, callenUpdatesConfigured } from './updates';
import { applicationUpdatesUnsupportedReason } from '../distribution';

describe('CallenVoice update feed', () => {
  it('is off until our own release repository is configured', () => {
    expect(callenUpdatesConfigured({})).toBe(false);
    expect(callenUpdateRepo({ CALLENVOICE_UPDATE_REPO: '' })).toBe('');
  });

  it('accepts only a plain owner/repo value', () => {
    expect(callenUpdateRepo({ CALLENVOICE_UPDATE_REPO: 'acme/CallenVoice' })).toBe(
      'acme/CallenVoice',
    );
    for (const bad of ['acme', 'acme/x/y', 'https://github.com/acme/x', '../x/y', 'a b/c']) {
      expect(callenUpdateRepo({ CALLENVOICE_UPDATE_REPO: bad })).toBe('');
    }
  });

  it('keeps a packaged build from updating itself without a feed', () => {
    const saved = process.env.CALLENVOICE_UPDATE_REPO;
    delete process.env.CALLENVOICE_UPDATE_REPO;
    try {
      expect(applicationUpdatesUnsupportedReason(true, 'direct')).toBe('package-manager');
    } finally {
      if (saved !== undefined) process.env.CALLENVOICE_UPDATE_REPO = saved;
    }
    expect(applicationUpdatesUnsupportedReason(true, 'direct')).toBe(
      saved ? null : 'package-manager',
    );
  });
});
