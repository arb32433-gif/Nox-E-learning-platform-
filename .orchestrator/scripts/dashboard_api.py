import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ORCH_DIR = Path(__file__).resolve().parent.parent
PORT = 4040


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(LOGS), **kwargs)

    def do_GET(self):
        if self.path == "/api/findings":
            p = ORCH_DIR / "storage" / "logs" / "audit_findings.json"
            data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()


if __name__ == "__main__":
    httpd = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"[Orchestrator] Dashboard API on http://127.0.0.1:{PORT}")
    httpd.serve_forever()
