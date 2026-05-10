"""End-to-end: import inase54.pmx via mmd_tools' Python API (bypasses operator
context issues), apply RGBA rig, animate 上半身2, capture physics motion."""
import bpy, math, os, json
from mathutils import Euler

PMX_PATH = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"

print("=== STEP 0: Sanity ===")
print("PMX exists:", os.path.isfile(PMX_PATH))
print("scene objects:", len(bpy.data.objects))

# locate any existing MMD model
def find_root():
    for o in bpy.data.objects:
        if o.type == "EMPTY":
            try:
                if o.mmd_type == "ROOT": return o
            except: pass
    return None

root = find_root()
print("existing root:", root.name if root else None)

if not root:
    print("=== STEP 1: Import PMX via mmd_tools.core.pmx.importer ===")
    # PMX importer reads the file and creates the model. We must drive it without
    # operator context — call the importer class directly.
    from mmd_tools.core.pmx import importer as pmx_importer
    from mmd_tools.core.pmx import pmx as pmx_loader
    # The PMXImporter class entry point
    Importer = pmx_importer.PMXImporter
    inst = Importer()
    # Load the PMX file
    pmx_model = pmx_loader.load(PMX_PATH)
    # The execute() signature varies; in 1.0.2 it takes kwargs
    try:
        inst.execute(
            pmx=pmx_model,
            types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
            scale=1.0,
            clean_model=False,
            remove_doubles=False,
            log_level='ERROR',
        )
    except TypeError as e:
        # fallback: try calling the model.Model.create directly
        print("execute kwargs failed:", e)
        from mmd_tools.core import model as mmd_model
        from mmd_tools import bpyutils
        # last-resort: just temp_override an active obj
        # Pick something from the scene as an "anchor" active obj
        if bpy.data.objects:
            bpy.context.view_layer.objects.active = next(iter(bpy.data.objects))
        win = bpy.context.window_manager.windows[0] if bpy.context.window_manager.windows else None
        area = next((a for a in win.screen.areas if a.type=='VIEW_3D'), None) if win else None
        region = next((r for r in area.regions if r.type=='WINDOW'), None) if area else None
        ovr = {"window": win, "area": area, "region": region,
               "selected_objects": [], "active_object": bpy.context.view_layer.objects.active}
        with bpy.context.temp_override(**{k:v for k,v in ovr.items() if v is not None}):
            bpy.ops.mmd_tools.import_model(filepath=PMX_PATH,
                types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'})
    root = find_root()
    print("imported, root:", root.name if root else "STILL NONE")

if not root:
    raise SystemExit("import failed; no MMD root in scene")

arm = next((c for c in root.children if c.type == "ARMATURE"), None)
print(f"arm={arm.name} bones={len(arm.data.bones)}")

import RGBA_mmd.rig_builder as rb
bust = rb.detect_bust_bones(arm)
parent = rb.find_parent_bone(arm, "")
print(f"bust bones: {bust}")
print(f"parent bone: {parent}")
if not bust:
    # show what's there for debugging
    cand = [b.name for b in arm.data.bones if any(k in b.name.lower() for k in ("胸","乳","bust","breast","chest","boob","oppai")) or "胸" in b.name]
    print("all candidate-name bones:", cand)
    raise SystemExit("no bust bones")

print("=== STEP 2: Apply RGBA rig ===")
bpy.context.view_layer.objects.active = root
res = bpy.ops.rgba_mmd.apply()
print("apply:", res, "status:", bpy.context.scene.rgba_mmd.last_status)

print("=== STEP 3: Animate 上半身2 ===")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones["上半身2"]
pb.rotation_mode = 'XYZ'
for f in range(1, 91):
    angle = 0.6 * math.sin((f - 1) / 90 * 4 * math.pi)
    pb.rotation_euler = Euler((angle, 0, 0), 'XYZ')
    pb.keyframe_insert(data_path="rotation_euler", frame=f)
bpy.ops.object.mode_set(mode='OBJECT')
print("keyframed 90 frames (2 cycles ±0.6 rad on X)")

print("=== STEP 4: Step physics + capture ===")
scn = bpy.context.scene
scn.frame_start = 1; scn.frame_end = 90
if scn.rigidbody_world and scn.rigidbody_world.point_cache:
    scn.rigidbody_world.point_cache.frame_start = 1
    scn.rigidbody_world.point_cache.frame_end = 90
try: bpy.ops.ptcache.free_bake_all()
except: pass
scn.frame_set(1)
samples = []
for f in range(1, 91):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    cL = bpy.data.objects.get("胸.L")
    cR = bpy.data.objects.get("胸.R")
    bL = arm.pose.bones[bust[1][0]] if len(bust) > 1 else None  # left side is index 1 typically
    bR = arm.pose.bones[bust[0][0]]
    samples.append((f,
        round(cL.evaluated_get(dg).matrix_world.translation.z, 4) if cL else None,
        round(cR.evaluated_get(dg).matrix_world.translation.z, 4) if cR else None,
        round(bL.matrix.translation.z, 4) if bL else None,
        round(bR.matrix.translation.z, 4) if bR else None,
    ))
print("frame, 胸.L_z, 胸.R_z, bone_L_z, bone_R_z")
for s in samples[::5]:
    print(s)
cl_zs = [s[1] for s in samples if s[1] is not None]
bone_zs = [s[3] for s in samples if s[3] is not None]
if cl_zs and bone_zs:
    print(f"\n胸.L Z amplitude: {max(cl_zs)-min(cl_zs):.4f}m  ({min(cl_zs):.3f} → {max(cl_zs):.3f})")
    print(f"bone_L Z amplitude: {max(bone_zs)-min(bone_zs):.4f}m  ({min(bone_zs):.3f} → {max(bone_zs):.3f})")

# Save the test scene so the user can open and play
save_path = r"C:\Users\haoni\Desktop\rgba_test.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"saved: {save_path}")
except Exception as e:
    print("save failed:", e)

print("=== DONE ===")
