import bpy, math, time

scn = bpy.context.scene
arm = next((o for o in bpy.data.objects if o.type == "ARMATURE"), None)

# Very soft springs = exaggerated lag/bounce
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        rbc.type = 'GENERIC_SPRING'
        lim = math.radians(30)
        for ax in ("x", "y", "z"):
            setattr(rbc, f"limit_ang_{ax}_lower", -lim)
            setattr(rbc, f"limit_ang_{ax}_upper", lim)
            setattr(rbc, f"limit_lin_{ax}_lower", 0)
            setattr(rbc, f"limit_lin_{ax}_upper", 0)
            setattr(rbc, f"use_spring_ang_{ax}", True)
            setattr(rbc, f"spring_stiffness_ang_{ax}", 5.0)
            setattr(rbc, f"spring_damping_ang_{ax}", 0.3)
            setattr(rbc, f"use_spring_{ax}", False)
        print(f"  {o.name}: ±30° k=5 (very soft)")

# Moderate body damping
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb and "胸" in o.name and "anchor" not in o.name and "phys" not in o.name:
        rb.linear_damping = 0.5
        rb.angular_damping = 0.5
        rb.mass = 1.0

# Re-bake
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake: {time.time()-t0:.1f}s")

# Check mesh vertex movement: sample a vertex near bust bone
# First find which mesh vertices are weighted to bust bone
mesh_obj = None
for o in bpy.data.objects:
    if o.type == "MESH" and o.parent and o.parent.type == "ARMATURE":
        mesh_obj = o
        break

if mesh_obj:
    vg = mesh_obj.vertex_groups.get("boob left 1")
    if vg:
        weighted_verts = []
        for v in mesh_obj.data.vertices:
            for g in v.groups:
                if g.group == vg.index and g.weight > 0.5:
                    weighted_verts.append(v.index)
        print(f"\nMesh: {mesh_obj.name}")
        print(f"Verts weighted to 'boob left 1' (w>0.5): {len(weighted_verts)}")
        if weighted_verts:
            # Sample first few vertex positions at different frames
            test_vi = weighted_verts[0]
            print(f"Tracking vertex {test_vi}:")
            for f in (1, 50, 100, 150):
                scn.frame_set(f)
                bpy.context.view_layer.update()
                dg = bpy.context.evaluated_depsgraph_get()
                ev_mesh = mesh_obj.evaluated_get(dg)
                co = ev_mesh.data.vertices[test_vi].co
                world_co = ev_mesh.matrix_world @ co
                print(f"  f{f}: world=({world_co.x:.3f}, {world_co.y:.3f}, {world_co.z:.3f})")
    else:
        print(f"No vertex group 'boob left 1' found!")
        print(f"Available groups: {[vg.name for vg in mesh_obj.vertex_groups][:20]}")

# Save
bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_exaggerated.blend")
print("\nSAVED - press Alt+A to play")
