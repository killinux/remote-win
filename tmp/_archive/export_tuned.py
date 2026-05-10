import bpy, os, math
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.pmx.exporter import export as pmx_export
from mmd_tools.core.model import Model

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"
PMX_OUT = r"E:\mywork\mymodel\inase54_RGBA_v2.pmx"

# 1. Clean
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

# 2. Import
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)
bpy.context.view_layer.objects.active = root

# 3. Apply RGBA with tuned settings
s = bpy.context.scene.rgba_mmd
s.main_mass = 1.5
s.aux_mass = 0.1
s.linear_damping = 0.3
s.angular_damping = 0.3
s.spring_stiff_strong = 150.0
s.spring_stiff_loose = 20.0
s.spring_damp = 0.2
s.body_radius = 0.08
s.overwrite = True

bpy.ops.rgba_mmd.apply()
print(f"应用: {s.last_status}")

# 4. After build_rig, tweak Blender-side joint properties for more wiggle
for o in bpy.data.objects:
    rbc = o.rigid_body_constraint
    if rbc and "胸" in o.name:
        rbc.type = 'GENERIC_SPRING'
        # Widen limits slightly from zero
        for ax in ("x", "y", "z"):
            cur_lo = getattr(rbc, f"limit_lin_{ax}_lower")
            cur_hi = getattr(rbc, f"limit_lin_{ax}_upper")
            if abs(cur_hi - cur_lo) < 0.02:
                setattr(rbc, f"limit_lin_{ax}_lower", cur_lo - 0.003)
                setattr(rbc, f"limit_lin_{ax}_upper", cur_hi + 0.003)
            cur_alo = getattr(rbc, f"limit_ang_{ax}_lower")
            cur_ahi = getattr(rbc, f"limit_ang_{ax}_upper")
            if abs(cur_ahi - cur_alo) < 0.1:
                setattr(rbc, f"limit_ang_{ax}_lower", cur_alo - 0.01)
                setattr(rbc, f"limit_ang_{ax}_upper", cur_ahi + 0.01)
        # Lower spring damping
        for ax in ("x", "y", "z"):
            if getattr(rbc, f"use_spring_ang_{ax}", False):
                setattr(rbc, f"spring_damping_ang_{ax}", 0.1)
            if getattr(rbc, f"use_spring_{ax}", False):
                setattr(rbc, f"spring_damping_{ax}", 0.1)

# 5. Lower damping on bust rigid bodies
for o in bpy.data.objects:
    rb = o.rigid_body
    if rb and "胸" in o.name and "anchor" not in o.name:
        rb.linear_damping = 0.3
        rb.angular_damping = 0.3

rb_count = len(list(model.rigidBodies()))
j_count = len(list(model.joints()))
print(f"物理: {rb_count} 刚体, {j_count} 关节")

# 6. Export
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
print(f"\n导出完成: {PMX_OUT}")
print(f"文件: {size/1024:.0f} KB, {rb_count} 刚体, {j_count} 关节")
print(f"\n调整参数:")
print(f"  Main Mass: 1.5 (原 0.5)")
print(f"  Damping: 0.3 (原 0.7)")
print(f"  Loose Spring k: 20 (原 50)")
print(f"  Spring Damp: 0.2 (原 0.4)")
print(f"  Body Radius: 0.08 (原 0.10)")
