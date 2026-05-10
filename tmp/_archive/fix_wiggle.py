import bpy, os, sys

addon_dir = bpy.utils.user_resource('SCRIPTS', path='addons')
wiggle_path = os.path.join(addon_dir, "blender-wiggle-2-main")

print(f"Addon dir: {addon_dir}")
print(f"Wiggle path: {wiggle_path}")
print(f"Exists: {os.path.isdir(wiggle_path)}")

# List files in the wiggle directory
if os.path.isdir(wiggle_path):
    files = os.listdir(wiggle_path)
    print(f"Files: {files}")

    # Check if __init__.py exists (required for Blender addon)
    has_init = "__init__.py" in files
    has_wiggle_py = "wiggle_2.py" in files
    print(f"Has __init__.py: {has_init}")
    print(f"Has wiggle_2.py: {has_wiggle_py}")

    # Wiggle 2 is a single-file addon (wiggle_2.py), not a package
    # It needs to be at addons/wiggle_2.py, not inside a subfolder
    # OR the folder needs to be named properly with __init__.py

    # Check if wiggle_2.py is the main file
    if has_wiggle_py:
        # Copy wiggle_2.py to addons root as a single-file addon
        src = os.path.join(wiggle_path, "wiggle_2.py")
        dst = os.path.join(addon_dir, "wiggle_2.py")
        with open(src, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\nCopied wiggle_2.py -> {dst}")

        # Refresh and enable
        import addon_utils
        addon_utils.modules_refresh()
        try:
            addon_utils.enable('wiggle_2', default_set=True, persistent=True)
            print("wiggle_2 ENABLED")
        except Exception as e:
            print(f"Enable error: {e}")

# Verify
has_wiggle = hasattr(bpy.context.scene, 'wiggle_enable')
print(f"\nScene has wiggle_enable: {has_wiggle}")
