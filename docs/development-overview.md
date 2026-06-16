# WTACMI Development Overview

## Project Name

WTACMI: War Thunder Air Combat Maneuvering Instrumentation

Japanese display name: 空戦機動計測 Air Combat Maneuvering Instrumentation

## Goal

Build a local-first training and analysis tool for War Thunder air combat practice. The recorder captures War Thunder localhost `8111` telemetry and local player input during training. The future analyzer will import one or two `.acmi` recordings, synchronize them, reconstruct 3D dogfight trajectories, and provide replay plus ACM metric views.

## Current Implementation

The repository currently includes a lightweight Python recorder:

- `recorder/wtacmi_recorder.py`: CLI recorder and reusable recording core.
- `recorder/wtacmi_gui.py`: PyQt6 GUI wrapper around the recorder core.
- `recorder/output/`: default GUI/CLI output directory for `.acmi` files.

The recorder:

- polls War Thunder localhost `8111`;
- parses a selected War Thunder controls `.blk` file;
- samples keyboard and mouse button state on Windows;
- writes raw telemetry and input samples into `.acmi`;
- records request errors instead of stopping immediately;
- can benchmark local `8111` polling speed and suggest a conservative telemetry Hz.

## Target Users

- War Thunder pilots practicing dogfight tactics.
- Training partners who want to compare maneuver choices after a sortie.
- Instructors who need repeatable review of geometry, closure, energy, timing, and control inputs.

## Core Capabilities

Implemented recorder capabilities:

- Record local telemetry from `http://localhost:8111`.
- Record selected keyboard/mouse input values with timestamps.
- Store each pilot's session as a portable `.acmi` file.
- Use a GUI to choose controls file, output path, pilot name, sample rates, and duration.
- Remember last GUI settings across launches.

Planned analyzer capabilities:

- Import records from both pilots for one fight.
- Synchronize two independent timelines.
- Reconstruct 3D aircraft trajectories.
- Replay the engagement at variable speed.
- Inspect the fight from top, side, front, chase, free, and orthographic views.
- Display derived ACM metrics such as range, aspect angle, heading crossing angle, altitude separation, closure rate, turn rate, and energy trend.

## Non-Goals

- No memory reading or game process modification.
- No code injection into War Thunder.
- No gameplay automation.
- No real-time multiplayer telemetry exchange in the first version.
- No full flight-dynamics simulation. Replay should reconstruct measured and derived tracks from recorded data.

## High-Level Workflow

1. Pilot A and Pilot B both start WTACMI Recorder before training.
2. Each recorder polls War Thunder localhost `8111` and captures local input state.
3. Each pilot stops recording and exports a `.acmi` file.
4. One user imports both `.acmi` files into the future WTACMI Analyzer.
5. The analyzer aligns timelines, validates data quality, and derives replay tracks.
6. Users replay the fight and inspect ACM metrics from multiple views.

## Technology Direction

Current recorder stack:

- Python 3.
- PyQt6 for GUI.
- Standard-library HTTP, ZIP, JSON, timing, and Windows input APIs.

Recommended future analyzer stack:

- TypeScript, React, and Three.js for interactive replay.
- A small import/analysis layer that reads `.acmi` and derives viewer tracks offline.
- Rust or Python helper modules only if performance or tooling requires them.

## Repository Layout

Current layout:

```text
WTACMI/
  README.md
  docs/
  recorder/
    README.md
    wtacmi_recorder.py
    wtacmi_gui.py
    output/
```

Future layout may add:

```text
apps/
  analyzer/
packages/
  recording-format/
  sync/
  reconstruction/
  metrics/
  viewer/
samples/
tests/
```
