import bpy, math, json
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# Clean
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

# Import
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")

VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm)
scn = bpy.context.scene
fr = arm.animation_data.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])

# Record parent bone world rotation per frame
parent_bone = arm.pose.bones["上半身2"]
data = {"frames": [], "px": [], "py": [], "pz": []}

for f in range(scn.frame_start, scn.frame_end + 1):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    mat = arm.matrix_world @ parent_bone.matrix
    rot = mat.to_euler()
    data["frames"].append(f)
    data["px"].append(rot.x)
    data["py"].append(rot.y)
    data["pz"].append(rot.z)

# Save rotation data
import json
with open(r"E:\mywork\mymodel\parent_rot.json", "w") as fp:
    json.dump(data, fp)

print(f"PMX+VMD loaded, frames {scn.frame_start}-{scn.frame_end}")
print(f"Parent rotation recorded: {len(data['frames'])} frames")
print("Saved to parent_rot.json")
