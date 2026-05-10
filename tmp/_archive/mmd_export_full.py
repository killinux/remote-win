import bpy, os, math
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.pmx.exporter import export as pmx_export
from mmd_tools.core.model import Model

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
PMX_OUT = r"E:\mywork\mymodel\inase54_RGBA_v2.pmx"

# 1. Import
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)
bpy.context.view_layer.objects.active = root
print(f"Imported: {root.name}")

# 2. Set RGBA params tuned for MMD
s = bpy.context.scene.rgba_mmd
s.main_mass = 1.0
s.aux_mass = 0.05
s.linear_damping = 0.95
s.angular_damping = 0.95
s.spring_stiff_strong = 100.0
s.spring_stiff_loose = 20.0
s.spring_damp = 0.3
s.body_radius = 0.08
s.overwrite = True

# 3. Apply RGBA rig
bpy.ops.rgba_mmd.apply()
print(f"Applied: {s.last_status}")

# 4. Check what mmd_joint has BEFORE we tweak
print("\n=== Before tweak ===")
for j in list(model.joints())[:2]:
    mj = j.mmd_joint
    rbc = j.rigid_body_constraint
    print(f"  {j.name}: spring_ang=({mj.spring_angular[0]:.0f},{mj.spring_angular[1]:.0f},{mj.spring_angular[2]:.0f}) blender_type={rbc.type if rbc else '?'}")

# 5. Fix for MMD export: ensure mmd_joint spring values are set
# The RGBA apply converts to GENERIC and disables springs in Blender,
# but we need the mmd_joint properties to have spring values for PMX export.
# Also convert joints back to GENERIC_SPRING for proper PMX export.
for j in model.joints():
    mj = j.mmd_joint
    rbc = j.rigid_body_constraint
    if rbc is None:
        continue

    # Restore to GENERIC_SPRING
    rbc.type = 'GENERIC_SPRING'

    is_free = any(x in j.name for x in ("前1", "回転1"))
    is_yfree = "前後1" in j.name

    if is_free:
        # Rotation-allowing joints: loose angular spring
        mj.spring_angular = (s.spring_stiff_loose, s.spring_stiff_loose, s.spring_stiff_loose)
        mj.spring_linear = (s.spring_stiff_strong, s.spring_stiff_strong, s.spring_stiff_strong)
    elif is_yfree:
        # Y-free joints: loose linear Y, strong others
        mj.spring_angular = (s.spring_stiff_strong, s.spring_stiff_strong, s.spring_stiff_strong)
        mj.spring_linear = (s.spring_stiff_strong, s.spring_stiff_loose, s.spring_stiff_strong)
    else:
        # Locked joints: strong springs everywhere
        mj.spring_angular = (s.spring_stiff_strong, s.spring_stiff_strong, s.spring_stiff_strong)
        mj.spring_linear = (s.spring_stiff_strong, s.spring_stiff_strong, s.spring_stiff_strong)

    # Also set Blender-side springs to match
    for ax in ("x", "y", "z"):
        setattr(rbc, f"use_spring_{ax}", True)
        setattr(rbc, f"use_spring_ang_{ax}", True)

print("\n=== After tweak ===")
for j in model.joints():
    mj = j.mmd_joint
    rbc = j.rigid_body_constraint
    print(f"  {j.name}: spring_lin=({mj.spring_linear[0]:.0f},{mj.spring_linear[1]:.0f},{mj.spring_linear[2]:.0f}) spring_ang=({mj.spring_angular[0]:.0f},{mj.spring_angular[1]:.0f},{mj.spring_angular[2]:.0f})")

# 6. Verify rigid body properties
print("\n=== Rigid bodies ===")
for rb in model.rigidBodies():
    mmd = rb.mmd_rigid
    blender_rb = rb.rigid_body
    if blender_rb:
        print(f"  {rb.name}: type={mmd.type} mass={blender_rb.mass:.2f} damp=({blender_rb.linear_damping:.2f},{blender_rb.angular_damping:.2f})")

# 7. Export
pmx_export(
    filepath=PMX_OUT, scale=1.0, root=root,
    armature=model.armature(),
    meshes=list(model.meshes()),
    rigid_bodies=list(model.rigidBodies()),
    joints=list(model.joints()),
    copy_textures=False, sort_materials=False,
    disable_specular=False, sort_vertices='NONE',
)

size = os.path.getsize(PMX_OUT)
rb_n = len(list(model.rigidBodies()))
j_n = len(list(model.joints()))
print(f"\nExported: {PMX_OUT}")
print(f"  {size/1024:.0f} KB, {rb_n} rigids, {j_n} joints")
print(f"\nMMD 参数:")
print(f"  Mass: 1.0, Damping: 0.95")
print(f"  Strong spring: 100, Loose spring: 20")
print(f"  Body radius: 0.08 (小刚体=更多振荡)")
print(f"\n在 MMD 中加载此 PMX + VMD 播放测试")
