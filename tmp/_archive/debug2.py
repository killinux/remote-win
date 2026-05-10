import bpy
o = bpy.data.objects.get("胸.L")
scn = bpy.context.scene
w = scn.rigidbody_world
print(f"world: enabled={w.enabled} substeps={w.substeps_per_frame} iter={w.solver_iterations}")
print(f"  collection: {w.collection.name if w.collection else None}")
print(f"  collection.objects count: {len(w.collection.objects) if w.collection else None}")
print(f"  胸.L in collection: {o.name in w.collection.objects if w.collection else None}")
pc = w.point_cache
print(f"  point_cache: frame_start={pc.frame_start} frame_end={pc.frame_end} is_baked={pc.is_baked}")

# Check ALL joints — find any rbc connecting 胸.L
all_joints = [obj for obj in bpy.data.objects if obj.rigid_body_constraint is not None]
print(f"\nTotal joint objects in scene: {len(all_joints)}")
for j in all_joints:
    rbc = j.rigid_body_constraint
    if rbc.object1 == o or rbc.object2 == o:
        print(f"  {j.name}: type={rbc.type} enabled={rbc.enabled} "
              f"o1={rbc.object1.name if rbc.object1 else None} "
              f"o2={rbc.object2.name if rbc.object2 else None}")

# Now: COMPLETELY remove 胸.L from rigid body world and re-add as FREE dynamic
# to see if Blender even simulates a fresh body
print("\n--- TEST: remove and re-add 胸.L's rigid_body ---")
bpy.context.view_layer.objects.active = o
o.select_set(True)
bpy.ops.rigidbody.object_remove()
print(f"after remove: rb={o.rigid_body}")
bpy.ops.rigidbody.object_add(type='ACTIVE')
o.rigid_body.mass = 0.2
o.rigid_body.kinematic = False
print(f"after add: rb.type={o.rigid_body.type} mass={o.rigid_body.mass} kinematic={o.rigid_body.kinematic}")

# Unparent so parent transform doesn't fight gravity
o.parent = None
print(f"unparented: parent={o.parent}")

# Move it up to give it room to fall
o.location.z = 20.0
print(f"new z: {o.location.z}")

# Free cache and step
try: bpy.ops.ptcache.free_bake_all()
except: pass
scn.frame_set(1)
samples = []
for f in (1, 5, 10, 20, 30, 60):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    eo = o.evaluated_get(dg)
    samples.append((f, round(eo.matrix_world.translation.z, 3)))
print(f"胸.L Z (free body, gravity test): {samples}")
