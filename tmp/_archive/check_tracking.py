import bpy, math

scn = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")

# Find the bonetrack empty and rigid body
bt = bpy.data.objects.get("mmd_bonetrack")
rigid = bpy.data.objects.get("胸.L")
bone = arm.pose.bones["boob left 1"]

print("Tracking chain:")
print(f"  bone 'boob left 1' <- COPY_TRANSFORMS <- '{bt.name}' (parented to '{bt.parent.name}')")
print(f"  bt.parent_type: {bt.parent_type}")

print("\nframe | rigid_pos | rigid_rot | empty_pos | empty_rot | bone_world_rot")
for f in (1, 30, 60, 100, 150, 200):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()

    # Rigid body (evaluated = physics result)
    ev_r = rigid.evaluated_get(dg)
    rp = ev_r.matrix_world.translation
    rr = ev_r.matrix_world.to_euler()

    # Empty (evaluated)
    ev_bt = bt.evaluated_get(dg)
    ep = ev_bt.matrix_world.translation
    er = ev_bt.matrix_world.to_euler()

    # Bone
    br = bone.matrix.to_euler()

    # Distance between rigid and empty
    dist_re = (ev_r.matrix_world.translation - ev_bt.matrix_world.translation).length

    print(f"  f{f}:")
    print(f"    rigid:  pos=({rp.x:.2f},{rp.y:.2f},{rp.z:.2f}) rot=({math.degrees(rr.x):.1f},{math.degrees(rr.y):.1f},{math.degrees(rr.z):.1f})")
    print(f"    empty:  pos=({ep.x:.2f},{ep.y:.2f},{ep.z:.2f}) rot=({math.degrees(er.x):.1f},{math.degrees(er.y):.1f},{math.degrees(er.z):.1f})")
    print(f"    bone:   rot=({math.degrees(br.x):.1f},{math.degrees(br.y):.1f},{math.degrees(br.z):.1f})")
    print(f"    rigid-empty dist: {dist_re:.4f}")
