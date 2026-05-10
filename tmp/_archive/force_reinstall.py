import bpy, addon_utils, os, sys, shutil

addon_dir = bpy.utils.user_resource('SCRIPTS', path='addons', create=True)
target = os.path.join(addon_dir, 'RGBA_mmd')

# 1. Fully disable and remove old version
try:
    addon_utils.disable('RGBA_mmd', default_set=False)
except:
    pass
for mod_name in list(sys.modules):
    if mod_name == 'RGBA_mmd' or mod_name.startswith('RGBA_mmd.'):
        del sys.modules[mod_name]

# Remove old directory completely
if os.path.isdir(target):
    shutil.rmtree(target)
    print(f"Removed old: {target}")

os.makedirs(target, exist_ok=True)

# 2. Write all files
FILES = {
    "__init__.py": r'''bl_info = {
    "name": "RGBA-Style MMD Bust Rig",
    "author": "RGBA-MMD addon (port of rgba.blog.jp/archives/10475373.html)",
    "version": (1, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N-Panel > RGBA MMD",
    "description": "Build the RGBA-style 5-rigid-body / 8-joint bust physics rig for any MMD model loaded via mmd_tools.",
    "category": "Physics",
    "warning": "Requires the mmd_tools addon to be installed and enabled.",
}

from . import properties, operators, ui


_modules = (properties, operators, ui)


def register():
    for m in _modules:
        m.register()


def unregister():
    for m in reversed(_modules):
        m.unregister()


if __name__ == "__main__":
    register()
''',
}

# Read actual files from the addon source (already on disk from previous install_remote)
# The key files that changed: operators.py, properties.py, ui.py
print("Writing files...")
for fn, content in FILES.items():
    fp = os.path.join(target, fn)
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  {fn}: {len(content)} bytes")

print("__init__.py written, now need operators/properties/ui/rig_builder from relay...")
print("PARTIAL - need full file transfer")
