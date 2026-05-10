import bpy
o = bpy.data.objects.get("胸.L")
print("胸.L exists:", o is not None)
if o:
    rb = o.rigid_body
    print(f"rb: type={rb.type} kinematic={rb.kinematic} enabled={rb.enabled} mass={rb.mass}")
    print(f"  use_deactivation={rb.use_deactivation} deactivate_linear_velocity={rb.deactivate_linear_velocity}")
    print(f"  deactivate_angular_velocity={rb.deactivate_angular_velocity}")
    print(f"  collision_shape={rb.collision_shape} collision_groups={list(rb.collision_collections)}")
    print(f"  linear_damping={rb.linear_damping} angular_damping={rb.angular_damping}")
    print(f"  parent={o.parent.name if o.parent else None}")

# Test: free the body from all constraints temporarily
import RGBA_mmd.rig_builder as rb_mod
joints_for_chest = []
for j in rb_mod.iter_rgba_joints():
    rbc = j.rigid_body_constraint
    if rbc and (rbc.object1 == o or rbc.object2 == o):
        joints_for_chest.append((j.name, rbc.enabled, rbc.type))
        rbc.enabled = False  # disable joint
print(f"disabled {len(joints_for_chest)} joints touching 胸.L:")
for jn, e, t in joints_for_chest: print(f"  {jn} type={t} (was enabled={e})")

# Step physics with only the chest body free + animation; should fall under gravity
scn = bpy.context.scene
if scn.rigidbody_world.point_cache:
    scn.rigidbody_world.point_cache.frame_start = 1
    scn.rigidbody_world.point_cache.frame_end = 60
try: bpy.ops.ptcache.free_bake_all()
except: pass
scn.frame_set(1)
samples = []
for f in (1, 5, 10, 15, 20, 30, 45, 60):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    eo = o.evaluated_get(dg)
    samples.append((f, round(eo.matrix_world.translation.z, 3)))
print("胸.L Z (joints disabled):", samples)

# re-enable joints
for jn, e, t in joints_for_chest:
    j = bpy.data.objects[jn]
    j.rigid_body_constraint.enabled = True
print("re-enabled all joints")
