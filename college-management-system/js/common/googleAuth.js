// ==================================================
// GOOGLE SIGN-IN
// Uses the Firebase modular SDK loaded straight from Google's CDN,
// so no build step / bundler is needed for this vanilla-JS project.
// Requires js/firebaseConfig.js to be filled in with a real project.
// ==================================================

import { firebaseConfig, isFirebaseConfigured } from '../firebaseConfig.js';

const FIREBASE_VERSION = '10.12.2';

let authPromise;

async function getFirebaseAuth() {
  if (!authPromise) {
    authPromise = (async () => {
      const { initializeApp } = await import(
        `https://www.gstatic.com/firebasejs/${FIREBASE_VERSION}/firebase-app.js`
      );
      const authModule = await import(
        `https://www.gstatic.com/firebasejs/${FIREBASE_VERSION}/firebase-auth.js`
      );
      const app = initializeApp(firebaseConfig);
      return { auth: authModule.getAuth(app), authModule };
    })();
  }
  return authPromise;
}

/**
 * Opens the Google sign-in popup and resolves with
 * { name, email } on success. Throws a user-friendly Error otherwise.
 */
export async function signInWithGoogle() {
  if (!isFirebaseConfigured()) {
    throw new Error(
      "Google sign-in isn't set up yet — add your Firebase project details in js/firebaseConfig.js."
    );
  }

  const { auth, authModule } = await getFirebaseAuth();
  const provider = new authModule.GoogleAuthProvider();

  try {
    const result = await authModule.signInWithPopup(auth, provider);
    const user = result.user;
    return { name: user.displayName || user.email, email: user.email };
  } catch (error) {
    if (error?.code === 'auth/popup-closed-by-user') {
      throw new Error('Sign-in was cancelled.');
    }
    throw new Error('Google sign-in failed. Please try again.');
  }
}
