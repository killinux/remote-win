import bpy
scn = bpy.context.scene
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
print(f"arm={arm.name}")

# Find the renamed chest body
chest_L = None
for o in bpy.data.objects:
    if "胸.L" in o.name and "_前" not in o.name and "_後" not in o.name and "_回転" not in o.name and "_前後" not in o.name and "anchor" not in o.name.lower():
        chest_L = o; break
print(f"chest_L={chest_L.name if chest_L else None}")

samples = []
for f in (1, 30, 60, 90, 120, 150, 180, 210, 240, 270, 295):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    bL = arm.pose.bones.get("boob left 1")
    samples.append((f,
        round(chest_L.evaluated_get(dg).matrix_world.translation.z, 3) if chest_L else None,
        round(bL.matrix.translation.z, 3) if bL else None,
    ))
print("frame, chest_L.z, bone_L.z")
for s in samples: print(s)

cz = [s[1] for s in samples if s[1] is not None]
bz = [s[2] for s in samples if s[2] is not None]
if cz and bz:
    print(f"\nchest amp={max(cz)-min(cz):.3f} bone amp={max(bz)-min(bz):.3f}")
    diffs = [abs(s[1]-s[2]) for s in samples if s[1] is not None and s[2] is not None]
    print(f"chest-bone gap mean={sum(diffs)/len(diffs):.3f} max={max(diffs):.3f}")
