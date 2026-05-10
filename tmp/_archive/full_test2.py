import bpy, math, json
from mathutils import Euler

# The user's PMX (inase54.pmx) is already loaded as "Inase54" — same model.
# Skip re-import (mmd_tools.import_model needs UI context we can't replicate cleanly).
# Test plan: clean any prior RGBA rig → apply RGBA rig → animate 上半身2 → step physics → report.

print("=== STEP 1: Locate model ===")
root = None
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT": root = o; break
        except: pass
arm = None
for c in (root.children if root else []):
    if c.type == "ARMATURE": arm = c; break
print(f"root={root.name if root else None} arm={arm.name if arm else None} bones={len(arm.data.bones) if arm else 0}")
if not (root and arm): raise SystemExit("no MMD model loaded")

import RGBA_mmd.rig_builder as rb
bust = rb.detect_bust_bones(arm)
parent = rb.find_parent_bone(arm, "")
print(f"bust={bust} parent={parent}")

print("=== STEP 2: Clean any prior RGBA rig ===")
from mmd_tools.core.model import Model
m = Model(root)
removed = rb.remove_rgba_objects(m)
print(f"removed {removed} prior RGBA objects")

print("=== STEP 3: Clear 上半身2 keyframes ===")
ad = arm.animation_data
if ad and ad.action:
    fcs_to_rm = []
    for fc in ad.action.fcurves:
        if "上半身2" in fc.data_path:
            fcs_to_rm.append(fc)
    for fc in fcs_to_rm:
        ad.action.fcurves.remove(fc)
    print(f"removed {len(fcs_to_rm)} fcurves on 上半身2")
else:
    arm.animation_data_create()
    new_action = bpy.data.actions.new("rgba_test_action")
    arm.animation_data.action = new_action
    print("created new action 'rgba_test_action'")

print("=== STEP 4: Apply RGBA rig ===")
bpy.context.view_layer.objects.active = root
res = bpy.ops.rgba_mmd.apply()
print("apply:", res, "status:", bpy.context.scene.rgba_mmd.last_status)

print("=== STEP 5: Animate 上半身2 with sinusoidal X-rotation ===")
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones.get("上半身2")
if pb is None: raise SystemExit("no 上半身2 bone")
pb.rotation_mode = 'XYZ'
for f in range(1, 91):
    angle = 0.6 * math.sin((f - 1) / 90 * 4 * math.pi)
    pb.rotation_euler = Euler((angle, 0, 0), 'XYZ')
    pb.keyframe_insert(data_path="rotation_euler", frame=f)
bpy.ops.object.mode_set(mode='OBJECT')
print("keyframed 90 frames (2 cycles)")

print("=== STEP 6: Free cache, step physics, capture motion ===")
scn = bpy.context.scene
scn.frame_start = 1
scn.frame_end = 90
if scn.rigidbody_world and scn.rigidbody_world.point_cache:
    scn.rigidbody_world.point_cache.frame_start = 1
    scn.rigidbody_world.point_cache.frame_end = 90
try: bpy.ops.ptcache.free_bake_all()
except Exception as e: print("free cache:", e)

scn.frame_set(1)
samples = []
for f in range(1, 91):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    chest_L = bpy.data.objects.get("胸.L")
    chest_R = bpy.data.objects.get("胸.R")
    bone_R = arm.pose.bones[bust[0][0]] if bust else None
    bone_L = arm.pose.bones[bust[1][0]] if len(bust) > 1 else None
    cl_z = round(chest_L.evaluated_get(dg).matrix_world.translation.z, 4) if chest_L else None
    cr_z = round(chest_R.evaluated_get(dg).matrix_world.translation.z, 4) if chest_R else None
    bL_z = round(bone_L.matrix.translation.z, 4) if bone_L else None
    bR_z = round(bone_R.matrix.translation.z, 4) if bone_R else None
    samples.append((f, cl_z, cr_z, bL_z, bR_z))

# print every 5th frame
print("frame, 胸.L_z, 胸.R_z, bone_L_z, bone_R_z")
for s in samples[::5]:
    print(s)

# Compute amplitudes
cl_zs = [s[1] for s in samples if s[1] is not None]
bone_zs = [s[3] for s in samples if s[3] is not None]
print(f"\n胸.L Z range: [{min(cl_zs):.4f}, {max(cl_zs):.4f}] amplitude={max(cl_zs)-min(cl_zs):.4f}")
print(f"bone_L Z range: [{min(bone_zs):.4f}, {max(bone_zs):.4f}] amplitude={max(bone_zs)-min(bone_zs):.4f}")
print(f"chest amplitude / bone amplitude = {(max(cl_zs)-min(cl_zs)) / max(0.0001, (max(bone_zs)-min(bone_zs))):.3f}")
# A ratio close to 1.0 means chest follows bone exactly (no bounce)
# A ratio different from 1.0 (and time-shifted oscillation) means physics is contributing

print("=== DONE ===")
