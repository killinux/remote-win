import bpy, json
from mmd_tools.core.model import Model
import RGBA_mmd.rig_builder as rb

# locate root
root = None
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT": root = o; break
        except: pass

# clean previous attempt
m = Model(root)
removed = rb.remove_rgba_objects(m)
print("CLEANED:", removed)

# set frame to 1 to clear physics cache
bpy.context.scene.frame_set(1)
if bpy.context.scene.rigidbody_world and bpy.context.scene.rigidbody_world.point_cache:
    bpy.context.scene.rigidbody_world.point_cache.frame_start = 1
    bpy.context.scene.rigidbody_world.point_cache.frame_end = 250

# Set active to root so the operator can find it
bpy.context.view_layer.objects.active = root

# Apply
res = bpy.ops.rgba_mmd.apply()
print("APPLY:", res, "STATUS:", bpy.context.scene.rgba_mmd.last_status)

# Check rigid body parent linkage (mmd_tools_rigid_parent should now exist under armature)
arm = None
for c in root.children:
    if c.type == "ARMATURE": arm = c; break
print("ARM:", arm.name if arm else None)
parent_obj = None
if arm:
    for c in arm.children:
        if c.name == "mmd_tools_rigid_parent" or "mmd_tools_rigid_parent" in c.name:
            parent_obj = c
            break
print("RIGID_PARENT_EMPTY:", parent_obj.name if parent_obj else "NOT_FOUND",
      "children=", len(parent_obj.children) if parent_obj else 0)

# Check anchor body's rigid_body settings
anchor = bpy.data.objects.get("上半身2_RGBAanchor")
if anchor and anchor.rigid_body:
    print("ANCHOR rb:", "kinematic=", anchor.rigid_body.kinematic,
          "type=", anchor.rigid_body.type,
          "parent=", anchor.parent.name if anchor.parent else None,
          "parent_type=", anchor.parent_type)

# Check main bust rigid body settings
for nm in ("胸.L", "胸.R"):
    o = bpy.data.objects.get(nm)
    if o and o.rigid_body:
        print(f"{nm}:", "type=", o.rigid_body.type,
              "kinematic=", o.rigid_body.kinematic,
              "parent=", o.parent.name if o.parent else None)

# Step physics 30 frames and read bust bone delta
bpy.context.scene.frame_set(1)
arm = bpy.data.objects["Inase54_arm"]
init_y = arm.pose.bones["boob right 1"].matrix.translation.y
for f in range(2, 31):
    bpy.context.scene.frame_set(f)
final_y = arm.pose.bones["boob right 1"].matrix.translation.y
print(f"BONE Y: init={init_y:.4f} final={final_y:.4f} delta={final_y-init_y:.4f}")
