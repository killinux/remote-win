import bpy, math
from mmd_tools.core.model import Model

root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)
model = Model(root)
bpy.context.view_layer.objects.active = root

# 1. Clean everything: remove all existing rigids, joints, tracking
bpy.ops.mmd_tools.clean_rig()
print("clean_rig done")

for rb in list(model.rigidBodies()):
    bpy.data.objects.remove(rb, do_unlink=True)
for j in list(model.joints()):
    bpy.data.objects.remove(j, do_unlink=True)
print("all rigids/joints removed")

# Remove leftover constraints
for bone in arm.pose.bones:
    for c in list(bone.constraints):
        if "mmd" in c.name.lower() or "rigid" in c.name.lower():
            bone.constraints.remove(c)

# Remove tracking empties
for o in list(bpy.data.objects):
    if "mmd_bonetrack" in o.name or "mmd_tools_rigid" in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

print("\nBuilding new physics...")

# 2. Get bone positions
parent_bone_name = "上半身2"
bust_bones = [("boob left 1", "L"), ("boob right 1", "R")]

def bone_world_pos(bname):
    b = arm.data.bones[bname]
    return arm.matrix_world @ b.head_local

parent_pos = bone_world_pos(parent_bone_name)

# 3. Create STATIC parent rigid (type=0, follows bone)
grp = 14  # collision group 15 (0-indexed)
mask = [True] * 16  # no collision

parent_rb = model.createRigidBody(
    name="上半身2_anchor",
    shape_type=0,  # sphere
    location=tuple(parent_pos),
    rotation=(0, 0, 0),
    size=(0.05, 0.05, 0.05),
    dynamics_type=0,  # STATIC
    collision_group_number=grp,
    collision_group_mask=mask,
    bone=parent_bone_name,
    mass=1.0,
)
print(f"parent rigid: {parent_rb.name}")

# 4. Create DYNAMIC+BONE bust rigids (type=2)
bust_rbs = {}
for bname, side in bust_bones:
    pos = bone_world_pos(bname)
    rb = model.createRigidBody(
        name=f"胸.{side}",
        shape_type=0,
        location=tuple(pos),
        rotation=(0, 0, 0),
        size=(0.12, 0.12, 0.12),
        dynamics_type=2,  # Dynamic+Bone
        collision_group_number=grp,
        collision_group_mask=mask,
        bone=bname,
        mass=1.0,
        linear_damping=0.95,
        angular_damping=0.95,
    )
    bust_rbs[side] = rb
    print(f"bust rigid: {rb.name} bone={bname}")

# 5. Create spring joints between parent and each bust
# This is the key: angular limits control how much the chest can rotate
for side, bust_rb in bust_rbs.items():
    pos = bone_world_pos(bust_bones[0][0] if side == "L" else bust_bones[1][0])
    j = model.createJoint(
        name=f"J.胸.{side}",
        rigid_a=parent_rb,
        rigid_b=bust_rb,
        location=tuple(pos),
        rotation=(0, 0, 0),
        # Linear: locked tight
        maximum_location=(0, 0, 0),
        minimum_location=(0, 0, 0),
        # Angular: allow rotation on X (forward/back nod) and Z (side sway)
        maximum_rotation=(math.radians(15), math.radians(5), math.radians(10)),
        minimum_rotation=(math.radians(-15), math.radians(-5), math.radians(-10)),
        # Spring: soft return force
        spring_linear=(0, 0, 0),
        spring_angular=(50, 100, 80),
    )
    print(f"joint: {j.name}")

# 6. Build rig (creates bone tracking)
bpy.context.view_layer.objects.active = root
bpy.ops.mmd_tools.build_rig()
print("\nbuild_rig done")

# 7. Setup rigid body world
scn = bpy.context.scene
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 10
w.solver_iterations = 10
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end

# 8. Verify
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if bone:
        cnames = [f"{c.type}:{c.name}" for c in bone.constraints]
        print(f"  {bname} constraints: {cnames}")

# 9. Check joint properties in Blender
for o in bpy.data.objects:
    if o.name.startswith("J.胸"):
        rbc = o.rigid_body_constraint
        if rbc:
            print(f"\n{o.name}: type={rbc.type}")
            print(f"  ang_limits: x=[{math.degrees(rbc.limit_ang_x_lower):.1f},{math.degrees(rbc.limit_ang_x_upper):.1f}]"
                  f" y=[{math.degrees(rbc.limit_ang_y_lower):.1f},{math.degrees(rbc.limit_ang_y_upper):.1f}]"
                  f" z=[{math.degrees(rbc.limit_ang_z_lower):.1f},{math.degrees(rbc.limit_ang_z_upper):.1f}]")
            for ax in ("x","y","z"):
                sp = getattr(rbc, f"use_spring_ang_{ax}", False)
                sk = getattr(rbc, f"spring_stiffness_ang_{ax}", 0)
                print(f"  spring_ang_{ax}: use={sp} k={sk}")

print("\nDone! Press Alt+A in Blender to play")
