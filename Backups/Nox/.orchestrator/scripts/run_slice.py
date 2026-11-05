import subprocess
import sys
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
SCRIPTS = ORCH_DIR / "scripts"

def main():
    subprocess.run([sys.executable, str(SCRIPTS / "audit_code.py")], check=True)
    subprocess.run([sys.executable, str(SCRIPTS / "generate_report.py")], check=True)
    print("[Orchestrator] Slice 1 complete. Run dashboard_api.py to view.")

if __name__ == "__main__":
    main()
