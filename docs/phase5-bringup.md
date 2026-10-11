# Phase 5 native bring-up

Phase 5 began and completed on 2026-10-01. This document records native compilation and progressively meaningful execution through the first playable area. It does not imply full-game compatibility beyond the milestones explicitly validated.

## Milestones

| Milestone | Status | Evidence |
|---|---|---|
| M5.1 — generation succeeds | Complete | Achieved during Phase 4: 227 boot functions, four C shards and a 227-entry dispatch table |
| M5.2 — native project compiles | Complete | Release/Ninja build completed all 149 steps and linked the Windows executable |
| M5.3 — process starts / window opens | Complete | Correctly titled window remained responsive for the bounded 15-second test |
| M5.4 — runtime initializes | Complete | Configuration, OpenBIOS, OpenGL renderer, text guard and scheduler initialized |
| M5.5 — disc access works | Complete | Execution reached generated `SLUS_014.15` and subsequently the loaded `US.GAM` image |
| M5.6 — publisher/developer boot sequence appears | Complete | Warner and EA logos displayed with working audio |
| M5.7 — main menu is reachable | Complete | Language selection and title screen worked |
| M5.8 — new game starts | Complete | New game began after declining memory-card creation |
| M5.9 — first playable area loads | Complete | Intro completed and the Dumbledore scene loaded |
| M5.10 — basic gameplay works | Complete | Movement, pause menu and conversation with Dumbledore worked |

## M5.2 build checkpoint

The previously configured `build-phase4` tree was built with the pinned `cmake-clang-v1` 1.0.14 toolchain. The build compiled the framework runtime, OpenBIOS and all four generated `SLUS_014.15` shards, then linked:

`build-phase4/Harry_Potter_and_the_Sorcerer_s_Stone_Recompiled.exe`

| Property | Value |
|---|---|
| Size | 12,817,408 bytes |
| SHA-256 | `05489444631AE573C13EE34836844752A852AE269E411F92410E8B28D49883CC` |
| Build result | Success |
| Launch performed | No |

Compiler warnings were confined to the pinned framework and dependencies: comment-token warnings, format truncation, deprecated literal-operator spacing and a resource-preprocessor warning caused by the apostrophe in the window title. None prevented linking. Their runtime significance, if any, is not established.

## M5.3–M5.4 launch checkpoint

A controlled 15-second launch created a window titled `Harry Potter and the Sorcerer's Stone Recompiled`; the process remained running until deliberately terminated by the test. Runtime output confirmed:

- `game.toml` loaded for `SLUS-01415`
- OpenBIOS loaded and execution started at `PC=0xBFC00000`
- OpenGL 3.3 core context and GPU pipeline initialized
- the local boot text guard armed for `0x00100000–0x0010D800`
- the deterministic HLE thread scheduler initialized
- the local disc identity was recognized as NTSC-U / `SLUS-01415`

The test also reported that no bundled overlay TCC toolchain was present, so overlay gaps would fall back to the interpreter. That is consistent with the initial safe bring-up plan and is not yet evidence that `US.GAM` executes correctly.

The runtime wrote `keybinds.ini`, `overlay_captures.json` and bounded stdout/stderr logs inside the ignored build tree. No repository-owned or retail files changed.

## M5.5 disc and executable-chain checkpoint

The initial stdout-only diagnosis incorrectly treated the absence of later log messages as absence of VBlank or disc access. A temporary environment-gated PC sampler established the actual execution state without altering guest behavior:

- frame 85: generated boot code at `PC=0x801008A0`
- frames 115–236: scheduler/BIOS transitions with published `PC=0`
- frame 265: main-game code at `PC=0x0005B7D8`, with `RA=0x0005B6CC`

Reaching the generated boot address proves that OpenBIOS completed enough of the disc boot path to enter `SLUS_014.15`. Reaching a resident address inside the independently identified `US.GAM` image then proves that the boot executable loaded and transferred execution to the secondary game image. M5.5 is therefore complete.

The PC sampler was removed immediately after the bounded capture and the runtime was rebuilt successfully from the clean pinned submodule. No diagnostic source change remains.

The clean post-diagnostic executable is 12,817,408 bytes with SHA-256 `A0C410DD0A93BDCE61BE83D4BBCEC8C71D855D29A1039B5AFEA238598E2D7670`. Its hash differs from the initial successful build because the Windows link is not treated as reproducible evidence; source cleanliness and behavior, rather than binary identity across rebuilds, are the acceptance criteria.

## M5.6–M5.10 manual gameplay checkpoint

A controlled manual run of the clean native executable confirmed:

- Warner and EA logos appeared and advanced normally
- video and audio were present throughout the boot sequence
- language selection accepted controller input and Spanish was selected
- the title screen appeared and a new game started
- declining memory-card creation continued into the opening movie
- the opening movie rendered and played audio correctly
- the post-intro scene loaded with Dumbledore and Harry
- player movement, directional input, the pause menu and conversation with Dumbledore worked

This run establishes the complete Phase 5 bring-up ladder through basic gameplay. It does not validate saving, extended play, every audiovisual path, level transitions or full-game completion. Those belong to Phase 6.

## Closure boundary

Phase 5 is complete because the generated native project compiles, starts, initializes its runtime, reads the canonical disc, loads the boot and secondary executables, reaches the menu, starts a new game and provides basic playable interaction. Known static risks—including live instruction writes and secondary-image fallback behavior—remain explicit Phase 6 validation targets even though they did not prevent this first successful run.
