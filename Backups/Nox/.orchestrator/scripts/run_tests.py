import json
import subprocess
import sys
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ORCH_DIR.parent
DB_PATH = ORCH_DIR / "state.db"


def log(status, details):
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("INSERT INTO audit_logs (check_type, status, details) VALUES (?, ?, ?)", ("TEST_RUN", status, details))
        conn.commit()
    finally:
        conn.close()


def run_tests():
    if (PROJECT_ROOT / "pytest.ini").exists() or (PROJECT_ROOT / "pyproject.toml").exists() or (PROJECT_ROOT / "setup.cfg").exists():
        cmd = [sys.executable, "-m", "pytest", "-q"]
    elif (PROJECT_ROOT / "package.json").exists():
        cmd = ["npm", "test"]
    else:
        print("[Orchestrator] No test runner detected.")
        return
    print("[Orchestrator] Running tests:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    status = "SUCCESS" if result.returncode == 0 else "FAILURE"
    log(status, (result.stdout + result.stderr)[:2000])
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    print(f"[Orchestrator] Tests finished: {status}")


if __name__ == "__main__":
    run_tests()
