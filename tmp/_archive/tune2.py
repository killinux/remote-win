import bpy, math, time

scn = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")

# Reset to moderate mass, lower spring
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb and "胸" in o.name and "anchor" not in o.name and "phys" not in o.name:
        rb.mass = 1.0
        rb.linear_damping = 0.4
        rb.angular_damping = 0.4

for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        lim = math.radians(15)
        for ax in ("x","y","z"):
            setattr(rbc, f"limit_ang_{ax}_lower", -lim)
            setattr(rbc, f"limit_ang_{ax}_upper", lim)
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 40.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.15)

scn.rigidbody_world.substeps_per_frame = 30
scn.rigidbody_world.solver_iterations = 30

try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake: {time.time()-t0:.1f}s")

# Compare
mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

bone_L = arm.pose.bones["boob left 1"]
ct = bone_L.constraints["mmd_tools_rigid_track"]

print(f"Vertex {test_vi} ON/OFF:")
for f in (1, 20, 40, 60, 80, 100, 130, 160, 200, 250, 290):
    ct.mute = False
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    on_pos = mesh_obj.evaluated_get(dg).matrix_world @ mesh_obj.evaluated_get(dg).data.vertices[test_vi].co

    ct.mute = True
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    off_pos = mesh_obj.evaluated_get(dg).matrix_world @ mesh_obj.evaluated_get(dg).data.vertices[test_vi].co

    dist = (on_pos - off_pos).length
    print(f"  f{f}: {dist:.4f}")

ct.mute = False
bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_final.blend")
print("SAVED")
