import bpy
for jn in ("J.胸_後1.L", "J.胸_後2.L"):
    j = bpy.data.objects.get(jn)
    if not j: continue
    print(f"{jn}: parent={j.parent.name if j.parent else None} type={j.parent_type} bone={j.parent_bone}")
    print(f"  loc={list(j.location)} world={list(j.matrix_world.translation)}")
print()
# Compare to a built-in mmd joint (anything pre-existing)
print("--- mmd joints under 'joints' empty ---")
for o in bpy.data.objects:
    if o.name == "joints" or (hasattr(o, 'mmd_type') and getattr(o,'mmd_type',None) == 'JOINT_GRP_OBJ'):
        for c in list(o.children)[:3]:
            print(f"{c.name}: parent={c.parent.name if c.parent else None} type={c.parent_type} bone={c.parent_bone}")
        break
print()
# Existing mmd rigid body — see how it's parented (e.g. boob bones already had rigid bodies)
print("--- mmd rigid bodies ---")
for o in bpy.data.objects:
    if hasattr(o, 'mmd_type') and getattr(o,'mmd_type',None) == 'RIGID_GRP_OBJ':
        for c in list(o.children)[:5]:
            if "胸" not in c.name and "RGBA" not in c.name:
                print(f"{c.name}: parent={c.parent.name if c.parent else None} type={c.parent_type} bone={c.parent_bone}")
                if c.mmd_rigid:
                    print(f"  mmd_rigid bone={c.mmd_rigid.bone}")
        break
