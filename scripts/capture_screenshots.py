"""Captures genuine, authentic screenshots of the running Streamlit multi-page application.

Uses Playwright with installed Google Chrome to wait for Streamlit's WebSocket connection
and complete DOM rendering before capturing the screenshot.
"""

import subprocess
import time
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright


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
        for _ in range(20):
            time.sleep(1)
            try:
                r = requests.get(url, timeout=1)
                if r.status_code == 200:
                    started = True
                    break
            except Exception:
                pass

        if not started:
            print("Failed to connect to Streamlit server within 20s")
            return

        print("Streamlit server is up. Launching Playwright to render and capture screenshot...")
        time.sleep(2)

        screenshot_path = out_dir / "streamlit_home_page.png"

        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=chrome_path, headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 1080})
            page = context.new_page()

            page.goto(url, wait_until="networkidle", timeout=30000)
            # Wait for Streamlit root element and hero banner / main header
            page.wait_for_selector(".hero-banner, .main-header", timeout=15000)
            time.sleep(2)  # Allow charts and metrics to finish animating

            page.screenshot(path=str(screenshot_path), full_page=False)
            browser.close()

        if screenshot_path.exists():
            size = screenshot_path.stat().st_size
            print(f"Successfully captured genuine, fully rendered screenshot: {screenshot_path} ({size:,} bytes)")
        else:
            print("Screenshot file was not created.")

    except Exception as e:
        print(f"Error capturing screenshot: {e}")
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
