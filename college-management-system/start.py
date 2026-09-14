#!/usr/bin/env python3
"""
Starts the whole project with one command:
  - Static frontend (index.html + login pages)  -> http://localhost:8000
  - Streamlit AI Assistant (app.py)              -> http://localhost:8501

Usage:
    python start.py

Stop both with Ctrl+C.
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FRONTEND_PORT = 8000
STREAMLIT_PORT = 8501

def main():
    print(f"Starting frontend server on http://localhost:{FRONTEND_PORT}")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(FRONTEND_PORT)],
        cwd=ROOT,
    )

    print(f"Starting Streamlit assistant (app.py) on http://localhost:{STREAMLIT_PORT}")
    streamlit = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(STREAMLIT_PORT),
            "--server.headless", "true",
        ],
        cwd=ROOT,
    )

    time.sleep(2)
    webbrowser.open(f"http://localhost:{FRONTEND_PORT}")

    print("\nBoth servers are running. Press Ctrl+C to stop.\n")

    try:
        frontend.wait()
        streamlit.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
        frontend.terminate()
        streamlit.terminate()

if __name__ == "__main__":
    main()
