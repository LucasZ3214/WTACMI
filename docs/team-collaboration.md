# Team Collaboration Guide

## Recommended Roles

Several people may participate in this project. One person can hold multiple roles early on:

- Project lead: prioritizes milestones and keeps scope controlled.
- Recorder developer: maintains `recorder/wtacmi_recorder.py`, `recorder/wtacmi_gui.py`, input capture, and `.acmi` writing.
- Recording-format maintainer: reviews changes to `manifest.json`, NDJSON files, and migration rules.
- Analysis developer: implements import, synchronization, reconstruction, and metrics.
- Viewer developer: implements 3D replay, camera modes, overlays, and UI.
- QA/test pilot: records sample sessions and verifies replay accuracy.
- Documentation maintainer: keeps user and developer docs aligned with implementation.

## Branch Strategy

Use short-lived feature branches:

```text
master
feature/recorder-input-axis
feature/acmi-importer
feature/replay-viewer
fix/sync-offset
docs/update-recorder-guide
```

Each feature branch should be merged through a pull request once the team grows. Direct commits to `master` are acceptable only during very early solo prototyping.

## Commit Style

Use concise commit messages:

```text
docs: update recorder usage
feat: add PyQt recorder GUI
feat: add acmi importer
fix: handle missing telemetry gaps
test: add sync offset fixtures
```

## Pull Request Checklist

Before merging:

- The change has a clear purpose.
- New behavior has tests or a manual verification note.
- Public data formats are documented.
- Existing `.acmi` sample files still import when applicable.
- Recorder changes do not add unnecessary runtime overhead.
- No unrelated formatting churn is included.

## Code Ownership By Area

Suggested ownership:

```text
docs/                         Documentation maintainer
recorder/                      Recorder developer
recorder/wtacmi_recorder.py    Recorder developer
recorder/wtacmi_gui.py         Recorder developer
packages/recording-format/     Recording-format maintainer
packages/sync/                 Analysis developer
packages/reconstruction/       Analysis developer
packages/metrics/              Analysis developer
packages/viewer/               Viewer developer
samples/                       QA/test pilot
tests/                         Area owner plus reviewer
```

Ownership means the person reviews changes in that area. It does not prevent others from contributing.

## Issue Labels

Recommended labels:

- `area: recorder`
- `area: gui`
- `area: format`
- `area: viewer`
- `area: sync`
- `area: metrics`
- `area: docs`
- `type: bug`
- `type: feature`
- `type: research`
- `priority: high`
- `good first issue`

## Development Rules

- Keep raw telemetry and normalized analysis models separate.
- Keep the recorder lightweight; do expensive derivation in analyzer/replay code.
- Do not introduce game-process memory access.
- Do not silently change `.acmi` format semantics.
- Add sample files for bugs in synchronization or reconstruction when practical.
- Prefer small pull requests that can be reviewed quickly.

## Verification Expectations

Recorder changes should usually verify:

- Python syntax compilation.
- GUI offscreen initialization.
- GUI start/stop recording path.
- `.acmi` ZIP contents.

Analyzer changes should usually verify:

- Import of valid `.acmi`.
- Clear errors for missing or malformed files.
- Stable output for known sample recordings.

## Communication Rhythm

- Keep a short roadmap issue pinned.
- Use one issue per feature or bug.
- Record decisions in `docs/` when they affect architecture or file formats.
- For training validation, note aircraft, map, game mode, recording version, and telemetry Hz.
