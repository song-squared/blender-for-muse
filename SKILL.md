# blender-for-muse · Agent Skill

> 让 AI agent 在无头 Linux 机器上用 Blender 建模的工作流。
> 参考实现：`examples/nut.py`（参数化 M12 螺母：六角体 + 布尔打孔 + 螺旋内螺纹 + 三点布光 + 多视角/剖切/旋转动画）。

## 0. 环境与调用

| 项目 | 值 |
|---|---|
| Blender | 4.5 LTS（`setup.sh` 安装；`./setup.sh check` 自检） |
| 可执行文件 | `$BLENDER_BIN`，默认 `$HOME/tools/blender/current/blender`（版本无关的稳定软链接，升级 Blender 不用改路径） |
| 调用方式 | `blender -b --python script.py`（无头执行脚本）/ `-- <args>` 透传参数 |
| 渲染单帧 | `blender -b scene.blend -f 1` |
| 硬件假设 | **无 GPU**：只有 Cycles CPU 可用；内存可能紧张（无 swap，爆内存会被杀进程） |

调用前先看一眼内存：`free -m`，available < 1G 时不要起大渲染。

## 1. 核心循环（The Loop）

```
用户意图（语音/文字/截图）
  → 生成 bpy 脚本（小步，只做一件事）
  → blender -b --python 执行
  → 出错？抓 traceback，回传修复，重试（最多 3 轮，修不好就停下来问）
  → 渲染验证帧（低采样 PNG）
  → 看图自检：形状对吗？比例对吗？穿插/浮空吗？
  → 不对就改脚本再来一轮；对了就交付
```

**铁律**：

1. **永远先渲染再说话**——无头模式没有视口，渲染图是唯一的眼睛。
2. **小步执行**——一次只改一个东西，不要攒个大脚本一次性跑。
3. **traceback 是燃料**——把完整报错贴回给模型修，不要猜。
4. **验证帧用低采样**（32~64 sp，640×480 左右），成品帧才上高采样。

## 2. bpy GOTCHA 清单（4.x/5.x）

- `bpy.ops.object.modifier_apply` 要求目标是 **active object** 且处于 Object Mode；先 `bpy.context.view_layer.objects.active = obj`。
- `bpy.ops` 在 background 模式下大部分可用，但依赖 3D 视口上下文的操作（如 `bpy.ops.view3d.*`）会失败——全部用 data API + `bpy.context.scene.camera` 代替。
- 布尔修改器：cutter 物体 apply 后记得 `bpy.data.objects.remove(cutter, do_unlink=True)`，否则场景里留垃圾。
- bmesh 里 `BMFace` 没有 `calc_center()`（那是 `MeshPolygon` 的方法），用法线检查时用 `calc_center_median()`。
- 螺旋/扫掠几何自己用 bmesh 生成时，建完面检查法线朝向（参考 `examples/nut.py` 的 radial 检查 + `reverse_faces`）。
- 布尔求交的两个物体如果有**共面**，把一方半径做大一点点（如 6.0 → 6.05）嵌入，避免 z-fighting。
- 灯光能量是物理单位（瓦特）；场景整体缩放 k 倍时，灯光距离变 k 倍，能量要乘 k² 才保持亮度。

## 3. 渲染配置模板（Cycles CPU）

```python
s = bpy.context.scene
s.render.engine = 'CYCLES'
s.cycles.device = 'CPU'          # 无 GPU 机器唯一选择；EEVEE 在无头无 GPU 下基本不可用
s.cycles.samples = 64            # 验证帧 32~64，成品 128~256
s.cycles.use_denoising = True
s.cycles.denoiser = 'OPENIMAGEDENOISE'
s.render.resolution_x = 800
s.render.resolution_y = 600
s.render.image_settings.file_format = 'PNG'
```

动画直接输出 mp4，不需要外部 ffmpeg：

```python
s.render.image_settings.file_format = 'FFMPEG'
s.render.ffmpeg.format = 'MPEG4'
s.render.ffmpeg.codec = 'H264'
s.render.ffmpeg.constant_rate_factor = 'MEDIUM'
bpy.ops.render.render(animation=True)
```

**时间预算**（2 核无 GPU 实测）：默认立方体 640×360/16sp 约 6 秒；M12 螺母 800×600/64sp 约 90~160 秒；36 帧旋转动画约 20 分钟。先报预算，再开工。

## 4. 建模约定

- 脚本顶部放 `PARAMS` 字典：所有可调尺寸集中一处，**单位统一用毫米**。
- 相机视角做成 `CAM_PRESETS` 字典：`hero`（3/4 视角）、`top`（俯视）、`side`（侧视）、`top_close`（特写）、`section`（剖切），用 `-- <preset>` 切换。
- 相机对准目标的标准写法：

```python
d = mathutils.Vector(target) - cam.location
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
```

- 每次跑完顺手 `bpy.ops.wm.save_as_mainfile(filepath='xxx.blend')` 存档——`.blend` 跨平台，本地 Blender 双击即开。

## 5. 相机/灯光/材质速查

- 三点布光：主光（key）+ 辅光（fill，约主光 1/3 能量）+ 轮廓光（rim，放背后）。
- 金属材质：Principled BSDF，Metallic=1.0，Roughness=0.3~0.4，Base Color 浅灰。
- 地面：大平面 + 粗糙度 0.9 的深灰漫反射，接住阴影。
- 特写用长焦（85mm+）怼近拍；剖切用布尔 DIFFERENCE 切掉一半（`examples/nut.py` 的 section 模式）。

## 6. 交付物

一次完整交付 = 参数化 `.py` 脚本 + 渲染 PNG（多视角）+ `.blend` 存档。动画再加 mp4。

## 7. 已知局限（诚实版）

- 螺纹牙形是简化三角 profile，视觉够用，**不是 ISO 标准牙形**（真牙形牙顶牙底有平顶/圆弧）。
- 单张截图复现 3D：简单几何体/硬表面产品可行，复杂有机形态（人物/动物）别指望。
- Blender 是网格建模器：导出 FBX/OBJ/glTF/STL 给 DCC/打印没问题；要参数化 STEP 实体请走 CAD 路线（如 text-to-cad）。
- 大渲染很慢是物理限制：这套流程的定位是**验证与小场景**，大场面请上 GPU 机器。

## 8. 上 VPS 做大渲染

远端机（2 核无 GPU）只适合验证和小场景。要出成品质量，把同一套东西搬到租用的 VPS 上。

**用户侧要给 Muse 的配置**：

1. 租一台 Ubuntu VPS：多核 CPU 版便宜够用，要快就上带 GPU 的（按小时计费的 GPU 云也行）
2. 在 VPS 上开好 SSH，配好密钥登录
3. 把连接信息（host、用户名、密钥）通过 Muse 的安全凭证流程交给 Muse——**不要直接贴在聊天里**

**Muse 侧操作**（agent 照做）：

1. `ssh user@host` 连上，跑一遍 `./setup.sh`（同一个脚本，装 Blender 无头版）
2. 把脚本传过去：`scp examples/nut.py user@host:~/blender-for-muse/examples/`
3. GPU 机器上改渲染配置（只改这几行，`PARAMS` 建模参数完全不用动）：
   ```python
   s.cycles.device = 'GPU'   # 需要 NVIDIA 驱动；官方 tarball 自带 CUDA 支持
   s.cycles.samples = 256    # 成品采样，验证时用 32~64
   ```
4. 渲完把结果拿回来：`scp user@host:~/blender-for-muse/examples/outputs/* ./`

**改哪里**：只动渲染配置块（`device` / `samples` / 分辨率）。模型与渲染解耦——
这就是参数化的好处：换机器、换画质，建模脚本一行不用改。

## 9. VM 重置/替换恢复

远端机可能随时重启或被替换重建。规则很简单：

- **`~` 下的一切都会保留**：Blender 二进制、安装包 tar.xz（留在安装目录，重装不用重新下载）、
  本仓库、渲染输出、脚本。全部在持久目录里，没有东西放在 `/tmp`、`/usr/local`、`/opt`。
- **运行中的进程会死**：重启后正在渲的东西没了，重跑即可（脚本和参数都在）。
- **Blender 不依赖 apt 装的系统包**（`ldd` 干净，`setup.sh` 全程不碰 apt），
  所以替换后无需重装系统依赖。

替换后恢复流程（agent 照做）：

```bash
cd ~/workspace/blender-for-muse && ./setup.sh check   # 二进制还在？版本对吗？
```

- `check` 通过 → 什么都不用做，直接开工。
- `check` 失败 → 跑 `./setup.sh`（tar.xz 还在就地解压，不用重新下载 400MB）。
