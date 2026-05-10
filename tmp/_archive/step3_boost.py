import bpy, time

RGBA_TOKENS = ("胸_後", "胸_前", "胸_回転", "胸_前後")

# 1. Widen joint limits and re-enable springs
tweaked = 0
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

    if is_free_rot:
        lim = 0.015
        rbc.limit_lin_x_lower = -lim
        rbc.limit_lin_x_upper = lim
        rbc.limit_lin_y_lower = -lim
        rbc.limit_lin_y_upper = lim
        rbc.limit_lin_z_lower = -lim
        rbc.limit_lin_z_upper = lim
        for ax in ("x", "y", "z"):
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 15.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.1)
            setattr(rbc, f"use_spring_{ax}", True)
            setattr(rbc, f"spring_stiffness_{ax}", 80.0)
            setattr(rbc, f"spring_damping_{ax}", 0.1)
    elif is_y_free:
        rbc.limit_lin_y_lower = -0.08
        rbc.limit_lin_y_upper = 0.08
        rbc.limit_lin_x_lower = -0.015
        rbc.limit_lin_x_upper = 0.015
        rbc.limit_lin_z_lower = -0.015
        rbc.limit_lin_z_upper = 0.015
        for ax in ("x", "y", "z"):
            setattr(rbc, f"use_spring_{ax}", True)
            setattr(rbc, f"spring_stiffness_{ax}", 40.0)
            setattr(rbc, f"spring_damping_{ax}", 0.1)
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 80.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.1)
    else:
        lim = 0.015
        rlim = 0.06
        rbc.limit_lin_x_lower = -lim
        rbc.limit_lin_x_upper = lim
        rbc.limit_lin_y_lower = -lim
        rbc.limit_lin_y_upper = lim
        rbc.limit_lin_z_lower = -lim
        rbc.limit_lin_z_upper = lim
        rbc.limit_ang_x_lower = -rlim
        rbc.limit_ang_x_upper = rlim
        rbc.limit_ang_y_lower = -rlim
        rbc.limit_ang_y_upper = rlim
        rbc.limit_ang_z_lower = -rlim
        rbc.limit_ang_z_upper = rlim
        for ax in ("x", "y", "z"):
            setattr(rbc, f"use_spring_{ax}", True)
            setattr(rbc, f"spring_stiffness_{ax}", 80.0)
            setattr(rbc, f"spring_damping_{ax}", 0.1)
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 80.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.1)

    tweaked += 1
    print(f"  tweaked: {o.name} type={rbc.type}")

# 2. Lower damping on rigid bodies
for o in bpy.data.objects:
    if any(tok in o.name for tok in RGBA_TOKENS) or (o.name.startswith("胸.") and o.rigid_body):
        rb = o.rigid_body
        if rb:
            rb.linear_damping = 0.3
            rb.angular_damping = 0.3
            print(f"  rb damping: {o.name} lin={rb.linear_damping} ang={rb.angular_damping}")

print(f"\ntweaked {tweaked} joints")

# 3. Re-bake
scn = bpy.context.scene
w = scn.rigidbody_world
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake: {time.time()-t0:.1f}s")

# 4. Sample
chest_L = next((o for o in bpy.data.objects
                if "胸.L" in o.name and not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor"))), None)
samples = []
for f in range(scn.frame_start, min(scn.frame_end, scn.frame_start + 300), 30):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    z = round(chest_L.evaluated_get(dg).matrix_world.translation.z, 4) if chest_L else None
    samples.append((f, z))

print("\nframe, chest_L.z")
for row in samples:
    print(row)
zs = [v for _, v in samples if v is not None]
if zs:
    print(f"\nBOOSTED amplitude={max(zs)-min(zs):.4f} (original was 1.4367)")
