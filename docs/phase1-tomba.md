# Phase 1 — Tomba Windows smoke test

Validated on 2026-09-30 using the Windows toolchain in [environment.md](environment.md).

## Source identity and revisions

- Reference project: https://github.com/mstan/TombaRecomp
- TombaRecomp: `070f1296f940f1f235d56aa35f631e8272512ac6`
- Bundled PSXRecomp: `c68bf6e08568327d0c6816d083cf7d00875593f0`
- recomp-net: `859ba28b93f7374f2ac1eb70d2171594c5cd4f4b`
- retcomm-rbengine: `a7b98507a62fe00e5aec3b90c52a4134f3c174bc`
- recomp-ui: `0cd5652955fd975fbad91fd241ce5a483598f95f`

These are the reference project's revisions, separate from the standalone Phase 0 framework pins.

Tomba! (USA) BIN: 280193760 bytes; MD5 `c80636a28de4abcfa34f9e57fb3b043d`, matching the reference configuration.
Extracted `SCUS_942.36`: 559104 bytes; SHA-256 `c45cd788df40a540d8641dc9682007c80e6ab8a4bcdd0e4a4e2c14c5108aa10b`.

## Build workflow

Run from the reference checkout after activating the HP1 development environment. Retail data stays local. Extract the executable with the reference project's `tools/extract_psx_exe.py` into `disc/SCUS_942.36`.

```powershell
$pythonExe = (Get-Command python).Source
cmake -S psxrecomp/recompiler -B psxrecomp/recompiler/build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ "-DPython3_EXECUTABLE=$pythonExe"
cmake --build psxrecomp/recompiler/build --parallel 4
```

Before CTest, generate the runtime codegen header using the same canonical source list as the recompiler. The initial checkout lacked that header, causing the two overlay tests to compare baked hash `8ee36729` against fallback `00000000`.

```powershell
$helper = Join-Path $env:TEMP "hp1-codegen-hash.cmake"
@'
include("${PSXRECOMP_CODEGEN_HASH_ROOT}/runtime/codegen_hash_sources.cmake")
set(SRCS "${PSXRECOMP_CODEGEN_HASH_SRCS}")
set(OUT "${PSXRECOMP_CODEGEN_HASH_ROOT}/runtime/include/overlay_codegen_hash.h")
include("${PSXRECOMP_CODEGEN_HASH_ROOT}/runtime/hash_codegen.cmake")
'@ | Set-Content $helper -Encoding ascii
$frameworkRoot = ((Resolve-Path .\psxrecomp).Path -replace '\\','/')
cmake "-DPSXRECOMP_CODEGEN_HASH_ROOT=$frameworkRoot" -P $helper
ctest --test-dir psxrecomp/recompiler/build --output-on-failure
bash psxrecomp/tools/regen_bios.sh --config bios/OpenBIOS.toml
.\psxrecomp\recompiler\build\psxrecomp-game.exe --config game.toml
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ "-DPython3_EXECUTABLE=$pythonExe"
cmake --build build --target psx-runtime --parallel 4
.\build\Tomba__Recompiled.exe --game .\game.toml --disc "<local Tomba USA CUE>"
```

Check native command exit codes; stop on failure.

## Results and limits

- Initial CTest: 78 passed, 2 failed, 3 disabled.
- After generating the matching header and selecting Python 3.12 explicitly, both failed tests passed: `compile_overlays_static_tail` and `aot_overlay_discovery`.
- The original 78 passing tests were not rerun after that preparation change.
- OpenBIOS generation, Tomba generation, game configuration and compilation succeeded.
- Produced `build/Tomba__Recompiled.exe`.
- Manual gameplay confirmed: playable movement/jumping, audible sound and video playback.

OpenBIOS generation reported eight unsupported instructions skipped during emission and unresolved cross-function targets, including `0xA0850000`, `0x24840001` and `0xAC850000`. These warnings remain unresolved. They did not prevent the observed gameplay test; full-game compatibility, save/load and extended stability were not tested.

Phase 1 exit criteria are satisfied. This validates the reference workflow on the workstation, not HP1 compatibility.
