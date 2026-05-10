import bpy, math, time

scn = bpy.context.scene
w = scn.rigidbody_world
w.substeps_per_frame = 60
w.solver_iterations = 60

# Fix damping: 0.5 allows oscillation, not frozen
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb and "胸" in o.name:
        if "anchor" not in o.name:
            rb.linear_damping = 0.5
            rb.angular_damping = 0.5
            rb.mass = 0.5
            print(f"  {o.name}: mass={rb.mass} damp=0.5")

# Joint: ±8° with moderate spring, low spring-damping for bounce
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        rbc.type = 'GENERIC_SPRING'
        lim = math.radians(8)
        for ax in ("x", "y", "z"):
            setattr(rbc, f"limit_ang_{ax}_lower", -lim)
            setattr(rbc, f"limit_ang_{ax}_upper", lim)
            setattr(rbc, f"limit_lin_{ax}_lower", 0)
            setattr(rbc, f"limit_lin_{ax}_upper", 0)
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 150.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.2)
            setattr(rbc, f"use_spring_{ax}", False)
        print(f"  {o.name}: ±8° k=150 spring_damp=0.2")

# Rebake
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"\nbake: {time.time()-t0:.1f}s")

# Save
save_path = r"E:\mywork\mymodel\inase_bounce_test.blend"
bpy.ops.wm.save_as_mainfile(filepath=save_path)
print(f"SAVED: {save_path}")
print("\nOpen in Blender, press Alt+A to play")
print("Look at the chest area for jiggle effect")
