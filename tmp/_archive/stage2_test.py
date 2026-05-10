import bpy, math
from mathutils import Euler
import RGBA_mmd.rig_builder as rb
from mmd_tools.core.model import Model

# locate
root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"root={root.name} arm={arm.name}")
bust = rb.detect_bust_bones(arm)
parent = rb.find_parent_bone(arm, "")
print(f"bust={bust} parent={parent}")

# Apply
bpy.context.view_layer.objects.active = root
res = bpy.ops.rgba_mmd.apply()
print(f"apply={res} status={bpy.context.scene.rgba_mmd.last_status}")

# Animate 上半身2
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones["上半身2"]
pb.rotation_mode = 'XYZ'
for f in range(1, 91):
    a = 0.6 * math.sin((f-1)/90 * 4 * math.pi)
    pb.rotation_euler = Euler((a,0,0),'XYZ')
    pb.keyframe_insert(data_path="rotation_euler", frame=f)
bpy.ops.object.mode_set(mode='OBJECT')
print("keyframed 90 frames")

# Step physics
scn = bpy.context.scene
scn.frame_start=1; scn.frame_end=90
if scn.rigidbody_world and scn.rigidbody_world.point_cache:
    scn.rigidbody_world.point_cache.frame_start=1
    scn.rigidbody_world.point_cache.frame_end=90
try: bpy.ops.ptcache.free_bake_all()
except: pass

scn.frame_set(1)
samples=[]
for f in range(1,91):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    cL = bpy.data.objects.get("胸.L")
    bL = arm.pose.bones[bust[1][0]] if len(bust)>1 else arm.pose.bones[bust[0][0]]
    bR = arm.pose.bones[bust[0][0]]
    samples.append((f,
        round(cL.evaluated_get(dg).matrix_world.translation.z,4) if cL else None,
        round(bL.matrix.translation.z,4),
        round(bR.matrix.translation.z,4),
    ))
print("frame, 胸.L_z, bone_L_z, bone_R_z (every 5th frame)")
for s in samples[::5]: print(s)
cz = [s[1] for s in samples if s[1] is not None]
bz = [s[2] for s in samples]
print(f"\n胸.L Z range=[{min(cz):.3f},{max(cz):.3f}] amp={max(cz)-min(cz):.3f}")
print(f"bone_L Z range=[{min(bz):.3f},{max(bz):.3f}] amp={max(bz)-min(bz):.3f}")

# Save
sp = r"C:\Users\haoni\Desktop\rgba_test.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=sp)
    print(f"SAVED: {sp}")
except Exception as e:
    print("save fail:", e)
