import bpy, json
scn = bpy.context.scene
scn.frame_set(15)
dg = bpy.context.evaluated_depsgraph_get()
out = {}
for nm in ("上半身2_RGBAanchor", "胸_後.L", "胸_前.L", "胸_回転.L", "胸_前後.L", "胸.L"):
    o = bpy.data.objects.get(nm)
    if not o: continue
    eo = o.evaluated_get(dg)
    out[nm] = {
        "loc_z": round(eo.matrix_world.translation.z, 4),
        "rot_x": round(eo.rotation_euler.x, 4),
        "rot_y": round(eo.rotation_euler.y, 4),
        "rot_z": round(eo.rotation_euler.z, 4),
        "matrix_rot_x": round(eo.matrix_world.to_euler().x, 4),
    }
print(json.dumps(out, ensure_ascii=False, indent=2))

# Check the COPY_ROTATION targets — what bones does mmd_bonetrack get its rotation from?
print("--- mmd_bonetrack ---")
for tn in ("mmd_bonetrack", "mmd_bonetrack.001"):
    o = bpy.data.objects.get(tn)
    if o:
        eo = o.evaluated_get(dg)
        print(tn, "loc:", list(eo.matrix_world.translation), "rot_x:", eo.matrix_world.to_euler().x)
        for c in o.constraints:
            print("  constraint:", c.type, "target:", c.target.name if c.target else None,
                  "subtarget:", getattr(c, "subtarget", None) if hasattr(c, "subtarget") else None)
