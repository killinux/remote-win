import bpy, json
arm = bpy.data.objects["Inase54_arm"]
out = {}
for bn in ("boob right 1", "boob left 1", "上半身2"):
    pb = arm.pose.bones.get(bn)
    if not pb:
        out[bn] = "missing"
        continue
    out[bn] = {
        "constraints": [(c.type, c.name, getattr(c, "target", None).name if getattr(c, "target", None) else None) for c in pb.constraints],
        "loc_lock": list(pb.lock_location),
        "rot_lock": list(pb.lock_rotation),
    }
print(json.dumps(out, ensure_ascii=False, indent=2))

# Check if there's an action driving the bones
print("---ACTION---")
ad = arm.animation_data
if ad and ad.action:
    print("action:", ad.action.name, "frames:", ad.action.frame_range)
    # Find fcurves on bust bones
    chans = []
    for fc in ad.action.fcurves:
        if any(b in fc.data_path for b in ("boob right 1", "boob left 1")):
            chans.append((fc.data_path, fc.array_index, len(fc.keyframe_points)))
    print("bust_fcurves:", chans[:20])
else:
    print("no animation_data")

# Check if main 胸 rigid has actually moved (read from depsgraph)
dg = bpy.context.evaluated_depsgraph_get()
for nm in ("胸.L", "胸.R"):
    o = bpy.data.objects.get(nm)
    if o:
        eo = o.evaluated_get(dg)
        print(nm, "eval_loc:", list(eo.matrix_world.translation), "rest_loc:", list(o.matrix_world.translation))
