import bpy, os, math
import RGBA_mmd.rig_builder as rb

VMD_PATH = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"
print("VMD_EXISTS:", os.path.isfile(VMD_PATH), "size:", os.path.getsize(VMD_PATH) if os.path.isfile(VMD_PATH) else None)

# locate model
root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"root={root.name} arm={arm.name}")

# Clear any keyframes we previously added on 上半身2 so we don't interfere
ad = arm.animation_data
if ad and ad.action:
    fcs = [fc for fc in ad.action.fcurves if "上半身2" in fc.data_path]
    for fc in fcs: ad.action.fcurves.remove(fc)
    print(f"cleared {len(fcs)} prior 上半身2 fcurves")

# Import VMD via mmd_tools' VMDImporter
print("=== Loading VMD ===")
from mmd_tools.core.vmd.importer import VMDImporter
importer = VMDImporter(filepath=VMD_PATH, scale=1.0,
                       bone_mapper=None,
                       use_pose_mode=True,
                       convert_mmd_camera=True,
                       convert_mmd_lamp=False,
                       frame_margin=5,
                       use_mirror=False)
# The importer is applied to objects (armature, mesh for morphs, etc.)
# Apply to the armature
importer.assign(arm)
print("VMD assigned to armature")

# Also try assigning to the root for camera/lamp / morph data
try:
    importer.assign(root)
    print("VMD assigned to root")
except Exception as e:
    print("root assign skipped:", e)

# Check action info
ad = arm.animation_data
if ad and ad.action:
    print(f"action='{ad.action.name}' frame_range={list(ad.action.frame_range)} fcurves={len(ad.action.fcurves)}")
    # bones with fcurves
    bones_animated = set()
    for fc in ad.action.fcurves:
        if "pose.bones" in fc.data_path:
            try:
                bn = fc.data_path.split('"')[1]
                bones_animated.add(bn)
            except: pass
    print(f"animated bones count: {len(bones_animated)}")
    print(f"sample bones: {sorted(bones_animated)[:15]}")

# Set frame range
scn = bpy.context.scene
fr = ad.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])
print(f"timeline: {scn.frame_start} - {scn.frame_end}")

# Re-apply rig (in case prior cleanup removed anything)
import RGBA_mmd.rig_builder as rb
from mmd_tools.core.model import Model
m = Model(root)
removed = rb.remove_rgba_objects(m)
print(f"removed {removed} prior RGBA objs")
bpy.context.view_layer.objects.active = root
res = bpy.ops.rgba_mmd.apply()
print(f"apply={res} status={bpy.context.scene.rgba_mmd.last_status}")

# Reset cache then sample motion
if scn.rigidbody_world and scn.rigidbody_world.point_cache:
    scn.rigidbody_world.point_cache.frame_start = scn.frame_start
    scn.rigidbody_world.point_cache.frame_end = scn.frame_end
try: bpy.ops.ptcache.free_bake_all()
except: pass

scn.frame_set(scn.frame_start)
samples=[]
total = scn.frame_end - scn.frame_start + 1
step = max(1, total // 30)
for f in range(scn.frame_start, scn.frame_end+1):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    cL = bpy.data.objects.get("胸.L")
    bL = arm.pose.bones.get("boob left 1")
    bR = arm.pose.bones.get("boob right 1")
    samples.append((f,
        round(cL.evaluated_get(dg).matrix_world.translation.z,4) if cL else None,
        round(bL.matrix.translation.z,4) if bL else None,
        round(bR.matrix.translation.z,4) if bR else None,
    ))

print("frame, 胸.L_z, bone_L_z, bone_R_z")
for s in samples[::step]: print(s)

cz = [s[1] for s in samples if s[1] is not None]
bz = [s[2] for s in samples if s[2] is not None]
if cz:
    print(f"\n胸.L Z: min={min(cz):.3f} max={max(cz):.3f} amp={max(cz)-min(cz):.3f}")
if bz:
    print(f"bone_L Z: min={min(bz):.3f} max={max(bz):.3f} amp={max(bz)-min(bz):.3f}")

# Save
sp = r"C:\Users\haoni\Desktop\rgba_yaoxiang_test.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=sp)
    print(f"SAVED: {sp}")
except Exception as e:
    print("save fail:", e)
