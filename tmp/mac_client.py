#!/usr/bin/env python3
"""
Blender-MCP Mac Client — runs on Mac alongside Blender.

Polls the Windows relay server for commands, forwards them to
local blender-mcp on localhost:9876, posts results back.

Usage:
    python3 mac_client.py --server http://WINDOWS_IP:8080
    python3 mac_client.py --server http://WINDOWS_IP:8080 --blender localhost:9876
"""

import argparse
import http.client
import json
import socket
import sys
import time
import urllib.request
import urllib.error


def _http_json_get(url, timeout=10, retries=3):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"Connection": "close"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (http.client.IncompleteRead, http.client.RemoteDisconnected,
                ConnectionResetError, urllib.error.URLError, OSError) as e:
            last = e
            time.sleep(0.5 * (attempt + 1))
    raise last


def _http_json_post(url, body, timeout=15, retries=3):
    last = None
    payload = json.dumps(body).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json", "Connection": "close"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp.read()
            return True
        except (http.client.IncompleteRead, http.client.RemoteDisconnected,
                ConnectionResetError, urllib.error.URLError, OSError) as e:
            last = e
            time.sleep(0.5 * (attempt + 1))
    raise last


class BlenderBridge:
    def __init__(self, host="localhost", port=9876, timeout=180):
        self.host = host
        self.port = port
        self.timeout = timeout

    def send(self, command):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((self.host, self.port))
            payload = json.dumps(command).encode("utf-8")
            sock.sendall(payload)

            buffer = b""
            while True:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                buffer += chunk
                try:
                    return json.loads(buffer.decode("utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue

            if buffer:
                try:
                    return json.loads(buffer.decode("utf-8"))
                except Exception:
                    return {"status": "error", "message": f"invalid response: {buffer[:200]}"}
            return {"status": "error", "message": "empty response from blender"}
        except socket.timeout:
            return {"status": "error", "message": "blender timeout"}
        except ConnectionRefusedError:
            return {"status": "error", "message": f"cannot connect to blender-mcp on {self.host}:{self.port}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            sock.close()


class RelayPoller:
    def __init__(self, server_url, bridge):
        self.server_url = server_url.rstrip("/")
        self.bridge = bridge

    def poll_once(self):
        try:
            data = _http_json_get(f"{self.server_url}/commands/pending", timeout=10, retries=3)
        except Exception as e:
            print(f"  [!] Poll error: {e}")
            return False

        if data.get("id") is None:
            return False

        cmd_id = data["id"]
        request = data["request"]
        req_type = request.get("type", "?")
        print(f"  [{cmd_id}] Got command: {req_type}")

        response = self.bridge.send(request)
        print(f"  [{cmd_id}] Blender responded: {response.get('status', '?')}")

        try:
            _http_json_post(
                f"{self.server_url}/command/{cmd_id}/response",
                response, timeout=15, retries=4,
            )
        except Exception as e:
            print(f"  [{cmd_id}] Failed to post response: {e}")

        return True

    def run(self, interval=1.0):
        print(f"=== Blender-MCP Mac Client ===")
        print(f"Relay:   {self.server_url}")
        print(f"Blender: {self.bridge.host}:{self.bridge.port}")
        print()

        idle_count = 0
        while True:
            did_work = self.poll_once()
            if did_work:
                idle_count = 0
                time.sleep(0.1)
            else:
                idle_count += 1
                wait = min(interval * (1 + idle_count // 30), 3.0)
                time.sleep(wait)


def main():
    parser = argparse.ArgumentParser(description="Blender-MCP Mac Client")
    parser.add_argument("--server", required=True, help="Relay server URL (e.g. http://192.168.1.100:8080)")
    parser.add_argument("--blender", default="localhost:9876", help="Blender-MCP address (default: localhost:9876)")
    parser.add_argument("--interval", type=float, default=1.0, help="Poll interval in seconds (default: 1)")
    args = parser.parse_args()

    blender_parts = args.blender.split(":")
    blender_host = blender_parts[0]
    blender_port = int(blender_parts[1]) if len(blender_parts) > 1 else 9876

    bridge = BlenderBridge(blender_host, blender_port)
    poller = RelayPoller(args.server, bridge)

    try:
        poller.run(args.interval)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
