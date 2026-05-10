import bpy
scn = bpy.context.scene
scn.frame_set(1)

for nm in ("joints", "rigidbodies", "Inase54"):
    o = bpy.data.objects.get(nm)
    if not o: continue
    print(f"{nm}: parent={o.parent.name if o.parent else None} type={o.parent_type} bone={o.parent_bone}")
    print(f"  loc={list(o.location)} world_loc={list(o.matrix_world.translation)}")

scn.frame_set(60)
print("\n--- AT FRAME 60 ---")
for nm in ("joints", "rigidbodies", "Inase54"):
    o = bpy.data.objects.get(nm)
    if not o: continue
    print(f"{nm}: world_loc={list(o.matrix_world.translation)}")

# Also where is 上半身2_RGBAanchor at frame 60
a = bpy.data.objects.get("上半身2_RGBAanchor")
if a:
    print(f"\n上半身2_RGBAanchor at frame 60: world={list(a.matrix_world.translation)}")
c = bpy.data.objects.get("胸.L")
if c:
    print(f"胸.L at frame 60: world={list(c.matrix_world.translation)}")
# also the bone position in world
arm = bpy.data.objects.get("Inase54_arm")
if arm:
    pb = arm.pose.bones.get("boob left 1")
    if pb:
        wm = arm.matrix_world @ pb.matrix
        print(f"boob left 1 at frame 60 (world): {list(wm.translation)}")
