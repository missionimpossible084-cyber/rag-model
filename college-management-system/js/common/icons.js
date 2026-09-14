// ==================================================
// Minimal inline SVG icon set.
// icon('name') returns a raw <svg> string (currentColor stroke).
// ==================================================

const ICONS = {
  shield: '<path d="M12 2 4 5v6c0 5 3.4 8.4 8 11 4.6-2.6 8-6 8-11V5l-8-3Z"/><path d="m9 12 2 2 4-4"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-6 8-6s8 2 8 6"/>',
  graduation: '<path d="M22 10 12 5 2 10l10 5 10-5Z"/><path d="M6 12v5c0 1.7 2.7 3 6 3s6-1.3 6-3v-5"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6V21a2 2 0 1 1-4 0v-.2a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.6-1H3a2 2 0 1 1 0-4h.2a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.6V3a2 2 0 1 1 4 0v.2a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V9c.1.7.6 1.3 1.3 1.6l.3.1h.2a2 2 0 1 1 0 4h-.2a1.7 1.7 0 0 0-1.6 1Z"/>',
  arrowRight: '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
  arrowLeft: '<path d="M19 12H5"/><path d="m11 18-6-6 6-6"/>',
  mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
  lock: '<rect x="4" y="11" width="16" height="9" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
  eye: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
  eyeOff: '<path d="M3 3l18 18"/><path d="M10.6 5.2A10.6 10.6 0 0 1 12 5c6.4 0 10 7 10 7a17.7 17.7 0 0 1-3.2 4.2M6.6 6.6A17.7 17.7 0 0 0 2 12s3.6 7 10 7c1.3 0 2.5-.2 3.6-.6"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
  alertCircle: '<circle cx="12" cy="12" r="10"/><path d="M12 8v5"/><path d="M12 16h.01"/>',
};

export function icon(name, { size = 20 } = {}) {
  const body = ICONS[name] || ICONS.alertCircle;
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
}

// Google's "G" logo is multi-color, so it's kept as a standalone
// full <svg> (not run through the currentColor icon() wrapper above).
export function googleIcon(size = 18) {
  return `<svg width="${size}" height="${size}" viewBox="0 0 48 48">
    <path fill="#EA4335" d="M24 9.5c3.4 0 6.4 1.2 8.8 3.4l6.5-6.5C35.3 2.5 30 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.6 5.9C12.1 13 17.6 9.5 24 9.5Z"/>
    <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.6c-.5 3-2.2 5.4-4.6 7.1l7.2 5.6c4.2-3.9 6.8-9.6 6.8-17.2Z"/>
    <path fill="#FBBC05" d="M10.2 19.1a14.5 14.5 0 0 0 0 9.8l-7.6 5.9a24 24 0 0 1 0-21.6l7.6 5.9Z"/>
    <path fill="#34A853" d="M24 48c6 0 11.3-2 15.1-5.3l-7.2-5.6c-2 1.4-4.7 2.2-7.9 2.2-6.4 0-11.9-3.5-13.8-8.6l-7.6 5.9C6.5 42.6 14.6 48 24 48Z"/>
  </svg>`;
}
