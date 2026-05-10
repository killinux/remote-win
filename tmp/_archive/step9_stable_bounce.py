import bpy, math, time

scn = bpy.context.scene

# 1. Higher physics quality
w = scn.rigidbody_world
w.substeps_per_frame = 60
w.solver_iterations = 60

# 2. Higher damping on bust bodies to prevent runaway
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb and "胸" in o.name:
        rb.linear_damping = 0.999
        rb.angular_damping = 0.999
        rb.mass = 0.3
        print(f"  {o.name}: mass={rb.mass} damp=0.999")

# 3. Tighter joint limits with controlled spring
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        rbc.type = 'GENERIC_SPRING'

        # Tight angular limits: ±3° X (nod), ±2° Y, ±3° Z (sway)
        rbc.limit_ang_x_lower = math.radians(-3)
        rbc.limit_ang_x_upper = math.radians(3)
        rbc.limit_ang_y_lower = math.radians(-2)
        rbc.limit_ang_y_upper = math.radians(2)
        rbc.limit_ang_z_lower = math.radians(-3)
        rbc.limit_ang_z_upper = math.radians(3)

        # Lock linear
        for ax in ("x", "y", "z"):
            setattr(rbc, f"limit_lin_{ax}_lower", 0)
            setattr(rbc, f"limit_lin_{ax}_upper", 0)

        # Soft springs with low damping = visible oscillation
        for ax in ("x", "y", "z"):
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 200.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.15)
            setattr(rbc, f"use_spring_{ax}", False)

        print(f"  {o.name}: ±3° limits, k=200, damp=0.15")

# 4. Re-bake
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"\nbake: {time.time()-t0:.1f}s")

# 5. Sample bone rotation deltas from frame 1
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)
scn.frame_set(1)
bpy.context.view_layer.update()
bone_L = arm.pose.bones.get("boob left 1")
rest_rot = bone_L.matrix.to_euler() if bone_L else None

print(f"\nRest rotation (f1): x={math.degrees(rest_rot.x):.1f} z={math.degrees(rest_rot.z):.1f}")
print("\nframe, delta_x(deg), delta_z(deg)")
for f in range(1, min(scn.frame_end + 1, 300), 10):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    if bone_L:
        rot = bone_L.matrix.to_euler()
        dx = math.degrees(rot.x - rest_rot.x)
        dz = math.degrees(rot.z - rest_rot.z)
        print(f"  f{f}: dx={dx:.2f} dz={dz:.2f}")

print("\nDone - Alt+A to play")
