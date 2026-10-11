# Phase 7 — Fidelity, regression and release hardening

Status: **in progress**
Started: 2026-10-11

## Goal

Turn the validated native baseline into the first reproducible release-quality Windows package. Phase 7 fixes or classifies the deviations observed during Phase 6, protects critical behavior with focused regressions and documents the exact supported boundary.

A complete start-to-credits playthrough remains valuable release validation, but it is not required to begin or finish the engineering work in this phase. Release notes must not claim coverage that was not observed.

## Starting baseline

| Area | Baseline |
|---|---|
| Native execution | `SLUS_014.15` and KUSEG `US.GAM` providers linked and active |
| Extended play | 49.5-minute new-game route, normal exit, 59.79 average guest frames/s |
| Persistence | Memory-card creation plus save/restart/load validated |
| Transitions | Repeated indoor, outdoor, room and loading transitions validated on the tested route |
| Presentation | Post-Warner RGB corruption fixed with an event-driven MDEC guard |
| Live code | Both known `US.GAM` instruction writes use exact-range fallback |
| Automated runtime coverage | 109 enabled runtime tests pass; focused project and recompiler contracts pass |

## Initial worklist

1. ~~Reproduce and diagnose vertical screen-centering flicker without encoding a title-specific workaround.~~ Completed with a generic runtime fix and regression coverage.
2. Measure the DualSense analog path and decide whether its sensitivity is original behavior, configuration or a runtime deadzone/range defect.
3. ~~Repair the playtest wrapper's empty numeric exit-code field and remove unsupported diagnostic requests.~~ Completed in the retained Phase 6 playtest kit.
4. Add or strengthen focused regressions for any confirmed fix.
5. Verify the new clean Windows package and its legal-data onboarding flow on a staged first launch.

The isolated clipped spell prompt and intermittent EA/audio timing remain observations until reproduced. They must not trigger speculative fixes.

## Playtest wrapper cleanup

The retained Phase 6 launcher no longer sends the unsupported `overlay_state`
request on every capture. After process completion it refreshes the Windows
process object and records the exit code once. If Windows no longer exposes the
process result, a clean runtime `atexit` report maps to `0`; an unavailable and
unclassified result maps to numeric `-1` instead of producing a blank field.
The same captured value drives both the session summary and console result.

## Vertical screen-centering fix

The title's center-screen control changes the display start between two PS1
VRAM pages. Moving the image downward can make a 240-row scanout cross the
bottom of the 512-row VRAM image. The CPU display path already wrapped those
rows correctly, but the OpenGL and Vulkan direct paths represented the scanout
as one clamped texture rectangle. One alternating page therefore sampled the
last VRAM row repeatedly and appeared as persistent whole-screen flicker.

PSXRecomp now detects this rare boundary-crossing rectangle and stages it
through the existing wrapped CPU readout. Ordinary direct GPU presentation is
unchanged. Unit and source-contract regressions cover the boundary. An
automated visible run then entered the title options, moved the vertical
position into the formerly failing range (`display_y = 511`) and captured six
successive composed frames; both alternating pages remained complete and
visually coherent.

## Windows package baseline

The project-owned `tools/package_release.ps1` now performs a clean Release
configuration and build, stages the runtime with OpenBIOS and required notices,
checks that only Windows system DLLs are imported, rejects retail and local
state files, and creates a portable ZIP plus SHA-256 receipt. Player-facing
controller defaults, first-run instructions and alpha release notes are source
controlled under `packaging/release`.

The first `v0.1.0-alpha` candidate completed all 216 build steps. Its ZIP held
11 allowed files and no disc image, memory card, local setting, capture or dump.
An independently extracted copy ran headlessly against the canonical legal
disc, identified `SLUS-01415`, armed both the boot and `US.GAM` live-text guards
and entered the game main function. The remaining package check is the visible
clean first-run disc picker; this headless smoke intentionally supplied the disc
on the command line.

## Exit criteria

- important gameplay and persistence paths have repeatable regression checks
- previously fixed presentation and live-code failures remain protected
- confirmed Phase 6 deviations are fixed or documented with their impact and workaround
- a clean checkout plus legitimate canonical data produces a verified distributable Windows package
- release notes distinguish tested behavior, known limitations and untested full-game coverage
