#!/usr/bin/env python3
"""Lightweight SSE server for incremental diagram rendering. Zero dependencies."""

import json
import os
import queue
import sys
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
clients: list[queue.Queue] = []
lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence logs

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self._serve_template()
        elif self.path == "/events":
            self._serve_sse()
        elif self.path == "/status":
            self._serve_status()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/cmd":
            self._handle_cmd()
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
        self._cors()
        self.end_headers()
        self.wfile.write(html)

    def _serve_sse(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self._cors()
        self.end_headers()
        q: queue.Queue = queue.Queue()
        with lock:
            clients.append(q)
        try:
            while True:
                data = q.get()
                self.wfile.write(f"data: {data}\n\n".encode())
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with lock:
                if q in clients:
                    clients.remove(q)

    def _serve_status(self):
        body = json.dumps({"status": "ok", "clients": len(clients)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _handle_cmd(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        # broadcast to all SSE clients
        with lock:
            for q in clients:
                q.put(body)
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
    threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()


if __name__ == "__main__":
    main()
