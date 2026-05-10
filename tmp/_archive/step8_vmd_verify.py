import bpy, math, time
from mmd_tools.core.vmd.importer import VMDImporter

root = next((o for o in bpy.data.objects if o.type == "EMPTY" and getattr(o, "mmd_type", None) == "ROOT"), None)
arm = next((c for c in root.children if c.type == "ARMATURE"), None)

# Load VMD
VMD = r"E:\mywork\mymodel\yaoxiang\yaoxiang.vmd"
VMDImporter(filepath=VMD, scale=1.0, bone_mapper=None, use_pose_mode=True,
            convert_mmd_camera=False, convert_mmd_lamp=False, frame_margin=5,
            use_mirror=False).assign(arm)
scn = bpy.context.scene
fr = arm.animation_data.action.frame_range
scn.frame_start = int(fr[0])
scn.frame_end = int(fr[1])
print(f"VMD: {scn.frame_start}-{scn.frame_end}")

# Bake
w = scn.rigidbody_world
w.point_cache.frame_start = scn.frame_start
w.point_cache.frame_end = scn.frame_end
try: bpy.ops.ptcache.free_bake_all()
except: pass
t0 = time.time()
with bpy.context.temp_override(scene=scn):
    bpy.ops.ptcache.bake_all(bake=True)
print(f"bake: {time.time()-t0:.1f}s")

# Check joint Blender properties (name is J.J.胸.*)
print("\nJoint properties:")
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        print(f"  {o.name}: type={rbc.type}")
        print(f"    use_limit_ang: x={rbc.use_limit_ang_x} y={rbc.use_limit_ang_y} z={rbc.use_limit_ang_z}")
        print(f"    ang_x: [{math.degrees(rbc.limit_ang_x_lower):.1f}, {math.degrees(rbc.limit_ang_x_upper):.1f}]")
        print(f"    ang_y: [{math.degrees(rbc.limit_ang_y_lower):.1f}, {math.degrees(rbc.limit_ang_y_upper):.1f}]")
        print(f"    ang_z: [{math.degrees(rbc.limit_ang_z_lower):.1f}, {math.degrees(rbc.limit_ang_z_upper):.1f}]")
        for ax in ("x","y","z"):
            sp = getattr(rbc, f"use_spring_ang_{ax}", False)
            sk = getattr(rbc, f"spring_stiffness_ang_{ax}", 0)
            sd = getattr(rbc, f"spring_damping_ang_{ax}", 0)
            print(f"    spring_ang_{ax}: use={sp} k={sk:.1f} damp={sd:.2f}")

# Sample bust bone rotation to see actual bone movement
print("\nBust bone rotation over time:")
print("frame, boob_L_rot_x(deg), boob_L_rot_z(deg)")
for f in range(1, min(scn.frame_end + 1, 300), 15):
    scn.frame_set(f)
    bpy.context.view_layer.update()
    bone = arm.pose.bones.get("boob left 1")
    if bone:
        rot = bone.matrix.to_euler()
        print(f"  f{f}: x={math.degrees(rot.x):.2f} z={math.degrees(rot.z):.2f}")

print("\nDone - press Alt+A to play")
