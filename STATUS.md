# HP1Recomp Status

Last updated: 2026-10-11

## Current phase

**Phases 0–6 complete — Phase 7 in progress**

HP1Recomp has moved from initial bring-up into fidelity, regression and release hardening for the first useful Windows package.

Phase 6 closed on representative extended compatibility rather than an unsupported full-game claim. A preserved 49.5-minute new-game session progressed through story scenes, lessons, combat, saving and repeated indoor/outdoor transitions, then exited normally at frame 177,588 with an average guest cadence of 59.79 frames/s. A separate save/restart/load cycle also restored progress successfully.

## Release target

The current release target is **v0.1.0-alpha**.

The project-owned Windows packager builds a clean portable ZIP, stages OpenBIOS and required notices, rejects retail game data and local player state, and verifies that the executable imports only Windows system libraries. A separately extracted candidate has already identified the canonical `SLUS-01415` disc, armed both executable text guards and entered the game main function in a bounded headless smoke.

The remaining package-level gate before publishing the candidate is a visible clean first-run test of the disc-selection flow.

## Validated baseline

| Area | State |
|---|:---:|
| Native boot / disc chain | ✅ |
| Language selection / title | ✅ |
| New game / early story | ✅ |
| Basic gameplay / input | ✅ |
| Memory-card creation | ✅ |
| Save / restart / reload | ✅ |
| Repeated indoor/outdoor transitions | ✅ |
| Warner → EA corruption fix | ✅ |
| Vertical screen-adjust flicker fix | ✅ |
| KUSEG `US.GAM` static provider | ✅ |
| Exact fallback for known live-code writes | ✅ |
| Enabled MinGW runtime regression tests | 109 / 109 passing |
| Full start-to-credits playthrough | Not yet performed |

## Phase 7 work

1. Measure and classify DualSense left-stick sensitivity.
2. Validate the packaged build through a visible clean first-run disc picker.
3. Preserve regression coverage for presentation, live-code fallback, persistence and packaging.
4. Reproduce the isolated clipped spell prompt before treating it as a defect.
5. Reproduce earlier EA/audio timing deviations before changing scheduler or audio behavior.

The vertical-centering flicker is already fixed at its generic runtime cause: a 240-row scanout crossing the bottom of the 512-row PS1 VRAM image now uses the existing wrapped CPU staging path instead of a clamped GPU-direct rectangle.

The retained playtest wrapper has also been cleaned up so it no longer polls an unsupported diagnostic and always records a numeric exit result.

## Compatibility boundary

The project does **not** currently claim complete full-game compatibility. Later story and level boundaries remain less tested than the validated route, and a complete start-to-credits playthrough is still desirable release validation.

This is an evidence boundary, not a known blocker: no current crash or fatal incompatibility prevents continued play on the tested route.

## Technical baseline

- Reference build: USA / NTSC-U / `SLUS-01415`
- Initial host: Windows x64
- Primary framework: PSXRecomp
- Auxiliary analysis: PS1Recomp
- Native executable providers: boot `SLUS_014.15` plus KUSEG `US.GAM`
- Retail game data: never committed or redistributed

For detailed evidence, see [Phase 6 compatibility closure](docs/phase6-compatibility.md), [Phase 7 fidelity and release hardening](docs/phase7-fidelity.md), [reverse-engineering research](RESEARCH.md) and the [build workflow](docs/build.md).
