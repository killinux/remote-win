import bpy, json
scene = bpy.context.scene

# ensure rigid body world exists
if scene.rigidbody_world is None:
    bpy.ops.rigidbody.world_add()

# set frame range
scene.frame_start = 1
scene.frame_end = 60
if scene.rigidbody_world.point_cache:
    scene.rigidbody_world.point_cache.frame_start = 1
    scene.rigidbody_world.point_cache.frame_end = 60

# Get armature, capture initial pose of bust bones
arm = bpy.data.objects.get("Inase54_arm")
target_bones = ["boob right 1", "boob left 1"]
results = {}

scene.frame_set(1)
init = {}
for bn in target_bones:
    pb = arm.pose.bones.get(bn)
    if pb:
        init[bn] = {
            "loc": list(pb.location),
            "rot": list(pb.rotation_quaternion),
            "matrix": [list(r) for r in pb.matrix],
        }

# Step the simulation forward
for f in (10, 20, 30, 45, 60):
    scene.frame_set(f)

# Read pose at frame 60
final = {}
for bn in target_bones:
    pb = arm.pose.bones.get(bn)
    if pb:
        final[bn] = {
            "loc": list(pb.location),
            "rot": list(pb.rotation_quaternion),
            "matrix": [list(r) for r in pb.matrix],
        }

# Check bust rigid body positions vs initial
rb_groups = [o for o in bpy.data.objects if getattr(o, "mmd_type", None) == "RIGID_GRP_OBJ"]
rb_obj = rb_groups[0] if rb_groups else None
rb_state = {}
if rb_obj:
    for c in rb_obj.children:
        if "胸" in c.name and "anchor" not in c.name:
            rb_state[c.name] = {
                "loc": list(c.matrix_world.translation),
                "rb_present": c.rigid_body is not None,
                "rbc_present": c.rigid_body_constraint is not None,
                "bone": c.mmd_rigid.bone,
                "type": c.mmd_rigid.type,
                "mass": c.rigid_body.mass if c.rigid_body else None,
            }

print(json.dumps({
    "initial_pose": init,
    "final_pose": final,
    "rigid_state": rb_state,
}, ensure_ascii=False, indent=2))
