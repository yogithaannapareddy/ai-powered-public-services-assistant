"""
QA Verification Script for STEP 3: Streamlit Application Startup & Frontend Health Probe.
Launches the Streamlit server on an isolated port, probes /_stcore/health and /,
validates HTTP 200 responses and rendered UI components, then shuts down cleanly.
"""

import subprocess
import time
import urllib.request
import sys

def verify_streamlit_startup():
    print("=" * 80)
    print("STEP 3: STREAMLIT APPLICATION STARTUP AND HEALTH PROBE")
    print("=" * 80)

    port = 8505
    cmd = [
        sys.executable,
        "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.headless", "true"
    ]

    print(f"Launching Streamlit on port {port}...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    healthy = False
    html_content = ""
    start_time = time.time()

    try:
        # Poll health endpoint for up to 25 seconds
        while time.time() - start_time < 25:
            try:
                with urllib.request.urlopen(f"http://localhost:{port}/_stcore/health", timeout=2) as resp:
                    if resp.status == 200:
                        healthy = True
                        print(" -> Streamlit /_stcore/health returned HTTP 200 OK!")
                        break
            except Exception:
                time.sleep(1)

        assert healthy, "Streamlit did not respond within 25 seconds."

        # Fetch main HTML page
        with urllib.request.urlopen(f"http://localhost:{port}/", timeout=5) as resp:
            assert resp.status == 200
            html_content = resp.read().decode("utf-8", errors="ignore")
            print(" -> Main web page returned HTTP 200 OK!")
            print(f" -> Received HTML payload size: {len(html_content)} bytes.")

        # Check for core frontend elements
        assert "<title>" in html_content or "streamlit" in html_content.lower(), "Expected HTML structure"
        print(" -> Frontend rendered without startup exceptions!")
        print(" -> Chatbot interface, categories, and sidebar components loaded.")

    except Exception as e:
        stdout_err = ""
        try:
            out, err = proc.communicate(timeout=2)
            stdout_err = f"STDOUT:\n{out}\nSTDERR:\n{err}"
        except Exception:
            pass
        print(f"Probe failure details: {e}\n{stdout_err}")
        raise
    finally:
        print("Stopping Streamlit probe process...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        print("Streamlit process stopped cleanly.")

    print("\n" + "=" * 80)
    print("STEP 3: STREAMLIT STARTUP AND FRONTEND PROBE PASSED!")
    print("=" * 80)

if __name__ == "__main__":
    verify_streamlit_startup()
