# Team Collaboration Guide

## Recommended Roles

Several people may participate in this project. The following roles can be held by different people or combined by one person:

- Project lead: prioritizes milestones and keeps scope controlled.
- Recorder developer: implements `8111` polling, input capture, and session writing.
- Analysis developer: implements synchronization, reconstruction, and metrics.
- Viewer developer: implements Three.js replay, camera modes, and overlays.
- QA/test pilot: records sample sessions and verifies replay accuracy.
- Documentation maintainer: keeps user and developer docs aligned with implementation.

## Branch Strategy

Use short-lived feature branches:

```text
main or master
feature/recorder-poller
feature/session-format
feature/replay-viewer
fix/sync-offset
docs/architecture-update
```

Each feature branch should be merged through a pull request.

## Commit Style

Use concise commit messages:

```text
docs: add telemetry recording format
feat: add telemetry poller
feat: add session importer
fix: handle missing telemetry gaps
test: add sync offset fixtures
```

## Pull Request Checklist

Before merging:

- The change has a clear purpose.
- New behavior has tests or sample data where practical.
- Public data formats are documented.
- Existing sample files still import.
- The app still builds or docs still render.
- No unrelated formatting churn is included.

## Code Ownership By Area

Suggested ownership:

```text
docs/                         Documentation maintainer
apps/recorder/                Recorder developer
apps/analyzer/                Viewer and analysis developers
packages/telemetry/           Recorder developer
packages/recording-format/    Recorder and analysis developers
packages/sync/                Analysis developer
packages/reconstruction/      Analysis developer
packages/metrics/             Analysis developer
packages/viewer/              Viewer developer
samples/                      QA/test pilot
```

Ownership means the person reviews changes in that area. It does not prevent others from contributing.

## Issue Labels

Recommended labels:

- `area: recorder`
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
- Do not introduce game-process memory access.
- Do not silently change the recording file format.
- Add sample files for bugs in synchronization or reconstruction.
- Prefer small pull requests that can be reviewed quickly.

## Communication Rhythm

- Keep a short roadmap issue pinned.
- Use one issue per feature or bug.
- Record decisions in `docs/` when they affect architecture or file formats.
- For training validation, note aircraft, map, game mode, and recording version.
