import bpy, math, time

scn = bpy.context.scene

# Restore the settings from the successful 0.08 test
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb and "胸" in o.name and "anchor" not in o.name and "phys" not in o.name:
        rb.mass = 1.0
        rb.linear_damping = 0.5
        rb.angular_damping = 0.5

for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        rbc.type = 'GENERIC_SPRING'
        rbc.limit_ang_x_lower = math.radians(-8)
        rbc.limit_ang_x_upper = math.radians(8)
        rbc.limit_ang_y_lower = math.radians(-5)
        rbc.limit_ang_y_upper = math.radians(5)
        rbc.limit_ang_z_lower = math.radians(-8)
        rbc.limit_ang_z_upper = math.radians(8)
        for ax in ("x","y","z"):
            setattr(rbc, f"limit_lin_{ax}_lower", 0)
            setattr(rbc, f"limit_lin_{ax}_upper", 0)
        rbc.use_spring_ang_x = True
        rbc.use_spring_ang_y = True
        rbc.use_spring_ang_z = True
        rbc.spring_stiffness_ang_x = 80.0
        rbc.spring_stiffness_ang_y = 120.0
        rbc.spring_stiffness_ang_z = 80.0
        rbc.spring_damping_ang_x = 0.2
        rbc.spring_damping_ang_y = 0.2
        rbc.spring_damping_ang_z = 0.2

scn.rigidbody_world.substeps_per_frame = 30
scn.rigidbody_world.solver_iterations = 30

try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake: {time.time()-t0:.1f}s")

mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

ct = arm.pose.bones["boob left 1"].constraints["mmd_tools_rigid_track"]
print(f"Vertex {test_vi}:")
for f in (1, 30, 60, 100, 150, 200):
    ct.mute = False
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    on = mesh_obj.evaluated_get(dg).matrix_world @ mesh_obj.evaluated_get(dg).data.vertices[test_vi].co
    ct.mute = True
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    off = mesh_obj.evaluated_get(dg).matrix_world @ mesh_obj.evaluated_get(dg).data.vertices[test_vi].co
    print(f"  f{f}: dist={(on-off).length:.4f}")

ct.mute = False
bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_final.blend")
print("SAVED - press Alt+A to play")
