import { ASSISTANT_URL, ROUTES, resolvePath } from '../config.js';
import { $, esc } from './dom.js';
import { icon } from './icons.js';
import { findAccount } from './accountStore.js';
import { signInWithGoogle } from './googleAuth.js';

// ==================================================
// MOCK CREDENTIALS (Phase 1 — see README "Demo credentials")
// Swap `verify()` for a real authService/Firebase call in Phase 2;
// everything else here stays the same.
// ==================================================

const MOCK_USERS = {
  faculty: { email: 'faculty@miet.edu', password: 'faculty123', name: 'Faculty User' },
  student: { email: 'student@miet.edu', password: 'student123', name: 'Student User' },
  admin: { email: 'admin@miet.edu', password: 'admin123', name: 'Admin User' },
};

function verify(role, email, password) {
  const normalizedEmail = email.trim().toLowerCase();

  const mockUser = MOCK_USERS[role];
  if (mockUser && normalizedEmail === mockUser.email && password === mockUser.password) {
    return { name: mockUser.name, email: mockUser.email };
  }

  const account = findAccount(role, normalizedEmail);
  if (account && account.password === password) {
    return { name: account.name, email: account.email };
  }

  return null;
}

function saveSessionAndRedirect(role, user) {
  localStorage.setItem(
    'askbook_session',
    JSON.stringify({ role, email: user.email, name: user.name, loggedInAt: Date.now() })
  );
  // Successful login hands off straight to the AI Assistant
  // (the Streamlit app / app.py) instead of a role dashboard.
  window.location.href = ASSISTANT_URL;
}

/**
 * Wires up a login form for the given role.
 * Expects the page to contain:
 *   <form id="loginForm"> #email #password </form>
 *   <div id="formError" hidden></div>
 *   <button id="submitBtn" type="submit">
 *   <button id="googleBtn" type="button">   (optional)
 */
export function initLoginPage(role) {
  const form = $('#loginForm');
  const errorEl = $('#formError');
  const submitBtn = $('#submitBtn');
  const googleBtn = $('#googleBtn');

  if (!form) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const email = $('#email').value;
    const password = $('#password').value;

    hideError();

    if (!email || !password) {
      showError('Please enter both email and password.');
      return;
    }

    setLoading(true, submitBtn, 'Sign in', 'Signing in…');

    // Simulate a network round-trip so the loading state is visible;
    // replace with `await authService.login(role, email, password)` in Phase 2.
    setTimeout(() => {
      const user = verify(role, email, password);

      if (!user) {
        setLoading(false, submitBtn, 'Sign in');
        showError('Invalid email or password for this role.');
        return;
      }

      saveSessionAndRedirect(role, user);
    }, 400);
  });

  if (googleBtn) {
    googleBtn.addEventListener('click', async () => {
      hideError();
      setLoading(true, googleBtn, googleBtn.dataset.label || 'Continue with Google', 'Connecting…');

      try {
        const user = await signInWithGoogle();
        saveSessionAndRedirect(role, user);
      } catch (error) {
        setLoading(false, googleBtn, googleBtn.dataset.label || 'Continue with Google');
        showError(error.message);
      }
    });
  }

  function setLoading(isLoading, btn, idleLabel, loadingLabel) {
    if (!btn) return;
    btn.disabled = isLoading;
    const labelEl = btn.querySelector('.btn-label');
    if (labelEl) {
      labelEl.textContent = isLoading ? (loadingLabel || idleLabel) : idleLabel;
    } else {
      btn.textContent = isLoading ? (loadingLabel || idleLabel) : idleLabel;
    }
  }

  function showError(message) {
    if (!errorEl) return;
    errorEl.innerHTML = `${icon('alertCircle', { size: 16 })} <span>${esc(message)}</span>`;
    errorEl.hidden = false;
  }

  function hideError() {
    if (!errorEl) return;
    errorEl.hidden = true;
    errorEl.innerHTML = '';
  }
}

export function backToHomeLink() {
  return resolvePath(ROUTES.HOME);
}

export function signupLink(role) {
  return resolvePath(`${role}/signup.html`);
}

export function loginLink(role) {
  return resolvePath(`${role}/login.html`);
}
