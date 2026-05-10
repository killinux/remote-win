import bpy, os
from mmd_tools.core.model import Model
from mmd_tools.core.pmx.exporter import export as pmx_export

root = next(o for o in bpy.data.objects if o.type=="EMPTY" and getattr(o,"mmd_type",None)=="ROOT")
arm = next(c for c in root.children if c.type=="ARMATURE")
model = Model(root)

PMX_OUT = r"E:\mywork\mymodel\inase54_RGBA.pmx"

pmx_export(
    filepath=PMX_OUT,
    scale=1.0,
    root=root,
    armature=model.armature(),
    meshes=list(model.meshes()),
    rigid_bodies=list(model.rigidBodies()),
    joints=list(model.joints()),
    copy_textures=False,
    sort_materials=False,
    disable_specular=False,
    sort_vertices='NONE',
)

size = os.path.getsize(PMX_OUT)
print(f"导出完成: {PMX_OUT}")
print(f"文件大小: {size:,} bytes ({size/1024/1024:.1f} MB)")
print(f"包含: {len(list(model.rigidBodies()))} 刚体, {len(list(model.joints()))} 关节")
print(f"\n你可以用以下方式验证:")
print(f"  1. 在 PMXEditor 中打开 {PMX_OUT}，查看刚体/关节标签页")
print(f"  2. 在 MMD 中加载此模型 + VMD，播放查看胸部弹跳效果")
print(f"  3. 重新导入到 Blender 验证刚体是否保留")
