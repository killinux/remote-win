"""Stage A+B: import PMX and VMD only (fast)."""
import bpy, os
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# import PMX
inst = PMXImporter()
inst.execute(filepath=PMX, types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
             scale=1.0, clean_model=False, remove_doubles=False)
root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"PMX OK: root={root.name} arm={arm.name}")

# import VMD
v = VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None,
                use_pose_mode=True, convert_mmd_camera=False,
                convert_mmd_lamp=False, frame_margin=5, use_mirror=False)
v.assign(arm)
print("VMD OK on armature")
ad = arm.animation_data
fr = ad.action.frame_range if ad and ad.action else None
print(f"action={ad.action.name if ad and ad.action else None} frames={list(fr) if fr else None}")

# set timeline
scn = bpy.context.scene
if fr:
    scn.frame_start = int(fr[0]); scn.frame_end = int(fr[1])
print(f"timeline {scn.frame_start}-{scn.frame_end}")
