import bpy, math, time, os
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter
from mmd_tools.core.model import Model

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# ===== 1. Clean scene =====
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)
print("Scene cleared")

# ===== 2. Import PMX =====
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)
print(f"PMX: root={root.name} arm={arm.name}")

# ===== 3. Create physics =====
def bone_pos(name):
    b = arm.data.bones[name]
    return tuple(arm.matrix_world @ b.head_local)

grp = 14
mask = [True] * 16

# Static parent on 上半身2
parent_rb = model.createRigidBody(
    name="上半身2_phys", shape_type=0,
    location=bone_pos("上半身2"), rotation=(0,0,0),
    size=(0.05,0.05,0.05), dynamics_type=0,  # STATIC
    collision_group_number=grp, collision_group_mask=mask,
    bone="上半身2", mass=1.0)

# Dynamic (TYPE 1!) bust rigids -> build_rig will create COPY_TRANSFORMS
for bname, side in [("boob left 1","L"), ("boob right 1","R")]:
    rb = model.createRigidBody(
        name=f"胸.{side}", shape_type=0,
        location=bone_pos(bname), rotation=(0,0,0),
        size=(0.10,0.10,0.10),
        dynamics_type=1,  # TYPE 1 = Dynamic (COPY_TRANSFORMS!)
        collision_group_number=grp, collision_group_mask=mask,
        bone=bname, mass=1.0,
        linear_damping=0.5, angular_damping=0.5)

    # Spring joint
    model.createJoint(
        name=f"胸_{side}",
        rigid_a=parent_rb, rigid_b=rb,
        location=bone_pos(bname), rotation=(0,0,0),
        maximum_location=(0,0,0), minimum_location=(0,0,0),
        maximum_rotation=(math.radians(8), math.radians(5), math.radians(8)),
        minimum_rotation=(math.radians(-8), math.radians(-5), math.radians(-8)),
        spring_linear=(0,0,0),
        spring_angular=(80, 120, 80))

print("Physics created: 3 rigids + 2 joints")

# ===== 4. Build rig (creates COPY_TRANSFORMS for type 1) =====
bpy.context.view_layer.objects.active = root
bpy.ops.mmd_tools.build_rig()
print("build_rig done")

# ===== 5. Verify constraint type =====
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if bone:
        for c in bone.constraints:
            print(f"  {bname}: {c.type} name={c.name} mute={c.mute}")

# ===== 6. Load VMD =====
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm)
scn = bpy.context.scene
fr = arm.animation_data.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])
print(f"VMD: {scn.frame_start}-{scn.frame_end}")

# ===== 7. Physics world =====
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 30
w.solver_iterations = 30
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end

# Set spring damping on joints
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        for ax in ("x","y","z"):
            setattr(rbc, f"spring_damping_ang_{ax}", 0.2)

# ===== 8. Bake =====
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"Bake: {time.time()-t0:.1f}s")

# ===== 9. ON/OFF comparison =====
mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

bone_L = arm.pose.bones["boob left 1"]
ct = bone_L.constraints.get("mmd_tools_rigid_track")

print(f"\nVertex {test_vi} ON/OFF comparison:")
for f in (1, 30, 60, 100, 150, 200):
    ct.mute = False
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    on_pos = ev.matrix_world @ ev.data.vertices[test_vi].co

    ct.mute = True
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    off_pos = ev.matrix_world @ ev.data.vertices[test_vi].co

    dist = (on_pos - off_pos).length
    print(f"  f{f}: dist={dist:.4f}")

ct.mute = False

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_final.blend")
print("\nSAVED: inase_final.blend")
