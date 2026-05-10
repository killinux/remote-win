import bpy
from mmd_tools.core.model import Model

root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
if root is None:
    print("No model found")
else:
    model = Model(root)
    print(f"Model: {root.name}")
    print(f"Rigids: {len(list(model.rigidBodies()))}, Joints: {len(list(model.joints()))}")

    # Check mmd_joint properties (what gets exported to PMX)
    print("\n=== Joint MMD properties (exported to PMX) ===")
    for j in model.joints():
        mj = j.mmd_joint
        rbc = j.rigid_body_constraint
        print(f"\n{j.name}:")
        print(f"  mmd_joint spring_linear: ({mj.spring_linear[0]:.1f}, {mj.spring_linear[1]:.1f}, {mj.spring_linear[2]:.1f})")
        print(f"  mmd_joint spring_angular: ({mj.spring_angular[0]:.1f}, {mj.spring_angular[1]:.1f}, {mj.spring_angular[2]:.1f})")
        if rbc:
            print(f"  blender type: {rbc.type}")
            for ax in ("x","y","z"):
                sp_use = getattr(rbc, f"use_spring_{ax}", False)
                sp_k = getattr(rbc, f"spring_stiffness_{ax}", 0)
                print(f"  blender spring_{ax}: use={sp_use} k={sp_k:.1f}")

    # Check rigid body mmd properties
    print("\n=== Rigid body MMD properties ===")
    for rb in model.rigidBodies():
        mmd = rb.mmd_rigid
        blender_rb = rb.rigid_body
        print(f"{rb.name}: mmd_type={mmd.type} bone='{mmd.bone}'")
        if blender_rb:
            print(f"  mass={blender_rb.mass:.2f} lin_damp={blender_rb.linear_damping:.2f} ang_damp={blender_rb.angular_damping:.2f}")
