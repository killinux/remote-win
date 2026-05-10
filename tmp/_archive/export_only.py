"""Just export the current scene to PMX, then list contents."""
import bpy, os, time
from mmd_tools.core.pmx.exporter import export as pmx_export

EXPORT_PMX = r"C:\Users\haoni\Desktop\inase54_RGBA.pmx"

root = next((o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT"), None)
if not root:
    print("no model"); raise SystemExit
print(f"root={root.name}")

# count children
arms = [c.name for c in root.children if c.type=="ARMATURE"]
print(f"armatures: {arms}")
rb_grp = next((o for o in bpy.data.objects if getattr(o,"mmd_type",None)=="RIGID_GRP_OBJ"), None)
jt_grp = next((o for o in bpy.data.objects if getattr(o,"mmd_type",None)=="JOINT_GRP_OBJ"), None)
print(f"pre-export: rigid_bodies={len(rb_grp.children) if rb_grp else 0} joints={len(jt_grp.children) if jt_grp else 0}")
rgba_rb = [c.name for c in (rb_grp.children if rb_grp else []) if "胸" in c.name or "RGBAanchor" in c.name]
print(f"pre-export RGBA rigid bodies: {len(rgba_rb)} {rgba_rb[:8]}")

# Make armature active and in object mode (some PmxExporter steps need pose access)
arm_obj = bpy.data.objects[arms[0]]
bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
try: bpy.ops.object.mode_set(mode='OBJECT')
except: pass
bpy.context.view_layer.objects.active = root
t0 = time.time()
# Use mmd_tools' Model helper to enumerate all parts
from mmd_tools.core.model import Model
m = Model(root)
arm_obj_real = m.armature()
meshes = list(m.meshes())
rigids = list(m.rigidBodies())
joints = list(m.joints())
print(f"to export: arm={arm_obj_real.name if arm_obj_real else None} meshes={len(meshes)} rigids={len(rigids)} joints={len(joints)}")
try:
    pmx_export(filepath=EXPORT_PMX, scale=1.0, root=root,
               armature=arm_obj_real,
               meshes=meshes, rigid_bodies=rigids, joints=joints,
               copy_textures=False, sort_materials=False, disable_specular=False,
               sort_vertices='NONE')
    print(f"EXPORT_OK in {time.time()-t0:.1f}s, file_size={os.path.getsize(EXPORT_PMX) if os.path.isfile(EXPORT_PMX) else 'MISSING'} bytes")
except Exception as e:
    print(f"EXPORT FAILED: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
