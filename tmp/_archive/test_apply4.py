import bpy, json
from mmd_tools.core.model import Model
import RGBA_mmd.rig_builder as rb

# locate root
root = None
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT": root = o; break
        except: pass

m = Model(root)
removed = rb.remove_rgba_objects(m)
print("CLEANED:", removed)

# Free the rigid body simulation cache (critical — old broken cache was being replayed)
try:
    bpy.ops.ptcache.free_bake_all()
except Exception as e:
    print("free_bake_all err:", e)

bpy.context.scene.frame_set(1)
bpy.context.view_layer.objects.active = root

res = bpy.ops.rgba_mmd.apply()
print("APPLY:", res, "STATUS:", bpy.context.scene.rgba_mmd.last_status)

# Free cache AGAIN after build_rig (build_rig may have populated it from old state)
try:
    bpy.ops.ptcache.free_bake_all()
except Exception as e:
    print("free_bake_all after err:", e)

# Inspect joints fully — every axis spring + limit
j = bpy.data.objects.get("J.胸_後1.L")
if j and j.rigid_body_constraint:
    rbc = j.rigid_body_constraint
    print("J胸_後1.L:")
    for ax in ("x","y","z"):
        print(f"  lin_{ax}: use_limit={getattr(rbc,'use_limit_lin_'+ax)} "
              f"lo={getattr(rbc,'limit_lin_'+ax+'_lower'):.3f} "
              f"hi={getattr(rbc,'limit_lin_'+ax+'_upper'):.3f} "
              f"use_spring={getattr(rbc,'use_spring_'+ax)} "
              f"k={getattr(rbc,'spring_stiffness_'+ax):.1f} "
              f"d={getattr(rbc,'spring_damping_'+ax):.3f}")
        print(f"  ang_{ax}: use_limit={getattr(rbc,'use_limit_ang_'+ax)} "
              f"lo={getattr(rbc,'limit_ang_'+ax+'_lower'):.3f} "
              f"hi={getattr(rbc,'limit_ang_'+ax+'_upper'):.3f}")

# Check world
w = bpy.context.scene.rigidbody_world
print("world.enabled:", w.enabled, "substeps:", w.substeps_per_frame, "iter:", w.solver_iterations)

# Step physics fresh from frame 1
bpy.context.scene.frame_set(1)
arm = bpy.data.objects["Inase54_arm"]
samples_y = []
for f in (1, 5, 10, 15, 20, 30):
    bpy.context.scene.frame_set(f)
    samples_y.append((f, round(arm.pose.bones["boob right 1"].matrix.translation.y, 4),
                          round(arm.pose.bones["boob left 1"].matrix.translation.y, 4)))
print("BONE_Y_OVER_TIME:", samples_y)
