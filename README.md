<p align="center">
  <img src="docs/assets/hp1recomp-logo.png" alt="HP1 Recomp" width="640">
</p>

<p align="center">
  <strong>Native recompilation of <em>Harry Potter and the Sorcerer's Stone</em> for Windows.</strong>
</p>

<p align="center">
  <img alt="Windows x64" src="https://img.shields.io/badge/Windows-x64-0078D4?style=for-the-badge&logo=windows11&logoColor=white">
  <img alt="PSXRecomp" src="https://img.shields.io/badge/Framework-PSXRecomp-C79A2B?style=for-the-badge">
  <img alt="SLUS-01415" src="https://img.shields.io/badge/Reference-SLUS--01415-2EA44F?style=for-the-badge">
  <img alt="Phase 7" src="https://img.shields.io/badge/Phase%207-Release%20Hardening-6F42C1?style=for-the-badge">
</p>

<p align="center">
  <a href="STATUS.md">Status</a> •
  <a href="ROADMAP.md">Roadmap</a> •
  <a href="RESEARCH.md">Research</a> •
  <a href="docs/build.md">Build</a> •
  <a href="docs/phase6-compatibility.md">Compatibility</a> •
  <a href="docs/phase7-fidelity.md">Release hardening</a>
</p>

---

> [!IMPORTANT]
> **HP1Recomp is still in development.** Phases 0–6 are complete and Phase 7 release hardening is active. The tested native route includes a stable 49.5-minute new-game session, repeated indoor/outdoor transitions and working save/restart/reload. A complete playthrough is **not** claimed.

## ✨ At a glance

| | |
|---|---|
| **Game** | Harry Potter and the Sorcerer's Stone |
| **Original platform** | Sony PlayStation |
| **Reference build** | USA / NTSC-U — `SLUS-01415` |
| **Languages** | English / French / Spanish |
| **Initial host** | Windows x64 |
| **Primary framework** | [PSXRecomp](https://github.com/RetroPortingToolKit/psxrecomp) |
| **Auxiliary analysis** | [PS1Recomp](https://github.com/PS1Recomp/ps1-recomp) |
| **Current phase** | **Phase 7 — Fidelity, regression and release hardening** |
| **Project goal** | Native Windows version of the original PS1 game |

## 🎮 Current compatibility

| Area | State | Current evidence |
|---|:---:|---|
| Boot / BIOS / disc chain | ✅ | Native Release build reaches the game correctly |
| Language selection / title | ✅ | Three-language selector and title flow work |
| New game / opening route | ✅ | Opening sequence and early story progression work on the tested path |
| Basic gameplay / input | ✅ | Movement, pause and conversations validated |
| Memory-card creation | ✅ | Local PS1 memory cards are created and detected |
| Save / restart / reload | ✅ | Real progress save survives process restart and reloads correctly |
| Extended tested route | ✅ | Lessons, combat and repeated indoor/outdoor transitions validated |
| Warner → EA transition | ✅ | Previously observed RGB corruption is fixed on the validated path |
| Streamed audio timing | ⚠️ | Earlier intermittent slowdown remains under observation |
| Major later-game boundaries | ⏳ | Not yet broadly validated |
| Full playthrough | ➖ | Not performed; retained as later release validation |

Detailed evidence and limitations live in [`docs/phase6-compatibility.md`](docs/phase6-compatibility.md).

## ⚡ How the project fits together

```text
Your original PS1 copy
          │
          ▼
   Disc verification
          │
          ▼
 SLUS_014.15 + US.GAM
          │
          ▼
   Code analysis
          │
          ▼
      PSXRecomp
          │
          ▼
 Native Windows build
          │
          ▼
 Compatibility testing
          │
          ▼
 Native Windows version
```

HP1Recomp starts with **static recompilation**, not a requirement for a complete traditional source decompilation. Original MIPS code can run as native generated code while code analysis helps identify systems, functions and potential C/C++ replacements.

## 🧭 Roadmap

**✅ Phase 0** → **✅ Phase 1** → **✅ Phase 2** → **✅ Phase 3** → **✅ Phase 4** → **✅ Phase 5** → **✅ Phase 6** → **🔵 Phase 7** → **⏳ Phase 8** → **⏳ Phase 9**

| Phase | Focus | State |
|---:|---|:---:|
| 0 | Repository & environment | ✅ |
| 1 | Known-title recompilation smoke test | ✅ |
| 2 | Canonical HP1 disc identification | ✅ |
| 3 | Executable reconnaissance | ✅ |
| 4 | HP1Recomp project scaffold | ✅ |
| 5 | First native bring-up | ✅ |
| 6 | Extended compatibility validation | ✅ |
| **7** | **Fidelity, regression & release hardening** | **🔵 Active** |
| 8 | Further analysis | ⏳ |
| 9 | Later development | ⏳ |

See [`ROADMAP.md`](ROADMAP.md) for the actual exit criteria and phase details.

## 🎯 Project goals

- **Faithful native Windows recompilation** of the original PS1 game.
- Preserve **original gameplay behavior** before adding enhancements.
- Build from evidence gathered from the real game rather than locking in early assumptions.
- Keep the codebase maintainable for ongoing development.
- Maintain strict separation between the project and **commercial game data**.
- Prefer root-cause fixes over permanent diagnostic hacks.

## 🖼️ Screenshots

Native screenshots will be added from validated HP1Recomp runs as compatibility testing progresses. Mock gameplay images are intentionally not used here.

<!--
Future layout:

<table>
  <tr>
    <td><img src="docs/assets/screenshots/boot.png" alt="Boot" width="100%"></td>
    <td><img src="docs/assets/screenshots/title.png" alt="Title screen" width="100%"></td>
    <td><img src="docs/assets/screenshots/gameplay.png" alt="Gameplay" width="100%"></td>
  </tr>
  <tr>
    <td align="center"><b>Boot / Intro</b></td>
    <td align="center"><b>Title Screen</b></td>
    <td align="center"><b>Native Gameplay</b></td>
  </tr>
</table>
-->

## 🛠️ Built with PSXRecomp

HP1Recomp currently uses a project-pinned fork of [PSXRecomp](https://github.com/RetroPortingToolKit/psxrecomp) as its primary static recompilation framework. [PS1Recomp](https://github.com/PS1Recomp/ps1-recomp) remains an auxiliary analysis/recompilation source where its tooling is useful.

The current HP1 architecture includes two independently generated executable providers:

```text
SLUS_014.15  ─┐
              ├─► composite native dispatch ─► PSXRecomp runtime
US.GAM KUSEG ─┘
```

The unusual `US.GAM` KUSEG execution path is handled without pretending KUSEG code is KSEG0 code. Exact live-code guards remain active for the known self-modifying instruction sites.

For the exact pinned revisions, see [`config/framework-pins.json`](config/framework-pins.json).

<details>
<summary><strong>🔧 Development toolchain and research references</strong></summary>

### Recompilation / runtime
- PSXRecomp
- PS1Recomp

### Code analysis
- Ghidra
- ghidra_psx_ldr
- PCSX-Redux
- DuckStation

### Disc tooling
- dumpsxiso
- mkpsxiso

### Argonaut / game-family references
- Harry Potter and the Chamber of Secrets (PS1)
- Croc: Legend of the Gobbos
- Croc European demo `SLED-00038`
- Croc 2
- Disney's Aladdin in Nasira's Revenge
- Tomba!
- Selected PSXRecomp game projects when a concrete implementation comparison is useful

### Development
- Git / GitHub
- Python
- CMake
- Ninja
- MSYS2 MinGW64 GCC/G++

</details>

## 📚 Project documentation

| Document | Purpose |
|---|---|
| [`STATUS.md`](STATUS.md) | Current state, evidence boundary and immediate next actions |
| [`ROADMAP.md`](ROADMAP.md) | Development phases and exit criteria |
| [`RESEARCH.md`](RESEARCH.md) | Technical findings and unresolved questions |
| [`docs/design-decisions.md`](docs/design-decisions.md) | Durable architecture and project decisions |
| [`docs/phase3-reconnaissance.md`](docs/phase3-reconnaissance.md) | Executable reconnaissance closure |
| [`docs/phase4-scaffold.md`](docs/phase4-scaffold.md) | Initial recompilation scaffold |
| [`docs/phase5-bringup.md`](docs/phase5-bringup.md) | First native bring-up |
| [`docs/phase6-compatibility.md`](docs/phase6-compatibility.md) | Extended compatibility closure and evidence |
| [`docs/phase7-fidelity.md`](docs/phase7-fidelity.md) | Active fidelity, regression and release-hardening plan |
| [`docs/build.md`](docs/build.md) | Generation and build workflow |
| [`docs/environment.md`](docs/environment.md) | Verified development environment |

## ⚖️ Legal / repository policy

**HP1Recomp does not include the original game.**

This repository must not contain copyrighted retail game data. In particular, do **not** commit:

- BIN / CUE disc images
- extracted retail assets
- `POTTER.DAT` / `POTTER.DIR`
- original PS-X executables
- other commercial game content

Developers and, eventually, players must provide their own legitimately obtained game data where required.

---

<p align="center">
  <strong>HP1Recomp</strong><br>
  Native Windows • PlayStation • SLUS-01415
</p>
