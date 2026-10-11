# License and third-party notices

## HP1Recomp

Original HP1Recomp code and other project-authored material, where the contributors
hold the necessary rights, are made available under the **PolyForm Noncommercial
License 1.0.0** in [LICENSE](LICENSE).

Required Notice: Copyright (c) 2026 l0rd92

This project license does not relicense third-party software or any material from
the original PlayStation game.

## PSXRecomp

[PSXRecomp](https://github.com/RetroPortingToolKit/psxrecomp) is the primary
recompilation framework, used as the pinned `psxrecomp/` Git submodule.
It has its **own** license, identified by the framework as PolyForm
Noncommercial 1.0.0. See [psxrecomp/LICENSE](psxrecomp/LICENSE) for the
framework's actual license terms. Those terms are not replaced by HP1Recomp's
license. The Windows packager copies that original framework license unchanged
to `licenses/PSXRecomp-LICENSE.txt`.

## OpenBIOS and runtime dependencies

OpenBIOS is distributed under its own MIT-related notices, provided in the
package as `bios/OpenBIOS.LICENSE`.

Third-party notices for linked runtime components, including libchdr,
stb_image and toml11, are copied without modification from
`psxrecomp/runtime/licenses/` into the Windows package's `licenses/`
directory. Refer to the framework's
[THIRD_PARTY_ATTRIBUTION.md](psxrecomp/THIRD_PARTY_ATTRIBUTION.md)
for additional dependencies and their terms. This list is not a substitute
for auditing the exact dependencies of a release build.

## PS1Recomp

[PS1Recomp](https://github.com/PS1Recomp/ps1-recomp) is an auxiliary,
separately used analysis tool licensed under **GPL-3.0-or-later**. It is
not currently linked into the HP1Recomp Windows executable or bundled as
part of the player package. Its license remains with that project.

## Original game

Harry Potter and the Sorcerer's Stone and its commercial game content are
not licensed by HP1Recomp. The project does not grant rights to game images,
assets, original executables or game-derived machine code.

Static recompilation may incorporate translated original game instructions
into compiled executables. The rights and redistribution status of any
such output require separate assessment before publishing a Windows binary.
Including a project license or excluding BIN/CUE files does not resolve
that question.
