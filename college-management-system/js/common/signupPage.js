import { ASSISTANT_URL, ROUTES, resolvePath } from '../config.js';
import { $, esc } from './dom.js';
import { icon } from './icons.js';
import { createAccount } from './accountStore.js';
import { signInWithGoogle } from './googleAuth.js';

function saveSessionAndRedirect(role, user) {
  localStorage.setItem(
    'askbook_session',
    JSON.stringify({ role, email: user.email, name: user.name, loggedInAt: Date.now() })
  );
  window.location.href = ASSISTANT_URL;
}

/**
 * Wires up a signup form for the given role.
 * Expects: #signupForm, #name, #email, #password, #confirmPassword,
 * #formError, #submitBtn, and optionally #googleBtn.
 */
export function initSignupPage(role) {
  const form = $('#signupForm');
  const errorEl = $('#formError');
  const submitBtn = $('#submitBtn');
  const googleBtn = $('#googleBtn');

  if (!form) return;

  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const name = $('#name').value;
    const email = $('#email').value;
    const password = $('#password').value;
    const confirmPassword = $('#confirmPassword').value;

    hideError();

    if (!name || !email || !password || !confirmPassword) {
      showError('Please fill in every field.');
      return;
    }

    if (password.length < 6) {
      showError('Password must be at least 6 characters.');
      return;
    }

    if (password !== confirmPassword) {
      showError('Passwords do not match.');
      return;
    }

    setLoading(true, submitBtn, 'Create account', 'Creating account…');

    setTimeout(() => {
      try {
        const account = createAccount({ role, name, email, password });
        saveSessionAndRedirect(role, account);
      } catch (error) {
        setLoading(false, submitBtn, 'Create account');
        showError(error.message);
      }
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
    btn.textContent = isLoading ? (loadingLabel || idleLabel) : idleLabel;
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

export function loginLink(role) {
  return resolvePath(`${role}/login.html`);
}
