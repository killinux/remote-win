import bpy, json
# clear active object so find_mmd_root falls to scan path
bpy.context.view_layer.objects.active = None
res = bpy.ops.rgba_mmd.detect()
s = bpy.context.scene.rgba_mmd
print("DETECT_RES", res, "STATUS:", s.last_status)
