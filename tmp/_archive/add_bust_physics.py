import bpy, math, time
from mmd_tools.core.model import Model

root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)
model = Model(root)
bpy.context.view_layer.objects.active = root

# Bone world positions
def bone_pos(name):
    b = arm.data.bones[name]
    return tuple(arm.matrix_world @ b.head_local)

# Collision group 15 (index 14), no collisions
grp = 14
mask = [True] * 16

# ===== Create STATIC parent rigid on 上半身2 =====
parent_rb = model.createRigidBody(
    name="上半身2_phys",
    shape_type=0,
    location=bone_pos("上半身2"),
    rotation=(0, 0, 0),
    size=(0.05, 0.05, 0.05),
    dynamics_type=0,  # STATIC
    collision_group_number=grp,
    collision_group_mask=mask,
    bone="上半身2",
    mass=1.0,
)
print(f"Parent: {parent_rb.name}")

# ===== Create DYNAMIC+BONE bust rigids =====
bust_data = [("boob left 1", "L"), ("boob right 1", "R")]
bust_rbs = {}
for bname, side in bust_data:
    rb = model.createRigidBody(
        name=f"胸.{side}",
        shape_type=0,
        location=bone_pos(bname),
        rotation=(0, 0, 0),
        size=(0.10, 0.10, 0.10),
        dynamics_type=2,  # Dynamic+Bone
        collision_group_number=grp,
        collision_group_mask=mask,
        bone=bname,
        mass=0.5,
        linear_damping=0.7,
        angular_damping=0.7,
    )
    bust_rbs[side] = rb
    print(f"Bust: {rb.name} -> {bname}")

# ===== Create spring joints =====
for side, bust_rb in bust_rbs.items():
    bname = bust_data[0][0] if side == "L" else bust_data[1][0]
    j = model.createJoint(
        name=f"胸_{side}",
        rigid_a=parent_rb,
        rigid_b=bust_rb,
        location=bone_pos(bname),
        rotation=(0, 0, 0),
        maximum_location=(0, 0, 0),
        minimum_location=(0, 0, 0),
        maximum_rotation=(math.radians(5), math.radians(3), math.radians(5)),
        minimum_rotation=(math.radians(-5), math.radians(-3), math.radians(-5)),
        spring_linear=(0, 0, 0),
        spring_angular=(100, 150, 100),
    )
    print(f"Joint: {j.name}")

# ===== Build rig (creates bone tracking) =====
bpy.ops.mmd_tools.build_rig()
print("\nbuild_rig done")

# ===== Manually set spring damping on Blender constraints =====
# (mmd_tools createJoint sets spring stiffness but damping defaults to 0.5)
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        for ax in ("x", "y", "z"):
            setattr(rbc, f"spring_damping_ang_{ax}", 0.25)
        print(f"  {o.name}: spring_damp_ang -> 0.25")

# ===== Rigid body world =====
scn = bpy.context.scene
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 60
w.solver_iterations = 60
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end

# ===== Bake =====
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"\nBake: {time.time()-t0:.1f}s")

# ===== Verify =====
print(f"\nRigid bodies: {len(list(model.rigidBodies()))}")
print(f"Joints: {len(list(model.joints()))}")
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if bone:
        cnames = [f"{c.type}({c.name})" for c in bone.constraints]
        print(f"  {bname}: {cnames}")

# Save
save_path = r"E:\mywork\mymodel\inase_phys_clean.blend"
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"\nSAVED: {save_path}")
print("Press Alt+A to play - watch chest for jiggle")
