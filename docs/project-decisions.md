# Project Decisions

This document records current product and engineering decisions so a small team can move in the same direction.

## Product Scope

- WTACMI is local-first.
- The first versions do not provide cloud sync, online accounts, or real-time network exchange.
- Two pilots manually exchange `.acmi` recordings after training.
- The first analyzer should import local files directly.

## Recorder Philosophy

- The recorder must have the smallest reasonable impact on War Thunder performance.
- The recorder stores raw telemetry and input samples.
- Expensive parsing, synchronization, interpolation, 3D track generation, and ACM metrics belong in the offline analyzer/replay app.
- The recorder must not read game memory, inject code, or automate gameplay.

## Input Scope

- Current phase records keyboard and mouse button state only.
- Joystick/gamepad axis support is deferred.
- Mouse aim position is not required for the current phase because War Thunder free-look and camera behavior make it hard to interpret reliably.

## Telemetry Scope

The recorder keeps `/map_obj.json` because it can provide map-position information useful for trajectory reconstruction. To reduce overhead, endpoints are sampled at different rates:

- High-rate: `/state`, `/indicators`
- Low-rate: `/map_obj.json`
- Startup/static: `/map_info.json`, `/mission.json`

Default rates:

- High-rate telemetry: `20 Hz`
- Map objects: `5 Hz`
- Input: `60 Hz`

These are starting defaults, not final truth. The GUI can benchmark current localhost `8111` response speed and suggest a conservative high-rate telemetry value.

## Analyzer Direction

- The next milestone should be a GUI `.acmi` importer/validator.
- Python should be used first to keep the toolchain simple.
- Visualization technology is not final.

## Visualization Options

Options to evaluate:

- PyQt6 + PyQtGraph/OpenGL: keeps everything Python, good for early prototypes, but 3D scene polish may be limited.
- PyQt6 + VisPy: Python-native GPU visualization, useful for trajectory lines and scientific-style 3D views.
- PyQt6 + VTK/PyVista: strong 3D and analysis visualization, heavier dependency footprint.
- Browser/Three.js frontend later: best long-term interactive 3D UX, but adds a TypeScript/web build stack.
- Blender export later: useful for offline cinematic review, not ideal as the primary analysis UI.

Recommended path:

1. Build the `.acmi` importer/validator in Python + PyQt6.
2. Prototype simple 3D trajectory viewing in Python.
3. Revisit Three.js only after data format, synchronization, and replay-track derivation are proven.
