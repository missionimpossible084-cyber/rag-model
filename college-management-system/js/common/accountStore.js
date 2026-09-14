// ==================================================
// LOCAL ACCOUNT STORE
// Phase 1 only: accounts created via "Create Account" are kept in
// localStorage so this demo can work without a real backend.
//
// IMPORTANT: passwords are stored in plain text in the browser.
// This is fine for a local demo but must NOT be used in production —
// swap this whole module for a real authService/API call in Phase 2.
// ==================================================

const STORAGE_KEY = 'askbook_accounts';

function readAll() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeAll(accounts) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(accounts));
}

export function findAccount(role, email) {
  const normalized = email.trim().toLowerCase();
  return readAll().find((a) => a.role === role && a.email === normalized);
}

export function createAccount({ role, name, email, password }) {
  const accounts = readAll();
  const normalizedEmail = email.trim().toLowerCase();

  if (accounts.some((a) => a.role === role && a.email === normalizedEmail)) {
    throw new Error('An account with this email already exists for this role. Try signing in instead.');
  }

  const account = {
    role,
    name: name.trim(),
    email: normalizedEmail,
    password, // demo only — see module note above
    createdAt: Date.now(),
  };

  accounts.push(account);
  writeAll(accounts);
  return account;
}
