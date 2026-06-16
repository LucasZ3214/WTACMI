# Architecture

## Current System Components

```text
War Thunder localhost 8111
          |
          v
Telemetry Poller ---- Controls .blk Parser ---- Windows Input Sampler
          |                       |                       |
          v                       v                       v
                 Sample Clock and Recorder Core
                              |
                              v
                       .acmi Session Package
```

The current recorder is intentionally lightweight. It writes raw telemetry and input samples only. It does not generate derived animation tracks during recording.

## Planned Analysis Components

```text
.acmi Session Package(s)
          |
          v
 Import, Validation, Synchronization
          |
          v
 Replay Track Derivation
          |
          v
 Reconstruction and Metrics Engine
          |
          v
        3D Replay Viewer
```

## Component Responsibilities

### PyQt6 Recorder GUI

- Lets the user select a War Thunder controls `.blk` file.
- Lets the user choose output `.acmi` path.
- Defaults output to `recorder/output/recording-YYYYMMDD-HHMMSS.acmi`.
- Defaults pilot name to `pilot`.
- Remembers last GUI settings through `QSettings`.
- Starts and stops the recorder core in a background `QThread`.
- Displays recorder logs.
- Runs a short localhost `8111` high-rate endpoint benchmark through `Detect Max Hz`.

### Telemetry Poller

- Polls `/state` and `/indicators` at the selected high-rate telemetry Hz.
- Polls `/map_obj.json` at a lower configurable rate.
- Polls `/map_info.json` and `/mission.json` at recording start.
- Stores raw JSON endpoint responses.
- Adds local monotonic timestamps.
- Records request latency and errors.

### Controls Parser

- Reads War Thunder `.blk` controls files.
- Extracts relevant keyboard and mouse button bindings.
- Converts DirectInput keyboard scan codes into Windows virtual-key codes.
- Stores selected bindings in `manifest.json`.

### Input Sampler

- Samples Windows keyboard and mouse button state.
- Records normalized control states such as `pitch`, `roll`, and `throttle_step`.
- Records active binding labels for debugging and replay overlays.

### Sample Clock

- Provides a monotonic recording clock.
- Stores wall-clock start time for human reference.
- Avoids relying only on system time during recording.

### Session Writer

- Writes `manifest.json`, `telemetry.ndjson`, `inputs.ndjson`, `events.ndjson`, and `errors.ndjson`.
- Packages those files as `.acmi`, which is a ZIP archive.
- Flushes NDJSON data regularly.

### Polling Benchmark

- Repeatedly requests the same endpoints used during recording.
- Currently benchmarks high-rate `/state` and `/indicators` cycles.
- Computes full-cycle Hz, successful-cycle Hz, average cycle time, p95 cycle time, and per-endpoint latency/error summaries.
- Fills GUI telemetry Hz with a conservative recommended value.

### Importer

Planned:

- Reads `.acmi` packages.
- Validates schema versions and required files.
- Reports missing fields, time gaps, and suspicious sample intervals.

### Synchronizer

Planned:

- Aligns Pilot A and Pilot B recordings onto a shared engagement timeline.
- Uses wall-clock metadata, shared event markers, automatic event matching, and manual offset controls.

### Replay Track Deriver

Planned:

- Converts raw `telemetry.ndjson` and `inputs.ndjson` data into viewer-ready tracks.
- Derives position, altitude, attitude, speed, surface state, propulsion state, and input overlays offline.
- Allows extraction rules to improve without requiring users to re-record sessions.

### Metrics Engine

Planned:

- Computes frame-by-frame ACM metrics from synchronized tracks.
- Emits event markers such as merge, overshoot, reversal, hard break, and firing windows where possible.

### Viewer

Planned:

- Renders aircraft, trails, ground/grid reference, labels, and metric overlays.
- Provides playback controls and camera modes.
- Uses the same synchronized timeline as the metrics engine.

## Data Flow

1. User starts the GUI or CLI recorder.
2. Recorder parses the selected `.blk` controls file.
3. Recorder polls `8111` telemetry and samples input state.
4. Recorder writes a `.acmi` session package.
5. Analyzer imports one or two `.acmi` files.
6. Analyzer validates raw data and derives replay tracks.
7. Synchronizer creates a shared timeline.
8. Metrics engine computes ACM values.
9. Viewer renders replay and analysis overlays.

## Coordinate System Notes

War Thunder telemetry and map data may not match the viewer coordinate system. Future replay code must keep coordinate transforms explicit:

- `source`: raw coordinate from telemetry.
- `world`: normalized analysis coordinate.
- `viewer`: Three.js/rendering coordinate.

Never mix these coordinate spaces without naming the conversion.

## Error Handling Principles

- Store raw request errors in `errors.ndjson`.
- Do not discard samples unless they are invalid by schema.
- Show import warnings to users.
- Keep replay usable even with partial data.
- Make synchronization confidence visible.
