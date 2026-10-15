# QUICKSTART

[English](QUICKSTART.md) | [中文](QUICKSTART.zh-CN.md)

Two ways in: 👶 Beginner Mode (just talk) or 🛠️ Manual Mode (run it yourself).

---

## 👶 Beginner Mode: just talk, install nothing

### Step 1: Ask Muse to look up the project

Tell Muse (copy-paste works):

> Check out the open-source project **blender-for-muse**

### Step 2: Ask Muse to install it on its remote computer

Tell Muse:

> Install blender-for-muse on your remote computer

Muse downloads headless Blender and verifies the install itself.
You do nothing; it tells you when it's done.

### Step 3: Say what you want modeled

Just use human language — voice, text, or a screenshot:

> Draw me an M12 hex nut

### Step 4: Look at the renders, ask for changes

Muse builds the model and sends you renders. Don't like something? Just say:

> Make the inner diameter bigger / Show me another angle / Cut it in half / Make a turntable animation

### Step 5: Take the model

Happy with it? Muse sends you the `.blend` file.
Open it in local Blender (free at blender.org) and keep editing.

**You only talked.** That's Beginner Mode. 🌱

---

## 🛠️ Manual Mode: first model in three steps

For hands-on geeks, or an AI agent using this project for the first time.

### Prerequisites

- Linux (tested on Ubuntu 22.04/24.04; other distros will probably work)
- Python 3 (system default is fine)
- ~1GB disk space (Blender download is ~400MB)

### Step 1 — Install

```bash
git clone https://github.com/song-squared/blender-for-muse.git
cd blender-for-muse
./setup.sh
```

`setup.sh` downloads Blender 4.5 LTS into `~/tools/blender` and verifies headless mode works.
Self-check after install:

```bash
./setup.sh check
```

> Install elsewhere? `BLENDER_DIR=/opt/blender ./setup.sh`.
> Another version? `BLENDER_VERSION=4.5.14 ./setup.sh`.

### Step 2 — Build your first model

```bash
export BLENDER_BIN="$HOME/tools/blender/current/blender"   # version-independent stable path
$BLENDER_BIN -b --python examples/nut.py -- hero
```

This builds a standard **M12 hex nut** (GB/T 6170: 18mm across flats,
10.8mm height, M12×1.75 internal thread), renders an 800×600 image to
`examples/outputs/nut_M12_hero.png`, and saves `nut_M12.blend`.

~90 seconds on a 2-core CPU-only box.

### Step 3 — More views

```bash
$BLENDER_BIN -b --python examples/nut.py -- top_close   # thread close-up
$BLENDER_BIN -b --python examples/nut.py -- section     # cross-section
$BLENDER_BIN -b --python examples/nut.py -- turntable   # 36-frame turntable animation mp4
```

## Next

- Tweak parameters: open `examples/nut.py`, edit the `PARAMS` dict at the top (millimeters).
- Read `SKILL.md`: the full agent loop — generate script → execute → fix errors → render → self-check → iterate.

## Big renders: move to a VPS

The remote box is for validation and small scenes. For production quality:
rent an Ubuntu VPS (multi-core CPU or GPU), hand Muse the SSH credentials
(host, user, key) through the secure flow. Muse runs `./setup.sh` on the VPS,
copies the script over, flips two render settings (`s.cycles.device = 'GPU'`,
higher samples), renders, and `scp`s the results back. Modeling params stay untouched.

Details in `SKILL.md` §8.
