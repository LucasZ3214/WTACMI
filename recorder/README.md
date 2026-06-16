# WTACMI Recorder

The recorder captures War Thunder localhost `8111` telemetry and local keyboard/mouse input into lightweight `.acmi` files.

## Requirements

- Windows for current input sampling.
- Python 3.
- PyQt6 for GUI usage.
- War Thunder running with localhost `8111` available.
- A War Thunder controls `.blk` file.

## What It Records

War Thunder localhost `8111` telemetry:

- `/state`
- `/indicators`
- `/map_info.json`
- `/mission.json`
- `/map_obj.json`

Local input state inferred from a selected War Thunder controls `.blk` file:

- pitch up/down
- roll left/right
- throttle up/down
- flaps
- airbrake
- primary/secondary fire
- weapon lock
- countermeasures

The recorder intentionally does not generate derived 3D animation data. Replay/analyzer tools should convert raw telemetry and input samples into viewer tracks offline.

## GUI Usage

Run:

```powershell
python recorder\wtacmi_gui.py
```

GUI fields:

- `Controls .blk`: War Thunder controls file.
- `Output .acmi`: destination recording path.
- `Pilot`: pilot alias stored in `manifest.json`.
- `8111 Base URL`: normally `http://localhost:8111`.
- `Telemetry Hz`: target full-cycle telemetry polling rate.
- `Input Hz`: local input sampling rate.
- `HTTP Timeout`: timeout per endpoint request.
- `Duration`: seconds to record; `0` means record until `Stop`.

Defaults:

- Output path is `recorder\output\recording-YYYYMMDD-HHMMSS.acmi`.
- Pilot is `pilot`.
- Telemetry Hz is `10`.
- Input Hz is `60`.
- GUI settings are remembered between launches.

Buttons:

- `Start`: starts recording in a background thread.
- `Stop`: requests clean stop and packages the `.acmi` file.
- `Detect Max Hz`: benchmarks current localhost `8111` response speed and fills `Telemetry Hz` with a conservative recommendation.

## CLI Usage

Run:

```powershell
python recorder\wtacmi_recorder.py --controls "C:\Users\ROG\Documents\My Games\WarThunder\Saves\xxx.blk" --output recorder\output\pilot-a.acmi --pilot pilot
```

Short test recording:

```powershell
python recorder\wtacmi_recorder.py --controls "C:\Users\ROG\Documents\My Games\WarThunder\Saves\xxx.blk" --duration 10
```

Stop an unlimited CLI recording with `Ctrl+C`.

## Detect Max Hz

`Detect Max Hz` runs a short benchmark against the same five endpoints used by recording. It reports:

- full-cycle Hz;
- successful-cycle Hz;
- average cycle duration;
- p95 cycle duration;
- recommended telemetry Hz;
- per-endpoint latency and error count.

The result is only an estimate for the current machine and current War Thunder state. It can change between hangar, battle, replay, or high-load situations.

## Output Package

The recorder writes a `.acmi` ZIP package containing:

```text
manifest.json
telemetry.ndjson
inputs.ndjson
events.ndjson
errors.ndjson
```

## Notes

- Start War Thunder before recording so `http://localhost:8111` is available.
- `telemetry.ndjson` preserves raw endpoint responses.
- `errors.ndjson` stores telemetry request failures instead of stopping the recording.
- Joystick/gamepad axis capture is not implemented yet.
- Mouse aim cursor position is not implemented yet.
