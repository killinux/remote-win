import bpy, json
from mathutils import Euler
arm = bpy.data.objects["Inase54_arm"]
scn = bpy.context.scene
scn.frame_set(1)

# pose-rotate 上半身2 by 0.5 rad over 30 frames (sinusoidal)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb = arm.pose.bones.get("上半身2")
pb.rotation_mode = 'XYZ'
import math
for f in range(1, 31):
    angle = 0.7 * math.sin((f-1) / 30 * 2 * math.pi)
    pb.rotation_euler = Euler((angle, 0, 0), 'XYZ')
    pb.keyframe_insert(data_path="rotation_euler", frame=f)
bpy.ops.object.mode_set(mode='OBJECT')

# Step physics and watch 胸.L world translation, anchor world translation, bust bone matrix
samples = []
scn.frame_set(1)
for f in range(1, 31):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    chest = bpy.data.objects.get("胸.L").evaluated_get(dg)
    anchor = bpy.data.objects.get("上半身2_RGBAanchor").evaluated_get(dg)
    pb = arm.pose.bones["boob right 1"]
    samples.append((f,
        round(chest.matrix_world.translation.z, 3),
        round(anchor.matrix_world.translation.z, 3),
        round(chest.rotation_euler.x, 3),
        round(pb.matrix.translation.z, 3),
    ))
print("frame, chest_z, anchor_z, chest_rot_x, bone_z")
for s in samples:
    print(s)
