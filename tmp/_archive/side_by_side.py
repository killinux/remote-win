import bpy, time
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter
from mmd_tools.core.model import Model

VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# Clean
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)
print("Scene cleared")

# === Import Model A: Inase54 Simple (left side, X = -15) ===
PMXImporter().execute(
    filepath=r"E:\mywork\mymodel\inase54_simple_phys.pmx",
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)

root_a = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm_a = next(c for c in root_a.children if c.type=="ARMATURE")
root_a.location.x = -15
print(f"Model A: {root_a.name} at X=-15")

# Load VMD on A
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm_a)
print("  VMD loaded on A")

# Build rig for A
bpy.context.view_layer.objects.active = root_a
bpy.ops.mmd_tools.build_rig()
print("  build_rig done on A")

# === Import Model B: Target (right side, X = +15) ===
PMXImporter().execute(
    filepath=r"E:\mywork\mymodel\Purifier Inase 18\Purifier Inase 18 V1.pmx",
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)

# Find the new root (not root_a)
roots = [o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"]
root_b = next(r for r in roots if r != root_a)
arm_b = next(c for c in root_b.children if c.type=="ARMATURE")
root_b.location.x = 15
print(f"Model B: {root_b.name} at X=+15")

# Load VMD on B
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm_b)
print("  VMD loaded on B")

# Build rig for B
bpy.context.view_layer.objects.active = root_b
bpy.ops.mmd_tools.build_rig()
print("  build_rig done on B")

# === Setup physics world ===
scn = bpy.context.scene
fr_a = arm_a.animation_data.action.frame_range
fr_b = arm_b.animation_data.action.frame_range
scn.frame_start = int(min(fr_a[0], fr_b[0]))
scn.frame_end = int(max(fr_a[1], fr_b[1]))

w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 10
w.solver_iterations = 10
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end

# Bake
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"\nBake: {time.time()-t0:.1f}s, frames {scn.frame_start}-{scn.frame_end}")

# Save
save_path = r"E:\mywork\mymodel\side_by_side_compare.blend"
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"SAVED: {save_path}")
print(f"\nLeft (X=-15): Inase54 Simple")
print(f"Right (X=+15): Purifier Inase 18 (Target)")
print(f"Press Alt+A to play and compare!")
