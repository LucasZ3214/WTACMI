# WTACMI

WTACMI (War Thunder Air Combat Maneuvering Instrumentation) is an air combat training and analysis project for War Thunder. The current implementation provides a lightweight local recorder that captures localhost `8111` telemetry and keyboard/mouse input into portable `.acmi` files. Future analyzer and replay tools will import one or two `.acmi` files, synchronize timelines, reconstruct 3D aircraft tracks, and support ACM review from multiple camera views.

## Current Status

Implemented:

- Python recorder core.
- PyQt6 recorder GUI.
- War Thunder localhost `8111` polling for `/state`, `/indicators`, `/map_info.json`, `/mission.json`, and `/map_obj.json`.
- War Thunder `.blk` controls-file parsing for keyboard and mouse button bindings.
- Portable `.acmi` ZIP package output.
- GUI defaults under `recorder/output/`.
- GUI setting persistence between launches.
- Local `8111` polling-rate detection with a conservative recommended Hz.

Planned:

- `.acmi` importer.
- Single-aircraft 3D replay.
- Two-pilot timeline synchronization.
- ACM geometry and energy metrics.
- Orthographic, chase, free, top, side, and front replay views.

## Quick Start

```powershell
python recorder\wtacmi_gui.py
```

Start War Thunder before recording so `http://localhost:8111` is available. Stop recordings with the GUI `Stop` button.

## Documentation

- [Development Overview](docs/development-overview.md)
- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Telemetry and Recording Format](docs/telemetry-recording-format.md)
- [Project Decisions](docs/project-decisions.md)
- [Team Collaboration Guide](docs/team-collaboration.md)
- [Roadmap](docs/roadmap.md)
- [Recorder User Guide](recorder/README.md)
