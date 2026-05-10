import bpy, math, time
from mmd_tools.core.vmd.importer import VMDImporter

VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"

root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")

# Load VMD
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
    convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
    use_mirror=False).assign(arm)
scn = bpy.context.scene
fr = arm.animation_data.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])
print(f"VMD: {scn.frame_start}-{scn.frame_end}")

# Setup rigid body world
w = scn.rigidbody_world
if w is None:
    bpy.ops.rigidbody.world_add()
    w = scn.rigidbody_world
w.enabled = True
w.substeps_per_frame = 30
w.solver_iterations = 30
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end

# Set spring damping
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        for ax in ("x","y","z"):
            setattr(rbc, f"spring_damping_ang_{ax}", 0.15)

# Bake
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"Bake: {time.time()-t0:.1f}s")

# Quick shape check at frame 1
mesh_obj = next(o for o in bpy.data.objects if o.type=="MESH" and o.parent and o.parent.type=="ARMATURE")
vg = mesh_obj.vertex_groups.get("boob left 1")
test_vi = None
for v in mesh_obj.data.vertices:
    for g in v.groups:
        if g.group == vg.index and g.weight > 0.5:
            test_vi = v.index; break
    if test_vi: break

scn.frame_set(1)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = mesh_obj.evaluated_get(dg)
p = ev.matrix_world @ ev.data.vertices[test_vi].co
print(f"\nFrame 1 v{test_vi}: ({p.x:.4f}, {p.y:.4f}, {p.z:.4f})")
print("(Original was: 0.5739, -1.0405, 17.4294)")

bpy.ops.wm.save_as_mainfile(filepath=r"E:\mywork\mymodel\inase_with_vmd.blend")
print("\nSAVED: inase_with_vmd.blend")
print("Press Alt+A to play - check for bounce")
