import bpy, addon_utils, json
out = {}
out["blender"] = bpy.app.version_string

# bust bones
arms = []
for o in bpy.data.objects:
    if o.type == "ARMATURE":
        bones = []
        for b in o.data.bones:
            n = b.name
            ln = n.lower()
            if "胸" in n or "bust" in ln or "breast" in ln or "oppai" in ln or "乳" in n:
                bones.append({"name": n, "parent": b.parent.name if b.parent else None})
        # also list any bone containing 上半身 for parent search
        upper = []
        for b in o.data.bones:
            if "上半身" in b.name:
                upper.append(b.name)
        arms.append({
            "obj": o.name,
            "bust_bones": bones,
            "upper_body_bones": upper,
            "all_bones_count": len(o.data.bones),
        })
out["armatures"] = arms

# mmd_root + its rigidbodies/joints group children
out["mmd_root"] = []
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT":
                kids = []
                for c in o.children:
                    kids.append({"name": c.name, "type": c.type, "mmd_type": getattr(c, "mmd_type", None)})
                out["mmd_root"].append({"name": o.name, "children": kids})
        except Exception as e:
            pass

# find rigidbodies/joints groups (they're empties with mmd_type)
rb_group = None
jt_group = None
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            mt = o.mmd_type
        except Exception:
            mt = None
        if mt == "RIGID_GRP_OBJ":
            rb_group = o
        elif mt == "JOINT_GRP_OBJ":
            jt_group = o

samples = {}
for label, p in (("rigidbodies", rb_group), ("joints", jt_group)):
    if not p:
        samples[label] = {"missing": True}
        continue
    info = {"group_name": p.name, "count": len(p.children)}
    info["first_names"] = [c.name for c in list(p.children)[:8]]
    if p.children:
        ex = p.children[0]
        info["example_name"] = ex.name
        if hasattr(ex, "mmd_rigid"):
            r = ex.mmd_rigid
            info["mmd_rigid"] = {
                "bone": getattr(r, "bone", None),
                "type": getattr(r, "type", None),
                "shape": getattr(r, "shape", None),
                "size": list(getattr(r, "size", [])) if hasattr(r, "size") else None,
                "collision_group_number": getattr(r, "collision_group_number", None),
                "collision_group_mask": list(getattr(r, "collision_group_mask", [])) if hasattr(r, "collision_group_mask") else None,
                "mass": getattr(r, "mass", None),
                "friction": getattr(r, "friction", None),
                "linear_damping": getattr(r, "linear_damping", None),
                "angular_damping": getattr(r, "angular_damping", None),
                "bounce": getattr(r, "bounce", None),
            }
            info["mmd_rigid_attrs"] = sorted([a for a in dir(r) if not a.startswith("_")])
        if hasattr(ex, "mmd_joint"):
            j = ex.mmd_joint
            info["mmd_joint_attrs"] = sorted([a for a in dir(j) if not a.startswith("_")])
            info["mmd_joint_sample"] = {
                "name_j": getattr(j, "name_j", None),
                "spring_linear": list(getattr(j, "spring_linear", [])) if hasattr(j, "spring_linear") else None,
                "spring_angular": list(getattr(j, "spring_angular", [])) if hasattr(j, "spring_angular") else None,
            }
        if ex.rigid_body_constraint:
            rbc = ex.rigid_body_constraint
            info["rbc"] = {
                "type": rbc.type,
                "object1": rbc.object1.name if rbc.object1 else None,
                "object2": rbc.object2.name if rbc.object2 else None,
                "use_limit_lin_x": rbc.use_limit_lin_x,
                "limit_lin_x_lower": rbc.limit_lin_x_lower,
                "limit_lin_x_upper": rbc.limit_lin_x_upper,
                "use_spring_x": getattr(rbc, "use_spring_x", None),
                "spring_stiffness_x": getattr(rbc, "spring_stiffness_x", None),
                "spring_damping_x": getattr(rbc, "spring_damping_x", None),
            }
    samples[label] = info
out["samples"] = samples

# operator surface
ops_check = {}
if hasattr(bpy.ops, "mmd_tools"):
    for nm in ("rigid_body_add", "joint_add", "build_rig"):
        ops_check[nm] = hasattr(bpy.ops.mmd_tools, nm)
out["ops"] = ops_check

print("RGBA_PROBE_BEGIN")
print(json.dumps(out, ensure_ascii=False, indent=2))
print("RGBA_PROBE_END")
