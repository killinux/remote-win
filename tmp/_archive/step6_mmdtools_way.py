import bpy, math
from mmd_tools.core.model import Model

# Get model
root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)
model = Model(root)

# 1. Remove all RGBA rig objects
bpy.context.view_layer.objects.active = root
bpy.ops.rgba_mmd.remove()
print("RGBA rig removed")

# 2. Also clean up bonetrack empties from previous build_rig
for o in list(bpy.data.objects):
    if "mmd_bonetrack" in o.name or "mmd_tools_rigid_parent" in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

# Remove old constraints from bust bones
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if bone:
        for c in list(bone.constraints):
            if "mmd_tools_rigid" in c.name:
                bone.constraints.remove(c)
                print(f"  removed constraint from {bname}")

# 3. List current rigids/joints to understand what mmd_tools already has
print("\nExisting rigid bodies:")
for rb in model.rigidBodies():
    mmd = rb.mmd_rigid
    print(f"  {rb.name}: bone='{mmd.bone}' type={mmd.type}")

print("\nExisting joints:")
for j in model.joints():
    print(f"  {j.name}")

# 4. Check what operators mmd_tools provides
ops = [attr for attr in dir(bpy.ops.mmd_tools) if not attr.startswith("_")]
print(f"\nmmd_tools operators: {ops}")
