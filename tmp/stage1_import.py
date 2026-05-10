import bpy, os
from mmd_tools.core.pmx.importer import PMXImporter

PMX_PATH = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
print("PMX_EXISTS:", os.path.isfile(PMX_PATH), "size:", os.path.getsize(PMX_PATH))

inst = PMXImporter()
inst.execute(
    filepath=PMX_PATH,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0,
    clean_model=False,
    remove_doubles=False,
)

# Find the new root
roots = []
for o in bpy.data.objects:
    if o.type == "EMPTY":
        try:
            if o.mmd_type == "ROOT": roots.append(o.name)
        except: pass
print("MMD_ROOTS:", roots)

arms = [(o.name, len(o.data.bones)) for o in bpy.data.objects if o.type == "ARMATURE"]
print("ARMATURES:", arms)
