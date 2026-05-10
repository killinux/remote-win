import bpy, time
from mmd_tools.core.vmd.importer import VMDImporter

root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)
print(f"model: {root.name}")

# Remove old RGBA rig
bpy.context.view_layer.objects.active = root
bpy.ops.rgba_mmd.remove()
print("old rig removed")

# Set bouncier parameters
s = bpy.context.scene.rgba_mmd
s.spring_stiff_loose = 20.0
s.spring_stiff_strong = 150.0
s.spring_damp = 0.15
s.linear_damping = 0.4
s.angular_damping = 0.4
s.main_mass = 1.0
s.overwrite = True
print("params: loose_k=20 strong_k=150 damp=0.15 lin=0.4 ang=0.4 mass=1.0")

# Re-apply
bpy.ops.rgba_mmd.apply()
print(f"apply: {s.last_status}")

# Re-load VMD
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
            convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
            use_mirror=False).assign(arm)
scn = bpy.context.scene
fr = arm.animation_data.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])

# Bake physics
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake: {time.time()-t0:.1f}s")

# Sample
chest_L = next((o for o in bpy.data.objects
                if "胸.L" in o.name and not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor"))), None)
samples = []
for f in range(scn.frame_start, min(scn.frame_end, scn.frame_start + 300), 30):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    z = round(chest_L.evaluated_get(dg).matrix_world.translation.z, 4) if chest_L else None
    samples.append((f, z))

print("frame, chest_L.z")
for row in samples:
    print(row)
zs = [v for _, v in samples if v is not None]
if zs:
    print(f"\nNEW amplitude={max(zs)-min(zs):.4f} (was 1.4367)")
