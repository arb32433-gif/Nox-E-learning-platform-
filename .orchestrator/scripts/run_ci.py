import subprocess
import sys
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
SCRIPTS = ORCH_DIR / "scripts"


def main():
    for script in ["check_health.py", "audit_code.py", "run_tests.py"]:
        print(f"\n=== {script} ===")
        subprocess.run([sys.executable, str(SCRIPTS / script)], check=False)
    print("\n[Orchestrator] CI pipeline complete.")


if __name__ == "__main__":
    main()
