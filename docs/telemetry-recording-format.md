# Telemetry And Recording Format

## File Package

WTACMI uses `.acmi` as the recording extension:

```text
session-name.acmi
```

The current `.acmi` file is a ZIP archive containing:

```text
manifest.json
telemetry.ndjson
inputs.ndjson
events.ndjson
errors.ndjson
```

The recorder intentionally keeps the package lightweight. It stores raw telemetry and input samples. Derived animation/replay tracks are generated later by the analyzer.

## Manifest

`manifest.json` describes the recording:

```json
{
  "formatVersion": 1,
  "appVersion": "0.1.0",
  "recordingId": "uuid",
  "pilotAlias": "pilot",
  "createdAtUtc": "2026-06-16T00:00:00.000+00:00",
  "clock": {
    "type": "monotonic",
    "startWallTimeUtc": "2026-06-16T00:00:00.000+00:00"
  },
  "sampleRates": {
    "telemetryHzTarget": 20.0,
    "mapObjectsHzTarget": 5.0,
    "inputHzTarget": 60.0
  },
  "source": {
    "localhostBaseUrl": "http://localhost:8111",
    "endpoints": {
      "state": "/state",
      "indicators": "/indicators",
      "map_info": "/map_info.json",
      "mission": "/mission.json",
      "map_objects": "/map_obj.json"
    },
    "endpointGroups": {
      "highRate": {
        "state": "/state",
        "indicators": "/indicators"
      },
      "lowRate": {
        "map_objects": "/map_obj.json"
      },
      "static": {
        "map_info": "/map_info.json",
        "mission": "/mission.json"
      }
    },
    "localhostDocumentation": "https://github.com/lucasvmx/WarThunder-localhost-documentation"
  },
  "controlsFile": {
    "path": "C:/Users/.../WarThunder/Saves/example.blk",
    "sha256": "..."
  },
  "inputBindings": {}
}
```

## Telemetry Samples

Each line in `telemetry.ndjson` is one endpoint response:

```json
{
  "tMs": 1234.56,
  "endpointName": "state",
  "endpoint": "/state",
  "latencyMs": 2.4,
  "data": {}
}
```

Notes:

- `tMs` is milliseconds since the recorder's monotonic start.
- `data` is the raw parsed JSON response from War Thunder.
- High-rate cycles produce `/state` and `/indicators` lines.
- `/map_obj.json` is stored at a lower rate.
- `/map_info.json` and `/mission.json` are stored at recording start.
- Request failures are stored in `errors.ndjson`, not in `telemetry.ndjson`.

## Input Samples

Each line in `inputs.ndjson` is one sampled input state:

```json
{
  "tMs": 1234.56,
  "controls": {
    "pitch_up": false,
    "pitch_down": true,
    "roll_left": false,
    "roll_right": true,
    "throttle_up": false,
    "throttle_down": false,
    "flaps": false,
    "flaps_up": false,
    "flaps_down": false,
    "airbrake": false,
    "fire_primary": false,
    "fire_secondary": false,
    "weapon_lock": false,
    "countermeasures": false,
    "pitch": 1.0,
    "roll": 1.0,
    "throttle_step": 0.0
  },
  "activeBindings": {
    "pitch_down": ["S"],
    "roll_right": ["D"]
  }
}
```

Control values:

- Boolean fields show whether a mapped action is pressed.
- `pitch`, `roll`, and `throttle_step` are normalized keyboard-derived values.
- `activeBindings` lists human-readable binding labels active at that sample.

## Event Samples

Events describe important points in time:

```json
{
  "tMs": 0,
  "type": "recording-started",
  "utc": "2026-06-16T00:00:00.000+00:00"
}
```

Current event types:

- `recording-started`
- `recording-stopped`

Planned event types:

- `manual-marker`
- `telemetry-gap`
- `weapon-fired`
- `merge-detected`
- `sync-anchor`

## Error Samples

Each line in `errors.ndjson` records one failed endpoint request:

```json
{
  "tMs": 2300.0,
  "endpointName": "state",
  "endpoint": "/state",
  "latencyMs": 50.1,
  "source": "telemetry-poller",
  "severity": "warning",
  "message": "timed out"
}
```

Errors are part of the recording and should be displayed by future import tools.

## Replay-Derived Animation Data

The recorder does not write `animation.ndjson`. Replay-ready animation data should be generated offline by the analyzer from `telemetry.ndjson` and `inputs.ndjson`.

The derived replay model should include values that can change 3D animation:

- map position and altitude;
- roll, pitch, heading, angle of attack, and sideslip;
- speed, vertical speed, load factor, and angular rates;
- aileron, elevator, rudder, flaps, landing gear, and airbrake state;
- throttle, engine state, fuel, and other propulsion values;
- player input state and active bindings.

Because this data is derived, extraction rules can improve without requiring users to re-record sessions.

## Polling Rate Detection

The PyQt6 GUI can run a short benchmark against the high-rate endpoints used by recording. The benchmark result is not stored in `.acmi` by default. It is a setup aid used to fill a conservative high-rate telemetry Hz value.

The benchmark reports:

- full-cycle Hz;
- successful-cycle Hz;
- average cycle duration;
- p95 cycle duration;
- recommended telemetry Hz;
- per-endpoint average latency, max latency, and error count.

## Import Contract

The analyzer must:

- reject unknown future major versions;
- warn on missing optional files or fields;
- preserve raw sample data;
- normalize data into an internal analysis model;
- generate replay animation tracks from raw telemetry and input samples;
- report sample gaps and schema issues before replay.

## Versioning Rules

- Increment `formatVersion` for breaking format changes.
- Add optional fields without breaking old readers.
- Keep migration functions for old sample files once real users begin recording.
