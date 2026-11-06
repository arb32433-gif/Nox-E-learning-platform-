import sqlite3
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ORCH_DIR / "state.db"

REQUIRED_PATHS = [
    "config.json",
    "schema.sql",
    "state.db",
    "agents",
    "scripts",
    "storage/backups",
    "storage/logs",
    "storage/diffs",
]


def log_audit(check_type: str, status: str, details: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO audit_logs (check_type, status, details) VALUES (?, ?, ?)",
            (check_type, status, details),
        )
        conn.commit()
    finally:
        conn.close()


def run_health_check():
    print("[Orchestrator] Running project health audit...")
    missing = [p for p in REQUIRED_PATHS if not (ORCH_DIR / p).exists()]
    # Add custom linting, broken link, or dependency checks here

    if missing:
        log_audit("HEALTH_CHECK", "FAILURE", f"Missing: {', '.join(missing)}")
        print(f"[Orchestrator] Audit failed. Missing: {', '.join(missing)}")
    else:
        log_audit("HEALTH_CHECK", "SUCCESS", "Orchestrator structure validated.")
        print("[Orchestrator] Audit complete. Logged to state.db.")


if __name__ == "__main__":
    run_health_check()
