# WTACMI

WTACMI (War Thunder Air Combat Maneuvering Instrumentation) is a planned air combat maneuvering instrumentation tool for War Thunder training. It records localhost `8111` telemetry and player input during air combat practice, imports records from both pilots, reconstructs the 3D dogfight trajectory, and provides replay plus orthographic analysis views.

## Documentation

- [Development Overview](docs/development-overview.md)
- [Requirements](docs/requirements.md)
- [Architecture](docs/architecture.md)
- [Telemetry and Recording Format](docs/telemetry-recording-format.md)
- [Team Collaboration Guide](docs/team-collaboration.md)
- [Roadmap](docs/roadmap.md)
- [Recorder](recorder/README.md)

## Project Status

The repository now includes an initial Python recorder prototype. Broader analyzer and replay implementation should follow the module boundaries and data contracts described in `docs/`.
