# WTACMI Recorder

Minimal recorder for War Thunder training sessions.

## What It Records

- War Thunder localhost `8111` telemetry:
  - `/state`
  - `/indicators`
  - `/map_info.json`
  - `/mission.json`
  - `/map_obj.json`
- Local input state inferred from a selected War Thunder controls `.blk` file:
  - pitch up/down
  - roll left/right
  - throttle up/down
  - flaps
  - airbrake
  - primary/secondary fire
  - weapon lock
  - countermeasures

## Run

CLI:

```powershell
python recorder\wtacmi_recorder.py --controls "C:\Users\ROG\Documents\My Games\WarThunder\Saves\xxx.blk" --output samples\pilot-a.acmi --pilot PilotA
```

GUI:

```powershell
python recorder\wtacmi_gui.py
```

By default, the GUI saves recordings under `recorder\output\`, uses `pilot` as the pilot name, and remembers the last entered settings.

The `Detect Max Hz` button runs a short localhost `8111` benchmark against the same endpoints used by recording. It reports the measured full-cycle polling rate and fills `Telemetry Hz` with a conservative recommended value. The result is an estimate for the current machine and current War Thunder state, not a fixed global limit.

Use `Ctrl+C` to stop recording. The recorder writes a `.acmi` ZIP package containing:

```text
manifest.json
telemetry.ndjson
inputs.ndjson
events.ndjson
errors.ndjson
```

## Notes

- Start War Thunder before recording so `http://localhost:8111` is available.
- The current implementation captures keyboard and mouse button states on Windows.
- `telemetry.ndjson` preserves raw endpoint responses.
- The recorder intentionally does not generate derived animation data. The replay/analyzer should convert raw telemetry and input samples into viewer tracks offline.
- Joystick/gamepad axis capture is not implemented yet.
- Mouse aim cursor position is not implemented yet.
- Telemetry request failures are stored in `errors.ndjson` instead of stopping the recording.
