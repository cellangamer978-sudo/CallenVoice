import { CALLEN_REPO_URL } from '@shared/callen/repo';
/**
 * CallenVoice product scope (v1: video dubbing and localization).
 *
 * Upstream features outside that scope stay in the code base so
 * upstream merges keep working, but they are hidden from navigation and their
 * routes redirect to the home page. To bring one back, remove it from this set.
 */
export const HIDDEN_ROUTES: ReadonlySet<string> = new Set([
  '/stories',
  '/audiobook',
  '/gallery',
  '/design',
  '/transcriptions',
  '/calls',
  '/workflows',
  '/tools',
  '/integrations',
  '/pro',
  // Donations, sponsors and Pro plans of the upstream project.
  '/settings/support',
]);

/**
 * Import from a video URL (yt-dlp) is off in v1: downloading from platforms
 * such as YouTube can breach their terms and the uploader's copyright.
 */
export const ALLOW_URL_IMPORT = false;

/**
 * The "Agent" translator sends the transcript to a coding agent or an LLM, which
 * may be a cloud service. v1 decision: local translation only.
 */
export const ALLOW_AGENT_TRANSLATION = false;

/** Dictation (floating widget, live transcription) is outside the v1 scope. */
export const ALLOW_DICTATION = false;

/** The upstream demo media was rendered with OmniVoice (non-commercial). */
export const SHOW_UPSTREAM_DEMOS = false;

/** Weights of the default voice engine (MOSS-TTS-Nano, Apache-2.0). Mirrors
 *  backend/callen/catalog.py REQUIRED_MODEL_REPOS. */
export const DEFAULT_VOICE_MODEL_REPO = 'OpenMOSS-Team/MOSS-TTS-Nano-100M';

/**
 * Where users get the complete corresponding source of this build (AGPL-3.0 §6
 * and §13). Must be set before any release: the About screen shows it.
 */
export const SOURCE_CODE_URL = CALLEN_REPO_URL;
export const UPSTREAM_PROJECT = {
  name: 'VoiceStudio',
  url: 'https://github.com/debpalash/VoiceStudio',
  copyright: 'Copyright 2024-present Palash Debnath and VoiceStudio contributors',
  license: 'GNU AGPL-3.0',
} as const;

function normalize(pathname: string): string {
  return pathname.replace(/\/+$/, '') || '/';
}

/** True when the route (or a sub-route of it) is outside the CallenVoice scope. */
export function isHiddenRoute(pathname: string): boolean {
  const path = normalize(pathname);
  for (const hidden of HIDDEN_ROUTES) {
    if (path === hidden || path.startsWith(`${hidden}/`)) return true;
  }
  return false;
}

/** Drops navigation entries whose first element is a hidden route. */
export function visibleDestinations<T extends readonly [string, ...unknown[]]>(
  destinations: readonly T[],
): T[] {
  return destinations.filter((destination) => !isHiddenRoute(destination[0]));
}

/** Command palette entries that open a hidden section, by command id. */
const COMMAND_ROUTES: Readonly<Record<string, string>> = {
  stories: '/stories',
  gallery: '/gallery',
  transcriptions: '/transcriptions',
  workflows: '/workflows',
  calls: '/calls',
  design: '/design',
  audiobook: '/audiobook',
  tools: '/tools',
  integrations: '/integrations',
  pro: '/pro',
};

/** False for palette commands (and voice-design entries) that lead to a hidden section. */
export function commandVisible(id: string, route?: string): boolean {
  const target = route ?? COMMAND_ROUTES[id];
  return !target || !isHiddenRoute(target);
}
