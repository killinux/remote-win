import bpy, math, time

scn = bpy.context.scene
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# 1. Much softer springs, lower damping, higher mass for inertia
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb and "胸" in o.name and "anchor" not in o.name:
        rb.mass = 2.0
        rb.linear_damping = 0.3
        rb.angular_damping = 0.3
        print(f"  {o.name}: mass=2.0 damp=0.3")

for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        rbc.type = 'GENERIC_SPRING'
        lim = math.radians(15)
        for ax in ("x", "y", "z"):
            setattr(rbc, f"limit_ang_{ax}_lower", -lim)
            setattr(rbc, f"limit_ang_{ax}_upper", lim)
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 10.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.05)
        print(f"  {o.name}: ±15° k=10 spring_damp=0.05")

# 2. Re-bake
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"\nbake: {time.time()-t0:.1f}s")

# 3. Check if rigid body actually moves between frames
chest_L = bpy.data.objects.get("胸.L")
print("\nRigid body 胸.L position/rotation per frame:")
for f in (1, 10, 20, 30, 50, 80, 100, 130, 160, 200):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = chest_L.evaluated_get(dg)
    p = ev.matrix_world.translation
    r = ev.matrix_world.to_euler()
    print(f"  f{f}: pos=({p.x:.3f},{p.y:.3f},{p.z:.3f}) rot=({math.degrees(r.x):.1f},{math.degrees(r.y):.1f},{math.degrees(r.z):.1f})")

# 4. ON/OFF comparison at key frames
mesh_obj = next((o for o in bpy.data.objects if o.type == "MESH" and o.parent and o.parent.type == "ARMATURE"), None)
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index
            break
    if test_vi: break

bone_L = arm.pose.bones["boob left 1"]
constraint = bone_L.constraints.get("bust_physics_track")

print(f"\nVertex {test_vi} ON/OFF comparison:")
for f in (1, 30, 60, 100, 150, 200):
    constraint.mute = False
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    on_pos = ev.matrix_world @ ev.data.vertices[test_vi].co

    constraint.mute = True
    scn.frame_set(f); bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh_obj.evaluated_get(dg)
    off_pos = ev.matrix_world @ ev.data.vertices[test_vi].co

    dist = (on_pos - off_pos).length
    print(f"  f{f}: dist={dist:.4f}")

constraint.mute = False
bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_fixed2.blend")
print("\nSAVED")
