import bpy, json
j = bpy.data.objects.get("J.胸_後1.L") or bpy.data.objects.get("J.胸_後1.R")
print("joint:", j.name if j else None)
if j and j.rigid_body_constraint:
    rbc = j.rigid_body_constraint
    info = {
        "type": rbc.type,
        "enabled": rbc.enabled,
        "object1": rbc.object1.name if rbc.object1 else None,
        "object2": rbc.object2.name if rbc.object2 else None,
        "use_limit_lin_x": rbc.use_limit_lin_x,
        "use_limit_lin_y": rbc.use_limit_lin_y,
        "use_limit_lin_z": rbc.use_limit_lin_z,
        "use_limit_ang_x": rbc.use_limit_ang_x,
        "use_limit_ang_y": rbc.use_limit_ang_y,
        "use_limit_ang_z": rbc.use_limit_ang_z,
        "limit_lin_x": (rbc.limit_lin_x_lower, rbc.limit_lin_x_upper),
        "limit_ang_x": (rbc.limit_ang_x_lower, rbc.limit_ang_x_upper),
        "use_spring_x": getattr(rbc, "use_spring_x", None),
        "spring_stiffness_x": getattr(rbc, "spring_stiffness_x", None),
        "spring_damping_x": getattr(rbc, "spring_damping_x", None),
    }
    print(json.dumps(info, ensure_ascii=False, indent=2))
print("---")
# also check rigid body world settings
w = bpy.context.scene.rigidbody_world
print("world:", "exists=", w is not None,
      "enabled=", w.enabled if w else None,
      "collection=", w.collection.name if w and w.collection else None,
      "constraints=", w.constraints.name if w and w.constraints else None)
if w and w.collection:
    print("rb_world.collection child count:", len(w.collection.objects))
if w and w.constraints:
    print("rb_world.constraints child count:", len(w.constraints.objects))
