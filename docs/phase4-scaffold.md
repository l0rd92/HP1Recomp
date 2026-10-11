# Phase 4 project scaffold

Phase 4 created the smallest maintainable HP1 PSXRecomp project capable of attempting generation from a clean checkout plus locally supplied canonical game data. It closed on 2026-10-01. Operational commands remain in [build.md](build.md).

## Result

| Exit criterion | Result |
|---|---|
| Framework pinned | PSXRecomp submodule at `1ec24e9d4915770a313e4fc19fad5430f55b00a2` |
| Canonical input gated | Track 01 identity verified through `game.toml` |
| Project inputs created | CMake, game configuration, symbols and boot seeds |
| Generation attempted | Successful for `SLUS_014.15` |
| Minimal runtime configured | Successful with OpenBIOS, SDL3, one player and UI/netplay disabled |
| Retail/generated data excluded | Verified through ignored local directories and repository status |

The phase intentionally stopped before native compilation or launch. Those are Phase 5 milestones.

## Repository-owned scaffold

| Artifact | Purpose |
|---|---|
| `psxrecomp/` | Pinned framework submodule |
| `game.toml` | Canonical disc identity and boot-image generation configuration |
| `CMakeLists.txt` | Minimal native runtime configuration |
| `symbols.toml` | Evidence-based project symbols |
| `seeds/hp1-boot-jal.txt` | 175 normalized boot function roots |
| `config/framework-pins.json` | Auditable framework revision record |
| `docs/build.md` | Reproduction and bring-up commands |

At Phase 4 closure the submodule and recorded upstream pin were both `1ec24e9d4915770a313e4fc19fad5430f55b00a2`. Phase 6 later advanced the active submodule to the project fork revision recorded as `commit` in `config/framework-pins.json`, while retaining the Phase 4 revision there as `upstream_base_commit` for provenance.

## Verified generation checkpoint

| Check | Result |
|---|---|
| Disc verification | Canonical main track accepted |
| Boot seeds loaded | 175 of 175 |
| Functions generated | 227 |
| Generated C | Four shards; 138,426 lines reported by the emitter |
| Dispatch table | 227 entries |
| Code-range manifest | Generated |
| CMake configure | Passed |
| Native compile / launch | Not attempted |

The framework selected portable toolchain `cmake-clang-v1` version `1.0.14` and compiled the `psxrecomp-game` and `psxrecomp-bios` emitters. The first recovered JAL roots used raw KUSEG aliases; normalizing them to KSEG0 caused all 175 to be accepted without changing the emitted function set.

Local `disc/`, `generated/`, `build-phase4/` and `toolchain/` contents are ignored and were not committed.

## Secondary-image boundary

The scaffold statically recompiles only `SLUS_014.15`. `US.GAM` declares KSEG0 load/entry values (`0x80010000` and `0x8005B2C8`) in its original header, while the boot program executes the loaded image through the KUSEG aliases `0x00010000` and `0x0005B2C8`. The Phase 4 scaffold therefore did not force the secondary image through the single-image AOT path or modify its original header.

The initial Phase 5 strategy is to let the secondary image enter through the runtime's safe interpreted or dirty-RAM path, then verify registration, execution and both known live instruction writes. Native secondary-image support may be added only after the framework-compatible behavior is demonstrated.

## Closure boundary

Phase 4 is complete because a clean checkout can initialize the pinned dependency, verify locally supplied canonical data, generate the boot program and configure the minimal runtime. It does not claim that the runtime compiles, starts, reaches `US.GAM` or displays gameplay. Those claims require Phase 5 evidence.
