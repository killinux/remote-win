import bpy, math, json
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.model import Model

# Clean
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)

PMX = r"E:\mywork\mymodel\Purifier Inase 18\Purifier Inase 18 V1.pmx"
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)

print(f"Model: {root.name}")
print(f"Bones: {len(arm.data.bones)}")
print(f"Rigids: {len(list(model.rigidBodies()))}")
print(f"Joints: {len(list(model.joints()))}")

# Find all bust-related rigid bodies
print("\n=== ALL Rigid Bodies ===")
for rb in model.rigidBodies():
    mmd = rb.mmd_rigid
    blender_rb = rb.rigid_body
    if blender_rb:
        print(f"  {rb.name}: bone='{mmd.bone}' type={mmd.type} shape={mmd.shape} "
              f"mass={blender_rb.mass:.3f} friction={blender_rb.friction:.2f} restitution={blender_rb.restitution:.2f} "
              f"lin_damp={blender_rb.linear_damping:.3f} ang_damp={blender_rb.angular_damping:.3f} "
              f"size=({mmd.size[0]:.3f},{mmd.size[1]:.3f},{mmd.size[2]:.3f}) "
              f"group={mmd.collision_group_number}")

# Find bust-related joints with full details
print("\n=== ALL Joints ===")
for j in model.joints():
    mj = j.mmd_joint
    rbc = j.rigid_body_constraint
    if rbc:
        obj1 = rbc.object1.name if rbc.object1 else "?"
        obj2 = rbc.object2.name if rbc.object2 else "?"
        print(f"\n  {j.name}: {obj1} -> {obj2}")
        print(f"    type={rbc.type}")
        print(f"    lin_limit: x=[{rbc.limit_lin_x_lower:.4f},{rbc.limit_lin_x_upper:.4f}] "
              f"y=[{rbc.limit_lin_y_lower:.4f},{rbc.limit_lin_y_upper:.4f}] "
              f"z=[{rbc.limit_lin_z_lower:.4f},{rbc.limit_lin_z_upper:.4f}]")
        print(f"    ang_limit: x=[{math.degrees(rbc.limit_ang_x_lower):.1f},{math.degrees(rbc.limit_ang_x_upper):.1f}] "
              f"y=[{math.degrees(rbc.limit_ang_y_lower):.1f},{math.degrees(rbc.limit_ang_y_upper):.1f}] "
              f"z=[{math.degrees(rbc.limit_ang_z_lower):.1f},{math.degrees(rbc.limit_ang_z_upper):.1f}]")
        print(f"    mmd spring_linear: ({mj.spring_linear[0]:.1f},{mj.spring_linear[1]:.1f},{mj.spring_linear[2]:.1f})")
        print(f"    mmd spring_angular: ({mj.spring_angular[0]:.1f},{mj.spring_angular[1]:.1f},{mj.spring_angular[2]:.1f})")

# Find bust bone names
print("\n=== Bust bone search ===")
for b in arm.data.bones:
    bl = b.name.lower()
    if any(kw in bl for kw in ("bust","breast","boob","chest","胸","乳","oppai")):
        print(f"  {b.name} parent={b.parent.name if b.parent else None}")
