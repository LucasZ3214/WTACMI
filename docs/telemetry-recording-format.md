# Telemetry And Recording Format

## File Package

Use a versioned package extension:

```text
session-name.wtacmi
```

For the first implementation, `.wtacmi` can be a ZIP archive containing JSON metadata and newline-delimited JSON sample files:

```text
manifest.json
telemetry.ndjson
inputs.ndjson
events.ndjson
errors.ndjson
```

This keeps files portable, streamable, and easy to inspect during development.

## Manifest

```json
{
  "formatVersion": 1,
  "appVersion": "0.1.0",
  "recordingId": "uuid",
  "pilotAlias": "Pilot A",
  "aircraftName": "unknown",
  "game": "War Thunder",
  "createdAtUtc": "2026-06-16T00:00:00.000Z",
  "clock": {
    "type": "monotonic",
    "startWallTimeUtc": "2026-06-16T00:00:00.000Z"
  },
  "sampleRates": {
    "telemetryHzTarget": 30,
    "inputHzTarget": 60
  },
  "source": {
    "localhostBaseUrl": "http://localhost:8111"
  }
}
```

## Telemetry Sample

Each line in `telemetry.ndjson` is one sample:

```json
{
  "tMs": 1234.56,
  "endpoint": "/state",
  "latencyMs": 2.4,
  "data": {
    "raw": {}
  }
}
```

Use `tMs` as milliseconds from local monotonic recording start.

## Input Sample

Each line in `inputs.ndjson` is one input sample:

```json
{
  "tMs": 1234.56,
  "controls": {
    "pitch": 0.0,
    "roll": 0.0,
    "yaw": 0.0,
    "throttle": 1.0,
    "flaps": false,
    "airbrake": false,
    "firePrimary": false
  }
}
```

Control values should be normalized to `-1.0..1.0` or `0.0..1.0` depending on control type. Keep raw device values only if needed for debugging.

## Event Sample

Events describe important points in time:

```json
{
  "tMs": 5000,
  "type": "manual-marker",
  "label": "Merge"
}
```

Potential event types:

- `recording-started`
- `recording-stopped`
- `manual-marker`
- `telemetry-gap`
- `weapon-fired`
- `merge-detected`
- `sync-anchor`

## Error Sample

```json
{
  "tMs": 2300,
  "source": "telemetry-poller",
  "severity": "warning",
  "message": "Request timeout",
  "details": {
    "endpoint": "/state"
  }
}
```

## Import Contract

The analyzer must:

- reject unknown future major versions;
- warn on missing optional fields;
- preserve raw sample data;
- normalize data into an internal analysis model;
- report sample gaps and schema issues before replay.

## Versioning Rules

- Increment `formatVersion` for breaking format changes.
- Add optional fields without breaking old readers.
- Keep migration functions for old sample files once real users begin recording.
