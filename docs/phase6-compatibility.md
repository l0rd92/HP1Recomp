# Phase 6 — Extended compatibility validation

Status: **complete (2026-10-11)**
Started: 2026-10-01

## Scope and exit criteria

Phase 6 validates sustained representative play on the canonical `SLUS-01415` build beyond initial bring-up. It requires usable save/restart/load behavior, repeated transitions, broad early-route subsystem coverage and explicit documentation of remaining deviations. A complete start-to-credits playthrough is valuable release validation but is not a Phase 6 gate; no untested route is claimed compatible.

## Current compatibility matrix

| Area | Status | Evidence and boundary |
|---|---|---|
| Boot, language and title flow | Pass | Native Release build reaches the three-language selector and title screen. The MDEC-released presentation guard removes the post-Warner corruption while preserving visible EA playback. |
| New game and early story route | Pass with intermittent deviation | A 49.5-minute run progressed through story scenes, lessons, combat and outdoor castle areas. Earlier runs showed EA/transition slowdown, so repeat timing observation remains necessary. |
| Basic input/gameplay | Pass | Cross and directional input, movement, pause and conversation with Dumbledore work. |
| Memory-card creation | Pass | A clean run created a card, accepted slot selection and continued normally. |
| Save and reload | Pass with minor pause | A real progress save on the common-room route survived process restart and loaded at the saved position through a visible loading screen with moving progress bar; card check/load each showed a brief sub-second pause. |
| Room/area transitions | Pass for extended early route | Repeated doors, loading screens and indoor/outdoor transitions completed normally through the captured 49.5-minute route. Later story and level boundaries remain untested. |
| Automated pinned-build smoke | Pass | A fresh 15-second headless run reached 2,089 frames, identified `SLUS-01415`, armed both executable text-image guards and produced no fatal condition or automatic freeze dump. |
| Full playthrough | Not performed | Retained as later release validation; no compatibility claim is made beyond the tested route. |
| Streamed audio timing | Failing intermittently | Reproducible host-performance starvation is described below. |
| Display centering | Failing when shifted downward | Moving vertical centering downward produces persistent flicker until the setting is restored. Root cause and original-hardware comparison are pending. |
| Analog input | Usable with deviation | DualSense digital input works; left-stick movement was reported as excessively sensitive. Deadzone/mapping diagnosis is pending. |

## Memory-card checkpoint

The native runtime created `card1.mcd` and `card2.mcd` as 131,072-byte local files. The tested flow detected the card, allowed a slot to be selected and continued into the opening sequence without a visible fault. Play then crossed several rooms, conversations and automatic story scenes before saving on the route to the common room. A later run closed and restarted the runtime, found the existing save, displayed a loading screen with a moving progress bar and restored that position. Brief sub-second pauses occurred during card checking and loading; no corruption or loss was observed in this single cycle.

Retail-independent hashes were recorded locally for comparison, but memory-card contents remain ignored runtime data and are not committed.

## Closure

Phase 6 closes on the preserved 49.5-minute session and the cumulative automated/runtime evidence below. The build sustained a new-game route through story scenes, lessons, combat, saving and repeated indoor/outdoor transitions; save/restart/load had already been validated independently. It exited normally with no fatal report, automatic freeze dump, unsupported mid-block instruction or diagnostic trip. Known visual, input and intermittent timing deviations remain Phase 7 work. This closure establishes representative compatibility, not full-game completion.

## Extended 2026-10-11 play session

The instrumented desktop build ran for 49 minutes 30 seconds from a new-game flow and exited normally through the SDL window close path at frame 177,588. The average guest cadence over wall time was 59.79 frames/s. Twenty-four automatic screenshots show continued progress through the menu, card selection, story/card presentation, multiple indoor areas, lessons, combat and outdoor castle areas. The tester reported working doors, loading screens, voices, videos, card collection and saving. `card1.mcd` was updated 16 seconds before shutdown.

The final report records no unsupported mid-block instruction, diagnostic trip, fatal condition or automatic freeze dump. Guest stack sampling remained at a maximum of 8 KiB and the companion control-exception profile reached 9 KiB. The diagnostic connection recorded no TCP stall or dropped client. The empty numeric exit-code field in the wrapper summary is a collection defect; the runtime's own report identifies a normal `atexit` caused by `sdl_window_close`.

Five executable-region captures were retained locally. The `0x80030000` image is byte-identical to canonical `US.GAM` and is therefore a KSEG0 alias rather than a new overlay. The `0x80057000` and `0x8006A000` captures lie inside the same retail image but contain live differences; the former includes the known modified-code page containing `0x80057F20`. The two low-RAM captures are also classified rather than new game overlays. Code executed at `0x8000281C` is an exact 16-byte match for OpenBIOS ROM offset `0x76F4` and saves exception context. Entries at `0x8000357C` and `0x8000DFAC` exactly match `US.GAM` file offsets `0x5B184` and `0x5B140`, corresponding to the imported PsyQ `_patch_card`/`PATCH_OBJ_B4` area; `_patch_card` writes the low-RAM continuation at `0x0000DFFC`. These are BIOS and memory-card patch handlers copied into low RAM, not evidence of streamed level code. The complete session is preserved outside the rotating playtest directory under local evidence storage and is not committed because it contains retail-derived bytes.

Three user-visible deviations remain separate pending diagnoses. Moving the screen-centering option downward causes persistent flicker until restored. DualSense left-stick movement feels substantially more sensitive than digital-pad movement. One spell-learning prompt appeared clipped even with centering restored, although a later automatic capture shows a similar four-button prompt fully inside the viewport; this may be scene-specific, intermittent or original behavior and is not classified yet. The card-creation pause was not timed and was reported as comparable to earlier runs, so it is not evidence of a regression.

## Audio/performance diagnosis

Release runtime telemetry used the existing `PSX_RUNTIME_PERF_DIAG` facility at two-second intervals. Healthy intervals sustain approximately 59.9 guest frames/s and 44.05 kHz of SPU output with no new underruns. During the reproducible bad interval:

| Metric | Healthy | Affected interval |
|---|---:|---:|
| Guest cadence | ~59.9 Hz | 31–36 Hz |
| SPU production | ~44,050 samples/s | 23,000–26,200 samples/s |
| Dirty interpreter | workload-dependent | ~9.5–10.0 million instructions/s |
| Output underruns per interval | 0 | ~26,000–43,000 |

The guest and audio rates fall together, the output buffer approaches empty and cadence later recovers to normal. This confirms a performance-driven starvation path in the native runtime. It does not support corrupt audio assets as the primary explanation, and it does not yet establish which specific `US.GAM` routines dominate the interpreted workload.

## Offline overlay-cache experiment

The existing PSXRecomp workflow was used without adding a project script:

1. The runtime-produced `overlay_captures.json` supplied three captured regions, including the secondary `US.GAM` image.
2. `compile_overlays.py --check` compiled all regions successfully with the existing MinGW64 GCC, reporting zero unsupported instructions and zero unknown/bad targets.
3. A real ignored cache was generated beside the Release executable. The runtime indexed the DLL inventory successfully.
4. Two 45-second Release runs, including a second pass after compiling newly accumulated variants, still reported zero native overlay activations and reproduced the same cadence/audio collapse.

This result narrows the problem: compilation and cache discovery work, but the captured shards cannot be selected for this execution segment. `US.GAM` runs through KUSEG PCs such as `0x0005B7D8`; overlay capture canonicalizes the corresponding code to KSEG0 entries such as `0x8005B7D8`. PSXRecomp deliberately rejects KUSEG and KSEG1 dispatch into KSEG0 overlay shards because the emitted body bakes architectural PCs affecting `$ra`, EPC and instruction-cache tags. The framework's segment-gate regression test passes and confirms that this rejection is intentional. Repeatedly compiling more variants cannot solve the mismatch. The cache, captures and telemetry logs are local generated artifacts and must not be committed.

An 8-second wall-time sample measured 38.9% in the dirty-RAM interpreter and 0% in native overlays. A second bounded snapshot found large interpreter chains entering at `0x000598AC`, `0x0005C868`, `0x00067A38`, `0x0005C538`, `0x0005B638` and related sites. Focused read-only Ghidra decompilation maps these to or inside GPU environment setup, ISO9660 routines, `_patch_gte`, `VSync`, formatted output and interrupt initialization. The per-entry counter includes locally chained execution after each entry, so these totals identify dispatch roots rather than proving that any named leaf alone consumes the attributed instructions.

## Next focused tasks

The static level-transition pipeline is now bounded well enough for targeted failure diagnosis. Main state 3 enters through coordinator `0x000264F4`, which selects a loading image, loads the formatted WAD through `0x00017754` and reinitializes Strategy and resident systems before the normal per-frame path. The canonical archive contains 59 matching level/introduction WADs. A 49-rule table selects among 30 loading-image names using destination, optional origin and first-load/cycle state; the uploader places a 512 by 240 image on both display pages. This maps the transition machinery but does not establish a complete story-order graph or validate every destination dynamically.

Strategy producer tracing identifies separate operations for checkpoint-state save/restore, an explicit three-field destination and a compact decimal destination. The reusable archive-index mode of `tools/inspect_dpsx.py` inspected all 59 level/introduction WAD windows without extraction. Opcode `179` is a proven destruction terminal. Breadth-first root scheduling, explicit repeated-call-context pruning and a configurable state ceiling expand the 100,000-context inventory to 357 reachable producer sites. Fifty-four WADs retain bounded stops, but only `MadameHoochTraining` in Quidditch reaches the ceiling. A targeted one-million-context pass adds internal nodes without another transition producer, and a context-insensitive return over-approximation finds the same three selected Quidditch sites with no additional candidate within confirmed layouts. These remain static provenance results rather than a complete directed story graph.

Loader-derived actor-local decoding and constant predecessor analysis now cover 269 compact-transition sites. Opcode `513` contributes 68 root-invariant and three root-bounded edges; `QuidditchDoor` remains the sole overwritten initial value and resolves to three constants. All 25 opcode-370 sites now have a provenance class: three use direct constants, six reproduce the decimal-split formula from invariant source locals, 15 minecart sites load game-state location properties `[87,88,89]` directly, and `WizardCardBook` reads dynamic state bytes `[31,32,33]` through opcode `371`. The current union contains 79 unique present static edges; the 16 dynamic-tuple sites are not counted as fixed destinations. Thirty source WADs expose the special zero case. These classes are static provenance, not observed story order, and do not exclude cross-Strategy writes or paths beyond bounded CFG stops.

The complementary opcode-373 pass reaches 1,107 state-byte writes at 100,000 contexts. A one-million-context pass reaches the additional Quidditch site and matches its five-site upper bound, yielding 1,108 exact sites. Reusable stack-expression recognition classifies every recovered expression: 332 constant indices, 773 actor-local indices and three private indirect indices populated through property `126`. It classifies 94 direct byte-counter increments, 94 adjusted increments, nine byte-minus-local updates and three minecart writes of `global[118]` to byte 30. Three other formerly complex sites have fixed byte-30 targets; the Gnome relative slot has two recovered writers and both store zero. The remaining three write value 3 to allocator-backed indices in `MadameHoochQuidditchTraining`; straight-line setup stores property-126 results into the exact three dereferenced entries, whose range starts at 64. Only three recovered writes target `[31,32,33]`, all zero assignments in `HousePointController`. The containing `0x580`-byte state block is preserved by the save/restore paths, and no nonzero producer exists among the 1,108 recovered opcode-373 sites. Bounded CFG stops and other native mechanisms remain explicit limitations, so this narrows the unknown without turning it into a fixed edge or a dead-code claim.

A focused automated compatibility pass now covers 18 relevant runtime tests: memory-card IRQ and protocol behavior, CD-ROM IRQ/lid integration, SPU edge cases, frame pacing, savestate status, RGB888 transition guards and multi-image live-text fallback. All 18 pass. Two source-contract tests were updated to follow existing refactors: vanilla snapshots remain version 7 while enhancement-memory snapshots use version 8, and forced CD reinsertion delegates to the shared tray-cycle helper.

The broader MinGW runtime tree was then rebuilt and exercised on the reference Windows workstation. All 109 enabled test entries completed without failure; two additional tests are disabled by project configuration and the platform-specific critical-section probe reported its expected skip. This broader pass also repaired test-only portability drift: Clang-only linker syntax is no longer sent to GNU ld, isolated GPU and launcher fixtures declare their real dependencies, the lobby-chat fixture follows the current identity-bearing API, and the cache-tag policy no longer mistakes a runtime `overlay_cache` configuration check for compiled-shard consumption. These changes validate the test harness and existing runtime contracts; they do not extend the amount of HP1 gameplay covered.

A separate ten-test recompiler pass covers KUSEG dispatch generation, exact segment gating, dirty-text admission and continuation, overlay store barriers, reachable discovery, FMV cycle batching, CLI project packaging and failure propagation. All ten pass with the pinned generator. A full 114-test recompiler-tree run is not claimed: its build currently stops at the unrelated `ws_cull_edge_interp_test` fixture under the portable Windows LLVM toolchain because that fixture's dead-code-elimination assumption no longer isolates it from the complete GPU dependency surface.

The pinned project was rebuilt after that pass and exercised headlessly for 15 seconds with an isolated writable-state directory. It identified the canonical NTSC-U disc, armed the boot text image at `0x00100000..0x0010D800` and the secondary image at `0x00010000..0x00079000`, reached 2,089 frames and reported neither a fatal condition nor an automatic freeze dump. Binary symbol inspection confirms that the Release executable contains the boot, `US.GAM` and composite dispatchers. Its imported libraries are Windows system/UCRT libraries; no MinGW runtime DLL dependency was found. This is a startup/integration smoke test, not audiovisual or gameplay validation.

Clean reproducibility was then checked without retaining another retail copy or build tree. Regeneration from the canonical `US.GAM` reproduced all 36 existing secondary-provider files byte for byte, including 33 shards and the 2,091-entry dispatch table. Both patched addresses retain independent four-byte code ranges. Independent clean links produce identical code, read-only data, writable data, exception-table and resource sections; only whole-PE metadata prevents raw executable hashes from matching. All temporary regeneration and build directories were removed after comparison.

Generated-manifest integrity was checked independently of gameplay. The boot provider contains 227 unique functions and valid ranges; the secondary provider contains 2,091. Every function entry is covered by an emitted range, no range is empty or wraps the address space, and the two providers' physical ownership windows are disjoint. The corresponding dispatch tables contain 2,238 and 15,829 unique, aligned and strictly ordered entry/continuation keys, all inside their owner window and backed by valid range slices. Some secondary function ranges overlap because independently discovered functions share code tails; their dispatch keys remain unique. A project-owned composite-dispatch regression now verifies boot and secondary routing, exclusive upper bounds and rejection of a KSEG0 alias for the KUSEG-only `US.GAM` provider.

1. Continue automated integrity and boundary checks that do not require interactive play.
2. Do not change audio or scheduling behavior on the basis of the uncertain single-pass impression.
3. Continue from the latest save toward the next major story or level boundary. Preserve a focused capture only for a reproducible audiovisual or control deviation.

## Secondary live-code fallback

Both known `US.GAM` instruction writes are dynamically established in order: `0x00056388` and `0x00057F20` change from retail word `0x240B00EF` to `0x240B0180`. The generated KUSEG provider contains an independent compiled entry and exact four-byte guard range at each address.

The real-memory runtime regression now registers simultaneous primary and secondary text images, changes code in the secondary image through the ordinary guest store path and verifies that the changed exact range is rejected from native execution. A neighboring secondary range and the primary image remain native-valid. The memory-map test, dirty-text admission test, continuation guard and mirror-PC guard all pass. Together with the earlier dynamic observation of HP1 performing both writes, this closes the secondary-image fallback contract; it does not claim that every path through the affected graphics functions has been exercised during native gameplay.

## Evidence boundary

- **Confirmed dynamically:** native basic gameplay, initial memory-card creation/slot flow, intermittent slowdown, its correlation with dirty interpretation and audio underruns, successful offline shard compilation, cache discovery, KUSEG `US.GAM` execution and zero native activations in the measured runs.
- **Confirmed by framework contract:** current overlay shards are KSEG0-only and non-KSEG0 aliases must stay interpreted. This is a correctness guard, not a cache-discovery failure.
- **Observed boundary:** exact-segment native coverage is active. Earlier visible runs reproduced intermittent EA slowdown; one later run did not, so frequency and stability remain unmeasured.
- **Confirmed by bounded native measurement:** both text references arm, the secondary static provider is linked and static execution dominates the measured post-load headless window. Exact-range guards remain active for the two known instruction writes.
- **Confirmed by visible validation:** the KUSEG-provider build supports an extended 49.5-minute route through repeated room/loading transitions, conversations, lessons, combat and outdoor castle areas; a real save survives restart and reloads through an active loading screen.
- **Confirmed by combined dynamic and regression evidence:** both `US.GAM` instruction writes occur, both emitted four-byte units are exactly guarded, and a secondary-image mismatch routes away from native code without blocking neighboring or primary-image ranges.
- **Carried to Phase 7 or later validation:** repeat EA timing observation, display-centering flicker, analog sensitivity, the isolated clipped spell prompt, later major story/level boundaries and an eventual complete playthrough.

## Warner-to-EA transition diagnosis

The visible order is confirmed as correct Warner screen, black, a brief corrupted Warner-like frame with RGB/block artifacts, black, then EA. GP1 tracing records the switch into 24-bit display mode at frames 418–419. MDEC tracing begins only at frame 428, leaving roughly ten frames in which stale 15-bit VRAM can be presented as packed RGB888. A two-present mode-edge blank was too short for this gap.

The first revised presentation guard waited for non-zero RGB888 upload coverage before exposing the framebuffer. Manual validation confirmed that it removed the glitch, but the display remained black throughout the audible EA movie and recovered at language selection. This proves that this MDEC route does not expose the expected upload-coverage signal.

The follow-up guard therefore also releases when traced MDEC activity begins, while retaining the two-present settling blank. It remains event-driven rather than using a title-specific frame count. Both focused regression tests and the full Release build pass. Manual validation confirms that the transient glitch is absent and that EA remains visible and audible. The tester was uncertain whether loading was slightly slower or EA audio/video alignment had changed; neither is classified as a regression without a repeatable observation.
