# Architecture

## System Components

```text
War Thunder localhost 8111
          |
          v
Telemetry Poller ---- Input Capture
          |                |
          v                v
      Sample Clock and Recorder
          |
          v
   Session Package (.wtacmi)
          |
          v
 Import, Validation, Synchronization
          |
          v
 Reconstruction and Metrics Engine
          |
          v
        3D Replay Viewer
```

## Component Responsibilities

### Telemetry Poller

- Polls `8111` endpoints at a configurable rate.
- Parses JSON responses into typed telemetry samples.
- Adds local monotonic timestamps to every sample.
- Records request latency and request errors.

### Input Capture

- Captures relevant control inputs:
  - pitch
  - roll
  - yaw
  - throttle
  - flaps
  - airbrake
  - weapon/fire states where available
  - view or tracking input only if useful for analysis
- Uses local monotonic timestamps.
- Keeps input capture implementation isolated behind an interface.

### Sample Clock

- Provides a monotonic recording clock.
- Stores wall-clock start time for human reference.
- Avoids relying only on system time during recording.

### Session Writer

- Writes raw telemetry, input samples, metadata, and errors.
- Flushes data regularly to reduce data loss after crashes.
- Produces a versioned session package.

### Importer

- Reads session packages.
- Validates schema versions and required fields.
- Reports missing fields, time gaps, and suspicious sample intervals.

### Synchronizer

- Aligns Pilot A and Pilot B recordings onto a shared engagement timeline.
- Uses one or more strategies:
  - wall-clock start time
  - shared event markers
  - takeoff/merge/fire event matching
  - manual offset adjustment

### Reconstruction Engine

- Converts raw telemetry into viewer-ready tracks.
- Interpolates positions and orientations.
- Handles coordinate system conversion.
- Marks confidence and missing-data intervals.

### Metrics Engine

- Computes frame-by-frame ACM metrics from synchronized tracks.
- Emits event markers such as merge, overshoot, reversal, hard break, and firing window where possible.

### Viewer

- Renders aircraft, trails, ground/grid reference, labels, and metric overlays.
- Provides playback controls and camera modes.
- Uses the same synchronized timeline as the metrics engine.

## Data Flow

1. Recorder collects telemetry and input samples.
2. Recorder writes a `.wtacmi` session package.
3. Analyzer imports one or two packages.
4. Analyzer validates package integrity and schema version.
5. Synchronizer creates a shared timeline.
6. Reconstruction engine generates tracks.
7. Metrics engine computes ACM values.
8. Viewer renders replay and analysis overlays.

## Coordinate System Notes

War Thunder telemetry and map data may not match the viewer coordinate system. The implementation must keep coordinate transforms explicit:

- `source`: raw coordinate from telemetry.
- `world`: normalized analysis coordinate.
- `viewer`: Three.js/rendering coordinate.

Never mix these coordinate spaces without naming the conversion.

## Error Handling Principles

- Store raw errors in the session package.
- Do not discard samples unless they are invalid by schema.
- Show import warnings to users.
- Keep replay usable even with partial data.
- Make synchronization confidence visible.
