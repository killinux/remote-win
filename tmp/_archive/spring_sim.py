import bpy, math
from mathutils import Vector, Quaternion, Euler

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# ===== 1. Clean + Import + VMD =====
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter

PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")

VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm)
scn = bpy.context.scene
fr = arm.animation_data.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])
print(f"Ready: {scn.frame_start}-{scn.frame_end}")

# ===== 2. Record parent bone (上半身2) rotation per frame =====
parent_bone = arm.pose.bones["上半身2"]
parent_rotations = {}

for f in range(scn.frame_start, scn.frame_end + 1):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    mat = arm.matrix_world @ parent_bone.matrix
    parent_rotations[f] = mat.to_euler()

print(f"Recorded {len(parent_rotations)} frames of parent rotation")

# ===== 3. Spring-damper simulation =====
# Simulate bust response to parent bone's angular acceleration
# Parameters (tune these for more/less bounce)
SPRING_K = 120.0      # spring stiffness (lower = more bounce)
DAMPING = 8.0         # damping (lower = more oscillation)
MASS = 1.0            # mass
AMPLITUDE = 2.5       # multiply the result for visibility
DT = 1.0 / 30.0       # assuming 30fps

def simulate_axis(parent_angles):
    """1D spring-damper: bust follows parent with lag."""
    pos = parent_angles[0]  # start at parent
    vel = 0.0
    result = []
    for target in parent_angles:
        # Spring force toward parent position
        force = SPRING_K * (target - pos) - DAMPING * vel
        acc = force / MASS
        vel += acc * DT
        pos += vel * DT
        # Delta = how much bust deviates from parent
        delta = pos - target
        result.append(delta * AMPLITUDE)
    return result

# Extract X and Z rotations of parent (main bounce axes)
frames = list(range(scn.frame_start, scn.frame_end + 1))
px = [parent_rotations[f].x for f in frames]
py = [parent_rotations[f].y for f in frames]
pz = [parent_rotations[f].z for f in frames]

dx = simulate_axis(px)
dy = simulate_axis(py)
dz = simulate_axis(pz)

max_dx = max(abs(v) for v in dx)
max_dy = max(abs(v) for v in dy)
max_dz = max(abs(v) for v in dz)
print(f"Simulated deltas: max_dx={math.degrees(max_dx):.2f}° max_dy={math.degrees(max_dy):.2f}° max_dz={math.degrees(max_dz):.2f}°")

# ===== 4. Apply delta rotations to bust bones as keyframes =====
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones[bname]
    bone.rotation_mode = 'XYZ'

    for i, f in enumerate(frames):
        scn.frame_set(f)
        # Add delta rotation on top of current pose
        bone.rotation_euler.x = dx[i]
        bone.rotation_euler.y = dy[i] * 0.3  # less Y movement
        bone.rotation_euler.z = dz[i]
        bone.keyframe_insert(data_path="rotation_euler", frame=f)

    print(f"  {bname}: keyframed {len(frames)} frames")

# ===== 5. Verify =====
mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

print(f"\nVertex {test_vi} positions:")
for f in (1, 30, 60, 100, 150, 200, 250):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    p = ev.matrix_world @ ev.data.vertices[test_vi].co
    print(f"  f{f}: ({p.x:.3f}, {p.y:.3f}, {p.z:.3f}) delta_x={math.degrees(dx[f-1]):.2f}°")

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_spring_sim.blend")
print("\nSAVED: inase_spring_sim.blend - press Alt+A!")
