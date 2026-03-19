#!/usr/bin/env python3
"""Lightweight SSE server for incremental diagram rendering. Zero dependencies.

Supports multiple sessions: each session has independent state and SSE clients.
- Browser: http://127.0.0.1:6100/?s=mydiagram
- Curl:    curl -s 127.0.0.1:6100/cmd?s=mydiagram -d '{"cmd":"node",...}'
- Default session "default" is used when ?s= is omitted.
"""

import json
import queue
import sys
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path
from urllib.parse import urlparse, parse_qs

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template-x6.html"
STATE_DIR = Path("/tmp/diagram-sessions")
lock = threading.Lock()

# Per-session storage: session_id -> {"state": [...], "clients": [Queue, ...]}
sessions: dict[str, dict] = {}


def _get_session(sid: str) -> dict:
    """Get or create a session."""
    if sid not in sessions:
        sessions[sid] = {"state": [], "clients": []}
        _load_session(sid)
    return sessions[sid]


def _save_session(sid: str):
    """Persist session state to disk."""
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        f = STATE_DIR / f"{sid}.json"
        f.write_text(json.dumps(sessions[sid]["state"], ensure_ascii=False))
    except Exception:
        pass


def _load_session(sid: str):
    """Load session state from disk."""
    try:
        f = STATE_DIR / f"{sid}.json"
        if f.exists():
            sessions[sid]["state"] = json.loads(f.read_text())
    except Exception:
        pass


def _parse_session(path: str) -> tuple[str, str]:
    """Extract session ID and clean path from request path."""
    parsed = urlparse(path)
    params = parse_qs(parsed.query)
    sid = params.get("s", ["default"])[0]
    return sid, parsed.path


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        sid, path = _parse_session(self.path)
        if path == "/":
            self._serve_template()
        elif path == "/events":
            self._serve_sse(sid)
        elif path == "/state":
            self._serve_state(sid)
        elif path == "/status":
            self._serve_status()
        elif path == "/sessions":
            self._serve_sessions()
        else:
            self.send_error(404)

    def do_POST(self):
        sid, path = _parse_session(self.path)
        if path == "/cmd":
            self._handle_cmd(sid)
        elif path == "/clear":
            self._handle_clear(sid)
        else:
            self.send_error(404)

    def _serve_template(self):
        try:
            html = TEMPLATE.read_bytes()
        except FileNotFoundError:
            self.send_error(500, "template.html not found")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self._cors()
        self.end_headers()
        self.wfile.write(html)

    def _serve_sse(self, sid: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._cors()
        self.end_headers()
        q: queue.Queue = queue.Queue()
        with lock:
            sess = _get_session(sid)
            sess["clients"].append(q)
        try:
            while True:
                data = q.get()
                self.wfile.write(f"data: {data}\n\n".encode())
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with lock:
                sess = sessions.get(sid)
                if sess and q in sess["clients"]:
                    sess["clients"].remove(q)

    def _serve_state(self, sid: str):
        with lock:
            sess = _get_session(sid)
            body = json.dumps(sess["state"], ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _serve_status(self):
        with lock:
            total_clients = sum(len(s["clients"]) for s in sessions.values())
            total_cmds = sum(len(s["state"]) for s in sessions.values())
            info = {
                "status": "ok",
                "sessions": len(sessions),
                "clients": total_clients,
                "commands": total_cmds,
            }
        body = json.dumps(info).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _serve_sessions(self):
        """List all sessions with their command counts."""
        with lock:
            info = {
                sid: {"commands": len(s["state"]), "clients": len(s["clients"])}
                for sid, s in sessions.items()
            }
        body = json.dumps(info).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _handle_cmd(self, sid: str):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        try:
            cmd = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        with lock:
            sess = _get_session(sid)
            if cmd.get("cmd") == "clear":
                sess["state"].clear()
            elif cmd.get("cmd") == "init":
                # init clears previous state for this session
                sess["state"].clear()
                sess["state"].append(cmd)
            else:
                sess["state"].append(cmd)
            _save_session(sid)
            for q in sess["clients"]:
                q.put(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def _handle_clear(self, sid: str):
        with lock:
            sess = _get_session(sid)
            sess["state"].clear()
            _save_session(sid)
            clear_cmd = json.dumps({"cmd": "clear"})
            for q in sess["clients"]:
                q.put(clear_cmd)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(b'{"ok":true}')


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def find_port(start=6100, tries=20):
    import socket
    for p in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", p)) != 0:
                return p
    return start


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else find_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Diagram server running at http://127.0.0.1:{port}", flush=True)
    # Don't auto-open browser — let the agent control when to open
    if "--open" in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
