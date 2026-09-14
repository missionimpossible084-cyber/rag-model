# Askbook — College Management Frontend + AI Assistant (app.py)

A frontend-only role-selection portal (Faculty / Student / Admin) for
Satpuda College of Engineering and Polytechnic (SCEP), where a successful
login on **any** role hands the user off to the **AI Assistant** — a
Streamlit app (`app.py`) backed by a RAG pipeline, document upload, and
placement prediction.

---

## Quick start (run everything at once)

You need Python installed. From the project root:

```bash
pip install -r requirements.txt
python start.py
```

This starts **two servers** and opens your browser automatically:

| Server                     | URL                          | Serves                          |
|-----------------------------|-------------------------------|----------------------------------|
| Static frontend             | http://localhost:8000        | `index.html` + role login pages |
| Streamlit AI Assistant      | http://localhost:8501        | `app.py`                        |

Stop both with `Ctrl+C`.

**Prefer running them manually in two terminals?**

```bash
# Terminal 1 — frontend
python -m http.server 8000

# Terminal 2 — backend/assistant
streamlit run app.py --server.port 8501
```

Then visit `http://localhost:8000`.

### Before running for the first time

1. Put your real Gemini key in `.env` (already renamed from the old `_env`):
   ```
   GEMINI_API_KEY=your-real-key-here
   ```
   **Never commit or paste this file anywhere.** If a key was ever pasted
   into a chat, ticket, or public repo, treat it as compromised and
   generate a new one in Google AI Studio.
2. Drop your existing `backend/` modules (`config.py`, `rag.py`,
   `vectorstore.py`, `placement.py`) into the `backend/` folder — see
   `backend/_PLACE_YOUR_BACKEND_FILES_HERE.txt`.

### Create Account & Google sign-in

Each login page now also has:

- **Create Account** — a link to `<role>/signup.html`. Accounts created
  there are stored in the browser's `localStorage` (key `askbook_accounts`)
  so this works without a real backend. **Passwords are stored in plain
  text in the browser for this Phase 1 demo — do not reuse a real
  password, and swap this for a real backend before going live.**
- **Continue with Google** — uses Firebase Authentication, loaded from
  Google's CDN so no bundler is required. To turn this on:
  1. Create a project at https://console.firebase.google.com
  2. Add a Web app, copy its config values
  3. Enable the "Google" sign-in provider under Authentication
  4. Add `localhost` under Authentication → Settings → Authorized domains
  5. Paste the config into `js/firebaseConfig.js`

  Until you do that, the Google button shows a friendly "not set up yet"
  message instead of crashing.

### Demo login credentials

| Role    | Email               | Password     |
|---------|---------------------|--------------|
| Faculty | faculty@miet.edu    | faculty123   |
| Student | student@miet.edu    | student123   |
| Admin   | admin@miet.edu      | admin123     |

All three roles currently redirect to the same AI Assistant
(`app.py`) on success — see **Login flow** below.

---

## Project structure

```
college-management-system/
├── index.html                  # Landing / role selection
├── start.py                    # Runs frontend + Streamlit together
├── app.py                      # AI Assistant UI (Streamlit)
├── requirements.txt            # Python deps for app.py
├── package.json / package-lock.json  # firebase (reserved for Phase 2 auth)
├── .env                        # GEMINI_API_KEY (never commit)
├── .gitignore
│
├── faculty/
│   ├── login.html
│   └── signup.html
├── student/
│   ├── login.html
│   └── signup.html
├── admin/
│   ├── login.html
│   └── signup.html
│
├── css/
│   ├── global.css              # Design tokens + shared form styles
│   └── auth.css                # Login/signup page layout
│
├── js/
│   ├── config.js                 # APP, ROUTES, ASSISTANT_URL, resolvePath()
│   ├── firebaseConfig.js         # Your Firebase project config (Google sign-in)
│   └── common/
│       ├── icons.js              # Inline SVG icon set (+ Google "G" logo)
│       ├── dom.js                 # $, esc, uid helpers
│       ├── accountStore.js        # localStorage "Create Account" (demo only)
│       ├── googleAuth.js          # Firebase Google sign-in (CDN, no bundler)
│       ├── loginPage.js           # Shared login controller (all 3 roles)
│       └── signupPage.js          # Shared signup controller (all 3 roles)
│
├── assets/
│   └── logo.svg
│
├── backend/                     # <- put your existing modules here (unchanged)
│   ├── config.py
│   ├── rag.py
│   ├── vectorstore.py
│   └── placement.py
│
├── chroma_db/                    # <- your existing vector DB folder (gitignored)
├── data/
│   └── uploads/                  # <- your existing uploaded-docs folder (gitignored)
├── models/                       # <- your existing local model files, if any (gitignored)
└── .venv/                        # <- created by `python -m venv .venv` (gitignored, not in this zip)
```

None of `backend/`, `chroma_db/`, `data/uploads/`, `models/`, or `.venv/`
were part of this upload/zip — they're placeholders. Just copy your real
folders from your existing local project into these exact spots (or drag
this zip's contents into your existing project folder instead, whichever
is easier) and everything lines up with what `app.py` and `.env` expect.

---

## Login flow

1. `index.html` shows three role cards (Faculty / Student / Admin), each
   linking to that role's `login.html`.
2. Each login page uses the shared `js/common/loginPage.js` controller,
   which checks the entered email/password against the demo credentials
   above (swap this for a real `authService`/Firebase call in Phase 2 —
   the function signature stays the same).
3. On success, instead of routing to a role dashboard, the browser is
   redirected straight to the AI Assistant:
   ```js
   window.location.href = ASSISTANT_URL; // http://localhost:8501 by default
   ```
   `ASSISTANT_URL` lives in `js/config.js`. If you deploy the Streamlit
   app somewhere else, either change that constant or set
   `window.__ASKBOOK_STREAMLIT_URL__ = "https://your-host"` in a
   `<script>` tag before `config.js` loads.

---

## ⚠️ Previously known issue in `app.py` — now fixed

Earlier `app.py` called `is_placement_question`, `answer_from_current_chat_document`,
and `general_gemini_answer` without importing or defining them. Your current
`app.py` now defines all three itself — nothing to change here.

---

## Setting this up in VS Code

1. **Merge folders** — copy this zip's contents into your existing local
   project folder (the one that already has your real `backend/`,
   `chroma_db/`, `data/`, `models/`, `.venv/`). Say **yes/merge** if asked
   to overwrite `app.py`, `requirements.txt`, `.env`, or `.gitignore` —
   this zip's copies are your own files, unmodified.
2. **Open the merged folder** in VS Code: `File → Open Folder…`
3. **Select your Python interpreter**: `Ctrl/Cmd+Shift+P` → "Python: Select
   Interpreter" → pick the one inside `.venv`. If you don't have a `.venv`
   yet: `python -m venv .venv`, then activate it and
   `pip install -r requirements.txt`.
4. **Two terminals** (VS Code: `Terminal → New Terminal`, then split):
   ```bash
   # Terminal 1
   python -m http.server 8000

   # Terminal 2
   streamlit run app.py --server.port 8501
   ```
   or just run `python start.py` in one terminal to launch both.
5. Open `http://localhost:8000` in your browser — that's the whole flow:
   **role card → login/signup → app.py's chat UI**, nothing else to wire up.

No code changes are needed for the login → assistant connection — it's
already just `window.location.href = ASSISTANT_URL` in `js/config.js`,
completely separate from your `backend/` logic.

---

1. **Auth (Firebase Authentication)** — replace the mock check in
   `loginPage.js`'s `verify()` with `signInWithEmailAndPassword`.
2. **REST API (Node + Express)** — only relevant if you reintroduce
   role dashboards later; not required for the current login → assistant flow.
3. **PostgreSQL** — backend concern only.
4. **File storage (Firebase Cloud Storage)** — for `app.py`'s document
   upload, swap local `UPLOAD_DIR` writes for a Storage upload + URL.
5. **Real-time (WebSocket)** — only needed if dashboards return.

---

## Security notes

- No real credentials, API keys or secrets should ever be committed —
  `.env` is gitignored.
- All user-generated content should be HTML-escaped (`esc()` in
  `js/common/dom.js`) before rendering.
- Frontend validation is for UX only; any real backend must re-validate
  every request and enforce authorization server-side.
