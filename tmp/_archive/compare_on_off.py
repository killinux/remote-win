import bpy, math

scn = bpy.context.scene
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
mesh_obj = next((o for o in bpy.data.objects if o.type == "MESH" and o.parent and o.parent.type == "ARMATURE"), None)

vg = mesh_obj.vertex_groups.get("boob left 1")
test_verts = []
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_verts.append(v.index)
            if len(test_verts) >= 5:
                break
    if len(test_verts) >= 5:
        break

bone_L = arm.pose.bones.get("boob left 1")
constraint = bone_L.constraints.get("mmd_tools_rigid_track")

frames = [1, 30, 60, 90, 120, 150, 200, 250]

def sample_vertex(f, vi):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    return tuple(round(x, 4) for x in (ev.matrix_world @ ev.data.vertices[vi].co))

# WITH physics constraint
constraint.mute = False
print("=== Physics ON ===")
on_data = {}
for f in frames:
    pos = sample_vertex(f, test_verts[0])
    on_data[f] = pos
    print(f"  f{f}: {pos}")

# WITHOUT physics constraint
constraint.mute = True
bpy.context.view_layer.update()
print("\n=== Physics OFF ===")
off_data = {}
for f in frames:
    pos = sample_vertex(f, test_verts[0])
    off_data[f] = pos
    print(f"  f{f}: {pos}")

# Difference
print("\n=== DIFFERENCE (ON - OFF) ===")
print("frame, dx, dy, dz, distance")
for f in frames:
    dx = on_data[f][0] - off_data[f][0]
    dy = on_data[f][1] - off_data[f][1]
    dz = on_data[f][2] - off_data[f][2]
    dist = (dx**2 + dy**2 + dz**2) ** 0.5
    print(f"  f{f}: dx={dx:.4f} dy={dy:.4f} dz={dz:.4f} dist={dist:.4f}")

# Re-enable
constraint.mute = False

# Also check: bone rotation difference
print("\n=== Bone rotation diff ===")
for f in frames:
    constraint.mute = False
    scn.frame_set(f)
    bpy.context.view_layer.update()
    rot_on = bone_L.matrix.to_euler()

    constraint.mute = True
    scn.frame_set(f)
    bpy.context.view_layer.update()
    rot_off = bone_L.matrix.to_euler()

    dx = math.degrees(rot_on.x - rot_off.x)
    dy = math.degrees(rot_on.y - rot_off.y)
    dz = math.degrees(rot_on.z - rot_off.z)
    print(f"  f{f}: drot=({dx:.2f}, {dy:.2f}, {dz:.2f})")

constraint.mute = False
