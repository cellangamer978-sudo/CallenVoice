import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import type { ReactNode } from 'react';
const browser = vi.hoisted(() => ({ open: vi.fn(async () => {}) }));
const files = vi.hoisted(() => ({ openExternal: vi.fn(async () => {}) }));
vi.mock('@/components/bridge', () => ({
  getBridge: () => ({ browser, files }),
}));

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}));
vi.mock('@tanstack/react-query', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@tanstack/react-query')>()),
  useQuery: () => ({ data: [] }),
}));
vi.mock('@/hooks/use-profiles', () => ({ useProfiles: () => ({ data: [] }) }));
vi.mock('@/components/app-shell/workspace-header', () => ({
  WorkspaceHeader: ({ children }: { children: ReactNode }) => <header>{children}</header>,
}));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key, i18n: { language: 'es' } }),
}));
import { HomePage } from './home-page';
import en from '@/i18n/locales/en.json';

// CallenVoice home: our own headline, only the in-scope destinations, and no
// upstream website link or contributor avatars (callen/product.ts, home-copy.ts).
afterEach(cleanup);

it('shows the CallenVoice headline without linking to the upstream website', () => {
  browser.open.mockClear();
  render(<HomePage />);
  const heading = screen.getByRole('heading', { name: 'Dobla y localiza tus videos' });
  expect(heading.parentElement).toContainElement(screen.getByText(/Traduce, dobla/));
  expect(document.querySelector('a[href="https://voicestudio.sh"]')).toBeNull();
  fireEvent.click(heading);
  expect(browser.open).not.toHaveBeenCalled();
});

it('does not show the upstream contributor avatars', () => {
  render(<HomePage />);
  expect(document.querySelector('.home-contributors')).toBeNull();
  expect(document.querySelector('[data-core-maintainer]')).toBeNull();
});

it('names the feature Dubbing consistently while preserving the existing route', () => {
  expect(en.dubWorkspace.title).toBe('Dubbing');
  expect(en.nav.dub).toBe('Dubbing');
  render(<HomePage />);
  expect(screen.getByRole('link', { name: /dubWorkspace.title/ })).toHaveAttribute('href', '/dub');
});

it('offers only the destinations inside the CallenVoice scope', () => {
  render(<HomePage />);
  const routes = Array.from(document.querySelectorAll('[data-destination]'), (node) =>
    node.getAttribute('data-destination'),
  );
  expect(routes).toEqual(['/clone', '/dub']);
});
