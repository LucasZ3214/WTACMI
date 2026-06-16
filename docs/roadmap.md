# Roadmap

## Milestone 0: Planning

Status: current

- Define project scope.
- Create developer documentation.
- Decide initial technology stack.
- Identify stable War Thunder `8111` endpoints.
- Define session file format.

## Milestone 1: Minimal Recorder

Goal: produce one valid `.wtacmi` session from one pilot.

- Poll localhost `8111`.
- Store timestamped telemetry samples.
- Capture basic control inputs.
- Write `manifest.json`, `telemetry.ndjson`, `inputs.ndjson`, and `errors.ndjson`.
- Add a simple recording status UI or CLI.

## Milestone 2: Import And Single-Track Replay

Goal: replay one recorded aircraft track.

- Import `.wtacmi`.
- Validate manifest and samples.
- Reconstruct one aircraft trajectory.
- Render aircraft path in 3D.
- Add play, pause, seek, and speed controls.

## Milestone 3: Two-Pilot Synchronization

Goal: import both pilots' files and show the same fight.

- Load two session files.
- Align timelines by offset.
- Provide manual sync adjustment.
- Display both trajectories.
- Show range, closure, and altitude separation.

## Milestone 4: ACM Analysis Views

Goal: make the tool useful for training review.

- Add top, side, front, chase, free, and orthographic cameras.
- Add input overlays.
- Add aspect angle and heading crossing angle.
- Add event markers.
- Add screenshot export.

## Milestone 5: Validation And Polish

Goal: make the project usable by a small training group.

- Record repeatable sample engagements.
- Compare replay output against known fight events.
- Improve interpolation and missing-data handling.
- Add user documentation.
- Package the app for Windows.

## Future Ideas

- Shared event marker protocol.
- Automatic merge and overshoot detection.
- Instructor annotation timeline.
- Cloudless session sharing bundle.
- Export to CSV or glTF for external analysis.
