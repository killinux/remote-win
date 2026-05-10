import mmd_tools, os, inspect

# Find mmd_tools source location
src = os.path.dirname(mmd_tools.__file__)
print(f"mmd_tools at: {src}")

# List all python files
for root, dirs, files in os.walk(src):
    for f in sorted(files):
        if f.endswith('.py'):
            rel = os.path.relpath(os.path.join(root, f), src)
            print(f"  {rel}")

# Find build_rig implementation
from mmd_tools.core import rigid_body as rb_mod
print(f"\nrigid_body module: {rb_mod.__file__}")

# Get build_rig source
src_code = inspect.getsource(rb_mod.RigidBodySetup.setup if hasattr(rb_mod, 'RigidBodySetup') else rb_mod)
# Just print first 3000 chars
print(f"\n--- rigid_body source (first 3000 chars) ---")
print(src_code[:3000])
