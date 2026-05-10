"""Helper: POST a python file to the relay as execute_code, poll, print result."""
import json, sys, time, urllib.request, pathlib

RELAY = "http://localhost:8080"

def submit(code: str) -> str:
    payload = json.dumps({"type": "execute_code", "params": {"code": code}}).encode("utf-8")
    req = urllib.request.Request(RELAY + "/command", data=payload,
                                 headers={"Content-Type": "application/json; charset=utf-8"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)["id"]

def poll(cmd_id: str, timeout: float = 60.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(RELAY + "/command/" + cmd_id, timeout=10) as r:
            obj = json.load(r)
        if obj.get("status") == "completed":
            return obj
        time.sleep(1.0)
    return {"status": "timeout", "id": cmd_id}

def main():
    if len(sys.argv) < 2:
        print("usage: send.py <python_file> [timeout_sec]")
        sys.exit(2)
    p = pathlib.Path(sys.argv[1])
    timeout = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
    code = p.read_text(encoding="utf-8")
    cid = submit(code)
    print(f"id={cid}")
    out = poll(cid, timeout)
    outpath = pathlib.Path("send_result.json")
    outpath.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {outpath} ({outpath.stat().st_size} bytes)")
    # Also dump just the inner stdout for convenience
    try:
        result_str = out["response"]["result"]["result"]
        pathlib.Path("send_stdout.txt").write_text(result_str, encoding="utf-8")
        print("wrote send_stdout.txt")
    except Exception:
        pass

if __name__ == "__main__":
    main()
