import bpy, math, time

scn = bpy.context.scene
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")

# Softer springs + more mass = bigger bounce
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb and "胸" in o.name and "anchor" not in o.name and "phys" not in o.name:
        rb.mass = 3.0
        rb.linear_damping = 0.3
        rb.angular_damping = 0.3
        print(f"  {o.name}: mass=3.0 damp=0.3")

for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        lim = math.radians(20)
        for ax in ("x","y","z"):
            setattr(rbc, f"limit_ang_{ax}_lower", -lim)
            setattr(rbc, f"limit_ang_{ax}_upper", lim)
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 15.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.1)
        print(f"  {o.name}: ±20° k=15 damp=0.1")

# Rebake
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"\nbake: {time.time()-t0:.1f}s")

# ON/OFF comparison
mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

bone_L = arm.pose.bones["boob left 1"]
ct = bone_L.constraints.get("mmd_tools_rigid_track")

print(f"\nVertex {test_vi} ON/OFF comparison:")
for f in (1, 20, 40, 60, 80, 100, 130, 160, 200, 250):
    ct.mute = False
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    on_pos = ev.matrix_world @ ev.data.vertices[test_vi].co

    ct.mute = True
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    off_pos = ev.matrix_world @ ev.data.vertices[test_vi].co

    dist = (on_pos - off_pos).length
    print(f"  f{f}: dist={dist:.4f}")

ct.mute = False
bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_final.blend")
print("\nSAVED")
