import bpy, math, json

# Load parent rotation data
with open(r"E:\mywork\mymodel\parent_rot.json", "r") as fp:
    data = json.load(fp)

frames = data["frames"]
px = data["px"]
py = data["py"]
pz = data["pz"]

# ===== Spring-damper simulation =====
# RGBA-style: bounce comes from TRANSLATION lag, not rotation
# We simulate the lag and convert to a small additive rotation on the bust bone

SPRING_K = 80.0    # stiffness
DAMPING = 6.0      # damping coefficient
MASS = 1.0
SCALE = 3.0        # amplify the delta for visibility
DT = 1.0 / 30.0

def spring_sim(targets):
    pos = targets[0]
    vel = 0.0
    deltas = []
    for t in targets:
        force = SPRING_K * (t - pos) - DAMPING * vel
        vel += (force / MASS) * DT
        pos += vel * DT
        deltas.append((pos - t) * SCALE)
    return deltas

dx = spring_sim(px)
dz = spring_sim(pz)

print(f"Spring sim done: max_dx={math.degrees(max(abs(v) for v in dx)):.2f}° max_dz={math.degrees(max(abs(v) for v in dz)):.2f}°")

# ===== Apply to bust bones =====
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
scn = bpy.context.scene

for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones[bname]
    bone.rotation_mode = 'XYZ'
    for i, f in enumerate(frames):
        bone.rotation_euler.x = dx[i]
        bone.rotation_euler.y = 0
        bone.rotation_euler.z = dz[i]
        bone.keyframe_insert(data_path="rotation_euler", frame=f)

print("Keyframes applied to bust bones")

# Verify: check vertex positions
mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

# Compare f1 with original
scn.frame_set(1)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = mesh_obj.evaluated_get(dg)
p1 = ev.matrix_world @ ev.data.vertices[test_vi].co
print(f"\nf1 vertex: ({p1.x:.4f}, {p1.y:.4f}, {p1.z:.4f})")
print(f"(should be near 0.5739, -1.0405, 17.4294)")
print(f"f1 delta_x={math.degrees(dx[0]):.3f}° delta_z={math.degrees(dz[0]):.3f}°")

# Sample a few frames
print("\nSample frames:")
for f in (1, 30, 60, 100, 150, 200):
    idx = f - frames[0]
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    p = ev.matrix_world @ ev.data.vertices[test_vi].co
    print(f"  f{f}: ({p.x:.3f},{p.y:.3f},{p.z:.3f}) dx={math.degrees(dx[idx]):.2f}° dz={math.degrees(dz[idx]):.2f}°")

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_spring.blend")
print("\nSAVED: inase_spring.blend - press Alt+A!")
