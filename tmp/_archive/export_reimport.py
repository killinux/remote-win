"""Export current rigged model as PMX → re-import → apply VMD → bake → sample.

This tests whether the RGBA rig survives a PMX round-trip and behaves consistently.
The exported PMX can also be opened in MMD itself (where RGBA's tuning was designed
for) — Blender's Bullet differs from MMD's Bullet so MMD playback may be the gold
standard for evaluating the rig.
"""
import bpy, os, time
from mmd_tools.core.pmx.exporter import export as pmx_export
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.vmd.importer import VMDImporter

EXPORT_PMX = r"C:\Users\haoni\Desktop\inase54_RGBA.pmx"
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

print("=== STEP 1: Locate currently-rigged model ===")
root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
if not root: raise SystemExit("no model loaded")
arm = next((c for c in root.children if c.type=="ARMATURE"), None)
print(f"root={root.name} arm={arm.name}")

# Count current rig
rgba_count = sum(1 for o in bpy.data.objects if "胸" in o.name or "RGBAanchor" in o.name)
print(f"RGBA objects in scene: {rgba_count}")

print("=== STEP 2: Export to PMX ===")
bpy.context.view_layer.objects.active = root
t0 = time.time()
from mmd_tools.core.model import Model
m = Model(root)
arm_obj_real = m.armature()
meshes = list(m.meshes())
rigids = list(m.rigidBodies())
joints_list = list(m.joints())
print(f"to export: arm={arm_obj_real.name} meshes={len(meshes)} rigids={len(rigids)} joints={len(joints_list)}")
try:
    pmx_export(
        filepath=EXPORT_PMX, scale=1.0, root=root,
        armature=arm_obj_real, meshes=meshes,
        rigid_bodies=rigids, joints=joints_list,
        copy_textures=False, sort_materials=False, disable_specular=False,
        sort_vertices='NONE',
    )
    print(f"export OK in {time.time()-t0:.1f}s, file={os.path.getsize(EXPORT_PMX) if os.path.isfile(EXPORT_PMX) else 'MISSING'} bytes")
except Exception as e:
    print(f"export FAILED: {type(e).__name__}: {e}")
    raise

print("=== STEP 3: Clean scene & re-import the exported PMX ===")
for o in list(bpy.data.objects):
    try: bpy.data.objects.remove(o, do_unlink=True)
    except: pass
PMXImporter().execute(filepath=EXPORT_PMX,
                     types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
                     scale=1.0, clean_model=False, remove_doubles=False)
new_root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
new_arm = next((c for c in new_root.children if c.type=="ARMATURE"), None)
print(f"re-imported: root={new_root.name} arm={new_arm.name} bones={len(new_arm.data.bones)}")

# Count rigid bodies + joints in re-imported model
rb_grp = next((o for o in bpy.data.objects if getattr(o,"mmd_type",None)=="RIGID_GRP_OBJ"), None)
jt_grp = next((o for o in bpy.data.objects if getattr(o,"mmd_type",None)=="JOINT_GRP_OBJ"), None)
rb_count = len(rb_grp.children) if rb_grp else 0
jt_count = len(jt_grp.children) if jt_grp else 0
print(f"re-imported rigid bodies: {rb_count}, joints: {jt_count}")
# RGBA-named survivors
rgba_rb = [c.name for c in (rb_grp.children if rb_grp else []) if "胸" in c.name or "RGBAanchor" in c.name]
rgba_jt = [c.name for c in (jt_grp.children if jt_grp else []) if "胸" in c.name or "RGBAanchor" in c.name]
print(f"RGBA rigid bodies survived: {len(rgba_rb)} {rgba_rb[:8]}")
print(f"RGBA joints survived: {len(rgba_jt)} {rgba_jt[:8]}")

print("=== STEP 4: Load VMD ===")
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
            convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
            use_mirror=False).assign(new_arm)
ad = new_arm.animation_data
fr = ad.action.frame_range if ad and ad.action else None
scn = bpy.context.scene
if fr:
    scn.frame_start = int(fr[0]); scn.frame_end = int(fr[1])
print(f"VMD loaded: action={ad.action.name if ad and ad.action else None} frames={scn.frame_start}-{scn.frame_end}")

print("=== STEP 5: Bake rigid body simulation ===")
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end
try: bpy.ops.ptcache.free_bake_all()
except Exception as e: print("free:", e)
t0 = time.time()
try:
    with bpy.context.temp_override(scene=scn):
        bpy.ops.ptcache.bake_all(bake=True)
    print(f"bake OK in {time.time()-t0:.1f}s, is_baked={w.point_cache.is_baked}")
except Exception as e:
    print(f"bake FAILED: {e}")

print("=== STEP 6: Sample motion ===")
samples = []
for f in (1, 30, 60, 90, 120, 150, 180, 210, 240, 270, 295):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    cL = bpy.data.objects.get("胸.L")
    bL = new_arm.pose.bones.get("boob left 1")
    samples.append((f,
        round(cL.evaluated_get(dg).matrix_world.translation.z, 3) if cL else None,
        round(bL.matrix.translation.z, 3) if bL else None,
    ))
print("frame, 胸.L_z, bone_L_z")
for s in samples: print(s)
cz = [s[1] for s in samples if s[1] is not None]
bz = [s[2] for s in samples if s[2] is not None]
if cz and bz:
    print(f"\n胸.L Z amp={max(cz)-min(cz):.3f}  bone_L Z amp={max(bz)-min(bz):.3f}")
    diffs = [abs(s[1]-s[2]) for s in samples if s[1] is not None and s[2] is not None]
    print(f"chest-bone gap mean={sum(diffs)/len(diffs):.3f} max={max(diffs):.3f}")

# Save final
sp = r"C:\Users\haoni\Desktop\rgba_roundtrip_test.blend"
try:
    bpy.ops.wm.save_as_mainfile(filepath=sp)
    print(f"SAVED BLEND: {sp}")
    print(f"EXPORTED PMX: {EXPORT_PMX}")
except Exception as e:
    print("save fail:", e)
