import bpy, json
arm = bpy.data.objects.get("Inase54_arm")
ad = arm.animation_data if arm else None
print("ACTION:", ad.action.name if (ad and ad.action) else None)
print("FRAME:", bpy.context.scene.frame_current)

# Now let's manually rotate 上半身2 and see if bust rigids react
if arm:
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm.pose.bones.get("上半身2")
    if pb:
        # rotate upper body to provoke movement
        from mathutils import Euler
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = Euler((0.5, 0, 0), 'XYZ')
        pb.keyframe_insert(data_path="rotation_euler", frame=1)
        pb.rotation_euler = Euler((-0.5, 0, 0), 'XYZ')
        pb.keyframe_insert(data_path="rotation_euler", frame=15)
        pb.rotation_euler = Euler((0.5, 0, 0), 'XYZ')
        pb.keyframe_insert(data_path="rotation_euler", frame=30)
    bpy.ops.object.mode_set(mode='OBJECT')

# Step physics and capture rigid body world translation
scn = bpy.context.scene
scn.frame_set(1)
samples = []
for f in (1, 5, 10, 15, 20, 25, 30):
    scn.frame_set(f)
    o = bpy.data.objects.get("胸.L")
    if o:
        dg = bpy.context.evaluated_depsgraph_get()
        eo = o.evaluated_get(dg)
        samples.append((f, round(eo.matrix_world.translation.x, 4),
                            round(eo.matrix_world.translation.y, 4),
                            round(eo.matrix_world.translation.z, 4)))
print("胸.L XYZ over time:", samples)

# Also bone matrix
samples2 = []
for f in (1, 5, 10, 15, 20, 25, 30):
    scn.frame_set(f)
    pb = arm.pose.bones["boob right 1"]
    samples2.append((f, round(pb.matrix.translation.y, 4), round(pb.matrix_basis.to_quaternion().w, 4)))
print("boob right 1 Y, basis_quat_w:", samples2)
