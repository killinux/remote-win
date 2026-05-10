import bpy

root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)
print(f"model: {root.name}")

bpy.context.view_layer.objects.active = root
bpy.ops.rgba_mmd.remove()
print("removed old rig")

s = bpy.context.scene.rgba_mmd
s.spring_stiff_loose = 20.0
s.spring_stiff_strong = 150.0
s.spring_damp = 0.15
s.linear_damping = 0.4
s.angular_damping = 0.4
s.main_mass = 1.0
s.overwrite = True

bpy.ops.rgba_mmd.apply()
print(f"apply: {s.last_status}")
