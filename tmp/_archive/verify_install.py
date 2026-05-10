import bpy

# Check operators
ops = [attr for attr in dir(bpy.ops.rgba_mmd) if not attr.startswith("_")]
print(f"Operators: {ops}")

# Check panels
panels = [cls for cls in dir(bpy.types) if 'RGBAMMD' in cls]
print(f"Panels: {panels}")

# Check if wiggle operators exist
print(f"Has wiggle_setup: {'wiggle_setup' in ops}")
print(f"Has wiggle_remove: {'wiggle_remove' in ops}")
print(f"Has wiggle_bake: {'wiggle_bake' in ops}")
print(f"Has RGBAMMD_PT_wiggle: {'RGBAMMD_PT_wiggle' in panels}")
