# HP1Recomp Roadmap

This roadmap describes the current development path. It is expected to change as the game reveals its actual technical constraints.

## Phase 0 — Repository and environment

Goal: establish a reproducible Windows development environment and a clean project repository.

Tasks:
- initialize the GitHub repository
- establish branch conventions
- install or verify Git, Python, CMake, Ninja and compiler toolchain
- install reverse-engineering/debugging tools
- clone/pin recompilation frameworks as appropriate
- confirm that copyrighted game material is excluded by `.gitignore`

Exit criteria:
- a clean checkout can reproduce the development environment with documented steps
- `main` contains only project-owned/configuration/documentation material

## Phase 1 — Known-title recompilation smoke test

Goal: prove that the local PSXRecomp workflow works before debugging Harry Potter-specific problems.

Preferred reference: **Tomba!** if an appropriate legitimate copy is available.

Tasks:
- use an already-supported/reference title
- run the documented generation/build pipeline
- produce a native Windows executable
- launch and confirm basic gameplay
- record exact tool versions and commands that worked

Exit criteria:
- one known title successfully generates, compiles and launches on the same machine intended for HP1Recomp work

This phase is deliberately short. It is a toolchain test, not a side project.

## Phase 2 — Canonical HP1 disc identification

Goal: establish an exact, reproducible identity for the initial `SLUS-01415` source disc.

Tasks:
- extract the source archive without modifying its contents
- identify BIN/CUE layout and tracks
- compute CRC32 / MD5 / SHA-1 / SHA-256 for the disc image files
- extract the disc filesystem
- identify and hash `SLUS_014.15`
- identify and hash `POTTER.DAT` and `POTTER.DIR`
- record `SYSTEM.CNF` boot information
- record sizes and disc layout
- create a local disc-identification script where useful

Exit criteria:
- the initial source build can be identified unambiguously from hashes and metadata
- no retail data is committed to Git

## Phase 3 — Executable reconnaissance

Goal: understand enough of the PS-X executable to support recompilation bring-up.

Status: **complete (2026-10-01)**. The two executables have documented memory maps and loading relationships; reusable Ghidra export and Strategy seeds exist; PS1Recomp supplied an independent function/library inventory; the main dispatch tables are resident and bounded; and the remaining overlay, mixed-PsyQ and self-modifying-code risks are explicit. This completion does not claim native compatibility. See [the Phase 3 closure record](docs/phase3-reconnaissance.md).

Tasks:
- load `SLUS_014.15` in Ghidra using PS1-aware tooling
- map entry point, text/data/BSS and obvious tables
- identify BIOS/PsyQ usage where possible
- inspect strings and file references
- determine whether the title appears to load executable overlays or other dynamic MIPS code
- evaluate PS1Recomp analysis output as a secondary source
- begin a function/symbol knowledge base with confidence levels

Exit criteria:
- basic executable memory map documented
- major unknowns affecting recompilation identified
- initial seeds/symbol information available for bring-up

## Phase 4 — HP1Recomp project scaffold

Goal: create the smallest maintainable project capable of attempting HP1 generation/build.

Status: **complete (2026-10-01)**. The repository pins PSXRecomp as a submodule, records the canonical disc identity in `game.toml`, carries KSEG0-normalized boot seeds and an evidence-based symbol file, generates four C shards plus a 227-entry dispatch table for `SLUS_014.15`, and configures the minimal OpenBIOS/SDL3 runtime. Retail and generated files remain ignored. `US.GAM` is deliberately left for safe runtime interpretation until its KUSEG secondary-image path is supported and validated; no native build or launch is claimed. See [the Phase 4 closure record](docs/phase4-scaffold.md).

Tasks:
- add the selected recompilation framework as a pinned dependency/submodule if appropriate
- create game configuration for `SLUS-01415`
- create generation/build scripts
- add local paths through environment/configuration rather than hard-coding retail data locations
- ensure generated/copyright-sensitive output is ignored
- document one-command or minimal-command build workflow where practical

Exit criteria:
- project generation can be attempted from a clean checkout plus locally supplied game data

## Phase 5 — First native bring-up

Goal: move through increasingly meaningful execution milestones.

Status: **complete (2026-10-01)**. Generation, native Release compilation, process/window startup, runtime initialization and disc/executable-chain loading succeeded. A manual native run then validated the Warner/EA sequence, language and title screens, new-game flow, opening movie, first playable scene, movement, pause and conversation with Dumbledore. See [the Phase 5 closure record](docs/phase5-bringup.md).

Milestones:

- M5.1 — generation succeeds (**completed during the Phase 4 verification run**)
- M5.2 — native project compiles (**complete 2026-10-01**)
- M5.3 — process starts / window opens (**complete 2026-10-01**)
- M5.4 — runtime initializes (**complete 2026-10-01**)
- M5.5 — disc access works (**complete 2026-10-01**)
- M5.6 — publisher/developer boot sequence appears (**complete 2026-10-01**)
- M5.7 — main menu is reachable (**complete 2026-10-01**)
- M5.8 — new game starts (**complete 2026-10-01**)
- M5.9 — first playable area loads (**complete 2026-10-01**)
- M5.10 — basic gameplay works (**complete 2026-10-01**)

Phase 5 execution begins at M5.2 because the scaffold verification reached M5.1 without performing a native compilation or launch. Milestone numbering is retained so earlier plans and reports remain comparable.

Every failure should be reduced to a reproducible case and documented in `STATUS.md` or a focused issue/branch.

## Phase 6 — Extended compatibility validation

Goal: establish that the native build supports sustained, representative normal play beyond initial bring-up.

Status: **complete (2026-10-11)**. A 49.5-minute new-game session exercised story scenes, lessons, combat, saving and repeated indoor/outdoor transitions at an average 59.79 guest frames/s, then exited normally. Save/restart/load, the exact-segment KUSEG provider, the post-Warner fix and exact fallback for both known live-code writes are validated. Known deviations and the untested full route remain explicit rather than being converted into unsupported compatibility claims. See [the Phase 6 closure record](docs/phase6-compatibility.md).

Subsystems to validate:
- controller input
- rendering
- level loading and transitions
- animation
- actor behavior
- sound effects
- streamed/level audio
- FMV/MDEC behavior
- CD-ROM access and timing-sensitive behavior
- memory card / saves
- pause/menu flows
- game-over/retry flows
- ending / credits

Exit criteria:
- an extended representative route runs without a fatal condition or automatic freeze
- save, process restart and reload behavior are usable and stable
- repeated room/loading transitions and core audiovisual/input paths work on the tested route
- no known blocker prevents continued play on that route
- known deviations and untested coverage are documented explicitly

## Phase 7 — Fidelity, regression and release hardening

Goal: make correctness measurable and produce the first reproducible release-quality Windows package.

Status: **in progress (started 2026-10-11)**. The starting baseline is the closed Phase 6 build and its preserved 49.5-minute session. Initial targets are the display-centering flicker, analog sensitivity, diagnostic-wrapper gaps and regression coverage for the already fixed presentation and live-code paths. A complete playthrough remains valuable release validation but is not a gate for this engineering phase.

Testing may include:
- repeatable input scripts
- screenshot comparisons
- framebuffer/VRAM comparison
- memory/state snapshots where technically useful
- save-file comparisons
- deterministic checkpoints
- targeted traces around known timing or logic problems

The project does not need to compare every byte of RAM on every frame to be useful. Differential testing is a debugging and verification tool to be applied where it provides value.

Exit criteria:
- important gameplay paths have repeatable regression checks
- previously fixed critical bugs are protected against recurrence
- observed Phase 6 deviations are fixed or explicitly classified with documented workarounds/limitations
- a clean checkout plus legitimate canonical game data produces a verified distributable Windows package
- release notes state the tested boundary without claiming an unperformed full playthrough

### First complete release milestone

The first useful project release follows Phase 7. Phases 8 and 9 are continued reverse-engineering and modding tracks; they improve the project after the faithful native baseline exists and do not block that first release.

## Phase 8 — Structured reverse engineering

Goal: progressively replace anonymous behavior with documented systems.

Tasks:
- maintain function/symbol database
- compare HP1 with HP2 where functions/structures are related
- use Croc/Croc 2/decomp symbols only when evidence supports a relationship
- document asset, actor, level and scripting systems
- identify clean boundaries for native hooks or C/C++ replacement
- mark findings with confidence rather than treating guesses as facts

Possible progression:

```text
FUN_800xxxxx
    ↓
probable subsystem identification
    ↓
confirmed semantic name
    ↓
documented inputs/state/callers
    ↓
optional clean native implementation
```

## Phase 9 — Modding foundation

Goal: make future modifications possible without compromising the vanilla baseline.

Potential work, only after the base is stable:
- data/file overrides
- patch/hook support
- asset replacement workflows
- documented stable hook points
- optional plugin/mod interfaces
- level/actor tooling as reverse engineering allows

A future mod API must be designed from actual knowledge of the engine, not invented prematurely.

## Long-term possibility — partial or full traditional decompilation

A complete matching decompilation is not a prerequisite for HP1Recomp.

Over time, sufficiently understood functions may be reconstructed in clean C/C++ and validated against the original MIPS behavior. If the project ever reaches broad source reconstruction, that work can coexist with or gradually replace automatically recompiled functions.
