# QUICKSTART

两种入门方式：👶 小白模式（全程动嘴）或 🛠️ 手动模式（三步自己跑）。
Two ways in: 👶 Beginner Mode (just talk) or 🛠️ Manual Mode (run it yourself).

---

## 👶 小白模式：全程动嘴，不用装任何东西

### 第 1 步：让 Muse 查项目

跟 Muse 说（复制这句就行）：

> 帮我查一下开源项目 **blender-for-muse**

### 第 2 步：让 Muse 在远端电脑上装好

跟 Muse 说：

> 在你的远端电脑上把 blender-for-muse 装好

Muse 会自己下载 Blender 无头版、验证安装。你什么都不用管，装好它会告诉你。

### 第 3 步：说出你想要的模型

直接说人话，语音、打字、发截图都行：

> 给我画一个 M12 的螺帽

### 第 4 步：看图，提修改

Muse 建好模型、渲染出图发你。哪里不满意，直接说：

> 内径改大一点 / 换个视角看看 / 切一半看剖面 / 做个旋转动画

### 第 5 步：拿走模型

满意了，Muse 会把 `.blend` 文件发你。本地装个 Blender（blender.org 免费下载），
双击打开就能继续编辑。

**全程你只动了嘴。** 这就是小白模式。🌱

> **You only talked.** That's Beginner Mode. 🌱

---

## 🛠️ 手动模式：三步跑通第一个模型

面向想自己动手的极客，或第一次用本项目的 AI agent。

### 前提 / Prerequisites

- Linux（Ubuntu 22.04/24.04 实测过；其他发行版大概率也行）
- Python 3（系统自带即可）
- 约 1GB 磁盘空间（Blender 安装包 ~400MB）

### 第一步：安装 / Step 1 — Install

```bash
git clone https://github.com/song-squared/blender-for-muse.git
cd blender-for-muse
./setup.sh
```

`setup.sh` 会下载 Blender 4.5 LTS 并解压到 `~/tools/blender`，然后验证无头模式能跑。
装完自检：

```bash
./setup.sh check
```

> 想装到别处？`BLENDER_DIR=/opt/blender ./setup.sh`。
> 想用别的版本？`BLENDER_VERSION=4.5.14 ./setup.sh`。

### 第二步：跑第一个模型 / Step 2 — Build your first model

```bash
export BLENDER_BIN="$HOME/tools/blender/current/blender"   # 版本无关的稳定路径
$BLENDER_BIN -b --python examples/nut.py -- hero
```

这会按 GB/T 6170 标准生成一个 **M12 六角螺母**（对边 18mm、高 10.8mm、M12×1.75 内螺纹），
渲染一张 800×600 的图：`examples/outputs/nut_M12_hero.png`，同时存下 `nut_M12.blend`。

This builds a standard **M12 hex nut** (GB/T 6170) and renders it. ~90 seconds on a 2-core CPU-only box.

### 第三步：换视角 / Step 3 — More views

```bash
$BLENDER_BIN -b --python examples/nut.py -- top_close   # 俯视特写看螺纹 / thread close-up
$BLENDER_BIN -b --python examples/nut.py -- section     # 剖切看剖面 / cross-section
$BLENDER_BIN -b --python examples/nut.py -- turntable   # 36 帧旋转动画 mp4 / turntable animation
```

## 下一步 / Next

- 改参数：打开 `examples/nut.py`，顶部 `PARAMS` 字典里改数字就行（单位：毫米）。
  All tunable dimensions live in the `PARAMS` dict at the top (millimeters).
- 读 `SKILL.md`：完整的 agent 工作流——生成脚本 → 执行 → 报错重修 → 渲染自检 → 迭代。
  Read `SKILL.md` for the full agent loop.

## 大渲染：上 VPS / Big renders: move to a VPS

远端机只够验证和小场景。要成品质量：租一台 Ubuntu VPS（多核 CPU 版或 GPU 版），
把 SSH 连接信息（host、用户名、密钥）通过安全流程交给 Muse。
Muse 在 VPS 上跑 `./setup.sh` 装好，把脚本传过去，
改两行渲染配置（`s.cycles.device = 'GPU'`，采样调高），开渲，
最后 `scp` 把结果拿回来。建模参数不用动。

细则见 `SKILL.md` 第 8 节。Details in `SKILL.md` §8.
