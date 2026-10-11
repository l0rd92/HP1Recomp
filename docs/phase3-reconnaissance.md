# Phase 3 executable reconnaissance

Phase 3 established the executable and runtime facts needed to begin a bounded HP1 recompilation bring-up. It closed on 2026-10-01. This document is the concise closure record; [RESEARCH.md](../RESEARCH.md) preserves the detailed evidence and chronological investigation.

## Result

| Exit criterion | Result |
|---|---|
| Executable memory maps documented | Complete for `SLUS_014.15` and `US.GAM` |
| Loading relationship established | Confirmed statically and observed dynamically |
| Recompilation risks identified | Secondary KUSEG image, live instruction writes, mixed PsyQ lineage and possible non-headered code |
| Initial seeds and symbols available | Ghidra inventories, boot JAL roots and confirmed Strategy symbols |

Phase 3 did not establish native compatibility. It produced bounded evidence and reusable inputs for the scaffold and bring-up phases.

## Executable layout and loading chain

| Image | Header load range | Entry point | Role |
|---|---:|---:|---|
| `SLUS_014.15` | `0x00100000–0x0010D800` | `0x00103DDC` | Disc boot executable |
| `US.GAM` | Header: `0x80010000–0x80079000`; observed execution: `0x00010000–0x00079000` | Header: `0x8005B2C8`; observed execution: `0x0005B2C8` | Main game executable loaded by the boot program |

The boot executable opens `US.GAM`, loads its PS-X EXE image and transfers control through the normal `Load`/`Exec` path. PCSX-Redux tracing confirmed this sequence. The raw header is linked in cached KSEG0 (`0x800...`), but the boot path enters the same physical RAM through KUSEG (`0x000...`). Because MIPS `J`/`JAL`, `$ra`, EPC and instruction-cache behavior retain architectural segment information, native code must be emitted for the observed KUSEG execution addresses rather than treating the two aliases as interchangeable.

## Confirmed bring-up risks

| Area | Confirmed evidence | Boundary |
|---|---|---|
| Secondary executable | `US.GAM` is loaded after boot and contains most game code | Its header is KSEG0 but the boot program enters it through KUSEG; native generation must preserve the observed execution segment without modifying the retail file or treating aliases as equivalent |
| Live instruction writes | Words at `0x00056388` and `0x00057F20` change from `0x240B00EF` to `0x240B0180`, in that order | Native execution must respect the framework's dirty/live-text fallback; HP1-specific behavior remains a Phase 5 validation |
| Dynamic code | No additional standalone executable or PS-X EXE header was found in the inspected filesystem or `POTTER.DAT` | Raw, compressed or constructed MIPS code cannot be excluded until broader execution |
| PsyQ | Component signatures indicate mixed lineage, including libcd 4.4/4.6, modern libgpu 4.3+ and some libgte 3.3 | No exact single SDK release is claimed |

## Static inventories and dispatch evidence

Read-only Ghidra exports from the saved projects recorded:

| Program | Functions | Call references | Total references | Memory blocks |
|---|---:|---:|---:|---:|
| `SLUS_014.15` | 404 | 556 | 4,588 | 26 |
| `US.GAM` | 1,206 | 3,414 | 30,932 | 26 |

PS1Recomp supplied an independent inventory of 227 boot functions and 1,593 main-game functions, including 57 and 103 PsyQ identifications respectively. Differences between analyzers are expected and are not semantic completeness claims.

Three resident main-game dispatch tables at `0x0006AF7C`, `0x0006AFB8` and `0x0006AFF4` each contain 15 valid targets inside `US.GAM`. The complete 45-target set is statically bounded. A later Phase 6 saved-reference inventory proved that every known direct producer preserves an index from 0 through 14; unresolved indirect writes and corruption remain dynamic validation concerns.

## Strategy virtual machine

The main Strategy interpreter is at `US.GAM` address `0x00036EBC`. It consumes 32-bit instructions, uses the low 16-bit opcode and dispatches through two handler regions. HP2 contains the confirmed shared implementation at `0x0003C1BC`; Aladdin contains a related earlier variant. Croc uses a different byte-indexed 256-entry design and is a lineage reference, not proof of identical HP1 behavior.

Seventeen HP1 handler names and local semantics are confirmed in `seeds/hp1-us-strategy.map`. Bounded traversal of `T1I0M000.WAD` found five actor roots, 1,149 reachable instructions and 1,279 control-flow edges. Embedded names identify `LevelSetup`, `TitleScreenCamera`, `MusicStreamer` and `StreamBox`; the fifth root remains unnamed. These names describe the embedded Strategy programs, not complete native subsystems.

## Runtime observations

PCSX-Redux established the boot-to-main transition, both live instruction writes and selected Strategy paths. A manual reference run reached language selection, title and the opening story sequence. Menu audio worked, the EA logo audio was degraded, and the first story page animated with subtitles but did not advance or produce narration. The EA movie and storybook observations are separate: `MOVIES/EA.STR` is a standalone pre-menu stream, while the storybook uses 64 `STORY*.IMG` archive entries.

The cause of the story behavior remains unknown. CD-ROM/XA timing, narration source and event-level audiovisual synchronization require targeted dynamic validation; the observation is not a confirmed game bug or recompiler diagnosis.

## Reusable project evidence

- `tools/ghidra/ExportProgramFacts.java` — read-only functions, symbols, calls, references and memory maps
- `tools/ghidra/ExportSelectedFunctions.java` — bounded function export
- `tools/ghidra/ImportLinkerMap.java` — exact-build map import
- `tools/inspect_dpsx.py` — bounded single-WAD or archive-index Strategy traversal without retail extraction; breadth-first root scheduling, reported recursive-context pruning, a configurable state ceiling and a context-insensitive selected-opcode upper bound keep unresolved layouts and truncation explicit
- `tools/pcsx-redux/trace_hp1_strategy.lua` — bounded reference-runtime tracing
- `seeds/hp1-boot-jal.txt` — boot generation roots
- `seeds/hp1-us-strategy.map` — confirmed Strategy symbol seed

Generated reports remain local. The latest provisional report and logs from the latest three executions are retained; unique evidence is preserved separately and is not automatically deleted.

## Closure boundary

Phase 3 is complete because the executable relationship, core memory maps, principal dynamic-code risks and initial machine-readable knowledge base are sufficient for a controlled scaffold and bring-up attempt. Open questions are carried forward as validation targets, not as reasons to reopen the phase automatically.
