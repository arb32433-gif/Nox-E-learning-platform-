import sqlite3
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ORCH_DIR / "state.db"
SCHEMA_PATH = ORCH_DIR / "schema.sql"


def init_db():
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()
    print(f"[Orchestrator] Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()
