import bpy, math, time
from mathutils import Euler

scn = bpy.context.scene
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# Remove the broken COPY_ROTATION constraints and tracking empties
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if bone:
        for c in list(bone.constraints):
            if "bust_physics" in c.name or "mmd_tools_rigid" in c.name:
                bone.constraints.remove(c)
                print(f"  removed constraint from {bname}")

for o in list(bpy.data.objects):
    if "bust_track" in o.name or "mmd_bonetrack" in o.name:
        bpy.data.objects.remove(o, do_unlink=True)

print("Cleaned old tracking")

# Register a frame_change handler that reads physics state
handler_code = '''
import bpy
from mathutils import Matrix

def bust_physics_update(scene, depsgraph):
    arm = None
    for o in bpy.data.objects:
        if o.type == "ARMATURE" and "Inase54" in o.name:
            arm = o
            break
    if arm is None:
        return

    mapping = {
        "boob left 1": "胸.L",
        "boob right 1": "胸.R",
    }

    for bone_name, rigid_name in mapping.items():
        bone = arm.pose.bones.get(bone_name)
        rigid = bpy.data.objects.get(rigid_name)
        if bone is None or rigid is None:
            continue

        # Get physics-evaluated rotation
        ev_rigid = rigid.evaluated_get(depsgraph)
        rigid_world_rot = ev_rigid.matrix_world.to_euler()

        # Convert world rotation to bone local rotation
        # bone.matrix = armature.matrix_world @ bone_parent_chain @ bone_local
        # We want to set bone rotation so its world rotation matches the rigid
        parent_mat = arm.matrix_world
        if bone.parent:
            parent_mat = arm.matrix_world @ bone.parent.matrix @ bone.parent.bone.matrix_local.inverted() @ bone.bone.matrix_local
        else:
            parent_mat = arm.matrix_world @ bone.bone.matrix_local

        # Target world matrix (only rotation, keep bone's rest position)
        target_world_rot_mat = rigid_world_rot.to_matrix().to_4x4()

        # Solve for local rotation
        rest_mat = arm.matrix_world @ bone.bone.matrix_local
        rest_rot_inv = rest_mat.to_3x3().inverted()
        local_rot = (rest_rot_inv @ target_world_rot_mat.to_3x3()).to_euler()

        bone.rotation_mode = 'XYZ'
        bone.rotation_euler = local_rot

# Remove old handler if exists
for h in list(bpy.app.handlers.frame_change_post):
    if hasattr(h, '__name__') and h.__name__ == 'bust_physics_update':
        bpy.app.handlers.frame_change_post.remove(h)

bpy.app.handlers.frame_change_post.append(bust_physics_update)
print("Handler registered")
'''

exec(handler_code)

# Verify: sample bone rotation at different frames
print("\nVerification - bone rotation at key frames:")
for f in (1, 30, 60, 100, 150, 200):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    bone = arm.pose.bones["boob left 1"]
    rot = bone.rotation_euler
    print(f"  f{f}: local_rot=({math.degrees(rot.x):.1f}, {math.degrees(rot.y):.1f}, {math.degrees(rot.z):.1f})")

# Check vertex positions with handler active
mesh_obj = next((o for o in bpy.data.objects if o.type == "MESH" and o.parent and o.parent.type == "ARMATURE"), None)
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

print(f"\nVertex {test_vi} positions:")
for f in (1, 30, 60, 100, 150):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    p = ev.matrix_world @ ev.data.vertices[test_vi].co
    print(f"  f{f}: ({p.x:.3f}, {p.y:.3f}, {p.z:.3f})")

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_handler.blend")
print("\nSAVED - press Alt+A to play")
