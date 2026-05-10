import bpy
import RGBA_mmd.rig_builder as rb

rgba_objs = [o.name for o in bpy.data.objects if "胸" in o.name or "RGBAanchor" in o.name]
print("RGBA_OBJS:", len(rgba_objs))

# Check joint types
fixed_count = 0
spring_count = 0
for j in rb.iter_rgba_joints():
    if j.rigid_body_constraint:
        if j.rigid_body_constraint.type == 'FIXED': fixed_count += 1
        elif j.rigid_body_constraint.type == 'GENERIC_SPRING': spring_count += 1
print(f"FIXED={fixed_count}  GENERIC_SPRING={spring_count}")

# Check action
arm = bpy.data.objects.get("Inase54_arm")
ad = arm.animation_data if arm else None
print("ACTION:", ad.action.name if (ad and ad.action) else None)

# Sample only 5 frames quickly
scn = bpy.context.scene
print(f"timeline: {scn.frame_start}-{scn.frame_end}")
scn.frame_set(1)
samples = []
for f in (1, 50, 100, 150, 200):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    cL = bpy.data.objects.get("胸.L")
    bL = arm.pose.bones.get("boob left 1") if arm else None
    samples.append((f,
        round(cL.evaluated_get(dg).matrix_world.translation.z,3) if cL else None,
        round(bL.matrix.translation.z,3) if bL else None,
    ))
print("frame, 胸.L_z, bone_L_z")
for s in samples: print(s)
