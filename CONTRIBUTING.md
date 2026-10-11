# Contributing to HP1Recomp

HP1Recomp aims to reproduce the original PlayStation game faithfully as a native Windows application while keeping the codebase useful for continued reverse engineering and future modding.

## Priorities

Compatibility and correctness of the original game come before enhancements.

Useful contributions include compatibility and fidelity fixes, regression tests, reverse-engineering findings, build and packaging improvements, documentation, and reusable analysis or debugging tools.

## Retail game data

Do not submit copyrighted retail game data.

Pull requests must not include disc images, original executable files, extracted retail assets, `POTTER.DAT` / `POTTER.DIR`, or generated output that embeds copyrighted retail code/data and is not appropriate to redistribute.

Use hashes, metadata, scripts and tooling that operate on locally supplied copies instead.

## Changes

Prefer focused changes with a clear reason. For bug fixes, include where practical the observed behavior, expected/original behavior, suspected or confirmed cause, implementation summary and how the change was tested.

For reverse-engineering findings, distinguish confirmed evidence from hypotheses and preserve addresses, hashes or build identifiers when they matter.

Experimental workarounds are useful for diagnosis, but a title-specific workaround should not silently become the permanent solution when a more general correctness fix is possible.

## Tests

A retail-independent composite-dispatch regression can be built from a clean checkout:

```powershell
cmake -S tests -B build-tests -G Ninja
cmake --build build-tests
.\build-tests\game-dispatch-composite-test.exe
```

Additional runtime and recompiler tests live in the pinned PSXRecomp dependency.

## Documentation

Durable discoveries should not live only in commit messages or discussion threads. Update the relevant documentation or machine-readable symbols/configuration when a finding will matter to future contributors.

Repository documentation and code are written in English.
