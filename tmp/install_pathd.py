"""把本地 pathd 插件推送并启用到远程 Blender。仿 install_remote.py。"""
import json
import pathlib
import time
import urllib.request

RELAY = "http://localhost:8080"
LOCAL_ADDON = pathlib.Path(r"C:\Users\Administrator\Desktop\winwork\pathd")
ADDON_NAME = "pathd"
FILES = [f.name for f in LOCAL_ADDON.iterdir() if f.suffix == '.py' or f.name == 'README.md']


def submit(code: str) -> str:
    payload = json.dumps({"type": "execute_code", "params": {"code": code}}).encode("utf-8")
    req = urllib.request.Request(RELAY + "/command", data=payload,
                                 headers={"Content-Type": "application/json; charset=utf-8"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.load(r)["id"]


def poll(cmd_id: str, timeout: float) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with urllib.request.urlopen(RELAY + "/command/" + cmd_id, timeout=10) as r:
            obj = json.load(r)
        if obj.get("status") == "completed":
            return obj
        time.sleep(1.0)
    return {"status": "timeout", "id": cmd_id}


def main():
    files = {}
    for fn in FILES:
        p = LOCAL_ADDON / fn
        files[fn] = p.read_text(encoding="utf-8")

    code = []
    code.append("import bpy, addon_utils, os, sys, importlib, shutil")
    code.append("addon_dir = bpy.utils.user_resource('SCRIPTS', path='addons', create=True)")
    code.append(f"target = os.path.join(addon_dir, '{ADDON_NAME}')")
    code.append(f"try: addon_utils.disable('{ADDON_NAME}', default_set=False)")
    code.append("except: pass")
    code.append("for mod_name in list(sys.modules):")
    code.append(f"    if mod_name == '{ADDON_NAME}' or mod_name.startswith('{ADDON_NAME}.'):")
    code.append("        del sys.modules[mod_name]")
    code.append("if os.path.isdir(target): shutil.rmtree(target)")
    code.append("os.makedirs(target, exist_ok=True)")
    code.append("FILES = " + json.dumps(files, ensure_ascii=False))
    code.append("for fn, txt in FILES.items():")
    code.append("    with open(os.path.join(target, fn), 'w', encoding='utf-8') as f:")
    code.append("        f.write(txt)")
    code.append("addon_utils.modules_refresh()")
    code.append(f"ok = addon_utils.enable('{ADDON_NAME}', default_set=True, persistent=True)")
    code.append("if ok:")
    code.append("    try: importlib.reload(ok)")
    code.append("    except Exception as e: print('reload_err',e)")
    code.append("print('INSTALL_OK', target, 'enabled_obj=', repr(ok))")
    code.append(f"import {ADDON_NAME} as mod; print('mod.bl_info=', mod.bl_info.get('version'))")
    full = "\n".join(code)

    cid = submit(full)
    print(f"install id={cid}")
    out = poll(cid, 60.0)
    print(json.dumps(out.get("response", out), ensure_ascii=False, indent=2)[:4000])


if __name__ == "__main__":
    main()
