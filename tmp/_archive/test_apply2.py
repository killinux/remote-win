import bpy, json, sys, importlib, addon_utils
# Force-reload the addon code from disk to be safe
for mod_name in list(sys.modules):
    if mod_name == "RGBA_mmd" or mod_name.startswith("RGBA_mmd."):
        del sys.modules[mod_name]
addon_utils.modules_refresh()
ok = addon_utils.enable("RGBA_mmd", default_set=True, persistent=True)
print("ENABLED:", repr(ok))

# Clean any partial state from the earlier failed run
import RGBA_mmd.rig_builder as rb
from mmd_tools.core.model import Model
root = None
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT":
                root = o; break
        except: pass
m = Model(root)
removed = rb.remove_rgba_objects(m)
print("CLEANED:", removed)

bpy.context.view_layer.objects.active = None
res = bpy.ops.rgba_mmd.apply()
s = bpy.context.scene.rgba_mmd
print("APPLY_RES:", res)
print("STATUS:", s.last_status)

rb_grp = None; jt_grp = None
for o in bpy.data.objects:
    try:
        if o.mmd_type == "RIGID_GRP_OBJ": rb_grp = o
        elif o.mmd_type == "JOINT_GRP_OBJ": jt_grp = o
    except: pass
def names(g): return None if not g else sorted([c.name for c in g.children])
print("RIGID:", json.dumps(names(rb_grp), ensure_ascii=False))
print("JOINTS:", json.dumps(names(jt_grp), ensure_ascii=False))
