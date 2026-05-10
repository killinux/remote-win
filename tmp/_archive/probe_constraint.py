import bpy, math

arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
scn = bpy.context.scene

for bname in ("boob left 1", "boob right 1"):
    bone = arm.pose.bones.get(bname)
    if not bone:
        continue
    print(f"\n=== {bname} ===")
    print(f"  bone parent: {bone.parent.name if bone.parent else None}")
    for c in bone.constraints:
        print(f"  constraint: {c.name}")
        print(f"    type: {c.type}")
        print(f"    target: {c.target.name if c.target else None}")
        print(f"    subtarget: {getattr(c, 'subtarget', '')}")
        print(f"    owner_space: {c.owner_space}")
        print(f"    target_space: {c.target_space}")
        print(f"    influence: {c.influence}")
        print(f"    mute: {c.mute}")
        print(f"    use_x/y/z: {c.use_x} {c.use_y} {c.use_z}")
        print(f"    invert_x/y/z: {c.invert_x} {c.invert_y} {c.invert_z}")
        if hasattr(c, 'mix_mode'):
            print(f"    mix_mode: {c.mix_mode}")
        # Check target object
        if c.target:
            t = c.target
            print(f"    target obj type: {t.type}")
            print(f"    target parent: {t.parent.name if t.parent else None}")
            print(f"    target location: {tuple(round(x,3) for x in t.location)}")

# Check mmd_bonetrack empties
print("\n=== bonetrack empties ===")
for o in bpy.data.objects:
    if "mmd_bonetrack" in o.name:
        print(f"  {o.name}:")
        print(f"    parent: {o.parent.name if o.parent else None}")
        print(f"    parent_type: {o.parent_type}")
        for c in o.constraints:
            print(f"    constraint: {c.name} type={c.type} target={c.target.name if c.target else None}")

# Test: what happens at frame 1 vs 100
print("\n=== Frame comparison ===")
for f in (1, 100, 200):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    bone = arm.pose.bones.get("boob left 1")
    rot = bone.matrix.to_euler()
    # Also get the bone's LOCAL rotation (what constraint applies)
    loc_rot = bone.rotation_euler if bone.rotation_mode == 'XYZ' else bone.rotation_quaternion
    print(f"  f{f}: world_rot=({math.degrees(rot.x):.1f}, {math.degrees(rot.y):.1f}, {math.degrees(rot.z):.1f})")
    print(f"       loc_rot={tuple(round(x,3) for x in loc_rot)}")
    # Check if bust rigid body position changes
    for o in bpy.data.objects:
        if o.name == "胸.L" and o.rigid_body:
            dg = bpy.context.evaluated_depsgraph_get()
            ev = o.evaluated_get(dg)
            p = ev.matrix_world.translation
            r = ev.matrix_world.to_euler()
            print(f"       胸.L pos=({p.x:.3f},{p.y:.3f},{p.z:.3f}) rot=({math.degrees(r.x):.1f},{math.degrees(r.y):.1f},{math.degrees(r.z):.1f})")
