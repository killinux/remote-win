import bpy, os, math
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.pmx.exporter import export as pmx_export
from mmd_tools.core.model import Model

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
PMX_OUT = r"E:\mywork\mymodel\inase54_simple_phys.pmx"

# 1. Clean
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

# 2. Import
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)
bpy.context.view_layer.objects.active = root
print(f"Imported: {root.name}")

# 3. Create physics exactly like the reference model
def bone_pos(name):
    b = arm.data.bones[name]
    return tuple(arm.matrix_world @ b.head_local)

# Same collision group as reference: group 15 (index 14)
grp = 15
mask = [True] * 16

# Static parent on 上半身2 (same as reference: 00J_上半身2)
parent_rb = model.createRigidBody(
    name="上半身2",
    shape_type=2,  # CAPSULE like reference
    location=bone_pos("上半身2"),
    rotation=(0, 0, 0),
    size=(1.394, 1.329, 0.0),  # same as reference
    dynamics_type=0,  # STATIC
    collision_group_number=0,  # group 0 like reference body bones
    collision_group_mask=[True]*16,
    bone="上半身2",
    mass=1.0,
    friction=0.5,
    linear_damping=0.5,
    angular_damping=0.5,
)
print(f"Parent: {parent_rb.name}")

# Dynamic bust rigids - EXACTLY like reference
bust_data = [
    ("boob left 1", "左乳奶"),
    ("boob right 1", "右乳奶"),
]
bust_rbs = {}
for bname, rigid_name in bust_data:
    rb = model.createRigidBody(
        name=rigid_name,
        shape_type=0,  # SPHERE like reference
        location=bone_pos(bname),
        rotation=(0, 0, 0),
        size=(0.597, 0.0, 0.0),  # same sphere size as reference
        dynamics_type=1,  # DYNAMIC (type=1, NOT type=2!)
        collision_group_number=grp,  # group 15
        collision_group_mask=[True]*16,
        bone=bname,
        mass=1.0,
        friction=0.5,
        linear_damping=0.5,
        angular_damping=0.5,
    )
    bust_rbs[bname] = rb
    print(f"Bust: {rb.name} -> {bname}")

# Joints - EXACTLY like reference
for bname, rigid_name in bust_data:
    j = model.createJoint(
        name=f"J.{rigid_name}",
        rigid_a=parent_rb,
        rigid_b=bust_rbs[bname],
        location=bone_pos(bname),
        rotation=(0, 0, 0),
        # Linear: locked (0,0,0) - same as reference
        maximum_location=(0, 0, 0),
        minimum_location=(0, 0, 0),
        # Angular: ±10° on all axes - EXACTLY like reference
        maximum_rotation=(math.radians(10), math.radians(10), math.radians(10)),
        minimum_rotation=(math.radians(-10), math.radians(-10), math.radians(-10)),
        # NO springs - same as reference (all zeros)
        spring_linear=(0, 0, 0),
        spring_angular=(0, 0, 0),
    )
    print(f"Joint: {j.name}")

# 4. Build rig
bpy.ops.mmd_tools.build_rig()
print("\nbuild_rig done")

# 5. Verify constraints (should be COPY_TRANSFORMS for type=1)
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if bone:
        for c in bone.constraints:
            print(f"  {bname}: {c.type} mute={c.mute}")

# 6. Verify joint properties
print("\nJoint properties:")
for j in model.joints():
    mj = j.mmd_joint
    rbc = j.rigid_body_constraint
    if rbc and "乳" in j.name:
        print(f"  {j.name}: type={rbc.type}")
        print(f"    ang: x=[{math.degrees(rbc.limit_ang_x_lower):.1f},{math.degrees(rbc.limit_ang_x_upper):.1f}]")
        print(f"    spring_lin: ({mj.spring_linear[0]:.0f},{mj.spring_linear[1]:.0f},{mj.spring_linear[2]:.0f})")
        print(f"    spring_ang: ({mj.spring_angular[0]:.0f},{mj.spring_angular[1]:.0f},{mj.spring_angular[2]:.0f})")

# 7. Export
pmx_export(
    filepath=PMX_OUT, scale=1.0, root=root,
    armature=model.armature(),
    meshes=list(model.meshes()),
    rigid_bodies=list(model.rigidBodies()),
    joints=list(model.joints()),
    copy_textures=False, sort_materials=False,
    disable_specular=False, sort_vertices='NONE',
)

size = os.path.getsize(PMX_OUT)
print(f"\nExported: {PMX_OUT}")
print(f"  {size/1024:.0f} KB")
print(f"  {len(list(model.rigidBodies()))} rigids, {len(list(model.joints()))} joints")
print(f"\n设置（完全参考 Purifier Inase 18）:")
print(f"  刚体: type=1(Dynamic), SPHERE, mass=1.0, damp=0.5, radius=0.597")
print(f"  关节: ±10°, 无弹簧, linear locked")
print(f"\n请重新导入此 PMX + VMD 测试弹跳效果")
