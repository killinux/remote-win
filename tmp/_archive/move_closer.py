import bpy

for o in bpy.data.objects:
    if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT":
        if "Inase54" in o.name:
            o.location.x = -5
            print(f"{o.name} -> X=-5")
        elif "Purifier" in o.name or "Inase 18" in o.name:
            o.location.x = 5
            print(f"{o.name} -> X=+5")

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\side_by_side_compare.blend")
print("Saved")
