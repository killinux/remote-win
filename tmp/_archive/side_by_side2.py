import bpy, time
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter

VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# Clean
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

# === Model A: Inase54 Simple (X=-5) ===
PMXImporter().execute(
    filepath=r"E:\mywork\mymodel\inase54_simple_phys.pmx",
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root_a = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm_a = next(c for c in root_a.children if c.type=="ARMATURE")
root_a.location.x = -5

VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm_a)

bpy.context.view_layer.objects.active = root_a
bpy.ops.mmd_tools.build_rig()
print(f"A: {root_a.name} X=-5")

# === Model B: Target (X=+5) ===
PMXImporter().execute(
    filepath=r"E:\mywork\mymodel\Purifier Inase 18\Purifier Inase 18 V1.pmx",
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root_b = next(r for r in bpy.data.objects if r.type=="EMPTY" and getattr(r,"mmd_type",None)=="ROOT" and r != root_a)
arm_b = next(c for c in root_b.children if c.type=="ARMATURE")
root_b.location.x = 5

VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm_b)

bpy.context.view_layer.objects.active = root_b
bpy.ops.mmd_tools.build_rig()
print(f"B: {root_b.name} X=+5")

# === Physics: bake from frame 1 ===
scn = bpy.context.scene
scn.frame_start = 1
scn.frame_end = 295
scn.frame_set(1)
bpy.context.view_layer.update()

w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 10
w.solver_iterations = 10
w.point_cache.frame_start = 1
w.point_cache.frame_end = 295

try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"Bake: {time.time()-t0:.1f}s")

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\side_by_side_compare.blend")
print("SAVED - Alt+A to compare")
