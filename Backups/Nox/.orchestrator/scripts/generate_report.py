import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

ORCH_DIR = Path(__file__).resolve().parent.parent
LOGS = ORCH_DIR / "storage" / "logs"


def generate_report():
    findings_path = LOGS / "audit_findings.json"
    findings = json.loads(findings_path.read_text(encoding="utf-8")) if findings_path.exists() else []
    report = LOGS / "report.html"
    rows = "".join(f"<tr><td>{f['file']}</td><td>{f['line']}</td><td>{f['issue']}</td></tr>" for f in findings)
    report.write_text(f"<html><body><h1>Audit Report</h1><table border=1><tr><th>File</th><th>Line</th><th>Issue</th></tr>{rows}</table></body></html>", encoding="utf-8")
    print(f"[Orchestrator] Report written: {report}")


if __name__ == "__main__":
    generate_report()
