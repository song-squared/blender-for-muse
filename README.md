# 🔩 blender-for-muse

[English](README.md) | [中文](README.zh-CN.md)

**Muse has a remote computer. Why not model in 3D on it?**

That's where it all starts. ✨

## 💡 Why this exists

3D modeling has a gatekeeper problem. 😤
Want a custom part? Install Blender, learn the interface, memorize hotkeys,
understand modeling, lighting, rendering — weeks of tutorials before your
first decent model. Most people who just *want a 3D model* never get there.

## 🚀 The idea

The open-source project [mcp-for-blender](https://github.com/ahujasid/mcp-for-blender)
did something cool: let AI drive Blender directly. But it needs a local Blender
install plus MCP server config — you install software on your own machine,
wire up the environment, keep the whole thing running.
All the hassle lives on your local machine. 😮‍💨

But Muse? Every Muse account comes with a remote computer. Terminal, browser,
installs software, runs programs. 💻

So why install Blender locally at all? 🤔

**One Muse remote computer is the entire 3D studio.** 🖥️

Send Muse a voice note or a screenshot. It installs Blender on its remote
computer, writes the modeling script, renders the result, checks the render
itself — you just collect two things:

- 🖼️ Rendered PNGs — inspect the model from any angle
- 📦 The `.blend` file — open it in local Blender and keep editing

What used to need a Blender install plus weeks of tutorials now takes
**one Muse account. That's it.**
Model in the cloud, check on your phone, zero local installs. ☁️

Even better: **📱 you can do 3D modeling from your phone.**
Send Muse a voice note — "draw me an M12 hex nut" — it models in the cloud,
you get back renders to inspect. A pocket 3D studio, no computer needed.

That's the innovation here: not algorithmic, but **conceptual — a new way of working**. 💡
A new way to play with Muse: treat the remote computer as an infinitely
extending workbench.

One more shift: **what used to require expertise now works for beginners**. 🌱

The traditional route demands you learn Blender — every step a gatekeeper,
each one blocking people who just want a 3D model. 🚧

The Muse version cuts the barrier down to one sentence: talk to Muse.
Isn't that exactly what Muse was designed for? AI for everyone,
regardless of technical skill. Our goals align. 🤝

## 🛠️ What it does

Tell Muse what you want — voice, text, or screenshot — and it models on its
remote computer:

- "Draw me a hex nut" → M12 nut per GB/T 6170, modeled and rendered
- "Make the inner diameter bigger" → parameter changed, re-rendered
- "Where are the internal threads?" → real M12×1.75 helical thread geometry
- "Cut it in half" → cross-section view
- "Make it rotate" → turntable animation mp4

```
You talk → Muse (remote computer) → Blender → renders + .blend
```

## ✏️ After building: tweak freely

Two ways to change the model:

**1. Ask Muse** 🗣️

Just talk to it like a human:

> "Make the inner diameter bigger"
> "Show me a top-down close-up of the threads"
> "Use the old DIN 934 dimensions instead"

Muse edits the parametric script, re-renders, sends you the new image.
Only what you asked for changes, everything else stays put.

**2. Edit the .blend yourself** 🖱️

Open it in local Blender (free at blender.org) — model, materials,
lights, cameras, all there.

## 🖥️ Big renders? Rent a VPS

The remote box (2 cores, no GPU) is for validation and small scenes.
For production quality:

1. Rent an Ubuntu VPS (multi-core CPU is cheap, GPU is faster)
2. Hand Muse the SSH credentials (host, user, key) through the secure flow
3. Muse installs the same way, flips `s.cycles.device` to `'GPU'`,
   raises the samples, and renders

Modeling params stay untouched — only the render config changes.
Full steps in `SKILL.md` §8.

## 🚀 Getting started

**👶 Beginner version** (two sentences):

> Tell your Muse: "Check out the open-source project blender-for-muse
> and install it on your remote computer." Then say: "Draw me an M12 hex nut."
>
> That's it. 😎

**👨‍💻 Technical version**: see [QUICKSTART.md](QUICKSTART.md) — your first model in three steps.

```bash
git clone https://github.com/song-squared/blender-for-muse.git
cd blender-for-muse
./setup.sh
```

## 📋 Workflow

[SKILL.md](SKILL.md) — the full spec: generate → execute → fix → render →
verify loop, bpy 4.x/5.x gotchas, Cycles CPU presets, honest time budgets. ✅

## 📁 Contents

| File | Description |
|---|---|
| `QUICKSTART.md` | Beginner mode + three-step quickstart 🚀 |
| `SKILL.md` | Full workflow spec 📋 |
| `setup.sh` | One-click install: Blender 4.5 LTS headless ⚙️ |
| `examples/nut.py` | Parametric M12 hex nut: the reference build 🔩 |
| `examples/outputs/` | Example renders, turntable mp4, .blend 🖼️ |

## ⚠️ Limitations (honest)

- **CPU rendering is slow**: ~90–160s per 800×600 frame on 2 cores, ~20 min
  for a 36-frame turntable. Built for **validation and small scenes**;
  big renders belong on a GPU box.
- **Thread profile is simplified**: looks right, but not true ISO thread form
  (real threads have flats/rounded crests and roots).
- **Single-screenshot 3D reconstruction has limits**: simple hard-surface parts
  (cups, chairs, standard fasteners) yes; complex organic shapes
  (humans, animals) no — that's the state of the industry, not just us.
- **Blender is a mesh modeler**: FBX/OBJ/glTF/STL export is seamless, great for
  visuals; for parametric STEP solids (feature tree, editable dimensions)
  use a CAD-kernel tool (e.g. text-to-cad), not this project.

## 📄 License

MIT

---

*Not affiliated with or endorsed by Meta or the Blender Foundation.
"Blender" is a trademark of the Blender Foundation; "Muse" is a Meta product.
This is a community project describing compatibility, nothing more.*

*Built with Muse* 🤖
