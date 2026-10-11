# Architecture and project decisions

This document records durable decisions that affect implementation or future contributors. It is intentionally limited to technical and release-relevant choices.

## Reference build

The initial reference build is **Harry Potter and the Sorcerer's Stone (USA), SLUS-01415**.

Using one canonical build keeps addresses, hashes, tests and reverse-engineering evidence stable. Additional regional builds may be investigated later.

## Initial host

Windows x64 is the first host platform.

Portability should not be unnecessarily damaged, but additional host platforms are not part of the first release milestone.

## Recompilation-first strategy

HP1Recomp uses a **recompilation-first, reverse-engineering-driven** approach.

A complete traditional source decompilation is not required before the native port can run. Clean human-written C/C++ may progressively complement or replace generated code when understanding and validation justify it.

## Recompiler selection

PSXRecomp is the primary recompilation framework.

PS1Recomp remains an auxiliary analysis and alternative recompilation source where its tooling is useful. This split can be revisited if HP1-specific evidence supports a different architecture.

## Fidelity before enhancements

The vanilla project prioritizes original behavior and compatibility.

Future modding and enhancements should remain possible, but they must not silently replace the faithful baseline.

## Retail-data boundary

Retail game images, executable/data files and commercial assets are not part of the repository or release package.

Developers and players supply their own legally obtained supported game copy. Project-owned tooling may verify, inspect or generate local derived data without committing those retail-derived outputs.

## Secondary executable model

`SLUS_014.15` and `US.GAM` are treated as independent executable providers.

`US.GAM` declares KSEG0 addresses in its PS-X EXE header but is observed executing through KUSEG. Its static provider therefore preserves those observed KUSEG program-counter semantics instead of pretending KUSEG and KSEG0 are interchangeable.

Exact live-code guards remain active for known self-modifying instruction sites, with interpretation as the fallback for modified or unsupported ranges.

## First-release compatibility boundary

A complete start-to-credits playthrough is valuable release validation, but it is not used to inflate claims about untested content.

The first alpha is based on representative extended native play, working save/restart/load, repeated transitions, audiovisual/input coverage, automated regressions and explicit documentation of known limitations. Release notes must distinguish tested behavior from untested later-game coverage.

## Documentation language

Repository documentation and technical artifacts are written in English to keep collaboration accessible to an international audience.
