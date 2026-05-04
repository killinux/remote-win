#!/usr/bin/env python3
"""
Blender-MCP HTTP Relay Server — runs on Windows.

Claude Code posts commands here. The Mac polls for them, forwards to
blender-mcp, and posts results back.

Usage:
    python server.py --port 8080
"""

import argparse
import json
import threading
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse


class CommandStore:
    def __init__(self):
        self.commands = {}
        self.lock = threading.Lock()
        self.mac_last_seen = None

    def add(self, request):
        cmd_id = uuid.uuid4().hex[:8]
        with self.lock:
            self.commands[cmd_id] = {
                "id": cmd_id,
                "status": "pending",
                "created_at": time.time(),
                "claimed_at": None,
                "completed_at": None,
                "request": request,
                "response": None,
            }
        return cmd_id

    def claim_next(self):
        with self.lock:
            self.mac_last_seen = time.time()
            for cmd_id, cmd in sorted(self.commands.items(), key=lambda x: x[1]["created_at"]):
                if cmd["status"] == "pending":
                    cmd["status"] = "processing"
                    cmd["claimed_at"] = time.time()
                    return cmd
        return None

    def set_response(self, cmd_id, response):
        with self.lock:
            if cmd_id in self.commands:
                self.commands[cmd_id]["response"] = response
                self.commands[cmd_id]["status"] = "completed"
                self.commands[cmd_id]["completed_at"] = time.time()
                return True
        return False

    def get(self, cmd_id):
        with self.lock:
            return self.commands.get(cmd_id)

    def stats(self):
        with self.lock:
            counts = {"pending": 0, "processing": 0, "completed": 0}
            for cmd in self.commands.values():
                counts[cmd["status"]] = counts.get(cmd["status"], 0) + 1
            mac_connected = self.mac_last_seen and (time.time() - self.mac_last_seen) < 10
            return {
                "mac_last_seen": self.mac_last_seen,
                "mac_connected": mac_connected,
                "queue": counts,
                "total": len(self.commands),
            }

    def recent(self, limit=20):
        with self.lock:
            cmds = sorted(self.commands.values(), key=lambda x: x["created_at"], reverse=True)
            return cmds[:limit]

    def cleanup(self, max_age=3600):
        now = time.time()
        with self.lock:
            expired = [k for k, v in self.commands.items() if now - v["created_at"] > max_age]
            for k in expired:
                del self.commands[k]


store = CommandStore()


class RelayHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/commands/pending":
            self._handle_poll()
        elif path.startswith("/command/"):
            cmd_id = path.split("/")[2]
            self._handle_get_command(cmd_id)
        elif path == "/status":
            self._handle_status_html()
        elif path == "/api/status":
            self._send_json(store.stats())
        else:
            self._send_json({"error": "not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/command":
            self._handle_submit()
        elif path.startswith("/command/") and path.endswith("/response"):
            parts = path.split("/")
            cmd_id = parts[2]
            self._handle_response(cmd_id)
        else:
            self._send_json({"error": "not found"}, 404)

    def _handle_poll(self):
        cmd = store.claim_next()
        if cmd:
            self._send_json({"id": cmd["id"], "request": cmd["request"]})
        else:
            self._send_json({"id": None})

    def _handle_get_command(self, cmd_id):
        cmd = store.get(cmd_id)
        if cmd:
            self._send_json({
                "id": cmd["id"],
                "status": cmd["status"],
                "request": cmd["request"],
                "response": cmd["response"],
            })
        else:
            self._send_json({"error": "not found"}, 404)

    def _handle_submit(self):
        body = self._read_body()
        if not body:
            self._send_json({"error": "empty body"}, 400)
            return
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, 400)
            return
        cmd_id = store.add(request)
        self._send_json({"id": cmd_id, "status": "pending"}, 201)

    def _handle_response(self, cmd_id):
        body = self._read_body()
        if not body:
            self._send_json({"error": "empty body"}, 400)
            return
        try:
            response = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, 400)
            return
        if store.set_response(cmd_id, response):
            self._send_json({"ok": True})
        else:
            self._send_json({"error": "command not found"}, 404)

    def _handle_status_html(self):
        stats = store.stats()
        recent = store.recent(15)
        mac_status = "CONNECTED" if stats["mac_connected"] else "DISCONNECTED"
        mac_color = "#4caf50" if stats["mac_connected"] else "#f44336"

        rows = ""
        for cmd in recent:
            age = time.time() - cmd["created_at"]
            if age < 60:
                age_str = f"{int(age)}s ago"
            else:
                age_str = f"{int(age/60)}m ago"
            req_type = cmd["request"].get("type", "?")
            status = cmd["status"]
            status_color = {"pending": "#ff9800", "processing": "#2196f3", "completed": "#4caf50"}.get(status, "#999")
            resp_preview = ""
            if cmd["response"]:
                resp_preview = json.dumps(cmd["response"])[:80]
            rows += f'<tr><td><code>{cmd["id"]}</code></td><td>{req_type}</td><td style="color:{status_color}">{status}</td><td>{age_str}</td><td><small>{resp_preview}</small></td></tr>\n'

        html = f"""<!DOCTYPE html>
<html>
<head><title>Blender Relay</title>
<meta http-equiv="refresh" content="3">
<style>
body {{ font-family: monospace; background: #1a1a1a; color: #eee; padding: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ text-align: left; padding: 8px; border-bottom: 1px solid #333; }}
th {{ color: #888; }}
.status {{ font-size: 1.2em; margin: 10px 0 20px; }}
</style>
</head>
<body>
<h2>Blender-MCP Relay</h2>
<div class="status">
Mac: <span style="color:{mac_color};font-weight:bold">{mac_status}</span>
&nbsp;&nbsp;|&nbsp;&nbsp;
Queue: {stats['queue']['pending']} pending, {stats['queue']['processing']} processing, {stats['queue']['completed']} completed
</div>
<table>
<tr><th>ID</th><th>Type</th><th>Status</th><th>Age</th><th>Response</th></tr>
{rows}
</table>
</body></html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return None
        return self.rfile.read(length)

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description="Blender-MCP HTTP Relay Server")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    # Cleanup thread
    def cleanup_loop():
        while True:
            time.sleep(300)
            store.cleanup()

    threading.Thread(target=cleanup_loop, daemon=True).start()

    server = ThreadedHTTPServer((args.host, args.port), RelayHandler)
    print(f"Relay server on http://{args.host}:{args.port}")
    print(f"  Status page: http://localhost:{args.port}/status")
    print(f"  Mac client polls: http://YOUR_IP:{args.port}/commands/pending")
    print(f"  Submit command: POST http://localhost:{args.port}/command")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutdown.")


if __name__ == "__main__":
    main()
