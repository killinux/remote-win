import bpy, RGBA_mmd.operators as ops, inspect
src = inspect.getsource(ops.RGBAMMD_OT_apply.execute)
print("HAS world.enabled fix:", "rigidbody_world.enabled = True" in src)
print("HAS build_rig:", "build_rig" in src)
w = bpy.context.scene.rigidbody_world
print("world.enabled:", w.enabled if w else None)
print("frame current:", bpy.context.scene.frame_current)
# count objects
rb_count = sum(1 for o in bpy.data.objects if "胸" in o.name or "_RGBAanchor" in o.name)
print("rgba_objs:", rb_count)
