import json
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = ORCH_DIR.parent


def run_audit():
    findings = []
    for p in PROJECT_ROOT.rglob("*.py"):
        if "orchestrator" in p.parts:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if "TODO" in line or "FIXME" in line:
                findings.append({"file": str(p.relative_to(PROJECT_ROOT)), "line": i, "issue": line.strip()})
    out = ORCH_DIR / "storage" / "logs" / "audit_findings.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(findings, indent=2), encoding="utf-8")
    print(f"[Orchestrator] Audit complete: {len(findings)} findings -> {out}")


if __name__ == "__main__":
    run_audit()
