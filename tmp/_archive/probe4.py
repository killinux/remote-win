import bpy, json, inspect
from mmd_tools.core.model import Model
out = {}
for fn in ("createRigidBody", "createJoint"):
    f = getattr(Model, fn, None)
    if f:
        try:
            out[fn + "_sig"] = str(inspect.signature(f))
        except Exception as e:
            out[fn + "_sig_err"] = str(e)
        out[fn + "_doc"] = (f.__doc__ or "").strip()[:400]
# also dump source first 80 lines of each
import mmd_tools.core.model as M
src = inspect.getsource(M)
out["src_len"] = len(src)
# extract createRigidBody and createJoint defs
import re
for fn in ("createRigidBody", "createJoint"):
    m = re.search(r"def " + fn + r"\([^)]*\)[^:]*:", src)
    if m:
        out[fn + "_def"] = m.group(0)
print("R4BEGIN"); print(json.dumps(out, ensure_ascii=False, indent=2)); print("R4END")
