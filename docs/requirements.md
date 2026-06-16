# Requirements

## Recorder Requirements

### Implemented

- Poll War Thunder localhost endpoints on port `8111`.
- Record raw endpoint responses with local monotonic timestamps.
- Record keyboard and mouse button input inferred from a selected War Thunder controls `.blk` file.
- Export one portable `.acmi` package per pilot.
- Continue recording when individual telemetry requests fail.
- Store request failures in `errors.ndjson`.
- Provide CLI and PyQt6 GUI entrypoints.
- Default GUI output path to `recorder/output/`.
- Use `pilot` as the default pilot alias.
- Remember last GUI inputs between launches.
- Provide a local `8111` polling-rate detection button that estimates current high-rate `/state` + `/indicators` Hz and fills a conservative recommended telemetry rate.

### Recorder Data Sources

The first recorder samples endpoints at different rates:

- High-rate: `/state`, `/indicators`
- Low-rate: `/map_obj.json`
- Startup/static: `/map_info.json`, `/mission.json`

The first recorder samples:

- pitch up/down bindings;
- roll left/right bindings;
- throttle up/down bindings;
- flaps up/down/toggle bindings;
- airbrake binding;
- primary/secondary fire bindings;
- weapon-lock bindings;
- countermeasure bindings.

### Recorder Limitations

- Joystick/gamepad axis capture is not implemented yet.
- Mouse aim cursor position is not implemented yet.
- Input capture currently targets Windows keyboard and mouse button state.
- The `Detect Max Hz` result is an estimate for the current machine and current War Thunder state, not a fixed official maximum.
- Default high-rate telemetry is `20 Hz`; default input is `60 Hz`; default map objects is `5 Hz`.

## Import And Synchronization Requirements

Planned analyzer behavior:

- Import one or two `.acmi` files.
- Validate file version, time range, sample count, required files, and required fields.
- Align timelines using metadata first.
- Provide manual sync controls when automatic alignment is uncertain.
- Preserve raw samples after synchronization so analysis can be reproduced.
- Report missing data, high latency, and sample gaps.

## 3D Reconstruction Requirements

Planned analyzer behavior:

- Generate derived replay tracks offline from `telemetry.ndjson` and `inputs.ndjson`.
- Reconstruct aircraft position, velocity, orientation, and trajectory over time.
- Interpolate samples for smooth replay.
- Keep raw and interpolated values distinguishable.
- Support coordinate transforms between War Thunder/map coordinates and viewer coordinates.
- Handle missing-data regions without crashing the viewer.

## Replay Viewer Requirements

Planned viewer behavior:

- Play, pause, seek, step frame by frame, and change playback speed.
- Display one or two aircraft trajectories.
- Display current aircraft attitude and recent trail.
- Provide top, side, front, chase, free camera, and orthographic views.
- Toggle labels, telemetry overlays, input overlays, and metric panels.
- Export screenshots or short clips in later milestones.

## ACM Metrics Requirements

Planned metrics:

- Range between aircraft.
- Closure rate.
- Altitude separation.
- Aspect angle.
- Heading crossing angle.
- Line-of-sight rate.
- Turn rate.
- Speed and energy trend.
- Time-to-merge and post-merge event markers when detectable.

## Non-Functional Requirements

- The recorder must stay lightweight enough to run during gameplay.
- Recording must not depend on internet access.
- Session files must be portable and inspectable.
- Data format changes must be versioned.
- Analyzer/replay should handle at least 10 minutes of two-aircraft data smoothly.
- The project should remain maintainable by several contributors working in parallel.

## Safety And Compliance Requirements

- Use only public localhost telemetry and normal OS input observation.
- Do not read or modify War Thunder process memory.
- Do not inject code into the game.
- Do not automate gameplay.
- Make recorder behavior transparent to users.

## Open Questions

- Which `8111` fields are stable enough for first replay reconstruction?
- What is the best future method for joystick/gamepad axis capture?
- What is the minimum viable synchronization method if pilot system clocks differ?
- Which aircraft and game modes should be used for validation samples?
