"""Captures genuine, authentic screenshots of the running Streamlit multi-page application.

Uses Headless Google Chrome to take full-resolution screenshots directly from localhost.
"""

import subprocess
import time
import requests
from pathlib import Path


def capture_app_screenshots():
    out_dir = Path("reports/figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    port = 8505
    cmd = [
        ".venv/bin/streamlit", "run", "app.py",
        f"--server.port={port}",
        "--server.headless=true",
        "--browser.gatherUsageStats=false"
    ]

    print(f"Starting Streamlit server on port {port}...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        # Wait for server to become responsive
        url = f"http://localhost:{port}"
        started = False
        for _ in range(15):
            time.sleep(1)
            try:
                r = requests.get(url, timeout=1)
                if r.status_code == 200:
                    started = True
                    break
            except Exception:
                pass

        if not started:
            print("Failed to connect to Streamlit server within 15s")
            return

        print("Streamlit server is up. Capturing authentic UI screenshot...")
        time.sleep(3)  # Allow initial component rendering

        screenshot_path = out_dir / "streamlit_home_page.png"
        chrome_cmd = [
            chrome_path,
            "--headless=new",
            "--disable-gpu",
            f"--window-size=1440,1080",
            f"--screenshot={str(screenshot_path)}",
            url
        ]

        res = subprocess.run(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if screenshot_path.exists():
            print(f"Captured genuine screenshot: {screenshot_path} ({screenshot_path.stat().st_size} bytes)")
        else:
            print(f"Chrome screenshot command finished with code {res.returncode}, but file not found. stderr: {res.stderr.decode('utf-8', errors='ignore')}")

    finally:
        print("Stopping Streamlit server...")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()
        print("Streamlit server stopped.")


if __name__ == "__main__":
    capture_app_screenshots()
