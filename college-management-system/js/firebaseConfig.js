// ==================================================
// FIREBASE CONFIG (for "Continue with Google")
//
// 1. Go to https://console.firebase.google.com -> create/open a project.
// 2. Project settings -> General -> "Your apps" -> Web app -> copy the config.
// 3. Authentication -> Sign-in method -> enable "Google".
// 4. Authentication -> Settings -> Authorized domains -> add "localhost"
//    (and your real domain when you deploy).
// 5. Paste the values below. Never commit real keys to a public repo
//    (this apiKey is safe to expose in frontend code by Firebase's design,
//    but keep authDomain/projectId matching your real project).
// ==================================================

export const firebaseConfig = {
  apiKey: 'YOUR_FIREBASE_API_KEY',
  authDomain: 'YOUR_PROJECT_ID.firebaseapp.com',
  projectId: 'YOUR_PROJECT_ID',
  appId: 'YOUR_FIREBASE_APP_ID',
};

export function isFirebaseConfigured() {
  return !Object.values(firebaseConfig).some((v) => v.startsWith('YOUR_'));
}
