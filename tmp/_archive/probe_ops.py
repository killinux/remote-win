import bpy
ops = sorted([n for n in dir(bpy.ops.mmd_tools) if "rig" in n.lower() or "build" in n.lower() or "joint" in n.lower()])
print("OPS:", ops)
