import bpy, math, time

RGBA_TOKENS = ("胸_後", "胸_前", "胸_回転", "胸_前後")

# Maximize rotational freedom on all joints
for o in bpy.data.objects:
    if not o.name.startswith("J."):
        continue
    if not any(tok in o.name for tok in RGBA_TOKENS):
        continue
    rbc = o.rigid_body_constraint
    if rbc is None:
        continue
    rbc.type = 'GENERIC_SPRING'

    # Wide rotation limits everywhere
    big_rot = math.radians(45)  # 45 degrees
    big_lin = 0.08

    for ax in ("x", "y", "z"):
        setattr(rbc, f"limit_lin_{ax}_lower", -big_lin)
        setattr(rbc, f"limit_lin_{ax}_upper", big_lin)
        setattr(rbc, f"limit_ang_{ax}_lower", -big_rot)
        setattr(rbc, f"limit_ang_{ax}_upper", big_rot)
        # Very soft angular springs = more visible rotation
        setattr(rbc, f"use_spring_ang_{ax}", True)
        setattr(rbc, f"spring_stiffness_ang_{ax}", 3.0)
        setattr(rbc, f"spring_damping_ang_{ax}", 0.03)
        setattr(rbc, f"use_spring_{ax}", True)
        setattr(rbc, f"spring_stiffness_{ax}", 10.0)
        setattr(rbc, f"spring_damping_{ax}", 0.03)

    print(f"  {o.name}: rot_limit=±45° lin_limit=±80mm ang_k=3 lin_k=10")

# Main chest bodies: lighter damping
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb is None:
        continue
    if any(tok in o.name for tok in RGBA_TOKENS) or \
       (("胸.L" in o.name or "胸.R" in o.name) and not any(x in o.name for x in ("anchor",))):
        rb.linear_damping = 0.15
        rb.angular_damping = 0.15

# Check mmd_bonetrack empties
for name in ("mmd_bonetrack", "mmd_bonetrack.001"):
    bt = bpy.data.objects.get(name)
    if bt:
        print(f"\n{name}: constraints={len(bt.constraints)}")
        for c in bt.constraints:
            print(f"  {c.type} target={c.target.name if hasattr(c,'target') and c.target else '?'} mute={c.mute}")
        print(f"  parent={bt.parent.name if bt.parent else None}")

# Re-bake
scn = bpy.context.scene
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"\nbake: {time.time()-t0:.1f}s")

# Sample rotation of chest rigid at key frames
chest_L = next((o for o in bpy.data.objects
                if "胸.L" in o.name and not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor"))), None)
print("\nframe, chest_L rot(deg), pos.z")
for f in (1, 30, 60, 90, 120, 150, 200, 250, 295):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = chest_L.evaluated_get(dg)
    rot = ev.matrix_world.to_euler()
    pos = ev.matrix_world.translation
    print(f"  f{f}: rot=({math.degrees(rot.x):.1f}, {math.degrees(rot.y):.1f}, {math.degrees(rot.z):.1f}) z={pos.z:.3f}")

# Save blend file for user inspection
save_path = r"E:\mywork\mymodel\inase_bouncy_test.blend"
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"\nSAVED: {save_path}")
print("Press Alt+A in Blender viewport to play animation")
