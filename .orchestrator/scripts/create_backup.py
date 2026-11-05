import hashlib
import json
import sqlite3
import tarfile
from datetime import datetime
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ORCH_DIR.parent
BACKUP_DIR = ORCH_DIR / "storage" / "backups"
DB_PATH = ORCH_DIR / "state.db"
CONFIG_PATH = ORCH_DIR / "config.json"

EXCLUDE_NAMES = {
    "orchestrator",
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
}


def calculate_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def exclude_filter(tarinfo):
    parts = Path(tarinfo.name).parts
    if any(part in EXCLUDE_NAMES for part in parts):
        return None
    return tarinfo


def rotate_snapshots(max_snapshots: int):
    snapshots = sorted(BACKUP_DIR.glob("snapshot_*.tar.gz"))
    for old in snapshots[:-max_snapshots] if max_snapshots > 0 else []:
        old.unlink()
        print(f"[Orchestrator] Removed old snapshot: {old.name}")


def create_snapshot():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    backup_cfg = config["backup"]
    if not backup_cfg["enabled"]:
        print("[Orchestrator] Backups disabled in config.json.")
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"snapshot_{timestamp}.tar.gz"
    backup_path = BACKUP_DIR / backup_filename

    print(f"[Orchestrator] Creating snapshot: {backup_filename}...")

    with tarfile.open(backup_path, "w:gz") as tar:
        for item in PROJECT_ROOT.iterdir():
            if item.name in EXCLUDE_NAMES:
                continue
            tar.add(item, arcname=item.name, filter=exclude_filter)

    file_size = backup_path.stat().st_size
    file_hash = calculate_sha256(backup_path)

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO backup_registry (filename, file_size_bytes, sha256_hash) VALUES (?, ?, ?)",
            (backup_filename, file_size, file_hash),
        )
        conn.commit()
    finally:
        conn.close()

    rotate_snapshots(backup_cfg["max_local_snapshots"])
    print(f"[Orchestrator] Backup completed and registered ({file_size} bytes).")


if __name__ == "__main__":
    create_snapshot()
