# WTACMI Development Overview

## Project Name

WTACMI: War Thunder Air Combat Maneuvering Instrumentation

Japanese display name: 空戦機動計測 Air Combat Maneuvering Instrumentation

## Goal

Build a training and analysis tool for War Thunder air combat practice. The tool records telemetry returned by the local War Thunder `8111` HTTP interface and player input state during training. When both pilots install and run the recorder, the software can import both records, synchronize them, reconstruct the 3D dogfight trajectory, and provide replay, free camera, and orthographic analysis views.

## Target Users

- War Thunder pilots practicing dogfight tactics.
- Training partners who want to compare maneuver choices after a sortie.
- Instructors who need a repeatable way to review geometry, closure, energy, timing, and control inputs.

## Core Capabilities

- Record local telemetry from `http://localhost:8111`.
- Record player input values with timestamps.
- Store each pilot's session as a portable file.
- Import records from both pilots for one fight.
- Synchronize two independent timelines.
- Reconstruct 3D aircraft trajectories.
- Replay the engagement at variable speed.
- Inspect the fight from top, side, front, chase, free, and orthographic views.
- Display derived ACM metrics such as range, aspect angle, heading crossing angle, altitude separation, closure rate, turn rate, and energy trend.

## Non-Goals For The First Version

- No memory reading or game process modification.
- No real-time multiplayer data exchange between machines.
- No automatic anti-cheat-sensitive behavior.
- No competitive ranking or public cloud service.
- No full flight dynamics simulation. The replay reconstructs measured/derived positions and attitudes from recorded data.

## High-Level Workflow

1. Pilot A and Pilot B both start WTACMI Recorder before training.
2. Each recorder polls War Thunder localhost `8111` telemetry and captures local input state.
3. After the fight, both pilots export their session files.
4. One user imports both files into WTACMI Analyzer.
5. The analyzer aligns timelines, validates data quality, and reconstructs the two-aircraft scene.
6. Users replay the fight and inspect ACM metrics from multiple views.

## Recommended Technology Direction

The final stack can still be chosen during implementation, but the recommended direction is:

- Desktop app: Tauri or Electron.
- Frontend: TypeScript, React, Three.js.
- Recorder core: TypeScript/Node.js or Rust, depending on desktop shell.
- Local storage: newline-delimited JSON for raw samples plus a session manifest.
- Analysis engine: TypeScript first, with Rust modules later if performance demands it.

## Repository Layout

Proposed layout:

```text
WTACMI/
  README.md
  docs/
  apps/
    recorder/
    analyzer/
  packages/
    telemetry/
    recording-format/
    sync/
    reconstruction/
    metrics/
    viewer/
  samples/
  tests/
```

The current repository only contains documentation. Create implementation folders as milestones begin.
