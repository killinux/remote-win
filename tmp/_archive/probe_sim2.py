import bpy, json
scn = bpy.context.scene
w = scn.rigidbody_world

# list current state
print("胸.L exists:", bpy.data.objects.get("胸.L") is not None)
all_objs = [o.name for o in bpy.data.objects if "胸" in o.name or "_RGBAanchor" in o.name]
print("rgba objs:", all_objs)
print("world.enabled:", w.enabled if w else None)
if w and w.collection:
    print("rb_world.collection:", sorted([o.name for o in w.collection.objects]))
if w and w.constraints:
    print("rb_world.constraints count:", len(w.constraints.objects))
