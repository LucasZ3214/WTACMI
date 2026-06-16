# Roadmap

## Milestone 0: Planning

Status: complete

- Define project scope.
- Create developer documentation.
- Decide first recorder implementation approach.
- Identify initial War Thunder `8111` endpoints.
- Define `.acmi` package structure.

## Milestone 1: Minimal Recorder

Status: implemented for keyboard/mouse first version

Goal: produce one valid `.acmi` session from one pilot.

Implemented:

- Poll localhost `8111`.
- Store timestamped raw telemetry samples.
- Capture basic keyboard/mouse control inputs from a selected `.blk` controls file.
- Write `manifest.json`, `telemetry.ndjson`, `inputs.ndjson`, `events.ndjson`, and `errors.ndjson`.
- Provide a PyQt6 GUI recorder.
- Default output to `recorder/output/`.
- Remember last GUI settings.
- Detect current localhost `8111` polling capacity and suggest telemetry Hz.
- Split endpoint sampling rates to reduce game-performance impact.

Remaining recorder work:

- Add joystick/gamepad axis capture.
- Add optional mouse aim data if useful and safe.
- Add better live recording status such as file size, sample counts, and last endpoint error.
- Add packaging for non-developer Windows users.

## Milestone 2: GUI ACMI Import And Validation

Status: next

Goal: read `.acmi` files and report whether they are usable.

- Load `.acmi` ZIP packages.
- Validate required files.
- Validate manifest version and sample rates.
- Count telemetry, input, event, and error samples.
- Report endpoint gaps and high-latency regions.
- Show basic recording summary.
- Provide this as a PyQt6 GUI.

## Milestone 3: Single-Track Replay

Goal: replay one recorded aircraft track.

- Derive replay track data from `telemetry.ndjson` and `inputs.ndjson`.
- Reconstruct one aircraft trajectory.
- Render aircraft path in 3D.
- Add play, pause, seek, and speed controls.
- Show telemetry and input overlays.

## Milestone 4: Two-Pilot Synchronization

Goal: import both pilots' files and show the same fight.

- Load two `.acmi` files.
- Align timelines by offset.
- Provide manual sync adjustment.
- Display both trajectories.
- Show range, closure, and altitude separation.

## Milestone 5: ACM Analysis Views

Goal: make the tool useful for training review.

- Add top, side, front, chase, free, and orthographic cameras.
- Add input overlays.
- Add aspect angle and heading crossing angle.
- Add event markers.
- Add screenshot export.

## Milestone 6: Validation And Polish

Goal: make the project usable by a small training group.

- Record repeatable sample engagements.
- Compare replay output against known fight events.
- Improve interpolation and missing-data handling.
- Add user documentation.
- Package the recorder and analyzer for Windows.

## Future Ideas

- Shared event marker protocol.
- Automatic merge and overshoot detection.
- Instructor annotation timeline.
- Cloudless session sharing bundle.
- Export to CSV or glTF for external analysis.
