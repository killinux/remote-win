import bpy

arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
scn = bpy.context.scene

# 1. Check rigid body world
w = scn.rigidbody_world
print(f"RB world: exists={w is not None}")
if w:
    print(f"  enabled={w.enabled} frames={w.point_cache.frame_start}-{w.point_cache.frame_end} baked={w.point_cache.is_baked}")

# 2. Check bust bone constraints
for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if bone:
        print(f"\nBone '{bname}': constraints={len(bone.constraints)}")
        for c in bone.constraints:
            print(f"  {c.type} name='{c.name}' mute={c.mute} influence={c.influence}")
            if hasattr(c, 'target'):
                print(f"    target={c.target.name if c.target else None}")
    else:
        print(f"\nBone '{bname}': NOT FOUND")

# 3. Check mmd_tools rigid tracking empties
track_empties = [o for o in bpy.data.objects if "mmd_tools_rigid" in o.name.lower() or "rigid_track" in o.name.lower()]
print(f"\nTracking empties: {[o.name for o in track_empties]}")

# 4. Check the main chest rigid bodies
for o in bpy.data.objects:
    if ("胸.L" in o.name or "胸.R" in o.name) and o.rigid_body:
        if not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor")):
            rb = o.rigid_body
            print(f"\n{o.name}: type={rb.type} enabled={rb.enabled} kinematic={rb.kinematic}")
            print(f"  mass={rb.mass} lin_damp={rb.linear_damping:.2f} ang_damp={rb.angular_damping:.2f}")
            mmd = getattr(o, "mmd_rigid", None)
            if mmd:
                print(f"  mmd_rigid: bone='{mmd.bone}' type={mmd.type}")
            # check parent chain
            p = o.parent
            chain = []
            while p:
                chain.append(p.name)
                p = p.parent
            print(f"  parent chain: {chain[:5]}")

# 5. Check a few joints
print("\nJoint types:")
for o in bpy.data.objects:
    if o.name.startswith("J.") and "胸" in o.name:
        rbc = o.rigid_body_constraint
        if rbc:
            springs = []
            for ax in ("x","y","z"):
                if getattr(rbc, f"use_spring_{ax}", False):
                    springs.append(f"{ax}={getattr(rbc, f'spring_stiffness_{ax}', 0):.0f}")
            print(f"  {o.name}: type={rbc.type} springs=[{','.join(springs)}]")

# 6. Test frame movement
print("\nFrame test (chest_L Z at key frames):")
chest_L = next((o for o in bpy.data.objects
                if "胸.L" in o.name and not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor"))), None)
if chest_L:
    for f in (1, 50, 100, 150, 200):
        scn.frame_set(f)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        pos = chest_L.evaluated_get(dg).matrix_world.translation
        print(f"  f{f}: x={pos.x:.3f} y={pos.y:.3f} z={pos.z:.3f}")
