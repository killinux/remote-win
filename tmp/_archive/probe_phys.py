import bpy, json
scn = bpy.context.scene
w = scn.rigidbody_world
print("WORLD:", "enabled=", w.enabled, "ew_gravity=", w.effector_weights.gravity if w.effector_weights else None)
print("scn.gravity:", list(scn.gravity), "scn.use_gravity:", scn.use_gravity)

# Check 胸.L thoroughly
o = bpy.data.objects.get("胸.L")
print("=== 胸.L ===")
print("loc:", list(o.location))
print("matrix_world:", [list(r) for r in o.matrix_world])
print("parent:", o.parent.name if o.parent else None, "type:", o.parent_type)
print("scale:", list(o.scale), "rest scale of parent:", list(o.parent.scale) if o.parent else None)
rb = o.rigid_body
print("rb.type:", rb.type, "rb.enabled:", rb.enabled, "rb.kinematic:", rb.kinematic,
      "rb.mass:", rb.mass, "rb.collision_shape:", rb.collision_shape,
      "use_deactivation:", rb.use_deactivation, "is_animated:", getattr(rb, "is_animated", "?"))

# Force world bake/sim
print("---BAKE TEST---")
scn.frame_set(1)
bpy.context.view_layer.update()
# unparent the body to test if gravity applies
import copy
mw = o.matrix_world.copy()
o.parent = None
o.matrix_world = mw
print("after unparent: parent=", o.parent, "world_z=", o.matrix_world.translation.z)
scn.frame_set(1)
samples = []
for f in (1, 3, 5, 10, 15, 20):
    scn.frame_set(f)
    dg = bpy.context.evaluated_depsgraph_get()
    eo = o.evaluated_get(dg)
    samples.append((f, round(eo.matrix_world.translation.z, 4)))
print("胸.L Z (unparented):", samples)
