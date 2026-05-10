import bpy, math, time
from mmd_tools.core.model import Model

root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)
model = Model(root)
scn = bpy.context.scene

# ===== Clean existing physics completely =====
bpy.context.view_layer.objects.active = root
try: bpy.ops.mmd_tools.clean_rig()
except: pass

for rb in list(model.rigidBodies()):
    bpy.data.objects.remove(rb, do_unlink=True)
for j in list(model.joints()):
    bpy.data.objects.remove(j, do_unlink=True)
for o in list(bpy.data.objects):
    if "mmd_bonetrack" in o.name or "mmd_tools_rigid" in o.name:
        bpy.data.objects.remove(o, do_unlink=True)
for bone in arm.pose.bones:
    for c in list(bone.constraints):
        if "mmd" in c.name.lower() or "rigid" in c.name.lower():
            bone.constraints.remove(c)
print("Cleaned all physics")

# ===== Create rigids =====
def bone_pos(name):
    b = arm.data.bones[name]
    return tuple(arm.matrix_world @ b.head_local)

grp = 14
mask = [True] * 16

# Static parent
parent_rb = model.createRigidBody(
    name="上半身2_anchor",
    shape_type=0, location=bone_pos("上半身2"), rotation=(0,0,0),
    size=(0.05,0.05,0.05), dynamics_type=0,
    collision_group_number=grp, collision_group_mask=mask,
    bone="上半身2", mass=1.0,
)

# Pure Dynamic bust rigids (type=1, NOT type=2)
bust_rbs = {}
for bname, side in [("boob left 1", "L"), ("boob right 1", "R")]:
    rb = model.createRigidBody(
        name=f"胸.{side}",
        shape_type=0, location=bone_pos(bname), rotation=(0,0,0),
        size=(0.10,0.10,0.10),
        dynamics_type=1,  # PURE DYNAMIC - no bone tracking by mmd_tools
        collision_group_number=grp, collision_group_mask=mask,
        bone=bname,
        mass=0.5, linear_damping=0.7, angular_damping=0.7,
    )
    bust_rbs[side] = rb
print(f"Created: parent + {list(bust_rbs.keys())} bust rigids (type=1 Dynamic)")

# Joints with moderate spring
for side, bust_rb in bust_rbs.items():
    bname = "boob left 1" if side == "L" else "boob right 1"
    model.createJoint(
        name=f"胸_{side}",
        rigid_a=parent_rb, rigid_b=bust_rb,
        location=bone_pos(bname), rotation=(0,0,0),
        maximum_location=(0,0,0), minimum_location=(0,0,0),
        maximum_rotation=(math.radians(10), math.radians(5), math.radians(10)),
        minimum_rotation=(math.radians(-10), math.radians(-5), math.radians(-10)),
        spring_linear=(0,0,0),
        spring_angular=(80, 120, 80),
    )
print("Joints created")

# ===== Build rig (this wires up static/dynamic rigids) =====
bpy.ops.mmd_tools.build_rig()
print("build_rig done")

# ===== Now MANUALLY add COPY_ROTATION for bust bones =====
# build_rig only adds tracking for type 2, not type 1
# We need to: create bonetrack empty parented to bust rigid, add COPY_ROTATION
for side in ("L", "R"):
    bname = "boob left 1" if side == "L" else "boob right 1"
    rigid_name = f"胸.{side}"
    rigid_obj = bpy.data.objects.get(rigid_name)
    if not rigid_obj:
        print(f"ERROR: {rigid_name} not found")
        continue

    # Create tracking empty
    bt = bpy.data.objects.new(f"bust_track.{side}", None)
    bpy.context.scene.collection.objects.link(bt)
    bt.empty_display_size = 0.01
    bt.parent = rigid_obj

    # Add COPY_ROTATION to bust bone
    bone = arm.pose.bones[bname]
    c = bone.constraints.new('COPY_ROTATION')
    c.name = "bust_physics_track"
    c.target = bt
    c.owner_space = 'WORLD'
    c.target_space = 'WORLD'
    c.mix_mode = 'REPLACE'
    c.influence = 1.0
    print(f"  {bname}: COPY_ROTATION -> {bt.name} (parented to {rigid_name})")

# ===== Adjust spring damping =====
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        for ax in ("x","y","z"):
            setattr(rbc, f"spring_damping_ang_{ax}", 0.2)

# ===== Rigid body world =====
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 60
w.solver_iterations = 60
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end

# Bake
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"\nBake: {time.time()-t0:.1f}s")

# ===== Verify with ON/OFF comparison =====
mesh_obj = next((o for o in bpy.data.objects if o.type == "MESH" and o.parent and o.parent.type == "ARMATURE"), None)
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index
            break
    if test_vi is not None:
        break

bone_L = arm.pose.bones["boob left 1"]
constraint = bone_L.constraints.get("bust_physics_track")

print("\n=== ON/OFF comparison ===")
print("frame, ON_pos, OFF_pos, distance")
for f in (1, 50, 100, 150, 200):
    constraint.mute = False
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    on_pos = ev.matrix_world @ ev.data.vertices[test_vi].co

    constraint.mute = True
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    off_pos = ev.matrix_world @ ev.data.vertices[test_vi].co

    dist = (on_pos - off_pos).length
    print(f"  f{f}: ON=({on_pos.x:.3f},{on_pos.y:.3f},{on_pos.z:.3f}) OFF=({off_pos.x:.3f},{off_pos.y:.3f},{off_pos.z:.3f}) dist={dist:.4f}")

constraint.mute = False

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_fixed.blend")
print("\nSAVED")
