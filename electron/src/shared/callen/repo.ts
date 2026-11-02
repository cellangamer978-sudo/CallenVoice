/**
 * CallenVoice public repository (AGPL-3.0: every build must point users to its
 * complete source). Empty until the repository exists; then set it here and in
 * pyproject.toml [project.urls].Repository (the backend's doc links read that).
 *
 * While empty: documentation links fall back to the upstream VoiceStudio docs
 * (same content, credited), and links that would offer the upstream download or
 * source checkout are hidden instead.
 */
export const CALLEN_REPO_URL = '';

const UPSTREAM_REPO_URL = 'https://github.com/debpalash/VoiceStudio';

/** Base for `docs/...` links: our repository when published, upstream until then. */
export const DOCS_REPO_URL = CALLEN_REPO_URL || UPSTREAM_REPO_URL;

/** `${DOCS_REPO_URL}/blob/main` — prefix for links to files in the repository. */
export const DOCS_BLOB_BASE = `${DOCS_REPO_URL}/blob/main`;

/** Our releases page, or null while no repository is published. */
export const CALLEN_RELEASES_URL: string | null = CALLEN_REPO_URL
  ? `${CALLEN_REPO_URL}/releases/latest`
  : null;
