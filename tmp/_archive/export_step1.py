import bpy, os
from mmd_tools.core.pmx.importer import PMXImporter
from mmd_tools.core.model import Model

PMX = r"E:\mywork\mymodel\inase (purifier)_lezisell-A\inase54.pmx"

# 1. 清空场景
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for a in list(bpy.data.armatures): bpy.data.armatures.remove(a)
for act in list(bpy.data.actions): bpy.data.actions.remove(act)

# 2. 导入 PMX
PMXImporter().execute(filepath=PMX,
    types={'MESH','ARMATURE','PHYSICS','MORPHS','DISPLAY'},
    scale=1.0, clean_model=False, remove_doubles=False)
root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)

print(f"导入完成: {root.name}, 骨骼数={len(arm.data.bones)}")
print(f"原始物理: {len(list(model.rigidBodies()))} 刚体, {len(list(model.joints()))} 关节")

# 3. 应用 RGBA 刚体
bpy.context.view_layer.objects.active = root
bpy.ops.rgba_mmd.detect()
print(f"检测: {bpy.context.scene.rgba_mmd.last_status}")

bpy.ops.rgba_mmd.apply()
print(f"应用: {bpy.context.scene.rgba_mmd.last_status}")

# 4. 统计结果
rb_count = len(list(model.rigidBodies()))
j_count = len(list(model.joints()))
print(f"\n应用后物理: {rb_count} 刚体, {j_count} 关节")

# 列出所有刚体
print("\n刚体列表:")
for rb in model.rigidBodies():
    mmd = rb.mmd_rigid
    print(f"  {rb.name}: bone='{mmd.bone}' type={mmd.type}")

print("\n关节列表:")
for j in model.joints():
    print(f"  {j.name}")
