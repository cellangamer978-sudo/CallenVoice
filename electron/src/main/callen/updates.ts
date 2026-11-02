/**
 * CallenVoice update feed.
 *
 * The upstream updater checks debpalash/VoiceStudio releases. A CallenVoice
 * build must never offer those, so in-app updates stay off until our own
 * release repository is configured here (or through CALLENVOICE_UPDATE_REPO,
 * "owner/repo", at build or run time).
 */
export const CALLEN_UPDATE_REPO = '';

export function callenUpdateRepo(env: NodeJS.ProcessEnv = process.env): string {
  const value = (env.CALLENVOICE_UPDATE_REPO ?? CALLEN_UPDATE_REPO).trim();
  return /^[A-Za-z0-9-]+\/[A-Za-z0-9._-]+$/.test(value) ? value : '';
}

export function callenUpdatesConfigured(env: NodeJS.ProcessEnv = process.env): boolean {
  return callenUpdateRepo(env) !== '';
}
