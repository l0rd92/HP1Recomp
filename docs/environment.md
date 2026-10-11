# Windows development environment

This document records the Phase 0 environment baseline. Statements about work being untested describe that checkpoint and may be superseded by later phase documents and `RESEARCH.md`.

## Verified on 2026-09-30

Verified workstation evidence confirms:
- Git 2.55.0.windows.3; HP1Recomp repository.
- MSYS2 MinGW64 GCC/G++ 16.2.0 targeting x86_64-w64-mingw32.
- CMake 4.4.2 and Ninja 1.13.2.
- CMake/Ninja configured, compiled and ran C99 and C++20 smoke programs.
- Python 3.12.10, 64-bit; pip 26.2.1; tomllib and venv import successfully.
- Git Bash 5.3.15.
- Temurin JDK/javac 21.0.12.1, 64-bit.
- Ghidra 12.1.4 launches.
- ghidra_psx_ldr at 6f6be18615d9b42b1ce07740780623c3cf6cbd2c builds against Ghidra 12.1.4; extension installation reported complete. At this Phase 0 checkpoint, actual PS-X EXE import remained untested.
- PCSX-Redux build 445 launches.
- mkpsxiso/dumpsxiso 2.30 run and display help.
- DuckStation Windows x64 launches to its welcome wizard.

## Session activation

From the checkout root in PowerShell:

```powershell
. .\tools\enter-dev.ps1
```

The script changes only the current process PATH. It selects Python 3.12 and Git Bash, and checks the MinGW tools. Set HP1_MINGW_ROOT for a non-default MSYS2 installation. Activation was verified from a fresh PowerShell: Python 3.12, MinGW tools and Git Bash resolve correctly.

Install missing CMake/Ninja in an MSYS2 MINGW64 shell:

```bash
pacman -S --needed mingw-w64-x86_64-cmake mingw-w64-x86_64-ninja
```

## Framework checkouts

Revisions are recorded in config/framework-pins.json:
- HP1Recomp PSXRecomp fork: `84ab7fe0cc34109d4ebc391ef173af829e8b21f2`, based on upstream `1ec24e9d4915770a313e4fc19fad5430f55b00a2`
- PS1Recomp/ps1-recomp analysis checkout: `ab4f0e01e6699c741bbc3d1ee73022be2803ff69`

The repository submodule points to the HP1Recomp fork revision containing the bounded KUSEG secondary-image, multi-image live-text and RGB888 transition work. The upstream base remains recorded separately for provenance; it is not the current submodule commit.

The PS1Recomp `ps1Analyzer` target was compiled locally with MinGW on 2026-10-01 and used successfully against both HP1 executables. This validates that bounded analyzer target only; the full PS1Recomp runtime/recompiler and HP1 compatibility remain untested. PSXRecomp's known-title workflow is documented separately in [Phase 1](phase1-tomba.md).

For HP1 Phase 4, PSXRecomp was added to the project as a submodule at the upstream base revision. Its `psxrecomp-game` and `psxrecomp-bios` emitters compiled with the framework's portable `cmake-clang-v1` 1.0.14 toolchain, HP1 boot generation succeeded and the minimal runtime configured successfully. Native HP1 compilation and launch were subsequently completed in Phase 5; Phase 6 then advanced the submodule to the recorded fork revision.

Keep auxiliary research-tool checkouts outside the game repository unless they are deliberately selected and pinned as project dependencies. PSXRecomp is the selected exception and is maintained as the repository submodule.

## Reference inventory

Local BIN/CUE pairs are present for HP1 USA, HP2 USA, Croc European demo, Croc USA, Croc 2 USA and European/USA Croc 2 demos, Aladdin USA and Tomba! USA. The inspected CUE files reference existing nonempty BIN files and declare MODE2/2352 data tracks. This establishes file presence and CUE linkage only, not canonical disc identity or image integrity.

Separate local Ghidra projects exist for HP1 USA, HP2 USA, the Croc European demo, Croc 2 USA, the European Croc 2 demo and Aladdin USA. The Croc demo's supplied `CROC.SYM` was imported into `CROC.EXE`; `DEMOFMV.SYM` has not been imported because no matching standalone program has been established. The European Croc 2 demo's on-disc `CROC2.MAP` was imported only into its exact matching `CROC2.EXE` project. These projects, extracted discs and generated structural exports remain outside Git.

Retail data stays outside Git. HP1 source identity is established in `docs/phase2-disc.md`; comparison-title hashes in `RESEARCH.md` identify the extracted executables only and are not whole-disc identity claims.

## Reproduction and layout

Use a clean clone of HP1Recomp and initialize its pinned PSXRecomp submodule. Keep downloaded GUI/analysis tools and auxiliary framework checkouts outside the repository; keep retail images in a separate games directory. The verified workstation uses `C:\path\to\HP1Recomp`, `C:\path\to\Tools` and `C:\path\to\Games` respectively. These are examples, not mandatory paths.

1. Install Git for Windows and Python 3.12 x64.
2. Install MSYS2, then install mingw-w64-x86_64-gcc, mingw-w64-x86_64-cmake and mingw-w64-x86_64-ninja from the MINGW64 shell.
3. Install Temurin JDK 21 x64. Extract Ghidra 12.1.4 to a separate tools directory and launch ghidraRun.bat.
4. Clone lab313ru/ghidra_psx_ldr with recursive submodules and check out 6f6be18615d9b42b1ce07740780623c3cf6cbd2c.
5. Using Gradle 9.1.0 and JAVA_HOME set to JDK 21, run from the loader checkout:
   `gradle -PGHIDRA_INSTALL_DIR=<Ghidra installation> buildExtension`.
   Install the resulting dist ZIP through File > Install Extensions and restart Ghidra.
6. Download the official DuckStation Windows x64 ZIP, PCSX-Redux build 445 and mkpsxiso 2.30 win64 ZIP; extract each into its own directory.
7. In HP1Recomp, run `git submodule update --init --recursive` to initialize the pinned PSXRecomp dependency. Clone PS1Recomp separately only when its auxiliary analyzer is needed, and check out the revision in `config/framework-pins.json` with recursive submodules initialized.
8. Dot-source tools/enter-dev.ps1 from a fresh PowerShell and confirm tool paths. Validate CMake/Ninja with a small C99/C++20 build before a game build.

Download sources:
- Ghidra: https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build
- Loader: https://github.com/lab313ru/ghidra_psx_ldr
- Gradle: https://services.gradle.org/distributions/gradle-9.1.0-bin.zip
- DuckStation: https://github.com/stenzek/duckstation/releases
- PCSX-Redux: https://distrib.app/pub/org/pcsx-redux/project/dev-win-x64
- Disc tools: https://github.com/Lameguy64/mkpsxiso/releases/tag/v2.30

Recorded package SHA-256:
- Ghidra 12.1.4: ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db
- DuckStation x64 ZIP downloaded 2026-09-30: 5ba3b9624b3073d3398c2cb8185ba3a014ff9e84f9c486627e0e8aa56371d352
- mkpsxiso 2.30 win64 ZIP: 7d3963cd322df365766cee1dbc3e405ea103bbe4e11c0db86c9688b32f5a1017
- PCSX-Redux build 445 ZIP: fee4558767d95301a056f3ff62b8bb3f30e97e6646d9576857c15808084f5779

Ghidra, DuckStation and mkpsxiso hashes were compared with published hashes. Redux hash was recorded locally only. DuckStation's latest release is mutable: future downloads may differ.

## Phase 0 result and limits

Phase 0 preparation is complete on the reference workstation. At its verification checkpoint, Git exclusion checks passed for BIN, CUE, CHD, game-data archives, retail executable/archive names, generated output and build output. Repository cleanliness is rechecked for each later task rather than inferred from this historical result.

At the Phase 0 checkpoint, Ghidra loader import of a PS-X EXE, emulator gameplay, framework builds and disc identity remained untested. Later work imported both HP1 executables and completed source-disc identification; see `RESEARCH.md` and [Phase 2 source identity](phase2-disc.md). This environment validation is still not proof that HP1 can be recompiled.
