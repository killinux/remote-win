import bpy, os
print("OBJ_COUNT:", len(bpy.data.objects))
roots = []
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT":
                roots.append(o.name)
        except: pass
print("MMD_ROOTS:", roots)
arms = [o.name for o in bpy.data.objects if o.type == "ARMATURE"]
print("ARMS:", arms)
# check rgba bodies
rgba = [o.name for o in bpy.data.objects if "胸" in o.name or "RGBAanchor" in o.name]
print("RGBA_BODIES:", rgba)
# check saved file
sp = r"C:\Users\haoni\Desktop\rgba_test.blend"
print("SAVED_FILE:", os.path.exists(sp), os.path.getsize(sp) if os.path.exists(sp) else None)
# check current frame
print("FRAME:", bpy.context.scene.frame_current)
# rigid body world
w = bpy.context.scene.rigidbody_world
print("WORLD:", w is not None, "enabled:", w.enabled if w else None,
      "collection:", len(w.collection.objects) if w and w.collection else None)
