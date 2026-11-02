/**
 * CallenVoice public repository (AGPL-3.0: every build must point users to its
 * complete source). Keep it in sync with pyproject.toml [project.urls].Repository
 * (the backend's doc links read that).
 *
 * If this is ever emptied: documentation links fall back to the upstream
 * VoiceStudio docs (same content, credited), and links that would offer a
 * download or source checkout are hidden instead.
 */
export const CALLEN_REPO_URL = 'https://github.com/cellangamer978-sudo/CallenVoice';

/**
 * True once the first CallenVoice release (installer) is published on GitHub.
 * Until then download links stay hidden: an empty releases page is a dead end.
 */
export const CALLEN_HAS_RELEASES = false;

const UPSTREAM_REPO_URL = 'https://github.com/debpalash/VoiceStudio';

/** Base for `docs/...` links: our repository when published, upstream until then. */
export const DOCS_REPO_URL = CALLEN_REPO_URL || UPSTREAM_REPO_URL;

/** `${DOCS_REPO_URL}/blob/main` — prefix for links to files in the repository. */
export const DOCS_BLOB_BASE = `${DOCS_REPO_URL}/blob/main`;

/** Our releases page, or null while there is no repository or no release yet. */
export const CALLEN_RELEASES_URL: string | null =
  CALLEN_REPO_URL && CALLEN_HAS_RELEASES
    ? `${CALLEN_REPO_URL}/releases/latest`
    : null;
