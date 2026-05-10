import bpy, json
scn = bpy.context.scene
w = scn.rigidbody_world

# Drop everything to frame 1 first to invalidate cache
scn.frame_set(1)

# Verify world membership
in_world = []
for o in (bpy.data.objects.get("胸.L"), bpy.data.objects.get("上半身2_RGBAanchor"), bpy.data.objects.get("胸_後.L")):
    if o is None: continue
    in_collection = (w.collection is not None and o.name in w.collection.objects)
    in_constraints = False
    if w.constraints:
        in_constraints = any(c.name == o.name for c in w.constraints.objects)
    info = {
        "name": o.name,
        "rb_present": o.rigid_body is not None,
        "in_world_collection": in_collection,
        "in_world_constraints": in_constraints,
        "parent": o.parent.name if o.parent else None,
        "parent_type": o.parent_type,
        "parent_bone": o.parent_bone if o.parent_bone else None,
    }
    if o.rigid_body:
        info["rb_type"] = o.rigid_body.type
        info["rb_kinematic"] = o.rigid_body.kinematic
        info["rb_mass"] = o.rigid_body.mass
        info["rb_enabled"] = o.rigid_body.enabled
    info["loc"] = list(o.location)
    in_world.append(info)

print(json.dumps(in_world, ensure_ascii=False, indent=2))

# Step the simulation forward and capture rigid body world positions
print("---STEP---")
for f in (1, 2, 5, 10, 15, 20):
    scn.frame_set(f)
    o = bpy.data.objects["胸.L"]
    dg = bpy.context.evaluated_depsgraph_get()
    eo = o.evaluated_get(dg)
    print(f"frame {f}: 胸.L world_z={eo.matrix_world.translation.z:.4f}")
