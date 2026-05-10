import bpy
import RGBA_mmd.rig_builder as rb
from mmd_tools.core.model import Model

# locate
root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"root={root.name} arm={arm.name}")

# clean prior rig
m = Model(root)
removed = rb.remove_rgba_objects(m)
print(f"removed {removed} prior RGBA objs")

# apply new rig
bpy.context.view_layer.objects.active = root
res = bpy.ops.rgba_mmd.apply()
print(f"apply={res} status={bpy.context.scene.rgba_mmd.last_status}")

# Verify joint types
locked_count = 0
spring_count = 0
for j in rb.iter_rgba_joints():
    if j.rigid_body_constraint:
        if j.rigid_body_constraint.type == 'FIXED':
            locked_count += 1
        elif j.rigid_body_constraint.type == 'GENERIC_SPRING':
            spring_count += 1
print(f"joints: FIXED={locked_count}  GENERIC_SPRING={spring_count}")

# Sample physics across the existing VMD timeline
scn = bpy.context.scene
# already 1-295 from VMD
print(f"timeline: {scn.frame_start}-{scn.frame_end}")
if scn.rigidbody_world and scn.rigidbody_world.point_cache:
    scn.rigidbody_world.point_cache.frame_start = scn.frame_start
    scn.rigidbody_world.point_cache.frame_end = scn.frame_end
try: bpy.ops.ptcache.free_bake_all()
except: pass

scn.frame_set(scn.frame_start)
samples = []
total = scn.frame_end - scn.frame_start + 1
for f in range(scn.frame_start, scn.frame_end+1):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    cL = bpy.data.objects.get("胸.L")
    bL = arm.pose.bones.get("boob left 1")
    bR = arm.pose.bones.get("boob right 1")
    samples.append((f,
        round(cL.evaluated_get(dg).matrix_world.translation.z,3) if cL else None,
        round(bL.matrix.translation.z,3) if bL else None,
        round(bR.matrix.translation.z,3) if bR else None,
    ))
step = max(1, total // 25)
print("frame, 胸.L_z, bone_L_z, bone_R_z")
for s in samples[::step]: print(s)

cz = [s[1] for s in samples if s[1] is not None]
bz = [s[2] for s in samples if s[2] is not None]
print(f"\n胸.L Z:   min={min(cz):.3f} max={max(cz):.3f} amp={max(cz)-min(cz):.3f}")
print(f"bone_L Z: min={min(bz):.3f} max={max(bz):.3f} amp={max(bz)-min(bz):.3f}")
# A healthy result: chest amp similar to bone amp, with chest tracking bone closely
# (no runaway). Difference indicates the bounce/lag.
diffs = [abs(s[1] - s[2]) for s in samples if s[1] is not None and s[2] is not None]
print(f"chest/bone Z gap: mean={sum(diffs)/len(diffs):.3f} max={max(diffs):.3f}")

# Save
sp = r"C:\Users\haoni\Desktop\rgba_yaoxiang_test.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=sp)
    print(f"SAVED: {sp}")
except Exception as e:
    print("save fail:", e)
