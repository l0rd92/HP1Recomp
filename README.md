<p align="center">
  <img src="docs/assets/hp1recomp-logo.png" alt="HP1 Recomp" width="640">
</p>

HP1Recomp is a native Windows recompilation project for **Harry Potter and the Sorcerer's Stone** on PlayStation.

<p align="center">
  <img alt="Windows x64" src="https://img.shields.io/badge/Windows-x64-0078D4?style=for-the-badge&logo=windows11&logoColor=white">
  <img alt="PSXRecomp" src="https://img.shields.io/badge/Framework-PSXRecomp-C79A2B?style=for-the-badge">
  <img alt="SLUS-01415" src="https://img.shields.io/badge/Reference-SLUS--01415-2EA44F?style=for-the-badge">
  <img alt="Phase 7" src="https://img.shields.io/badge/Phase%207-Release%20Hardening-6F42C1?style=for-the-badge">
</p>

| | |
|---|---|
| **Original game** | Harry Potter and the Sorcerer's Stone (PS1) |
| **Reference version** | USA / NTSC-U — `SLUS-01415` (English, French, Spanish) |
| **Target platform** | Windows x64 |
| **Main framework** | [PSXRecomp](https://github.com/RetroPortingToolKit/psxrecomp), using a pinned project fork |
| **Current phase** | Phase 7 — regression and release hardening |
| **Planned version** | `0.1.0-alpha` (not yet released) |

## Current status

The native build boots and runs the game. Testing has covered language selection, the title screen, cutscenes, gameplay, lessons, combat, indoor/outdoor transitions, memory cards and saving.

A recorded new-game session ran for approximately **49.5 minutes** and exited normally. A separate **save → restart → reload** test also succeeded.

**Full-game compatibility is not yet verified.** A complete start-to-credits playthrough has not been performed. See [STATUS.md](STATUS.md) and the [compatibility report](docs/phase6-compatibility.md) for the tested scope and known issues.

## Implementation

HP1Recomp uses static recompilation through PSXRecomp. The game's `SLUS_014.15` and `US.GAM` executables are handled by independent generated native-code providers sharing the runtime. PS1Recomp is also available as an auxiliary tool.

The current framework revisions are recorded in [config/framework-pins.json](config/framework-pins.json).

## Documentation

- [Build instructions](docs/build.md)
- [Project status](STATUS.md)
- [Roadmap](ROADMAP.md)
- [Phase 7 work](docs/phase7-fidelity.md)
- [Release notes](RELEASE_NOTES.md)
- [Contributing](CONTRIBUTING.md)

## Game data

**The original game is not included.** HP1Recomp does not distribute disc images, retail executables, extracted game assets or other commercial game data. A legitimately obtained copy of the supported game is required.
