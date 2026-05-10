import bpy, math, time
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.model import Model

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"

# ===== 1. Clean everything =====
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

# ===== 2. Fresh PMX import =====
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)
print(f"Imported: {root.name}")

# ===== 3. Record original vertex positions (before physics) =====
mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = mesh_obj.evaluated_get(dg)

vg = mesh_obj.vertex_groups.get("boob left 1")
test_verts = []
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_verts.append(v.index)
            if len(test_verts) >= 3: break
    if len(test_verts) >= 3: break

original_positions = {}
for vi in test_verts:
    p = ev.matrix_world @ ev.data.vertices[vi].co
    original_positions[vi] = (p.x, p.y, p.z)
    print(f"  Original v{vi}: ({p.x:.4f}, {p.y:.4f}, {p.z:.4f})")

# ===== 4. Create physics =====
def bone_pos(name):
    return tuple(arm.matrix_world @ arm.data.bones[name].head_local)

grp = 14
mask = [True] * 16

parent_rb = model.createRigidBody(
    name="上半身2_phys", shape_type=0,
    location=bone_pos("上半身2"), rotation=(0,0,0),
    size=(0.05,0.05,0.05), dynamics_type=0,
    collision_group_number=grp, collision_group_mask=mask,
    bone="上半身2", mass=1.0)

for bname, side in [("boob left 1","L"), ("boob right 1","R")]:
    rb = model.createRigidBody(
        name=f"胸.{side}", shape_type=0,
        location=bone_pos(bname), rotation=(0,0,0),
        size=(0.10,0.10,0.10), dynamics_type=1,
        collision_group_number=grp, collision_group_mask=mask,
        bone=bname, mass=1.0,
        linear_damping=0.5, angular_damping=0.5)
    model.createJoint(
        name=f"胸_{side}",
        rigid_a=parent_rb, rigid_b=rb,
        location=bone_pos(bname), rotation=(0,0,0),
        maximum_location=(0,0,0), minimum_location=(0,0,0),
        maximum_rotation=(math.radians(10), math.radians(5), math.radians(10)),
        minimum_rotation=(math.radians(-10), math.radians(-5), math.radians(-10)),
        spring_linear=(0,0,0), spring_angular=(60, 80, 60))

# ===== 5. build_rig - this repositions everything properly =====
bpy.context.view_layer.objects.active = root
bpy.ops.mmd_tools.build_rig()
print("build_rig done")

# ===== 6. CHECK: did the model change shape? =====
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = mesh_obj.evaluated_get(dg)

print("\n=== Shape check (original vs after build_rig) ===")
max_dist = 0
for vi in test_verts:
    p = ev.matrix_world @ ev.data.vertices[vi].co
    ox, oy, oz = original_positions[vi]
    dist = ((p.x-ox)**2 + (p.y-oy)**2 + (p.z-oz)**2) ** 0.5
    max_dist = max(max_dist, dist)
    print(f"  v{vi}: now=({p.x:.4f},{p.y:.4f},{p.z:.4f}) dist={dist:.6f}")

if max_dist < 0.001:
    print(f"\nSHAPE OK! Max displacement: {max_dist:.6f} (< 0.001)")
else:
    print(f"\nWARNING: Shape changed! Max displacement: {max_dist:.6f}")

# ===== 7. Check constraint details =====
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones[bname]
    for c in bone.constraints:
        print(f"  {bname}: {c.type} mute={c.mute} influence={c.influence}")

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_clean_check.blend")
print("\nSAVED - check in Blender that model looks normal")
