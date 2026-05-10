"""Apply RGBA rig + sample 30 frames evenly across timeline (fast)."""
import bpy
import RGBA_mmd.rig_builder as rb
from mmd_tools.core.model import Model

root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"root={root.name} arm={arm.name}")

# clean prior + apply
m = Model(root)
removed = rb.remove_rgba_objects(m)
print(f"removed {removed} prior")
bpy.context.view_layer.objects.active = root
res = bpy.ops.rgba_mmd.apply()
print(f"apply={res}")

fixed = sum(1 for j in rb.iter_rgba_joints() if j.rigid_body_constraint and j.rigid_body_constraint.type=='FIXED')
spring = sum(1 for j in rb.iter_rgba_joints() if j.rigid_body_constraint and j.rigid_body_constraint.type=='GENERIC_SPRING')
print(f"joints: FIXED={fixed} SPRING={spring}")

scn = bpy.context.scene
print(f"timeline {scn.frame_start}-{scn.frame_end}")
if scn.rigidbody_world and scn.rigidbody_world.point_cache:
    scn.rigidbody_world.point_cache.frame_start = scn.frame_start
    scn.rigidbody_world.point_cache.frame_end = scn.frame_end
try: bpy.ops.ptcache.free_bake_all()
except: pass

# sample 25 frames evenly
N = 25
total = scn.frame_end - scn.frame_start + 1
step = max(1, total // N)
scn.frame_set(scn.frame_start)
samples = []
for f in range(scn.frame_start, scn.frame_end + 1, step):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    cL = bpy.data.objects.get("胸.L")
    bL = arm.pose.bones.get("boob left 1")
    samples.append((f,
        round(cL.evaluated_get(dg).matrix_world.translation.z,3) if cL else None,
        round(bL.matrix.translation.z,3) if bL else None,
    ))
print("frame, 胸.L_z, bone_L_z")
for s in samples: print(s)

cz = [s[1] for s in samples if s[1] is not None]
bz = [s[2] for s in samples if s[2] is not None]
if cz:
    print(f"\n胸.L Z amp={max(cz)-min(cz):.3f}  range=[{min(cz):.3f},{max(cz):.3f}]")
if bz:
    print(f"bone_L Z amp={max(bz)-min(bz):.3f}  range=[{min(bz):.3f},{max(bz):.3f}]")
diffs = [abs(s[1]-s[2]) for s in samples if s[1] is not None and s[2] is not None]
if diffs:
    print(f"chest-bone Z gap mean={sum(diffs)/len(diffs):.3f} max={max(diffs):.3f}")
    if max(diffs) > 5:
        print("WARN: chest detached from bone (>5m gap) — physics still unstable")
    else:
        print("OK: chest tracks bone")
