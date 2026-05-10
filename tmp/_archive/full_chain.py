"""Full chain: clean scene → import original PMX → apply RGBA (rotation-fixed)
→ export → re-import → VMD → bake → sample. Run on a clean state."""
import bpy, os, time
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.pmx.exporter import export as pmx_export
from mmd_tools.core.vmd.importer import VMDImporter
from mmd_tools.core.model import Model

PMX_IN = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
PMX_OUT = r"C:\Users\haoni\Desktop\inase54_RGBA.pmx"
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

# Clean
for o in list(bpy.data.objects):
    try: bpy.data.objects.remove(o, do_unlink=True)
    except: pass
print("scene cleared")

# Import original PMX
PMXImporter().execute(filepath=PMX_IN, types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
                     scale=1.0, clean_model=False, remove_doubles=False)
root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"PMX imported: root={root.name} arm={arm.name}")

# Apply RGBA (uses NEW rotation-fixed builder)
bpy.context.view_layer.objects.active = root
bpy.ops.rgba_mmd.apply()
print(f"applied: {bpy.context.scene.rgba_mmd.last_status}")

# Export
m = Model(root)
pmx_export(filepath=PMX_OUT, scale=1.0, root=root,
           armature=m.armature(), meshes=list(m.meshes()),
           rigid_bodies=list(m.rigidBodies()), joints=list(m.joints()),
           copy_textures=False, sort_materials=False, disable_specular=False,
           sort_vertices='NONE')
print(f"exported: {os.path.getsize(PMX_OUT)} bytes")

# Clean and re-import the exported PMX
for o in list(bpy.data.objects):
    try: bpy.data.objects.remove(o, do_unlink=True)
    except: pass
PMXImporter().execute(filepath=PMX_OUT, types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
                     scale=1.0, clean_model=False, remove_doubles=False)
root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"re-imported: root={root.name} arm={arm.name}")

# Load VMD
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
            convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
            use_mirror=False).assign(arm)
ad = arm.animation_data
fr = ad.action.frame_range
scn = bpy.context.scene
scn.frame_start = int(fr[0]); scn.frame_end = int(fr[1])
print(f"VMD: {scn.frame_start}-{scn.frame_end}")

# Bake
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake OK in {time.time()-t0:.1f}s, is_baked={w.point_cache.is_baked}")

# Sample using flexible name match (re-imported names have prefixes)
chest_L = next((o for o in bpy.data.objects
                if "胸.L" in o.name and not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor"))), None)
chest_R = next((o for o in bpy.data.objects
                if "胸.R" in o.name and not any(x in o.name for x in ("_前","_後","_回転","_前後","anchor"))), None)
print(f"chest_L={chest_L.name if chest_L else None} chest_R={chest_R.name if chest_R else None}")

samples = []
for f in (1, 30, 60, 90, 120, 150, 180, 210, 240, 270, 295):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    bL = arm.pose.bones.get("boob left 1")
    samples.append((f,
        round(chest_L.evaluated_get(dg).matrix_world.translation.z, 3) if chest_L else None,
        round(bL.matrix.translation.z, 3) if bL else None,
    ))
print("frame, chest_L.z, bone_L.z")
for s in samples: print(s)
cz = [s[1] for s in samples if s[1] is not None]
bz = [s[2] for s in samples if s[2] is not None]
if cz and bz:
    print(f"\nchest amp={max(cz)-min(cz):.3f} bone amp={max(bz)-min(bz):.3f}")
    diffs = [abs(s[1]-s[2]) for s in samples if s[1] is not None and s[2] is not None]
    print(f"chest-bone gap mean={sum(diffs)/len(diffs):.3f} max={max(diffs):.3f}")

sp = r"C:\Users\haoni\Desktop\rgba_roundtrip_test.blend"
bpy.ops.wm.save_as_mainfile(filepath=sp)
print(f"SAVED: {sp}")
print(f"PMX: {PMX_OUT}")
