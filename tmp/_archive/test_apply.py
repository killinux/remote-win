import bpy, json
bpy.context.view_layer.objects.active = None
res = bpy.ops.rgba_mmd.apply()
s = bpy.context.scene.rgba_mmd
print("APPLY_RES", res)
print("STATUS:", s.last_status)
# Count what was created
root = None
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT":
                root = o; break
        except Exception:
            pass
rb_grp = None; jt_grp = None
for o in bpy.data.objects:
    try:
        if o.mmd_type == "RIGID_GRP_OBJ": rb_grp = o
        elif o.mmd_type == "JOINT_GRP_OBJ": jt_grp = o
    except Exception: pass
def names(grp):
    if not grp: return None
    return sorted([c.name for c in grp.children])
print("RIGID_BODIES:", json.dumps(names(rb_grp), ensure_ascii=False))
print("JOINTS:", json.dumps(names(jt_grp), ensure_ascii=False))
