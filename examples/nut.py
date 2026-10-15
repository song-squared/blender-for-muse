# 螺帽（六角螺母）参数化脚本 —— M12 按 GB/T 6170（1型六角螺母）
# 用法: blender -b --python nut.py -- [hero|top|side]
# M12 标准尺寸:对边 s=18mm（老 DIN 934 为 19mm），高 m=10.8mm，
# 内孔按 M12 粗牙底孔 10.25mm 取 10.2mm（视觉示意，非真实螺纹）
import bpy, math, mathutils, sys, time, os

# 输出目录：脚本所在目录下的 outputs/（clone 到哪都能跑）
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ================= 可调参数（单位:mm） =================
P = {
    "across_flats": 18.0,    # 六角对边宽度
    "height":       10.8,    # 螺母总高度
    "hole_diameter": 10.2,   # 内孔直径
    "bevel":        1.0,     # 倒角宽度
    "samples":      64,
    "res_x": 800,
    "res_y": 600,
}
CAM_PRESETS = {
    "hero":      ((3.6, -3.6, 2.6), 55),   # 3/4 视角
    "top":       ((0.8, -0.8, 6.2), 55),   # 近俯视
    "side":      ((5.2, -2.0, 1.0), 55),   # 低侧视
    "top_close": ((0.4, -0.4, 3.4), 85),   # 俯视特写（看螺纹）
    "section":   ((2.8, -5.2, 2.4), 55),   # 剖切视角
    "turntable": ((3.6, -3.6, 2.6), 55),   # 旋转动画机位
}
# ======================================================

cam_name = "hero"
argv = sys.argv
if "--" in argv:
    rest = argv[argv.index("--") + 1:]
    if rest and rest[0] in CAM_PRESETS:
        cam_name = rest[0]

SC = P["across_flats"] / 1.732   # 相对旧脚本的整体缩放
R = P["across_flats"] / math.sqrt(3)
hr = P["hole_diameter"] / 2.0
hh = P["height"] / 2.0

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 本体
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=R, depth=P["height"],
                                    location=(0, 0, 0), rotation=(0, 0, math.radians(30)))
nut = bpy.context.active_object
nut.name = "Nut_M12"

# 打孔（孔径取螺纹大径 12mm，牙形另做）
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=6.0, depth=P["height"] + 4,
                                    location=(0, 0, 0))
cutter = bpy.context.active_object
bm = nut.modifiers.new(name="Hole", type='BOOLEAN')
bm.operation = 'DIFFERENCE'
bm.object = cutter
bpy.context.view_layer.objects.active = nut
bpy.ops.object.modifier_apply(modifier=bm.name)
bpy.data.objects.remove(cutter, do_unlink=True)

# 倒角
bv = nut.modifiers.new(name="Bevel", type='BEVEL')
bv.width = P["bevel"]
bv.segments = 2
bv.limit_method = 'ANGLE'
bv.angle_limit = math.radians(30)
bpy.ops.object.modifier_apply(modifier=bv.name)
for poly in nut.data.polygons:
    poly.use_smooth = True

# 材质
mat = bpy.data.materials.new(name="Steel")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.75, 0.76, 0.78, 1.0)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.35
nut.data.materials.append(mat)

# ---- 内螺纹 M12x1.75：螺旋扫掠三角牙形 ----
# 牙根 r=6.05（略嵌入孔壁防共面），牙尖 r=5.05，螺距 1.75
import bmesh
THREAD_PITCH = 1.75
th_mesh = bpy.data.meshes.new("ThreadMesh")
th_obj = bpy.data.objects.new("Thread", th_mesh)
bpy.context.collection.objects.link(th_obj)
bm = bmesh.new()
segs = 64
turns = P["height"] / THREAD_PITCH
n = int(turns * segs)
z0 = -P["height"] / 2
rings = []
for i in range(n + 1):
    t = i / segs
    th = 2 * math.pi * t
    z = z0 + THREAD_PITCH * t
    c, s_ = math.cos(th), math.sin(th)
    vA = bm.verts.new((6.05 * c, 6.05 * s_, z - THREAD_PITCH * 0.30))
    vB = bm.verts.new((5.05 * c, 5.05 * s_, z))
    vC = bm.verts.new((6.05 * c, 6.05 * s_, z + THREAD_PITCH * 0.30))
    rings.append((vA, vB, vC))
bm.verts.ensure_lookup_table()
for i in range(n):
    A0, B0, C0 = rings[i]
    A1, B1, C1 = rings[i + 1]
    bm.faces.new((A0, A1, B1, B0))
    bm.faces.new((B0, B1, C1, C0))
bm.faces.new(rings[0])          # 首端封口
bm.faces.new(rings[-1])         # 末端封口
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
f0 = bm.faces[0]
radial = mathutils.Vector((f0.calc_center_median().x, f0.calc_center_median().y, 0)).normalized()
if f0.normal.dot(radial) < 0:   # 保证法线朝外
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
bm.to_mesh(th_mesh)
bm.free()
for poly in th_mesh.polygons:
    poly.use_smooth = True
th_mesh.materials.append(mat)

# ---- 剖切（section 模式）：布尔去掉 y>0 的一半，看剖面 ----
if cam_name == "section":
    bpy.ops.mesh.primitive_cube_add(size=80, location=(0, 40, 0))
    half = bpy.context.active_object
    for o in (nut, th_obj):
        sm = o.modifiers.new(name="Section", type='BOOLEAN')
        sm.operation = 'DIFFERENCE'
        sm.object = half
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.modifier_apply(modifier=sm.name)
    bpy.data.objects.remove(half, do_unlink=True)

# 地面
bpy.ops.mesh.primitive_plane_add(size=20 * SC, location=(0, 0, -hh - 0.1))
gnd = bpy.context.active_object
gmat = bpy.data.materials.new(name="Ground")
gmat.use_nodes = True
gmat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.15, 0.15, 0.16, 1.0)
gmat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
gnd.data.materials.append(gmat)

# 灯光（位置与能量按平方反比缩放）
def area_light(name, loc, energy, size=3.0):
    bpy.ops.object.light_add(type='AREA',
                             location=(loc[0] * SC, loc[1] * SC, loc[2] * SC))
    l = bpy.context.active_object
    l.name = name
    l.data.energy = energy * SC * SC
    l.data.size = size * SC

area_light("Key", (4, -3, 6), 2500)
area_light("Fill", (-4, -2, 3), 900)
area_light("Rim", (-1, 4, 5), 1400)

# 相机
(cx, cy, cz), lens = CAM_PRESETS[cam_name]
bpy.ops.object.camera_add(location=(cx * SC, cy * SC, cz * SC))
cam = bpy.context.active_object
d = mathutils.Vector((0, 0, 0.1)) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = lens
bpy.context.scene.camera = cam

# ---- 旋转动画（turntable 模式）：36帧转一周 ----
if cam_name == "turntable":
    P["samples"] = 32
    P["res_x"], P["res_y"] = 640, 480
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 36
    bpy.ops.object.empty_add(location=(0, 0, 0))
    rig = bpy.context.active_object
    rig.name = "Turntable"
    nut.parent = rig
    th_obj.parent = rig
    rig.rotation_euler = (0, 0, 0)
    rig.keyframe_insert(data_path="rotation_euler", frame=1)
    rig.rotation_euler = (0, 0, 2 * math.pi)
    rig.keyframe_insert(data_path="rotation_euler", frame=36)
    for fc in rig.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'LINEAR'

# 渲染
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.device = 'CPU'
s.cycles.samples = P["samples"]
s.cycles.use_denoising = True
s.cycles.denoiser = 'OPENIMAGEDENOISE'
s.render.resolution_x = P["res_x"]
s.render.resolution_y = P["res_y"]
s.render.filepath = os.path.join(OUT_DIR, 'nut_M12_%s.png' % cam_name)
s.render.image_settings.file_format = 'PNG'

# 存一份 .blend，本地 Blender 可直接打开继续编辑
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, 'nut_M12.blend'))

t0 = time.time()
if cam_name == "turntable":
    s.render.image_settings.file_format = 'FFMPEG'
    s.render.ffmpeg.format = 'MPEG4'
    s.render.ffmpeg.codec = 'H264'
    s.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    s.render.filepath = os.path.join(OUT_DIR, 'nut_M12_turntable.mp4')
    bpy.ops.render.render(animation=True)
else:
    s.render.filepath = os.path.join(OUT_DIR, 'nut_M12_%s.png' % cam_name)
    s.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
print("NUT_RENDER_SECONDS[%s]: %.1f" % (cam_name, time.time() - t0))
print("NUT_DIMS: M12x1.75 across_flats=%.1fmm height=%.1fmm"
      % (P["across_flats"], P["height"]))
