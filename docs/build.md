# HP1 generation and build

Phase 4 established the smallest PSXRecomp project that can generate the canonical boot executable without committing retail data. Phase 3 established that `SLUS_014.15` loads and executes the separate `US.GAM` image at runtime.

## Inputs and boundaries

| Input | Project treatment |
|---|---|
| `SLUS_014.15` | Main PSXRecomp image described by `game.toml` |
| `US.GAM` | Secondary PS-X EXE loaded by the original boot program |
| BIN/CUE and extracted files | Local under ignored `disc/`; never committed |
| Generated C and overlay caches | Local under ignored `generated/` and `.cache/` |

The initial generation compiles the boot executable. `US.GAM` has a KSEG0 PS-X EXE header but is executed by the boot program through KUSEG. Phase 6 adds an opt-in recompiler code view that emits the secondary image with those observed KUSEG PCs without changing the retail file, data pointers, GP, stack or BSS. Generate it locally under `generated/secondary` with `--runtime-code-segment kuseg`; CMake then links it as an independent provider. Boot and secondary code retain separate dispatch namespaces and exact live-byte references, with interpretation remaining the fallback for unknown or modified ranges.

## Local preparation

Initialize the pinned framework checkout and activate the documented development session, then verify and prepare a legally obtained canonical disc using the framework CLI. The source may be passed from any local path; prepared retail files stay under ignored `disc/`.

```powershell
git submodule update --init --recursive
. .\tools\enter-dev.ps1
python .\psxrecomp\psxrecomp_cli.py verify-disc --config .\game.toml --disc 'C:\path\to\HP1-USA.cue'
python .\psxrecomp\psxrecomp_cli.py generate --config .\game.toml --project-root . --disc 'C:\path\to\HP1-USA.cue' --no-aot-static
```

Generate the secondary executable from the verified extracted `US.GAM` without copying it into the repository:

```powershell
.\psxrecomp\recompiler\build\psxrecomp-game.exe 'C:\path\to\US.GAM' --out-dir .\generated\secondary --runtime-code-segment kuseg --strict
```

The canonical `US.GAM` SHA-256 is recorded in `docs/phase2-disc.md`; verify the input before generation. The generated provider is ignored retail-derived output and must not be committed.

Phase 4 verified configuration after generation:

```powershell
cmake -S . -B build -G Ninja
```

Native compilation was validated at the first Phase 5 checkpoint:

```powershell
cmake --build build
```

## Acceptance checks

Phase 4 verified:

1. Disc verification accepts only the recorded Track 01 identity.
2. Generation produces `SLUS_014.15` dispatch/full units without adding retail data to Git.
3. CMake configures the minimal OpenBIOS/SDL3 runtime.

Phase 5 subsequently verified:

1. The native project compiles and the process/runtime starts.
2. The runtime boots the generated `SLUS_014.15` path and reaches its request for `US.GAM`.
3. Loading `US.GAM` registers its live text image and safely falls back to interpretation where native code is unavailable or invalidated.
4. The writes at `0x00056388` and `0x00057F20` change live RAM from `0x240B00EF` to `0x240B0180`; stale generated native code must not execute for affected ranges.

Passing generation alone does not establish HP1 compatibility. These checks separate project scaffolding, boot-image generation and secondary-image correctness.

Phase 6 additionally verified the exact-segment KUSEG secondary provider, independent boot/secondary dispatch namespaces and exact-range fallback for both observed instruction writes. The current pinned tree builds successfully, its 109 enabled runtime tests complete without failure, and a 15-second isolated headless smoke arms both executable images without a fatal condition or automatic freeze dump. These automated checks complement the preserved extended-play evidence; they do not establish untested full-game behavior.

With `BUILD_TESTING` enabled, the project also builds `game-dispatch-composite-test`. This regression uses provider stubs to verify routing for the boot and `US.GAM` address spaces, their exclusive upper bounds and the rule that the KUSEG-only secondary provider must reject KSEG0 aliases. The test executable itself reads no retail data.

The same regression can be configured independently from a clean checkout, without the framework submodule, generated providers or retail data:

```powershell
cmake -S .\tests -B .\build-tests -G Ninja
cmake --build .\build-tests
.\build-tests\game-dispatch-composite-test.exe
```

The executable returns zero on success. A full CMake distribution may use `ctest --test-dir .\build-tests --output-on-failure` instead; the verified portable Windows toolchain does not bundle `ctest`.

## Windows release package

After generating both executable providers from a legally obtained canonical
disc, create the clean Windows package with:

```powershell
.\tools\package_release.ps1
```

The packager performs a fresh Release configuration and build, stages OpenBIOS
and third-party notices, verifies that the executable imports only Windows
system DLLs, rejects retail images, saves and local runtime state, then writes a
portable ZIP and matching SHA-256 file. The ignored output is
`HP1Recomp-v<version>-windows-x64.zip`; `VERSION` is the artifact version source
of truth.

A clean regeneration from the canonical `US.GAM` reproduces all 36 secondary-provider files byte for byte: 33 C shards, declarations, dispatch table and range manifest. It emits 2,091 entries. The two dynamically observed patch sites, `0x00056388` and `0x00057F20`, each have an independent function entry and exact four-byte range. Two clean links of the same object set produce identical `.text`, `.rdata`, `.data`, `.pdata` and `.rsrc` sections. Whole-PE hashes differ because of linker metadata outside those sections, so release reproducibility should compare the meaningful sections or use a future deterministic-PE packaging step rather than expecting identical raw hashes.

The generated range manifests contain 227 unique boot functions and 2,091 unique secondary functions. Every function entry is covered by a non-empty, non-wrapping range. Their dispatch tables contain 2,238 and 15,829 aligned entry/continuation keys respectively; all keys are unique, strictly ordered, inside their owning image and backed by valid range slices. Shared-tail range overlap in the secondary manifest is permitted; dispatch keys remain unique.

## Verified Phase 4 result

Verified on 2026-10-01 with PSXRecomp `1ec24e9d4915770a313e4fc19fad5430f55b00a2`:

| Check | Result |
|---|---|
| Canonical disc verification | Passed; main track accepted |
| Boot seeds | 175 KSEG0-normalized addresses loaded |
| Functions generated | 227 |
| Generated C | Four shards, 138,426 lines reported by the emitter |
| Dispatch table | 227 entries |
| CMake configuration | Passed with OpenBIOS, SDL3, one player, UI/netplay off |
| Native compilation | Passed; 149 build steps linked the Windows executable |
| Native launch | Not attempted; M5.3 |

The framework's portable CMake/Clang toolchain `cmake-clang-v1` version `1.0.14` was selected during generation. All prepared disc data, generated code, build trees and tool caches are ignored. The optional configuration auditor was not used as a pass/fail gate because it requires an `[audit]` block; adding an empty block would not provide evidence.
