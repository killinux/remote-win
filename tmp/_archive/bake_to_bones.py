import bpy, math, time
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter
from mmd_tools.core.model import Model
from mathutils import Matrix, Euler

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# ===== 1. Clean =====
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

# ===== 2. Import PMX + VMD =====
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)

VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm)
scn = bpy.context.scene
fr = arm.animation_data.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])
print(f"Imported: {scn.frame_start}-{scn.frame_end}")

# ===== 3. Create physics (type 1) + build_rig =====
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

bust_mapping = {}
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
    bust_mapping[bname] = f"胸.{side}"

bpy.context.view_layer.objects.active = root
bpy.ops.mmd_tools.build_rig()
print("build_rig done")

# Remove the COPY_TRANSFORMS constraints - we'll keyframe directly
for bname in bust_mapping:
    bone = arm.pose.bones[bname]
    for c in list(bone.constraints):
        if "mmd_tools_rigid_track" in c.name:
            bone.constraints.remove(c)
print("Removed constraints - will keyframe directly")

# Set spring damping
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        for ax in ("x","y","z"):
            setattr(rbc, f"spring_damping_ang_{ax}", 0.15)

# Physics world
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 30
w.solver_iterations = 30
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end

# Bake physics
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"Physics baked: {time.time()-t0:.1f}s")

# ===== 4. Read physics result and keyframe bust bones =====
print("\nBaking rigid body rotation to bone keyframes...")

for bname, rigid_name in bust_mapping.items():
    bone = arm.pose.bones[bname]
    bone.rotation_mode = 'QUATERNION'
    rigid_obj = bpy.data.objects[rigid_name]

    # Get the bone's rest rotation in armature space
    rest_mat = arm.matrix_world @ bone.bone.matrix_local

    for f in range(scn.frame_start, scn.frame_end + 1):
        scn.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()

        # Get physics-evaluated rigid body world matrix
        ev_rigid = rigid_obj.evaluated_get(dg)
        rigid_world_mat = ev_rigid.matrix_world

        # Compute the rotation delta: how much the rigid body rotated
        # relative to the bone's rest pose
        delta_rot = rest_mat.to_3x3().inverted() @ rigid_world_mat.to_3x3()
        bone.rotation_quaternion = delta_rot.to_quaternion()
        bone.keyframe_insert(data_path="rotation_quaternion", frame=f)

    print(f"  {bname}: keyframed {scn.frame_end - scn.frame_start + 1} frames")

# ===== 5. Verify vertex displacement =====
mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

print(f"\nVertex {test_vi} position per frame:")
for f in (1, 30, 60, 100, 150, 200, 250):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    p = ev.matrix_world @ ev.data.vertices[test_vi].co
    print(f"  f{f}: ({p.x:.3f}, {p.y:.3f}, {p.z:.3f})")

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_baked.blend")
print("\nSAVED: inase_baked.blend - press Alt+A to play")
