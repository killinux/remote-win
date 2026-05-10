"""Re-import + apply + BAKE the rigid body cache + sample motion."""
import bpy, os
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter
from mmd_tools.core.model import Model
import RGBA_mmd.rig_builder as rb

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# Clean scene
def clear_scene():
    for o in list(bpy.data.objects):
        try: bpy.data.objects.remove(o, do_unlink=True)
        except: pass
clear_scene()
print("scene cleared")

# Import PMX
PMXImporter().execute(filepath=PMX, types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
                     scale=1.0, clean_model=False, remove_doubles=False)
root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"PMX OK: root={root.name}")

# Import VMD
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
            convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
            use_mirror=False).assign(arm)
ad = arm.animation_data
fr = ad.action.frame_range
scn = bpy.context.scene
scn.frame_start = int(fr[0]); scn.frame_end = int(fr[1])
print(f"VMD OK: frames {scn.frame_start}-{scn.frame_end}")

# Apply RGBA
bpy.context.view_layer.objects.active = root
bpy.ops.rgba_mmd.apply()
print(f"applied: {scn.rgba_mmd.last_status}")

# Set point cache range
w = scn.rigidbody_world
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end
print(f"cache range: {w.point_cache.frame_start}-{w.point_cache.frame_end}")

# Free any prior bake
try: bpy.ops.ptcache.free_bake_all()
except Exception as e: print("free:", e)

# CRITICAL: bake the rigid body cache for the FULL range
print("=== Baking rigid body cache (this can take 60+ seconds) ===")
import time
t0 = time.time()
# Use 'point_cache' override
override = {'point_cache': w.point_cache, 'scene': scn}
try:
    with bpy.context.temp_override(scene=scn):
        bpy.ops.ptcache.bake_all(bake=True)
    print(f"baked in {time.time()-t0:.1f}s. is_baked={w.point_cache.is_baked}")
except Exception as e:
    print(f"bake failed: {e}")

# Sample post-bake
samples = []
for f in (1, 30, 60, 90, 120, 150, 180, 210, 240, 270, 295):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    cL = bpy.data.objects.get("胸.L")
    bL = arm.pose.bones.get("boob left 1")
    samples.append((f,
        round(cL.evaluated_get(dg).matrix_world.translation.z, 3) if cL else None,
        round(bL.matrix.translation.z, 3) if bL else None,
    ))
print("frame, 胸.L_z, bone_L_z")
for s in samples: print(s)

cz = [s[1] for s in samples if s[1] is not None]
bz = [s[2] for s in samples if s[2] is not None]
if cz and bz:
    print(f"\n胸.L Z amp={max(cz)-min(cz):.3f}  bone_L Z amp={max(bz)-min(bz):.3f}")
    diffs = [abs(s[1]-s[2]) for s in samples if s[1] is not None and s[2] is not None]
    print(f"chest-bone gap mean={sum(diffs)/len(diffs):.3f} max={max(diffs):.3f}")

# Save final
sp = r"C:\Users\haoni\Desktop\rgba_yaoxiang_test.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=sp)
    print(f"SAVED: {sp}")
except Exception as e: print("save fail:", e)
