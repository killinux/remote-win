import bpy, os, json, math
from mathutils import Euler

PMX_PATH = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"

print("=== STEP 1: Clean any existing MMD models ===")
to_remove = []
for o in bpy.data.objects:
    try:
        if o.mmd_type == "ROOT":
            for c in list(o.children_recursive):
                to_remove.append(c)
            to_remove.append(o)
    except Exception:
        pass
for o in to_remove:
    try:
        bpy.data.objects.remove(o, do_unlink=True)
    except Exception:
        pass
print("removed", len(to_remove), "objects from prior MMD models")

print("=== STEP 2: Import PMX (with context override) ===")
exists = os.path.isfile(PMX_PATH)
print("file exists:", exists, "size:", os.path.getsize(PMX_PATH) if exists else None)
if not exists:
    raise SystemExit("PMX not found")
# mmd_tools import_model requires selected_objects in context — provide it via temp_override
win = bpy.context.window_manager.windows[0] if bpy.context.window_manager.windows else None
area = None
region = None
if win:
    for a in win.screen.areas:
        if a.type == 'VIEW_3D':
            area = a
            for r in a.regions:
                if r.type == 'WINDOW':
                    region = r; break
            break
override_kwargs = {"window": win} if win else {}
if area: override_kwargs["area"] = area
if region: override_kwargs["region"] = region
override_kwargs["selected_objects"] = []
override_kwargs["active_object"] = None
print("override has area:", area is not None, "region:", region is not None)
with bpy.context.temp_override(**override_kwargs):
    bpy.ops.mmd_tools.import_model(filepath=PMX_PATH, types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'})
print("imported")

print("=== STEP 3: Locate model ===")
root = None
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT":
                root = o; break
        except: pass
print("root:", root.name if root else None)
arm = None
for c in (root.children if root else []):
    if c.type == "ARMATURE":
        arm = c; break
print("arm:", arm.name if arm else None, "bones:", len(arm.data.bones) if arm else 0)

# detect bust bones via the addon's logic
import RGBA_mmd.rig_builder as rb
bust = rb.detect_bust_bones(arm)
print("detected bust:", bust)
parent = rb.find_parent_bone(arm, "")
print("parent bone:", parent)

print("=== STEP 4: Apply RGBA rig ===")
bpy.context.view_layer.objects.active = root
res = bpy.ops.rgba_mmd.apply()
print("apply:", res, "status:", bpy.context.scene.rgba_mmd.last_status)

print("=== STEP 5: Add 上半身2 animation ===")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones.get("上半身2")
if pb is None:
    print("ERR: no 上半身2"); raise SystemExit
pb.rotation_mode = 'XYZ'
for f in range(1, 61):
    angle = 0.6 * math.sin((f - 1) / 60 * 4 * math.pi)
    pb.rotation_euler = Euler((angle, 0, 0), 'XYZ')
    pb.keyframe_insert(data_path="rotation_euler", frame=f)
bpy.ops.object.mode_set(mode='OBJECT')
print("keyframed 60 frames of sinusoidal upper body rotation")

print("=== STEP 6: Step physics + capture motion ===")
scn = bpy.context.scene
scn.frame_start = 1
scn.frame_end = 60
if scn.rigidbody_world and scn.rigidbody_world.point_cache:
    scn.rigidbody_world.point_cache.frame_start = 1
    scn.rigidbody_world.point_cache.frame_end = 60
try:
    bpy.ops.ptcache.free_bake_all()
except Exception as e:
    print("free cache:", e)

scn.frame_set(1)
samples = []
for f in range(1, 61):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    chest = bpy.data.objects.get("胸.L")
    bone_R = arm.pose.bones[bust[0][0]] if bust else None
    bone_L = arm.pose.bones[bust[1][0]] if len(bust) > 1 else None
    if chest:
        eo = chest.evaluated_get(dg)
        cz = round(eo.matrix_world.translation.z, 4)
    else:
        cz = None
    samples.append((f,
        cz,
        round(bone_R.matrix.translation.z, 4) if bone_R else None,
        round(bone_L.matrix.translation.z, 4) if bone_L else None,
    ))
print("frame, chest.L.z, bone_R.z, bone_L.z")
for s in samples:
    print(s)

# Compute oscillation amplitude
zs = [s[1] for s in samples if s[1] is not None]
if zs:
    print(f"\n胸.L Z amplitude: min={min(zs):.4f} max={max(zs):.4f} peak-to-peak={max(zs)-min(zs):.4f}")

print("=== DONE ===")
