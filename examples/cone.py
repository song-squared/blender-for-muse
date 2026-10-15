# 圆锥体参数化建模 —— 快速验证脚本
# 用法: blender -b --python cone.py
import bpy, math, mathutils, sys, os

# 输出目录：脚本所在目录下的 outputs/
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ================= 可调参数（单位:mm） =================
P = {
    "radius":  20.0,   # 底面半径
    "height":  45.0,   # 锥体高度
    "samples": 32,     # 验证用低采样
    "res_x": 800,
    "res_y": 600,
}
# ======================================================

# 清空场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 建圆锥（底面落在 z=0）
bpy.ops.mesh.primitive_cone_add(
    vertices=64, radius1=P["radius"], radius2=0.0, depth=P["height"],
    location=(0, 0, P["height"] / 2))
cone = bpy.context.active_object
cone.name = "Cone"

# 金属材质
mat = bpy.data.materials.new("Metal")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.35
bsdf.inputs["Base Color"].default_value = (0.7, 0.7, 0.72, 1.0)
cone.data.materials.append(mat)

# 地面
bpy.ops.mesh.primitive_plane_add(size=500, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
gmat = bpy.data.materials.new("Ground")
gmat.use_nodes = True
gmat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
gmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.15, 0.15, 0.16, 1.0)
ground.data.materials.append(gmat)

# 灯光：主光 + 辅光（SUN，能量与距离无关）
bpy.ops.object.light_add(type='SUN', location=(0, 0, 0))
key = bpy.context.active_object
key.name = "Key"
key.rotation_euler = (math.radians(50), 0, math.radians(-30))
key.data.energy = 5.0
bpy.ops.object.light_add(type='SUN', location=(0, 0, 0))
fill = bpy.context.active_object
fill.name = "Fill"
fill.rotation_euler = (math.radians(30), 0, math.radians(150))
fill.data.energy = 1.5

# 相机：3/4 视角看向锥体中心
target = mathutils.Vector((0, 0, P["height"] / 2))
bpy.ops.object.camera_add(location=(75, -75, 60), rotation=(0, 0, 0))
cam = bpy.context.active_object
cam.name = "Camera"
cam.data.lens = 55
d = target - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# 渲染配置
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.device = 'CPU'
s.cycles.samples = P["samples"]
s.cycles.use_denoising = True
s.render.resolution_x = P["res_x"]
s.render.resolution_y = P["res_y"]
s.render.image_settings.file_format = 'PNG'
s.render.filepath = os.path.join(OUT_DIR, 'cone_hero.png')

bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, 'cone.blend'))
print("DONE: cone r=%.1fmm h=%.1fmm" % (P["radius"], P["height"]))
