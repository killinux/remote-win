import bpy, os, time
from mmd_tools.core.vmd.importer import VMDImporter

VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"
print("VMD_EXISTS:", os.path.isfile(VMD), "size:", os.path.getsize(VMD) if os.path.isfile(VMD) else 0)

root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)
print(f"model: root={root.name} arm={arm.name}")

VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
            convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
            use_mirror=False).assign(arm)
ad = arm.animation_data
fr = ad.action.frame_range
scn = bpy.context.scene
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])
print(f"VMD loaded: frames {scn.frame_start}-{scn.frame_end}")

w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end
try:
    bpy.ops.ptcache.free_bake_all()
except:
    pass

t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake done in {time.time()-t0:.1f}s, is_baked={w.point_cache.is_baked}")

chest_L = next((o for o in bpy.data.objects
                if "胸.L" in o.name and not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor"))), None)
print(f"chest_L={chest_L.name if chest_L else None}")

samples = []
for f in range(scn.frame_start, min(scn.frame_end, scn.frame_start + 300), 30):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    z = round(chest_L.evaluated_get(dg).matrix_world.translation.z, 4) if chest_L else None
    samples.append((f, z))

print("frame, chest_L.z")
for s in samples:
    print(s)

if samples:
    zs = [s[1] for s in samples if s[1] is not None]
    if zs:
        print(f"\nchest_L amplitude={max(zs)-min(zs):.4f}")
