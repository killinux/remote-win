import bpy, time, math

RGBA_TOKENS = ("胸_後", "胸_前", "胸_回転", "胸_前後")

# Aggressive: much wider limits, very low spring/damping
for o in bpy.data.objects:
    if not o.name.startswith("J."):
        continue
    if not any(tok in o.name for tok in RGBA_TOKENS):
        continue
    rbc = o.rigid_body_constraint
    if rbc is None:
        continue

    rbc.type = 'GENERIC_SPRING'

    is_free_rot = any(x in o.name for x in ("前1", "回転1"))
    is_y_free = "前後1" in o.name

    big_lin = 0.05
    big_rot = 0.2
    y_range = 0.15

    if is_free_rot:
        for ax_l in ("x", "y", "z"):
            setattr(rbc, f"limit_lin_{ax_l}_lower", -big_lin)
            setattr(rbc, f"limit_lin_{ax_l}_upper", big_lin)
        for ax_l in ("x", "y", "z"):
            setattr(rbc, f"use_spring_{ax_l}", True)
            setattr(rbc, f"spring_stiffness_{ax_l}", 20.0)
            setattr(rbc, f"spring_damping_{ax_l}", 0.05)
            setattr(rbc, f"use_spring_ang_{ax_l}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax_l}", 5.0)
            setattr(rbc, f"spring_damping_ang_{ax_l}", 0.05)
    elif is_y_free:
        rbc.limit_lin_x_lower = -big_lin
        rbc.limit_lin_x_upper = big_lin
        rbc.limit_lin_y_lower = -y_range
        rbc.limit_lin_y_upper = y_range
        rbc.limit_lin_z_lower = -big_lin
        rbc.limit_lin_z_upper = big_lin
        for ax_l in ("x", "y", "z"):
            setattr(rbc, f"limit_ang_{ax_l}_lower", -big_rot)
            setattr(rbc, f"limit_ang_{ax_l}_upper", big_rot)
            setattr(rbc, f"use_spring_{ax_l}", True)
            setattr(rbc, f"spring_stiffness_{ax_l}", 10.0)
            setattr(rbc, f"spring_damping_{ax_l}", 0.05)
            setattr(rbc, f"use_spring_ang_{ax_l}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax_l}", 10.0)
            setattr(rbc, f"spring_damping_ang_{ax_l}", 0.05)
    else:
        for ax_l in ("x", "y", "z"):
            setattr(rbc, f"limit_lin_{ax_l}_lower", -big_lin)
            setattr(rbc, f"limit_lin_{ax_l}_upper", big_lin)
            setattr(rbc, f"limit_ang_{ax_l}_lower", -big_rot)
            setattr(rbc, f"limit_ang_{ax_l}_upper", big_rot)
            setattr(rbc, f"use_spring_{ax_l}", True)
            setattr(rbc, f"spring_stiffness_{ax_l}", 20.0)
            setattr(rbc, f"spring_damping_{ax_l}", 0.05)
            setattr(rbc, f"use_spring_ang_{ax_l}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax_l}", 20.0)
            setattr(rbc, f"spring_damping_ang_{ax_l}", 0.05)

# Lower body damping + increase mass
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb is None:
        continue
    if "胸.L" in o.name or "胸.R" in o.name:
        if not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor")):
            rb.mass = 1.5
            rb.linear_damping = 0.2
            rb.angular_damping = 0.2
            print(f"main rb: {o.name} mass={rb.mass} damp={rb.linear_damping}")
    elif any(tok in o.name for tok in RGBA_TOKENS):
        rb.linear_damping = 0.2
        rb.angular_damping = 0.2

# Re-bake
scn = bpy.context.scene
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake: {time.time()-t0:.1f}s")

# Sample: measure chest-bone GAP (the actual jiggle)
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
chest_L = next((o for o in bpy.data.objects
                if "胸.L" in o.name and not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor"))), None)

samples = []
for f in range(scn.frame_start, min(scn.frame_end + 1, scn.frame_start + 300), 10):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    chest_z = chest_L.evaluated_get(dg).matrix_world.translation.z if chest_L else 0
    bone = arm.pose.bones.get("boob left 1")
    bone_z = (arm.matrix_world @ bone.matrix @ bone.bone.matrix_local.inverted()).translation.z if bone else 0
    gap = chest_z - bone_z
    samples.append((f, round(chest_z, 4), round(bone_z, 4), round(gap, 4)))

print("frame, chest_z, bone_z, gap")
for s in samples:
    print(s)

gaps = [abs(s[3]) for s in samples]
czs = [s[1] for s in samples]
print(f"\nchest amplitude={max(czs)-min(czs):.4f}")
print(f"gap mean={sum(gaps)/len(gaps):.4f} max={max(gaps):.4f}")
