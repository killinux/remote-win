import bpy, os, math, time
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter
from mmd_tools.core.model import Model

PMX_PATH = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
VMD_PATH = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# ===== STEP 1: Clean scene completely =====
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes):
    bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures):
    bpy.data.armatures.remove(a)
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)
print("Scene cleared")

# ===== STEP 2: Import PMX =====
PMXImporter().execute(
    filepath=PMX_PATH,
    types={'MESH', 'ARMATURE', 'PHYSICS', 'MORPHS', 'DISPLAY'},
    scale=1.0,
    clean_model=False,
    remove_doubles=False,
)
root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)
model = Model(root)
print(f"Imported: root={root.name} arm={arm.name} bones={len(arm.data.bones)}")

# Count original physics
orig_rb = len(list(model.rigidBodies()))
orig_j = len(list(model.joints()))
print(f"Original physics: {orig_rb} rigids, {orig_j} joints")

# ===== STEP 3: Check if PMX already has bust physics =====
bust_rigids = []
for rb in model.rigidBodies():
    mmd = rb.mmd_rigid
    if any(kw in mmd.bone.lower() for kw in ("boob", "bust", "breast", "胸")):
        bust_rigids.append((rb.name, mmd.bone, mmd.type))
        print(f"  Existing bust rigid: {rb.name} -> bone={mmd.bone} type={mmd.type}")

if not bust_rigids:
    print("  No existing bust rigids in PMX")

# ===== STEP 4: Load VMD =====
VMDImporter(filepath=VMD_PATH, scale=1.0, bone_mapper=None, use_pose_mode=True,
            convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
            use_mirror=False).assign(arm)
scn = bpy.context.scene
fr = arm.animation_data.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])
print(f"VMD loaded: frames {scn.frame_start}-{scn.frame_end}")

# ===== STEP 5: Build rig with mmd_tools standard way =====
bpy.context.view_layer.objects.active = root
bpy.ops.mmd_tools.build_rig()
print("build_rig done")

# ===== STEP 6: Setup rigid body world =====
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 10
w.solver_iterations = 10
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end

# ===== STEP 7: Bake =====
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"Bake: {time.time()-t0:.1f}s")

# ===== STEP 8: Report state =====
print(f"\nFinal state:")
print(f"  Rigid bodies: {len(list(model.rigidBodies()))}")
print(f"  Joints: {len(list(model.joints()))}")

# Check bust bone constraints
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if bone:
        cst = [(c.name, c.type, c.mute) for c in bone.constraints]
        print(f"  {bname}: constraints={cst}")

print("\nReady - press Alt+A to play in Blender")
