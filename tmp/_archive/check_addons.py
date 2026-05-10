import bpy, addon_utils

# Check Wiggle 2
print("=== Wiggle 2 status ===")
has_wiggle = hasattr(bpy.context.scene, 'wiggle_enable')
print(f"scene.wiggle_enable exists: {has_wiggle}")
if has_wiggle:
    print(f"scene.wiggle_enable = {bpy.context.scene.wiggle_enable}")

# Check if wiggle_2 module is loaded
import sys
wiggle_mods = [m for m in sys.modules if 'wiggle' in m.lower()]
print(f"Wiggle modules loaded: {wiggle_mods}")

# Check RGBA_mmd
print("\n=== RGBA_mmd status ===")
has_rgba = hasattr(bpy.context.scene, 'rgba_mmd')
print(f"scene.rgba_mmd exists: {has_rgba}")

# Check registered operators
rgba_ops = [attr for attr in dir(bpy.ops.rgba_mmd) if not attr.startswith("_")]
print(f"rgba_mmd operators: {rgba_ops}")

# Check registered panels
panels = []
for cls in bpy.types.__dir__():
    if 'RGBAMMD' in cls:
        panels.append(cls)
print(f"RGBA panels: {panels}")

# Check if wiggle operators exist
try:
    wiggle_ops = [attr for attr in dir(bpy.ops.wiggle) if not attr.startswith("_")]
    print(f"\nwiggle operators: {wiggle_ops}")
except:
    print("\nNo bpy.ops.wiggle namespace")

# Try to reload RGBA_mmd to pick up latest version
print("\n=== Reloading RGBA_mmd ===")
try:
    addon_utils.disable('RGBA_mmd', default_set=False)
    for mod_name in list(sys.modules):
        if mod_name == 'RGBA_mmd' or mod_name.startswith('RGBA_mmd.'):
            del sys.modules[mod_name]
    addon_utils.modules_refresh()
    addon_utils.enable('RGBA_mmd', default_set=True, persistent=True)
    print("RGBA_mmd reloaded")

    # Re-check panels
    panels2 = []
    for cls in bpy.types.__dir__():
        if 'RGBAMMD' in cls:
            panels2.append(cls)
    print(f"RGBA panels after reload: {panels2}")

    # Re-check operators
    rgba_ops2 = [attr for attr in dir(bpy.ops.rgba_mmd) if not attr.startswith("_")]
    print(f"rgba_mmd operators after reload: {rgba_ops2}")
except Exception as e:
    print(f"Reload error: {e}")
