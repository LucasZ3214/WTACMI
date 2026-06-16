# Requirements

## Functional Requirements

### Recorder

- Poll War Thunder localhost endpoints on port `8111`.
- Record aircraft telemetry with stable timestamps.
- Record player input values with stable timestamps.
- Show recording status, sample rate, dropped samples, and current file size.
- Export one portable session package per pilot.
- Continue recording if individual telemetry requests fail briefly.
- Mark gaps and errors in the recording rather than silently hiding them.

### Import And Synchronization

- Import one or two pilot session files.
- Validate file version, aircraft identity, time range, sample count, and required fields.
- Align timelines using available timestamp metadata first.
- Provide manual sync controls when automatic alignment is uncertain.
- Preserve raw samples after synchronization so analysis can be reproduced.

### 3D Reconstruction

- Reconstruct aircraft position, velocity, orientation, and trajectory over time.
- Interpolate samples for smooth replay.
- Keep raw and interpolated values distinguishable.
- Support coordinate transforms between War Thunder/map coordinates and viewer coordinates.
- Support missing-data regions without crashing the viewer.

### Replay Viewer

- Play, pause, seek, step frame by frame, and change playback speed.
- Display both aircraft trajectories.
- Display current aircraft attitude and recent trail.
- Provide top, side, front, chase, free camera, and orthographic views.
- Toggle labels, telemetry overlays, input overlays, and metric panels.
- Export screenshots or short clips in later milestones.

### ACM Metrics

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

- The recorder must be lightweight enough to run during gameplay.
- Recording must not depend on internet access.
- Session files must be portable and inspectable.
- Data format changes must be versioned.
- Viewer should handle at least 10 minutes of two-aircraft data smoothly.
- The project should be maintainable by several contributors working in parallel.

## Safety And Compliance Requirements

- Use only public localhost telemetry and normal OS input observation.
- Do not read or modify War Thunder process memory.
- Do not inject code into the game.
- Do not automate gameplay.
- Make the recorder's behavior transparent to users.

## Open Questions

- Which exact `8111` endpoints and fields are stable enough for the first implementation?
- Which input capture method is acceptable on Windows without triggering security concerns?
- Should the first app be a single combined recorder/analyzer or two separate tools?
- What is the minimum viable synchronization method if system clocks differ between pilots?
- Which aircraft and game modes should be used for first validation?
