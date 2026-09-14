// ==================================================
// APP CONFIG
// Single source of truth for names, routes and the
// URL of the Streamlit "AI Assistant" (app.py).
// ==================================================

export const APP = {
  NAME: 'Askbook',
  VERSION: '1.0.0',
  COLLEGE_NAME: 'Satpuda College of Engineering and Polytechnic',
  COLLEGE_SHORT: 'Askbook',
  COLLEGE_LOGO: resolveAsset('assets/logo.svg'),
};

// Where the Streamlit backend (app.py) is served.
// Override by adding: <script>window.__ASKBOOK_STREAMLIT_URL__ = "http://your-host:8501"</script>
// before this module loads (e.g. when deploying), otherwise it
// defaults to the standard local Streamlit port.
export const ASSISTANT_URL =
  (typeof window !== 'undefined' && window.__ASKBOOK_STREAMLIT_URL__) ||
  'http://localhost:8501';

// All routes are given as root-relative paths (as if index.html
// were at "/"). resolvePath() rewrites them correctly no matter
// how deep the current page is nested (e.g. /faculty/login.html).
export const ROUTES = {
  HOME: 'index.html',
  FACULTY: { LOGIN: 'faculty/login.html' },
  STUDENT: { LOGIN: 'student/login.html' },
  ADMIN: { LOGIN: 'admin/login.html' },
  ASSISTANT: ASSISTANT_URL, // external, not root-relative
};

export const ENV = {
  USE_MOCK: true, // flip to false once a real backend/auth API is wired up
};

/**
 * Rewrites a root-relative path (e.g. "faculty/login.html") so it
 * works correctly from any page depth, and passes external URLs
 * (http://, https://) straight through untouched.
 */
export function resolvePath(path) {
  if (/^https?:\/\//i.test(path)) return path;

  const depth = window.location.pathname
    .replace(/\/index\.html$/, '')
    .split('/')
    .filter(Boolean).length - (window.location.pathname.endsWith('/') ? 0 : 1);

  // depth = 0 when we're at the site root (e.g. /index.html or /)
  const prefix = depth > 0 ? '../'.repeat(depth) : '';
  return prefix + path;
}

function resolveAsset(path) {
  return resolvePath(path);
}
