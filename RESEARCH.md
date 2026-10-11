# HP1Recomp Research Notes

This file records technical findings, useful external work, hypotheses and unanswered questions.

It is not a dumping ground for chat transcripts. Findings should be written as project knowledge and should clearly distinguish confirmed facts from hypotheses.

## 1. Initial target

The initial target is the USA PlayStation release:

- Serial: `SLUS-01415`
- Title: Harry Potter and the Sorcerer's Stone
- Languages: English / French / Spanish
- Region: NTSC-U

The build is used as the first canonical target so code addresses, hashes and tests have a stable reference.

Other regional builds can later be used for binary comparison and broader support.

## 2. Recompilation approaches under evaluation

### PSXRecomp

Current role: **primary candidate for native port bring-up**.

Reasons for interest:
- purpose-built static PS1 recompilation workflow
- existing game projects provide practical reference material
- Windows-oriented build workflow exists
- project scaffolding / game-specific configuration model
- suitable foundation for separating vanilla behavior from later modifications

Repository:
- https://github.com/RetroPortingToolKit/psxrecomp

### PS1Recomp

Current role: **auxiliary analysis and alternative recompilation environment**.

Reasons for interest:
- PS1 analysis/recompilation research
- PsyQ/library identification work
- Ghidra-oriented workflow
- useful second opinion when classifying code/functions

Repository:
- https://github.com/PS1Recomp/ps1-recomp

Decision rule: do not force either framework onto HP1 if evidence shows that another approach is more technically appropriate.

## 3. Harry Potter / Argonaut reverse engineering

### PS1-Argonaut-Reverse

Useful because it documents and extracts data formats associated with Argonaut PS1 titles including Harry Potter.

Areas of interest include:
- WAD structure
- textures
- sound
- models
- animation
- actors
- level data
- rendering/portal-related sections

Repository:
- https://github.com/OverSurge/PS1-Argonaut-Reverse

This work is primarily valuable for understanding game data and future tooling/modding. It does not replace executable reverse engineering.

### Hagrid

Tool/research focused on Harry Potter archive handling, including `POTTER.DAT` / `POTTER.DIR` extraction/repacking.

Research page:
- https://fhoughton.github.io/posts/potter/

Potential value:
- archive structure
- reproducible extraction/repacking
- identification of unusual/test content useful for understanding game data

### hptools

Repository:
- https://github.com/joshbarrass/hptools

Potential value:
- Potter archive/image tooling
- practical evidence that retail data can be extracted, modified and reconstructed

### HP1-PS1-Tools

Repository:
- https://github.com/mateusfavarin/HP1-PS1-Tools

Potential value:
- language/text/texture extraction research

## 4. Croc as an Argonaut reference

### Croc decompilation

Repository:
- https://github.com/Xeeynamo/croc

The European demo `SLED-00038` is particularly valuable because the decompilation project uses preserved symbols from that build.

Croc is **not assumed to share identical code with Harry Potter**. It is useful as an Argonaut technology reference only where binary/code/data evidence supports a relationship.

Research questions:
- Are function-level patterns recognizable across titles?
- Do naming conventions expose useful subsystem terminology?
- Which rendering/actor/data structures survived into later Argonaut engines?
- Can known compiler/toolchain behavior help identify HP1 build characteristics?

## 5. Harry Potter 2 as a comparison target

Harry Potter and the Chamber of Secrets for PS1 is not an initial port target.

It is valuable because it may preserve related:
- engine architecture
- file/data formats
- actor systems
- loading systems
- rendering conventions
- gameplay subsystems
- function implementations

Methodological rule: similarity must be demonstrated before labels or structures are transferred from HP2 to HP1.

## 6. PS1 reverse-engineering environment

### Ghidra + ghidra_psx_ldr

Repository:
- https://github.com/lab313ru/ghidra_psx_ldr

Expected uses:
- PS-X EXE loading
- MIPS disassembly/decompilation
- PS1-specific structures/import knowledge
- PsyQ/object/library-related analysis where supported

### PCSX-Redux

Expected role:
- debugging the original game
- memory inspection
- execution tracing/breakpoints
- reference behavior for difficult recompilation bugs

### DuckStation

Expected role:
- fast visual/gameplay reference
- convenient original-game playthrough comparison

PCSX-Redux should remain the more technical reference when low-level state matters.

## 7. Disc tools

### mkpsxiso / dumpsxiso

Repository:
- https://github.com/Lameguy64/mkpsxiso

Expected uses:
- extract disc filesystem
- inspect layout
- reconstruct modified/test disc images when legitimate local testing requires it

## 8. Traditional decompilation

A traditional matching decompilation would aim to reconstruct source that can reproduce original MIPS code or the original executable layout closely enough for binary matching.

That is a different goal from producing a native Windows executable.

Current strategy:
- recompilation first for execution
- reverse engineering continuously
- selective clean C/C++ reconstruction when useful
- do not block native-port progress on a complete matching decompilation

## 9. Validation model

For a reconstructed original PS1 function, binary/instruction matching can be meaningful.

For the final Windows executable, byte-for-byte comparison with `SLUS_014.15` is impossible and meaningless because the host architecture and executable format differ.

Useful native-port validation may include:
- repeatable inputs
- visual/frame comparisons
- framebuffer/VRAM state
- selected memory state
- save files
- event/trace comparison

Validation should be proportional to the problem being solved.

## 10. Open research questions

High priority:

1. Does runtime bring-up reveal raw or compressed executable code not visible to the completed filesystem/header scan?
2. How much of HP1 is data-driven versus hard-coded?
3. Which additional PsyQ functions can be identified, given the confirmed mixed component lineage?
4. What are the major runtime dependencies on GPU/SPU/CD-ROM/MDEC behavior?
5. Does HP1 contain a game-specific scripting/strategy VM descended from other Argonaut technology?
6. Which HP2 functions can be matched structurally to HP1?
7. Which Croc symbols/algorithms are genuinely relevant to HP1?
8. Can the known WAD/archive tooling be turned into deterministic asset tests later?

## 11. Confidence convention

Reverse-engineering claims should use one of these labels when uncertainty matters:

- `CONFIRMED` — directly observed or validated
- `HIGH` — multiple strong pieces of evidence
- `MEDIUM` — plausible and supported but not proven
- `LOW` — working hypothesis
- `UNKNOWN` — not yet understood

Avoid giving semantic names to functions solely because they "look like" a subsystem.

## 12. Phase 3 initial source review (2026-09-30)

Primary sources inspected:
- https://github.com/OverSurge/PS1-Argonaut-Reverse — explicitly supports HP1/HP2 asset extraction; format documentation and extraction scripts are relevant, but do not establish executable loading behavior.
- https://fhoughton.github.io/posts/potter/ — documents Hagrid and DAT/DIR structure.
- https://github.com/joshbarrass/hptools — independently documents the DIR structure and archive/image tools.
- https://github.com/mateusfavarin/HP1-PS1-Tools — repository inspected as an additional extraction reference; detailed code audit remains pending.

Hagrid and hptools describe a little-endian uint32 entry count followed by 20-byte records: 12-byte filename, uint32 byte length and uint32 DAT offset. The local 4044-byte POTTER.DIR is consistent with 4 + 202 × 20 bytes. This is a structural consistency check, not a substitute for validating its actual count, offsets and bounds.

The Hagrid article contains an apparent DAT/DIR naming typo in its introductory archive paragraph; use its explicit structure description and independent hptools documentation rather than copying that typo.

Historical scope at the time of this initial review: both SLUS_014.15 and US.GAM were confirmed to have PS-X EXE headers, while their loading relationship was still UNKNOWN. Later static analysis in section 14 established the boot executable's `Load`/`Exec` path to `US.GAM`. Asset extraction research by itself still does not prove overlay behavior or runtime compatibility.

## 13. Local POTTER archive index validation

CONFIRMED on the canonical USA source: POTTER.DIR contains 202 entries, exactly matching its 4044-byte length and the published 20-byte record layout. All indexed byte ranges fit in POTTER.DAT; start offsets are 2048-byte aligned; no duplicate names or overlapping ranges were reported.

| Extension | Entries |
|---|---:|
| BIN | 13 |
| DAT | 1 |
| DEM | 5 |
| IMG | 122 |
| WAD | 61 |

Local CSV inventory is retained outside Git. Language-named BIN/IMG entries include American, English, French, Spanish and other languages. Their presence does not establish selectable languages or completeness of localization in this release. File extensions and level-like names do not by themselves prove semantic roles or executable overlay behavior.

Historical next step, now completed: import SLUS_014.15 and US.GAM as separate PS-X programs using the installed PS1-aware Ghidra loader and verify their memory blocks and entry points. Results are recorded in sections 14–17.

## 14. Initial Ghidra boot and dispatch reconnaissance

Both executables were imported with PSX Executables Loader and PSX:LE:32:default:default. Screenshots confirm initialized CODE ranges SLUS_014.15 [0x00100000, 0x0010D800) and US.GAM [0x00010000, 0x00079000).

HIGH confidence, based on inspected decompilation: SLUS entry 0x00103DDC calls 0x0010014C. That function requests LEGAL.IMG and later invokes named BIOS Load with "cdrom:\\US.GAM;1", followed by Exec with the returned EXEC structure. This established the static boot-to-secondary-executable loading path. Later PCSX-Redux observation confirmed successful loading and execution in the reference emulator environment. The decompiled Load result condition still contains an unaff_s1 artifact.

Evidence boundary: the `Load`/`Exec` relationship is static evidence and its successful path is dynamically observed. Failure handling and exact native-runtime behavior remain unvalidated.

US.GAM entry 0x0005B2C8 calls 0x00010000 after memory clearing and heap initialization. Decompiled heap length 0x76F8C8 and references near 0x807FFFF0 require assembly and runtime-memory scrutiny; do not infer expanded hardware RAM from them.

At 0x00010000, inspected decompilation shows three initial calls (0x00010604, 0x000106CC, 0x000103F0), a permanent outer loop and three indirect dispatch tables indexed by DAT_000775DC:
- 0x0006AFB8: called before the inner loop.
- 0x0006AFF4: called within the inner loop.
- 0x0006AF7C: called within the inner loop; a nonzero return ends that loop.

State-machine interpretation: HIGH confidence hypothesis from control flow. Later bounded inspection established 15 entries per table and resident targets for all entries. A subsequent saved-reference inventory proves that every known direct writer preserves the 0-14 index contract; semantic state names and unresolved indirect writes remain outside that proof.

The function passes either FETHUND.WAD or FESOUND.WAD to 0x0004D700. Both names exist in the validated archive index. It configures subsequent calls with globals near 0x00082456; audio interpretation is plausible but not yet established.

PsyQ analyzer output applies many library signatures, sometimes multiple names/libraries at identical addresses. Treat these as candidates, not unique function identities or proof of an exact PsyQ version. No full-game execution, overlay classification or recompilation feasibility result follows from this analysis.

## 15. Runtime instruction patching and archive streaming

CONFIRMED static assembly at US.GAM 0x00010604: 0x00010608/0x0001060C construct 0x240B0180 in v1. Stores at 0x00010614 and 0x0001061C write it to 0x00056388 and 0x00057F20, respectively. Ghidra's destination annotations show original word 0x240B00EF at both sites. Both locations lie in the initialized executable payload. Instruction encoding changes addiu t3,zero,239 to addiu t3,zero,384. No rendering purpose is inferred from the constants alone. Static recompilation must preserve these writes' instruction effects; no framework handling has yet been validated.

CONFIRMED dynamically on PCSX-Redux build 445 with OpenBIOS and the interpreter CPU: three read-only execution checkpoints around the stores observed the following ordered states during `US.GAM` initialization:

| Checkpoint | `0x00056388` | `0x00057F20` |
|---|---:|---:|
| Before `0x00010614` | `0x240B00EF` | `0x240B00EF` |
| After `0x00010614`, before `0x0001061C` | `0x240B0180` | `0x240B00EF` |
| After `0x0001061C` | `0x240B0180` | `0x240B0180` |

This verifies both store effects and their execution order without suppressing or replacing either write. The trace itself does not establish how a native recompiler handles the modified locations.

Inspection of the pinned PSXRecomp revision `1ec24e9d4915770a313e4fc19fad5430f55b00a2` establishes that the framework has a general mechanism intended to preserve this class of behavior:

- every ordinary 32-bit RAM store passes through `text_guard_note_write` in `runtime/src/memory.c` before updating RAM;
- writes that differ from the registered executable reference image mark the containing text page as modified;
- generated game dispatch entries carry their exact emitted code ranges and call `dirty_ram_text_native_ok_ranges_from` before entering native code;
- a mismatching range is rejected from native dispatch, allowing `dirty_ram_dispatch` to interpret the current RAM instructions instead of executing stale generated C.

Therefore the two HP1 patches do not justify prepatching `US.GAM` or adding game-specific replacements. Later Phase 6 integration linked independent boot and `US.GAM` text references. The generated KUSEG provider gives `0x00056388` and `0x00057F20` separate four-byte compiled entries and exact guard ranges. A real-memory regression with simultaneous primary and secondary reference images proves that an ordinary guest write rejects the modified secondary range while preserving a neighboring exact range and the primary image. The local retail words at both HP1 addresses are `0x240B00EF`, matching the dynamically observed writes to `0x240B0180`. This combined evidence validates the secondary-image fallback contract; broader native gameplay coverage of the affected graphics paths remains part of compatibility testing.

Initialization decompilation at 0x00010604 reports build string "Oct 2 2001", "16:10:55", "special project". Function 0x000103F0 requests REFLECT.DAT and calls 0x00012394 with EA.STR and 0x7E. This associates initialization with the indexed DAT entry and disc movie, without yet proving exact helper semantics.

HIGH confidence streaming interpretation from decompilation:
- 0x00010AF8 accepts a filename, invokes 0x0001108C and combines a CD position with an entry offset at +0x10 divided by 2048. This is consistent with the validated DIR layout.
- 0x00010CDC accepts destination/byte count, copies from buffers using 2048-byte units and advances an index modulo 16. It contains CD-control polling and tracks pending reads.
- Conditional additional sector skips occur when DAT_00078B44 is nonzero. Their purpose remains UNKNOWN.
- Callbacks are registered using symbols at 0x000108AC and 0x00010950; exact API naming remains subject to signature validation.

0x0004D700's decompiled void signature conflicts with its caller's filename argument and the callee 0x00010AF8's string parameter. Preserve this as a calling-convention/type recovery issue until assembly is checked. The decompiler's removed-unreachable-block warnings in 0x00010AF8 are analysis artifacts requiring review, not observed runtime failures.

Historical follow-up, completed in the subsequent passes: both patch destinations were disassembled, archive lookup `0x0001108C` and initialization `0x000109A4` were inspected, and the main dispatch-table targets were classified as resident code.

## 16. Recovered rendering routines and corrected archive analysis

Writable-memory correction: Ghidra initially imported CODE and upper RAM without W. After setting both writable in US.GAM, 0x000109A4 correctly decompiled allocation/reading of DAT_00078B68 × 20 bytes after reading the four-byte DIR count. Previous zero-size reads were erroneous constant-folded analysis results. Retail bytes were not modified.

Assembly confirms 0x0001108C is an actual self-jump plus nop. It is called on the filename-not-found paths of 0x00011094 and 0x00010AF8. Both search the DIR table with 12-byte strncmp and 20-byte strides. In 0x00010AF8 the branch at 0x00010BA0 skips the error path when an entry is found; the earlier apparent unconditional stop was misleading decompilation.

The undefined data definitions at patch destinations were cleared and those bytes disassembled into functions, without patching retail bytes:
- 0x00056388: GTE projection, projected coordinates/depth, output flags and color processing.
- 0x00057F20: GTE projection, projected coordinates/depth and output flags.

Both use original immediate 0xEF (239) in a comparison against the derived vertical screen coordinate, alongside horizontal bound 0x1FF (511). HIGH confidence: the writes in 0x00010604 change the vertical comparison bound to 0x180 (384). This establishes the patch's role in these comparisons, not the complete display mode or exact visual effect. Runtime execution is observed, and Phase 6 subsequently validated exact-range fallback for both generated secondary-image entries. Do not permanently change the original instruction words to bypass self-modifying behavior.

## 17. Complete main dispatch tables from original US.GAM

CONFIRMED by direct little-endian reads and bounded surrounding-data inspection: each table contains 15 entries, covering indices 0–14, and all 45 targets lie inside the resident US.GAM load interval `[0x00010000, 0x00079000)`. The bases are separated by exactly `0x3C` bytes; the word following the third table is not another code pointer. The main loop indexes these tables through `DAT_000775DC` without a local bounds check. The saved direct-reference producer graph is now proven to preserve values 0–14; dynamic observation remains useful for unresolved indirect writes or memory corruption.

A later bounded reference scan completed the saved-database write inventory for `DAT_000775DC`: 14 direct write sites lie between `0x000243F0` and `0x00026568`. Bounded decompilation of the containing dispatch handlers then recovered the register provenance lost when those sites were decompiled individually. Every direct constant written to the active state lies in the table range (states 2, 3, 5, 6, 11, 12 and 14), and the initialization path writes 11. The remaining transitions copy `DAT_000775E4`. Its complete saved-reference inventory contains 24 writes: all direct assignments are constants from 2 through 14, while its sole non-constant assignment copies an active state selected on the same bounded path. Therefore the saved direct-reference producer graph preserves the 0-14 table contract. Dynamic observation is still appropriate because static reference inventories cannot exclude unresolved indirect writes or unrelated memory corruption; the main-loop dispatch itself has no local bounds check.

| Index | 0x0006AF7C | 0x0006AFB8 | 0x0006AFF4 |
|---:|---|---|---|
| 0 | 0x000241C4 | 0x000262D0 | 0x00026CA0 |
| 1 | 0x000243E8 | 0x00026398 | 0x00026E4C |
| 2 | 0x00024418 | 0x00026458 | 0x00026E54 |
| 3 | 0x00024790 | 0x000264F4 | 0x00027028 |
| 4 | 0x00024A0C | 0x00026734 | 0x00027028 |
| 5 | 0x00024AFC | 0x00026764 | 0x0002774C |
| 6 | 0x00025104 | 0x00026864 | 0x0002777C |
| 7 | 0x00025164 | 0x000269BC | 0x000279C8 |
| 8 | 0x0002516C | 0x000269C4 | 0x000279D0 |
| 9 | 0x000254EC | 0x00026AAC | 0x000279F0 |
| 10 | 0x00025500 | 0x00026ABC | 0x000279F8 |
| 11 | 0x000241CC | 0x000262D8 | 0x00026CA8 |
| 12 | 0x0002574C | 0x00026AC4 | 0x00027A00 |
| 13 | 0x00025508 | 0x000268E4 | 0x000277AC |
| 14 | 0x00025C44 | 0x00026C10 | 0x0002832C |

Indices 3 and 4 in the third table share 0x00027028. No semantic state labels have been assigned.

## 18. Phase 3 closure and validation boundary

Phase 3 completed on 2026-10-01 under the bounded mixed working method. Its exit criteria are satisfied: both executable memory maps and their loading relationship are documented; bring-up risks are explicit; and reusable function, reference, map and Strategy-symbol seeds are available.

An independent run of PS1Recomp `ps1Analyzer` revision `ab4f0e01e6699c741bbc3d1ee73022be2803ff69` reported 1,593 functions and 103 PsyQ matches for `US.GAM`, and 227 functions and 57 PsyQ matches for `SLUS_014.15`. These counts use that analyzer's recovery methodology and do not replace the saved Ghidra database counts. Outputs remain outside Git under the agreed retention policy.

The analyzer's disc scan found `US.GAM` as the only additional standalone executable candidate among the eight filesystem files. Direct byte searches found `PS-X EXE` only at offset zero of `SLUS_014.15` and `US.GAM`, not inside `POTTER.DAT`; all 13 archive members with a `.BIN` suffix are language resources. This is strong negative evidence against another ordinary headered executable overlay. It does not exclude raw or compressed MIPS embedded in a WAD/DAT member, because the scanner skips some data extensions and large files and no runtime trace has covered the full game.

Exact full or masked function hashes against the analyzer signature sources produced 56 source-qualified matches. They indicate mixed PsyQ component lineage rather than one defensible SDK release: several `libcd` routines narrow to 4.4/4.6, modern `libgpu` matches are compatible with 4.3 or later, and several `libgte` routines match 3.3 sources. The 2001 game build timestamp does not identify the SDK. Function-level library matches are usable; a single exact PsyQ version remains intentionally unclaimed.

At Phase 3 closure, confirmed evidence included both executable layouts, the dynamically observed boot-to-`US.GAM` chain, validated POTTER archive bounds and streaming code, ordered execution of both instruction writes, complete resident main dispatch tables, the Strategy interpreter and initial symbol seed. Later phases closed the saved direct-reference index contract, secondary-image registration and exact dirty-text fallback. Broader execution can still reveal raw/compressed dynamic code, archive/runtime edge cases or audiovisual synchronization failures. No HP1 native compatibility conclusion followed from completing reconnaissance alone.

## 19. Read-only structural export

`tools/ghidra/ExportProgramFacts.java` was verified against both saved programs using Ghidra 12.1.4 headless with `-readOnly -noanalysis`. The exporter records program identity, memory blocks, functions, Ghidra-recorded call references and all recorded references without decompiling functions or starting Auto Analysis.

The exporter was subsequently extended to include saved non-dynamic symbols and labels in `symbols.csv`. A read-only verification against the symbolized Croc demo exported 4,250 symbols, including 268 names beginning with `st`; this captures imported handler labels that Ghidra does not represent as independent functions. The output enables reusable opcode/name mapping without manual table copying.

| Program | Functions | Call references | All references | Memory blocks |
|---|---:|---:|---:|---:|
| SLUS_014.15 | 404 | 556 | 4,588 | 26 |
| US.GAM | 1,206 | 3,414 | 30,932 | 26 |

Both exported SHA-256 values match the canonical executables recorded in [Phase 2 source identity](docs/phase2-disc.md). Known saved functions in US.GAM, including the entry point and previously inspected initialization/archive functions, are present in the export.

Scope: these counts describe the current saved Ghidra databases. They do not prove that all functions, indirect calls or runtime-loaded code have been discovered. Unresolved indirect targets remain unresolved; the exporter does not infer them.

Operational constraint: the local desktop Ghidra project and headless analyzer cannot hold the project lock concurrently, even when headless uses `-readOnly`. Close the desktop project during export. Outputs are retained outside Git under `C:\path\to\HP1-work\exports`: the latest provisional export plus logs for the latest three executions, with unique evidence preserved separately before rotation.

## 20. Argonaut comparison set and public research

CONFIRMED local identity and preparation:

| Reference | Program | Bytes | SHA-256 | Saved functions |
|---|---|---:|---|---:|
| HP2 USA | `SLUS_015.03` | 73,728 | `6912259651239e1690d00c4df69f5471c2fb34f82e9d6b8b323c58870885f41c` | not exported |
| HP2 USA | `US.GAM` | 452,608 | `958fcb959f73c08f88fd8bc66a973cfa7dd10543df62d3110b4413bc2531d51f` | 1,235 |
| Croc European demo | `SLED_000.38` | 139,264 | `ca73d36707d68f263adbc444d46bbe00757b6ca353853e9c588277edab40138d` | not exported |
| Croc European demo | `CROC.EXE` | 411,648 | `68aa6147d8d28a715dd456ad81783860ca16eb6de464f68cf91fdd5e1f471f6a` | 1,279 |
| Aladdin USA | `SCUS_945.69` | 464,896 | `6f88e1152a597971be8539e027775bd15fad94a3fa5e67079f421850b4485a2e` | 1,085 |

The HP2 programs, both Croc demo programs and Aladdin program were imported and analyzed in separate local Ghidra projects. `CROC.SYM` imported successfully into `CROC.EXE`; all 1,279 exported functions have descriptive names, including `stProcessStrategies`, `stEvaluate`, `stResolveReferences`, `PreLoadStrats`, `StartLoader`, `MakeDirectoryQuickTable` and `MapLoad`. `DEMOFMV.SYM` remains intentionally unapplied until a corresponding program is established. Exports used the repository's read-only, no-analysis exporter and are retained outside Git.

Public evidence establishes a technology lineage, not binary equivalence. Jez San has stated that Croc engine technology was reused for the two PS1 Harry Potter games, Aladdin and Alien Resurrection. More recent Argonaut material describes Croc 2 as using a different engine from Croc 1. The safe interpretation is evolution and reuse across related branches; every transferred function name or structure still requires local corroboration.

Community documentation consistently groups Croc 2, Aladdin and the Harry Potter games around related DIR/DAT and sectioned WAD formats. HP1/HP2 WADs add `UNIF`, `LPSX` and `PORT` sections to the common texture, sound and data sections. This supports archive and data-format comparison but does not demonstrate executable overlays.

Croc Strategy research documents a function-pointer opcode table and names `stProcessStrategies`/`stEvaluate`. Croc 1 demo instructions are described as byte opcodes, while Croc 2 demo research reports 32-bit opcodes and different program-counter handling. Consequently, HP1's indirect tables are candidates for a related Strategy VM, not proof of one. Stratigise is useful as provisional terminology and format research, but its maintainers warn that current disassemblies can be invalid and that reassembly is primarily Croc-1-specific.

An unaffiliated public analysis describes an attributed Aladdin/Croc 2 source snapshot with functions such as `ReadWad` and a larger Strategy jump table. Its provenance and correspondence to the local retail binary have not been independently verified. Treat its claims as leads only; do not import or redistribute unverified proprietary source or assets.

Key public references:

- https://github.com/Xeeynamo/croc
- https://github.com/OverSurge/PS1-Argonaut-Reverse
- https://github.com/Argonaut-PS1-Reverse/Stratigise
- https://gist.github.com/knot126/bb80efbc838972e8e477ed7eaabdb221
- https://gist.github.com/knot126/e0551e4d88240d7c1476b990d928f4e0
- https://psx-spx.consoledev.net/ps1/cdr/cdromfileformats/archives/
- https://fhoughton.github.io/posts/potter/

Additional developer and Croc 2 sources reviewed:

- https://retrododo.com/lets-talk-retro-with-argonaut-games/ — Jez San states that CrocEd and the CrocStrat creature-behavior language were reused across multiple later games.
- https://www.timeextension.com/features/the-making-of-croc-3d-platformings-unsung-hero — Nic Cusworth states that later Argonaut PlayStation games including Aladdin and both Harry Potter titles used Croc-derived technology and that the scripting language continued throughout Argonaut's lifetime.
- https://gist.github.com/knot126/bc2fe3d7663ac1fdb179efd8cb433fe3 — community-prepared Croc 2 PS1 symbol list, including `ProcessStrategies`, `ReadWad`, many `st...` handlers and `strat_jump_table`. Its key addresses exactly match the on-disc map from the European Croc 2 demo; it is still secondary to that local map.
- https://pastebin.com/Q5aSxcpf — community Croc 2 Strategy list covering opcodes 0–321. It provides a substantially closer naming hypothesis for the later 32-bit Strategy format than Croc 1. Names are accepted for a different build only when code comparison independently supports them.

The Croc 2 list begins with expression/value operations (`stCommandError`, local/global access, arithmetic and comparisons) before movement and gameplay operations. This is consistent with the two-class dispatch structure observed directly in Aladdin, HP1 and HP2, but consistency alone is not sufficient to assign the names. The exact European demo map and local USA retail comparison now provide the required build separation and code fingerprints described below.

### Croc 2 USA retail validation

CONFIRMED local preparation: `SYSTEM.CNF` boots `SLUS_006.34`; the disc also contains the 403,456-byte main program `CROC2.EXE` with SHA-256 `9ab6718001ee0345dcbb5329b3849b5dd653dbac501cbbd84ff1fdca07e0b7b5`. The 163,840-byte boot executable `SLUS_006.34` has SHA-256 `a685d8dd79a37c8b8599ff9adf6ea9e6daebea91ecc5baa1662da5d3b9a112ff`. Both were imported and analyzed in a separate local Ghidra project.

A read-only structural export of `CROC2.EXE` records 1,125 functions, 3,052 non-dynamic symbols, 3,161 call references, 30,916 total references and 30 memory blocks. Direct examination of the original executable finds a clean run of exactly 323 code pointers at `0x80064EBC`–`0x800653C7`, independently matching the publicly reported final Croc 2 Strategy-table size. A separate nearby run at `0x8006493C` contains 70 pointers and requires classification.

The public Croc 2 symbol map places `strat_jump_table` at `0x8006A630`, so it is not address-compatible with this USA retail program and must not be imported directly. A separately preserved European Croc 2 demo provides the missing build identity: its disc includes `CROC2.MAP`, and that map places `ProcessStrategies` at `0x80038404`, `ReadWad` at `0x8001D968` and `strat_jump_table` at `0x8006A630`, exactly matching the previously secondary public symbol list. The public list can therefore be attributed to this demo build, but its addresses remain invalid for USA retail.

The European demo `CROC2.EXE` SHA-256 is `8EECAC736E1DDEBF9739C1ADF1CE912B7C83B7A0EE0B04AE73B9DF0CDE0F3AD2`; `CROC2.MAP` SHA-256 is `2009D7B5FC1256265CA4320DCF3FD447529ABCD5C368FEAD823580E529E11FC0`. The map contains 3,466 parseable address/name records. Importing it into the exact matching executable renamed 628 existing Ghidra functions and created 1,094 labels; 1,724 duplicate records and 20 addresses outside loaded memory were skipped. The resulting read-only export contains 1,095 functions, 4,030 non-dynamic symbols, 3,001 calls and 25,367 references.

CONFIRMED static comparison between the demo table at `0x8006A630` and USA retail table at `0x80064EBC`: both contain 323 entries in corresponding positions. Of the 318 demo entries with a recovered map name, 246 have at least 10 of their first 12 normalized MIPS words matching the retail handler at the same opcode position; 179 entries match all 12 words. This validates a large bounded vocabulary transfer from the exact demo map to retail, while leaving 77 entries unavailable or below the threshold.

HYPOTHESIS boundary for HP1: comparing those 246 validated Croc 2 retail handlers against HP1's 521 Strategy targets produces 63 matches at or above 10 of 12 normalized words, but only 20 select a unique best Croc 2 candidate. Strong unique candidates include arithmetic/logical operations and several waypoint operations. These are prioritization leads, not imported HP1 names: short or repetitive handlers can collide, and semantic or dynamic corroboration is still required before changing the HP1 database.

CONFIRMED static semantics for the first seven unique HP1 candidates after bounded decompilation of complete handlers:

| HP1 opcode | Address | Croc 2 name | HP1 behavior |
|---:|---:|---|---|
| 73 | `0x00055D3C` | `stAdd` | Adds the top two Strategy stack values and pops one operand. |
| 74 | `0x00055D64` | `stSub` | Subtracts the top value from the preceding Strategy stack value and pops one operand. |
| 75 | `0x00055DFC` | `stMul` | Multiplies two signed values, shifts the 64-bit product right by 12 and pops one operand, confirming 20.12-style fixed-point multiplication. |
| 171 | `0x00055E54` | `stInt` | Clears the low 12 fractional bits of the top stack value. |
| 182 | `0x00055E74` | `stOr` | Applies bitwise OR to the top two stack values and pops one operand. |
| 183 | `0x00055ECC` | `stBitwiseAnd` | Applies bitwise AND to the top two stack values and pops one operand. |
| 186 | `0x00055DD4` | `stNotEqual` | Replaces two operands with `1` when unequal or `0` when equal. |

These names now have both cross-build fingerprint evidence and direct local semantics. The bounded decompilation ran against the saved HP1 program with `-readOnly -noanalysis`; temporary function creation was discarded rather than saved. Dynamic validation is not required to establish these elementary operations, but remains required for gameplay-dependent handlers.

A second full-body comparison confirms seven orientation and waypoint handlers:

| HP1 opcode | Address | Confirmed name | Evidence summary |
|---:|---:|---|---|
| 106 | `0x0003A3A4` | `stTurnToPlayerY` | Computes horizontal angle to the global player Strategy and approaches it at the stack-supplied rate. |
| 108 | `0x00039B0C` | `stTurnToX` | Computes vertical angle to a stack-supplied position and rate-limits the X rotation. |
| 109 | `0x00039C14` | `stTurnToY` | Computes horizontal angle to a stack-supplied position and rate-limits the Y rotation. |
| 120 | `0x0003ABA0` | `stWPNearest` | Traverses the waypoint list and selects the entry with minimum squared 3D distance. |
| 122 | `0x00039FF4` | `stWPTurnToX` | Turns the X rotation toward the selected waypoint at a supplied rate. |
| 123 | `0x0003A0B8` | `stWPTurnToY` | Turns the Y rotation toward the selected waypoint at a supplied rate. |
| 193 | `0x0003A504` | `stTurnFromPlayerY` | Matches the player-Y turn routine but reverses the signed step, turning away from the player. |

The full-body pass also demonstrates the limit of short fingerprints. Opcode 336 toggles a global mode and is consistent with `stBinocs`, but remains PROBABLE until the affected state is tied to binocular behavior. Opcodes 354 and 355 select the nearest linked entry using squared horizontal X/Z distance, respectively from the current Strategy and from the player; they are confirmed nearest-waypoint variants but do not yet have exact source names. Three proposed matches were rejected: opcode 507 performs randomized integer selection rather than `stWPNearest`, opcode 494 resolves and draws text rather than `stBinocs`, and opcode 424 configures and emits an object/effect from three stack values rather than using a model bone like Croc 2 `stUseBone`.

The fourteen names confirmed at this comparison stage are stored in the safe machine-readable seed `seeds/hp1-us-strategy.map`; the bytecode pass below extends that seed to seventeen. At this historical comparison point, overlay classification, PsyQ lineage and runtime behavior were unresolved; sections 18 and the runtime observations below record their later bounded resolution.

### HP1 DPSX actor table and Strategy bytecode

CONFIRMED in the local `T1I0M000.WAD` entry without extracting or modifying retail data: its chunk sequence is `XSPT`, `XSPS`, `UNIF` (`FINU` on disc), `LPSX` (`XSPL`), `XSPD`, `PORT` (`TROP`) and `END` (` DNE`). This directly matches the chunked Argonaut WAD family described by PSX-SPX. The WAD starts at POTTER.DAT offset `19154944`; its `XSPD` chunk starts at WAD offset `0x55E84` and has a 36,712-byte payload.

Bounded decompilation of the `DPSX` branch in HP1's level loader (`0x00017754`) establishes the format path rather than relying on an opcode-pattern scan. The loader constructs a level header, finds a fixed-size actor table and relocates each actor's Strategy instruction pointer at actor-record offset `+0x18` by adding the DPSX payload base. `0x00036B54` later walks these `0x40`-byte actor records and passes that relocated pointer directly to the Strategy constructor at `0x000346A8`; the constructor stores it as the instruction pointer consumed by `0x00036EBC`.

For `T1I0M000.WAD`, the DPSX level block is at payload offset `0x7E78`, the level header at `0x7EF4`, and the seven-record actor table at `0x8CE0`. The seven actors reference five distinct non-null Strategy roots:

| Actor(s) | DPSX payload offset | WAD offset |
|---|---:|---:|
| 0 | `0x65A4` | `0x5C430` |
| 1 | `0x6788` | `0x5C614` |
| 2–4 | `0x6A6C` | `0x5C8F8` |
| 5 | `0x7194` | `0x5D020` |
| 6 | `0x7718` | `0x5D5A4` |

The instruction formats exercised by these roots were checked against their local HP1 handlers. Low opcodes `2` and `3` consume a counted event table, opcode `12` consumes two inline words, and control-flow opcodes `16`–`23` use the signed high-half immediate rather than inline data. High opcodes `69`, `177`, `210`, `350` and `435` consume one inline word; opcode `207` consumes two. Opcode `178` restores the instruction pointer from the value stack but has no inline payload. Opcode `177` also converts its inline DPSX-relative value to a runtime pointer in place, which is a confirmed data relocation rather than executable-code modification.

Using only those handler-verified formats, sequential decoding reaches non-opcode data at the following exclusive boundaries:

| Root | Exclusive end | Bytes | Decoded instructions | Boundary word |
|---:|---:|---:|---:|---:|
| `0x65A4` | `0x6770` | 460 | 85 | `0x6C746954` (`Tilt`) |
| `0x6788` | `0x6850` | 200 | 42 | `0x00001000` |
| `0x6A6C` | `0x6CDC` | 624 | 129 | `0x00A29000` |
| `0x7194` | `0x7924` | 1,936 | 381 | `0x0000FD33` |
| `0x7718` | `0x7924` | 524 | 128 | `0x0000FD33` |

The `0x7718` entry is physically nested in the sequential region beginning at `0x7194`, but this does not itself prove shared execution. Context-sensitive traversal below shows that the two roots reach disjoint instruction sets: the earlier root branches around the interleaved entry.

`tools/inspect_dpsx.py` implements the loader-derived traversal and these sequential formats. It accepts either a WAD or a bounded WAD window inside a DAT, reports the actor table, roots and extents, and can emit JSON. It reads retail data in place and does not extract or copy it. Its optional word dump is explicitly raw because some Strategy instructions consume following 32-bit payload words. Archive-index mode reuses the same parser to search selected opcodes across every level-like WAD window without extracting them. An unconfirmed inline or switch layout now closes only the affected control-flow path and is recorded as a bounded stop; reaching the context-state ceiling is reported separately as truncation rather than aborting the entire WAD. The CFG worklist is breadth-first so one recursive actor cannot starve later roots, repeated identical call-site return contexts are pruned and reported, and `--max-cfg-states` permits a deliberately deeper bounded pass when needed.

The reusable transition-producer query is `python tools/inspect_dpsx.py <POTTER.DAT> --archive-index <archive-index.csv> --opcodes 134,135,307,370,513`. Optional `--json` output is local generated evidence and should follow the normal bounded-retention policy.

### First HP1 Strategy control-flow graph

CONFIRMED by handler-derived static traversal of the five `T1I0M000.WAD` roots: calls (`16`, `17`), stack returns (`178`), conditional branches (`18`–`21`), unconditional branches (`22`, `43`) and switch tables (`23`) connect 1,149 distinct instructions through 1,279 edges and 1,599 call-context states. The reached address range is DPSX payload `0x5F48`–`0x7920`. Traversal stops only at `0x7924`, whose low half `0xFD33` is outside the confirmed opcode range; no other malformed or unaligned target was reached.

| Root | Reachable instructions |
|---:|---:|
| `0x65A4` | 414 |
| `0x6788` | 39 |
| `0x6A6C` | 136 |
| `0x7194` | 294 |
| `0x7718` | 266 |

The five reachable sets are disjoint in this static graph. This corrects the earlier physical-layout inference about `0x7194` and `0x7718`: they are interleaved entry regions, not demonstrated shared code. Conversely, the bytecode at DPSX offset `0x61C4` / WAD offset `0x5C050` is now confirmed reachable from actor root `0x65A4` through nested calls. Static reachability does not prove that a particular conditional path occurs during gameplay; that remains a dynamic-validation question.

The tool can write the full graph as machine-readable JSON, as a Graphviz DOT map and as a compact text listing. JSON nodes include the complete handler-verified instruction words and the sequential successor; the listing groups reachable instructions by root and records typed successors. This avoids copying instructions manually while keeping inline operands distinct from opcodes. Root nodes in DOT use a restrained blue fill; calls, returns and branches use distinct muted edge colors. Generated maps and listings remain local provisional outputs rather than committed retail-derived artifacts.

The root prologue handled by opcode `207` also contains a relative pointer to a zero-terminated Strategy name. The tool now resolves these names without hard-coding level-specific offsets:

| Root | Embedded name |
|---:|---|
| `0x65A4` | `LevelSetup` |
| `0x6788` | `TitleScreenCamera` |
| `0x6A6C` | no `207` prologue at this entry |
| `0x7194` | `MusicStreamer` |
| `0x7718` | `StreamBox` |

### `TitleScreenCamera` bounded behavior

CONFIRMED static behavior for the 39-instruction graph rooted at DPSX `0x6788`:

1. Opcode `506` receives fixed-point selector `7` and value `70`, then stores `70 - DAT_0007917C` in the seventh member of a seven-entry panel-graphics state. Its diagnostic string explicitly names unsupported `setpanelgfx` selectors.
2. Opcodes `198`, `180` and `199` register the current Strategy in three engine globals (`DAT_00078A0C`, `DAT_00078A00` and `DAT_00078A14`); two associated runtime flags are set. The exact source-level role names remain unknown.
3. Local slot zero is initialized to `-4096` and later holds the result returned by opcode `209`.
4. Opcode `7` with property index `167` reads global `DAT_0007B568`. A conditional branch waits while it is zero.
5. A six-way switch handles fixed-point values `0x1000` through `0x6000`. Values 1–5 submit request indices 0–4 through opcode `209` and save its returned handle. Value 6 passes the saved handle to opcode `152`. The called subsystem builds and submits command records through a per-bank object and is strongly consistent with starting and stopping sound, but the exact start/stop names remain PROBABLE pending dynamic observation.
6. Every nonzero/default switch path converges on opcode `64`, which pops zero and writes it to `next_instruction + 167 * 4`. At this site, `0x6840 + 167 * 4 = 0x6ADC`.
7. DPSX `0x6ADC` is an instruction reached from root `0x6A6C`, initially word `0x00010014` (opcode `20`, immediate `1`). The write changes the whole word to zero, after which opcode `43` yields and jumps back to the property-167 wait loop.

The cross-Strategy write is CONFIRMED static evidence of mutable interpreted bytecode. It is distinct from the previously observed writes to MIPS instructions: the target lies in the loaded DPSX Strategy data, not in `US.GAM` executable memory. A native implementation that translates Strategy bytecode ahead of time must preserve this mutation or prove an equivalent higher-level state transition. Static reachability proves the path exists; gameplay validation must still establish when the controlling global takes each value.

### `MusicStreamer` bounded behavior

CONFIRMED static structure for the 294-instruction graph rooted at DPSX `0x7194`:

1. The `207` prologue resolves the embedded name `MusicStreamer`. The root initializes local state, saves the Strategy transform through opcode `113`, calls an initialization subroutine, restores/reset state through opcode `114`, yields through opcode `138`, and then enters a persistent loop.
2. The loop derives a selector in local slot 6 and dispatches through a five-case opcode-`23` switch. Every case converges at DPSX `0x739C`, whose opcode `43` yields and returns to the selector loop at `0x7238`. This establishes a five-state streaming controller statically, but does not identify the gameplay meaning of each state.
3. Opcodes `112` and `113` restore and save, respectively, the Strategy position/rotation fields from/to its secondary transform fields. Opcode `114` resets the current linked-record pointer to its base record. Opcode `427` copies the position and rotation of the Strategy registered in `DAT_00078A0C` into the current Strategy.
4. Two spatial predicates contribute to state selection. Opcode `353` tests two stack-supplied coordinates against the rectangle in the selected linked record. Opcode `443` performs the same bounded X/Z test with the position of the Strategy registered in `DAT_00078A00`. The identities of those registered Strategies remain unknown.
5. Opcode `153` occurs in two yielding polling subroutines. It submits an audio request with fixed request-class arguments `(2, 4)`, an ID popped from the Strategy stack and maximum volume `0x7F`, then pushes the returned handle. Opcode `152` is used on existing handles in several transition paths and submits the complementary command identified in the `TitleScreenCamera` pass. This confirms that `MusicStreamer` controls audio handles; exact source-level operation names and audible results remain PROBABLE until runtime observation.
6. Opcode `289` queries the same per-bank command subsystem and pushes either a returned 16-bit value or `-1`. Opcodes `214` and `215` are fixed-point min/max operations, and opcode `225` submits command type 8 using the active bank object, an integer parameter and a fixed-point value. These establish bounded arithmetic and command behavior without yet proving whether the parameters represent track, fade, volume or another audio property.

The static graph therefore supports the embedded name: this Strategy repeatedly chooses among five states using linked spatial records and registered-Strategy positions, starts or queries audio commands, retains returned handles and issues complementary commands during transitions. It does not yet prove which music is selected in each region, the timing heard by a player or the exact meanings of local slots 6–12. Those are focused dynamic-validation targets rather than grounds for stronger static names.

### `StreamBox` bounded behavior

CONFIRMED static structure for the 266-instruction graph rooted at DPSX `0x7718`:

1. The `207` prologue resolves the embedded name `StreamBox`. Initialization calls its setup subroutine at `0x74D4`, then waits through opcode `18` while property 84 remains set before entering the persistent loop at `0x773C`.
2. The initialization subroutine builds a bit mask in local slot 16. Individual actor settings add bits `1`, `2`, `4`, `8` and `0x100`; a four-way switch adds one of `0x40`, `0x20`, `0x10` or `0x80`. Opcode `451` performs the underlying indirect integer addition, while opcode `453` performs indirect fixed-point multiplication. The engine-facing meaning of each bit is not yet established.
3. Properties 36, 37 and 38 are copied into local slots 19, 20 and 21 and then adjusted through linked-record arithmetic. Opcodes `116` and `352` advance the current linked-record cursor by one or by a signed count, wrapping through the linked list. This confirms that the box configuration is backed by a sequence of linked spatial records rather than one flat rectangle.
4. The main loop dispatches local slot 17 through a five-case switch. Two cases directly use opcode `443`, the confirmed test of the registered `DAT_00078A00` Strategy position against the selected record's X/Z rectangle. Other cases query or modify linked-record properties and can turn the Strategy toward the selected waypoint. All ordinary paths converge on opcode `43` at `0x7908`, which yields and returns to the loop.
5. Opcode `157` submits an audio request through the same command pipeline as `MusicStreamer`, but with request-class arguments `(1, 4)`, and stores its returned handle in local slot 18. Opcode `225` submits command type 8 for that active object, opcode `229` submits command type 4 with a converted parameter, and opcode `152` applies the complementary handle command on a terminal transition. Exact source-level command names remain unresolved.
6. A terminal path at `0x790C` yields once, applies cleanup/state flags through opcodes `141`, `179` and `1`, then reaches the graph's sole non-opcode boundary at `0x7924`. Opcode `179` sets Strategy flag bits `0x6`; opcode `1` clears or sets flag `0x01000000` according to its immediate. Static analysis establishes termination mechanics but not the event that selects this path during gameplay.

Together, `StreamBox` and `MusicStreamer` confirm that the title-screen level uses the same linked-region and audio-command primitives in two complementary Strategy roles: `StreamBox` configures and evaluates individual spatial zones while managing an associated audio handle, and `MusicStreamer` uses corresponding region predicates and commands to select transitions. No direct producer/consumer data flow between the two roots has yet been established. Runtime observation is still required to map the five states to concrete rooms, tracks, fades or audible effects.

### First Strategy runtime observation

CONFIRMED dynamically on PCSX-Redux build 445 using OpenBIOS, the interpreter CPU and bounded execution breakpoints:

1. The disc booted as `SLUS01415`; the boot executable loaded `cdrom:\US.GAM;1`, reported `Loaded Ok`, executed it and printed the previously identified `Oct 2 2001 / 16:10:55 / special project` build strings. This validates the static `SLUS_014.15` to `US.GAM` loading chain in this emulator environment.
2. The bounded observer reached `StreamBox` Strategy object `0x000D4EA0`. Two hits of opcode `443` had next instruction pointers `0x000B9994` and `0x000B9AB8`, corresponding exactly to static DPSX successors `0x7770` and `0x7894`. Both independently yield runtime DPSX payload base `0x000B2224`.
3. Local slot 16 held `258` (`0x102`), matching the statically reconstructed configuration-mask composition. Local slot 17 was observed successively as fixed-point states `0`, `0x1000` and `0x3000` at the sampled zone/audio events.
4. Opcode `157` executed at the statically predicted `StreamBox` site with stack input zero, local slot 17 equal to `0x1000` and local slot 18 still zero on handler entry. This confirms execution of the class-1 audio request path, but the returned handle was not sampled after the handler and its audible effect remains unverified.

The observer is `tools/pcsx-redux/trace_hp1_strategy.lua`. Its default mode makes no emulated-memory writes, records only distinct snapshots, stops after 200 events and keeps output in the local provisional log. It includes three initialization checkpoints for the executable instruction writes in addition to the eight Strategy checkpoints. The first unattended Strategy run produced three distinct events and was stopped after the address correspondence was established.

A subsequent opt-in controller-input pass issued a bounded `Start`, `Start`, `Cross`, `Cross` sequence and reached the next title-screen state without memory modification. CONFIRMED dynamic observations from that pass:

1. `MusicStreamer` executed as Strategy object `0x000DB208`; `StreamBox` executed as `0x000DB09C`. Their next-instruction addresses consistently give the newly loaded DPSX payload base `0x000B8820`.
2. `MusicStreamer` local slot 6 changed from fixed-point `0x1000` to `0x2000`. Opcode `289` executed along the statically predicted query paths, and opcode `153` submitted its class-2 audio request with ID zero.
3. The immediately following opcode-`65` store placed returned value zero in `MusicStreamer` local slot 7. `StreamBox` submitted its class-1 request with ID one and likewise stored returned value zero in local slot 18. Zero is therefore an observed returned handle value in this run, not evidence of a failed request; the handlers use `-1` as their static failure sentinel.
4. Strategy object `0x000DB7B8` executed opcode `64` with immediate `167`, next instruction `0x000BF060` and stack value zero. The confirmed handler target is `0x000BF060 + 167 * 4 = 0x000BF2FC`, exactly `0x000B8820 + 0x6ADC`. This dynamically validates execution of the `TitleScreenCamera` cross-Strategy write predicted by the static graph.

The automated input is deliberately opt-in and affects only the virtual controller. Exact track identity, audible transition timing and the meaning of the two fixed-point states remain pending audiovisual correlation. A separate earlier opcode-`64` hit with immediate 167 targeted data outside the sampled `T1I0M000` mapping and remains unclassified rather than being folded into this result.

### First manual audiovisual reference pass

CONFIRMED dynamically in a separate manual PCSX-Redux build 445 pass with OpenBIOS, Dynarec CPU and the XA decoder enabled:

1. The game progressed from the EA logo to the three-language selector. Selecting the USA flag with Cross reached the title screen.
2. Cross at the title screen selected Start Game. The game completed its memory-card check, displayed the no-save/create-card prompts and accepted the choice to continue without creating a save.
3. Music and interface audio were audible through the language, title and memory-card flow. The EA-logo audio was degraded or intermittent.
4. The opening story sequence began and reached the illustrated Privet Drive page with the subtitle `There was nothing about the starry sky that night to suggest that strange and mysterious things would soon be happening.` The lamp highlight remained animated, so display updates continued, but no narration was audible and the sequence did not advance further during the observation period. Start, Cross and directional input did not change this state.

This establishes a visible behavioral boundary: ordinary menu audio and interaction work before the transition into introductory streamed media, while narration/progression fails in this PCSX-Redux configuration. It does **not** yet prove whether the cause is XA/CD-ROM delivery, media timing, OpenBIOS, another emulator limitation or game-side synchronization. The result is a diagnostic reference for later traces, not evidence of a defect in the original game or a native recompilation.

The archive index separates this storybook sequence from the earlier EA logo. `MOVIES/EA.STR` is a standalone disc file reached before the language/menu flow, whereas `POTTER.DIR` contains 64 consecutive `STORY*.IMG` entries, each 123,392 bytes, covering 7,897,088 indexed bytes. The illustrated frame observed manually belongs to this story-image family rather than `EA.STR`. The degraded EA-logo audio and the later silent/stalled storybook sequence must therefore remain two distinct observations. This finding motivated the bounded caller and state analysis recorded below. The narration source and event that advances between story images remain unknown.

Bounded read-only decompilation now identifies the story-image path:

1. `0x00014208` is the sole direct user of the `STORY%d.IMG` format string at `0x00077874`. It substitutes global index `0x00078E8C` and supports three image-placement modes. Mode 1 loads both the selected story image and `PAGE.IMG`; modes 0 and 2 load the selected story image with alternate placement parameters.
2. `0x000124A0` resolves the archive name through `0x00011094`, drives an asynchronous operation through `0x0004CA30` until states 4 and 5, and transfers two image regions through `0x00059080`. The observed first story frame therefore shows that at least one complete name-resolution/load/upload path succeeded.
3. `0x00014CA8` controls the page transition mesh. Its transition value at `0x00078E90` moves between 0 and `0x800`; on the reverse transition from `0x800` it invokes story-loader mode 2. It clears several completion/control flags but does not directly increment the story index.
4. The main per-frame path `0x00027028` calls the story renderer `0x000155F8` whenever the story index is not `0xFF`. The level loader initializes the index to `0xFF`, so entering story mode requires a later indirect or data-driven update.

No direct writer outside level initialization appears in the saved Ghidra reference export for the story index or the transition-start flag. This is consistent with, but does not prove, Strategy/property-based indirect control. The next focused runtime trace should record entry to `0x00014208`, changes to `0x00078E8C`, `0x00078E90` and flags `0x00078E99`–`0x00078E9C`, plus the associated audio request. That trace can distinguish a missing transition trigger from an audio-completion wait without tracing the whole game.

The now-reachable run at WAD offset `0x5C050` contains `65(1), 6(44), 68(0x5000), 73, 4(1), 432, 6(49), 68(0x5000), 73, 69, ...`. It is not an independent actor root; control-flow traversal reaches it as called code from root `0x65A4`. Bounded decompilation confirms the individual instruction semantics represented in the run:

| Opcode | Address | Confirmed behavior |
|---:|---:|---|
| 4 | `0x0003E8EC` | Pushes `local[immediate]` onto the Strategy value stack (`stLocal`). |
| 6 | `0x0003E878` | Pushes `global[immediate]` onto the Strategy value stack (`stGlobal`). |
| 65 | `0x0003EC78` | Pops one value into `local[immediate]`; exact original name remains unknown. |
| 68 | `0x0003E7CC` | Pushes the signed 16-bit instruction immediate; exact original name remains unknown. |
| 69 | `0x0003E7A8` | Consumes the next full 32-bit word and pushes it (`stNumber`). |
| 73 | `0x00055D3C` | Pops two values and pushes their sum (`stAdd`). |
| 432 | `0x00040360` | Pops the value, then an encoded address, and writes the value to `encoded_address >> 10`; exact address convention and original name remain unresolved. |

The confirmed actor roots are the first loader-derived HP1 Strategy entry points rather than executable-table inference or pattern matching. They establish stack-based expression evaluation, local/global access, short and full-width constants, arithmetic and indirect writes in real level data. They do not yet establish every procedure/event boundary or the meaning of referenced variables. `stLocal`, `stGlobal` and `stNumber` have direct semantics and matching Argonaut vocabulary and are included in the symbol seed; the three still-unnamed handlers are deliberately excluded.

### Croc demo Strategy dispatch baseline

CONFIRMED static evidence from the symbolized European demo `CROC.EXE`: `stProcessStrategies` repeatedly reads the byte at the current Strategy instruction pointer and uses it directly to index `strat_jump_table`, passing the Strategy object to the selected handler. Processing continues until flag bit `0x2` is set. This independently corroborates the public description of the Croc 1 Strategy interpreter.

`strat_jump_table` starts at `0x8006AC70` and contains exactly 256 consecutive aligned pointers into initialized executable code, covering every byte opcode from `0x00` through `0xFF`. The table ends at `0x8006B070`; the following word is not another code pointer. Symbol-backed examples include `0x00 stCommandError`, `0x01 stLoadObject`, `0x02 stLoadSprite`, `0x03 stLoadAnim`, `0x0B stPlayAnim`, `0x15 stIf`, `0x16 stElse`, `0x1C stProcCall` and `0x1E stGoto`.

The same function contains a separate indirect table referenced as `PTR_LAB_80010900`, guarded by an index below 12. Its role is not established and it must not be conflated with the 256-entry Strategy opcode table. Later HP1, HP2 and Aladdin comparison, recorded below, established an evolved 32-bit instruction format and split dispatch design. The absence of Croc's exact byte-indexed signature therefore did not rule out the shared Strategy lineage.

### HP1 Strategy interpreter evidence

CONFIRMED static evidence in HP1 `US.GAM`: function `0x00036EBC` processes a structure containing an instruction pointer and flags. Unless a 16-bit delay/count field is nonzero, it repeatedly reads one 32-bit instruction word, advances the instruction pointer by four bytes, uses the low 16 bits as an opcode and dispatches indirectly. Opcodes below `0x45` index the table at `0x0006B7E0` and pass the instruction's signed high 16 bits as a second argument. Higher opcodes index the table at `0x0006B0D0` after subtracting `0x45`. Processing stops when flag mask `0x12` becomes nonzero. Structure-field semantics and individual opcode names remain unknown.

This is strong direct evidence that HP1 contains an evolved Argonaut Strategy interpreter and matches the public observation that the later engine uses 32-bit instructions rather than Croc 1's byte opcodes. It does not establish source-level identity with Croc 2 or Aladdin.

The top-level pointer run beginning at `0x0006B0D0` contains 549 consecutive code pointers, but the interpreter splits it at `0x0006B7E0`: the first region contains 452 pointers, while the second begins 452 entries later. Contiguity alone must not be treated as one logical table; precise bounds for the second dispatch class remain unproven.

CONFIRMED in HP2: function `0x0003C1BC` has the same decompiled logic, fields, masks, `0x45` threshold, 32-bit instruction format and dispatch order as HP1 `0x00036EBC`. Both functions are 224 bytes. Direct comparison finds 52 of 56 MIPS words identical; the four differing words encode relocated jump targets and the two table addresses. This is binary-level evidence of a shared implementation, not merely a similar design.

HP2's first dispatch region spans `0x0007007C` to `0x000707B4`, or 462 pointers, compared with 452 pointers between HP1's corresponding addresses. The low-opcode branch can index only 69 entries (`0x00`–`0x44`), so the additional 28 contiguous pointers after that logical table are unrelated or require separate classification. This supports ten additions to the high-opcode region in HP2; individual opcode identities remain to be established.

CONFIRMED in Aladdin USA: `0x8003A8B0` implements the same 32-bit Strategy instruction format and `0x45` two-class dispatch. It reads the low 16-bit opcode, passes the signed high 16 bits to low-class handlers, advances the instruction pointer by four bytes and loops until flag mask `0x12` is set. Its structure flags are at word index `0x34`, versus `0x27` in HP1/HP2, and it lacks their additional delay/count branch, showing a related but earlier structure and control path rather than an identical binary function.

Aladdin's high-opcode table spans `0x800726FC` to `0x80072CB0` and contains 365 pointers. Its low-opcode table contains the 69 entries selected by opcodes below `0x45`. The combined logical opcode space is therefore 434 entries, covering opcodes `0` through `433`; this likely explains the public description of a 433-entry Aladdin jump table if that value referred to the highest opcode rather than the count. HP1's corresponding layout supports 521 opcodes (`0`–`520`) and HP2 supports 531 (`0`–`530`), subject to later validation of the high-class table endpoints and scripts that exercise the upper ranges.

### HP1/HP2 Strategy handler comparison

A bounded positional comparison covered all 521 opcodes shared by HP1 and HP2. For each table target, the first 12 MIPS instructions were compared using an instruction-shape normalization that preserves opcodes/register fields while ignoring immediate values and absolute jump targets. Results: 462 opcodes matched all 12 normalized instructions, 466 matched at least 10, 473 matched at least 8 and 48 matched fewer than 8. This strongly supports stable opcode numbering and shared handlers for most of the table, but it is not semantic equivalence proof: short handlers, branches into shared code and ignored immediates require individual review.

HP2-only table entries are opcodes 521–530, targeting `0x00046034`, `0x00045CDC`, `0x00046590`, `0x0004662C`, `0x00058FBC`, `0x00058FD8`, `0x000466DC`, `0x00046328`, `0x00046774` and `0x00046718`. Their behavior and names remain unknown. At this checkpoint, Ghidra represented Strategy handlers primarily as labels rather than independent functions, so the function-only structural export could not name or bound them. The existing exporter was subsequently extended to include non-dynamic symbols and data labels instead of creating a separate one-off tool.

With symbol export added, all 256 Croc dispatch entries resolve to imported names (209 unique handler names). An all-pairs Croc-to-Aladdin comparison tested the first 12 normalized MIPS instructions of every handler. No Aladdin handler produced a unique Croc match at the strict threshold of at least 10/12 instructions. Croc names therefore must not be transferred mechanically to the later opcode tables; they remain vocabulary and focused comparison leads only.

### Level-transition and loading pipeline

CONFIRMED static evidence from bounded read-only decompilation: main state 3 uses `0x000264F4` as its entry coordinator and `0x00027028` as its per-frame path. The coordinator performs prior-level cleanup, optionally selects and uploads a loading image, calls the WAD loader at `0x00017754`, records the newly active location tuple and then reinitializes Strategy and other resident subsystems. The tuple passed to the loader contains four independent fields. Its fourth field selects the filename family: `0` formats `T%dL%dM%03d`, `1` formats `T%dB%dM%03d`, `2` formats `T%dS%dM%03d` and `3` formats `T%dI%dM%03d`; the WAD suffix is appended separately. On successful load, the first, second, third and family fields are retained in globals at `0x0007B5E8`, `0x0007B5DC`, `0x0007D338` and `0x0007C800` respectively.

`0x00010AF8` resolves the requested basename against the in-memory `POTTER.DIR` index, converts the selected entry offset to a CD sector and installs the streaming callbacks. `0x00010CDC` synchronously copies requested bytes from the 16-slot, 2,048-byte sector ring while advancing the read position, and `0x00010CAC` removes the callbacks. The WAD loader waits ten vertical syncs before opening the entry, reads tag/length pairs and handles the known on-disc chunk tags `TROP`/PORT, ` DNE`/END, `XSPD`/DPSX, `XSPL`/LPSX, `XSPT`, `XSPS` and `FINU`/UNIF. Its DPSX path performs the actor and Strategy relocations documented above. Unknown chunks are skipped by their recorded length, with an oversized-chunk diagnostic above 2 MiB.

Loading-screen selection is a separate data-driven path. `0x00026120` starts with `LOAD4.IMG` as a fallback and scans 49 fixed 20-byte rules at `0x00077BFC`. The rules match the three destination fields and may additionally require an exact three-field origin. They select among 30 distinct image names: `LOAD1` through `LOAD8`, `LOAD10` through `LOAD28`, plus `QUID_127`, `QUID_128` and `QUID_129`. The canonical archive contains those resources and the separately referenced `LOAD9.IMG`; all 31 are 262,144 bytes. The 49 selector rules comprise 37 single-choice entries, four three-choice entries, one first-load-dependent two-choice entry and seven exact-origin overrides. `LOAD9.IMG` is referenced outside this table by the state-14 entry path.

`0x00011700` opens the selected archive entry, allocates and reads `0x3C000` bytes, then uploads a `0x200` by `0xF0` image to both display pages before freeing the buffer. The archive files are `0x40000` bytes each, so the remaining file data is not part of that framebuffer upload. `0x0002A2C8` initializes the surrounding transition-effect callback and `0x00028734` exposes its completion flag to state handlers. Exact visual names for each transition mode remain unproven.

The canonical archive index contains 59 matching level/introduction WADs: five `I`-family entries and 54 `L`-family entries. Although the loader also supports `B` and `S` filename formats, no matching `T*B*M*.WAD` or `T*S*M*.WAD` entry exists in the canonical index. This is confirmed format capability, not evidence that those absent families are used dynamically. The 49 loading-image rules describe presentation choices, not a complete directed level graph: several transition destinations are written by state or Strategy data outside this table, and later-game runtime coverage remains pending.

The direct producer inventory separates four Strategy operations from the ordinary state and save/load paths. Opcode `134` copies the current `0x580`-byte game-state block at `0x00082404` to the secondary block at `0x00082984`; opcode `135` selects transition state 5 and restores that block, although no reachable opcode-135 site remains after the terminal-flow correction below. Opcode `370` saves the previous four-field location tuple, pops three fixed-point values, shifts them by 12 and installs them as a new family-0 destination before selecting transition state 7. Opcode `513` pops one fixed-point value, splits its integer part into decimal hundreds/tens/ones, uses those digits as a family-0 destination (with a zero hundreds digit preserving the first field) and selects transition state 10, 7 or 11 according to the current tuple and zero-value cases. Opcode `307` installs the fixed family-0 destination `(4, 1, 1)`, but no reachable use was found in the bounded archive pass.

A read-only archive-index pass inspected all 59 matching WAD windows with zero file-level errors. Focused decompilation established that opcode `179` sets Strategy flags `0x6`; the main Strategy loop sends any object with flag `0x4` directly to the destruction routine instead of interpreting it again. Treating opcode `179` as a CFG terminal removes false fallthrough into adjacent actor roots. Breadth-first root scheduling and explicit pruning of repeated call-site return contexts then prevent recursive actors from consuming the whole bounded worklist. A 100,000-context pass finds 63 opcode-134 sites, no opcode-135 or opcode-307 site, 25 opcode-370 sites and 269 opcode-513 sites: 357 reachable producers in total. Fifty-four WADs contain at least one bounded stop, but only `T1L1M003.WAD` still reaches the context-state ceiling, and root-isolated traversal attributes that growth solely to `MadameHoochTraining`. A targeted one-million-context pass expanded internal coverage from 2,091 to 2,347 nodes without adding another transition producer. A separate context-insensitive return over-approximation reaches exactly the same three selected producer sites in the handler-verified Quidditch graph—one opcode-134 and two opcode-370 sites—with no additional candidate. This closes the selected-opcode coverage gap within confirmed instruction layouts, but the inventory remains a static lower bound where decoding itself records bounded stops.

The actor constructor and DPSX relocation path establish where compact-transition operands originate. Actor-record offset `+0x1C` is the initial-local count, while `+0x20` is relocated relative to the base at level-block `+8`; the constructor copies those values into the Strategy local array consumed by `stLocal`. Of 269 recovered opcode-513 sites, 268 have one unique adjacent `stLocal` predecessor; the `WizardCardBook` site follows its adjacent opcode-370 tuple operation instead. The direct operands are `local[0]` at 53 sites, `local[1]` at two, `local[10]` at five, `local[12]` at nine, `local[16]` at one, `local[17]` at one, `local[18]` at two and `local[20]` at 195. The inspector follows the actual operand index for each site. It also follows unique constant predecessors into opcode `370`. Three destinations are fully constant on the recovered path: `T1L1M003` to itself, `T1L1M003` to `T1L1M001`, and `T1L2M005` to `T1L2M002`.

Opcode `65` at `0x0003EC78` is the direct current-Strategy local store: it pops one value and writes it to `local[immediate]`. A root-specific scan therefore classifies each actor definition conservatively according to whether that same local has any reachable opcode-65 store in the recovered root graph. Of 527 actor-local definitions feeding opcode `513`, 526 are root-invariant. The remaining `QuidditchDoor` definition in `T1L2M002.WAD` is overwritten on every recovered path to the transition: three mutually exclusive opcode-69/opcode-65 pairs at DPSX offsets `0x90320`/`0x90328`, `0x90330`/`0x90338` and `0x90340`/`0x90348` install fixed-point values `129`, `128` or `127`. These decode to `T1L2M009.WAD`, `T1L2M008.WAD` and `T1L2M007.WAD`. Removing all three stores disconnects the root from opcode `513`, while each store retains a path to it; the initial value therefore cannot reach this call in the recovered graph.

Cross-checking the corrected operand-index and bounded-store values against the canonical archive yields 71 unique opcode-513 source-to-existing-WAD edges: 68 from root-invariant initial definitions and three from the bounded `QuidditchDoor` assignment. No unresolved root-mutable edge remains in this pass, no corrected nonzero value targets an absent WAD, and 30 source WADs expose the opcode-513 zero case, which selects its special transition state rather than a normal destination. Root-invariant and root-bounded are static provenance, not proof that an edge is exercised in gameplay; cross-Strategy writes and the incomplete CFG boundary remain conservative limitations.

Of 25 reachable opcode-370 sites, three use direct constants and six implement the same decimal-split formula as opcode `513`: they derive a triplet from one compact source local, with property `87` supplying the first field when its hundreds digit is zero. Their source locals are invariant and resolve six edges: `T1L3M004` to `T1L3M003`, `T1L4M004` to `T1L8M004`, `T1L8M001` to `T1L3M002`, `T1L8M002` to `T1L2M002`, `T1L8M003` to `T1L1M004` and `T1L8M004` to `T1L4M001`. The prior apparent `TrollChaseTorch` mutation was false reachability past opcode `179`; the valid root is `TrollChaseEnd` with initial compact value `184`.

The remaining non-minecart opcode-370 site is `WizardCardBook` in `T1L1M009`. It consumes locals `[11,12,13]`, populated by fixed-point constants `31`, `32` and `33` followed by opcode `371`. The opcode-371 handler at `0x00037D84` converts its operand to an integer index, calls `0x00017054` and restores fixed-point form; `0x00017054` returns the signed byte at `0x0008245D + index`. The tuple is therefore a dynamic three-byte game-state destination using indices `[31,32,33]`, not an unresolved constant. The inspector now recognizes and reports this pattern automatically.

A follow-up writer inventory found 1,107 opcode-373 sites in the 100,000-context pass. A one-million-context pass reaches the sole additional upper-bound site in the truncated Quidditch WAD, producing 1,108 exact sites with no further opcode-373 site in the context-insensitive upper bound. The resident handler at `0x00037CFC` pops an index/value pair and writes one byte through `0x00016F34`. Initial simple stack provenance resolved 326 constant-index sites and identified 576 further index operands as actor locals. Reusable predecessor signatures then reduced the 206 complex sites to repeated expression families: 94 write `state[local[i]] + 1` back to `state[local[i]]`, 94 write `state[local[i]] - local[n] + 1`, nine write `state[local[i]] - local[n]`, and three minecart sites write `global[118]` to constant byte 30.

Focused read-only decompilation closes the six remaining expression shapes. Opcode `5` pushes a word addressed relative to the already-advanced Strategy instruction pointer; opcode `66` stores a popped value to such a relative slot; opcode `431` dereferences the fixed-point pointer on top of the stack; and opcode `432` stores a value through a fixed-point pointer. Opcode `429` passes an integer size to the same allocation helper used by Strategy construction and returns its pointer in fixed-point form. Opcodes `437` and `506` consume two arguments to configure panel state and do not feed the subsequent write. `QuidditchTrainingSnitch` writes `global[91] - global[90]` to byte 30, while `GoblinDoorUnlocker` writes `property[153] - 1` to byte 30. The two recovered opcode-66 writers feeding `GnomePopcornController` relative slot `0x2A4F4` both store zero, so its later operation is `state[30] = 0` on the recovered root paths.

The three `MadameHoochQuidditchTraining` sites write value 3 to indices obtained by dereferencing words 0, 1 and 2 from the allocation pointer held at relative slot `0x41604`. The straight-line setup immediately before the conditional stores three property-126 results through opcode `432` into those exact words. Property 126 is backed by the state-byte allocator whose range starts at 64, so these three dynamically allocated indices cannot be the global bytes `[31,32,33]`. The resulting recovered inventory has 332 constant indices, 773 actor-local indices, three private allocator-backed indirect indices and no unclassified expression. The five sites in the separately truncated Quidditch WAD are also classified: four write `global[x] - local[n]` to state byte `30`, and one writes `local[10]` to byte `0`.

The only recovered writes to bytes `[31,32,33]` are three zero assignments by `HousePointController` in `T1L3M008`. Every recovered store feeding the original 576 simple local-index operands comes from property `126`, as do the three allocator-backed indirect Quidditch indices. Its native property case calls `0x00016E48`, while `0x00016D58` initializes the byte allocator at `0x40`, so those assignments address actor-private state at index 64 or later rather than the global triplet. This proves that no nonzero producer for `[31,32,33]` exists among the 1,108 recovered opcode-373 sites; it does not prove that an untraversed bounded-stop path or another native mechanism is absent.

The complete `0x580`-byte game-state block at `0x00082404`, including bytes `[31,32,33]`, is copied to and from per-slot storage by `0x00033D80` and `0x00033C2C`; it is also cleared by initialization at `0x00034074`. Static analysis therefore confirms persistence and reset behavior, but has not found a nonzero producer for the `WizardCardBook` triplet. The branch may consume data restored from another state path or may be dormant for the canonical route. Treat both explanations as hypotheses until a producer or dynamic nonzero observation is obtained.

The remaining 15 opcode-370 sites belong to `MinecartEndGoblin` in `T1L7M002`, `T1L7M003` and `T1L7M004`. Each receives direct property loads `[87,88,89]`. The property getter proves that these are the three fixed-point location fields stored in the current game-state block beginning at `0x00082404`; they are dynamic state, not missed constants. Opcodes `373` and `374`, which occur immediately before related transitions, do not synthesize the tuple: their resident helpers respectively write one indexed byte at `0x0008245D` and set or clear a bit in one of two state arrays. The expanded archive map therefore contains 79 unique present static edges: 71 from opcode `513` and nine from opcode `370`, with one edge produced by both mechanisms. The 15 dynamic property-triplet sites and the dynamic `WizardCardBook` state-byte tuple are not counted as fixed WAD edges; all 25 reachable opcode-370 sites now have a static provenance classification.

## Native Phase 6 compatibility evidence

### Intermittent audio starvation

CONFIRMED dynamically in the native Release runtime with the existing two-second performance telemetry: the degraded EA/transition audio coincides with loss of guest cadence rather than a standalone asset decode failure. Healthy intervals sustain approximately 59.9 guest frames/s and 44.05 kHz of generated SPU audio. Repeated affected intervals fall to 31–36 guest frames/s and 23–26.2 kHz while the dirty-RAM interpreter executes approximately 9.5–10.0 million instructions/s. The output buffer falls effectively empty and accumulates roughly 26,000–43,000 underruns per interval. Cadence and audio production subsequently recover together.

This establishes host-side performance starvation as the immediate mechanism for the audible slowdown. It does not identify one source-level routine, prove that every audio deviation has the same cause or prove that the media data and decoder are otherwise perfect.

### Warner-to-EA 24-bit scanout gap

CONFIRMED dynamically: the visible sequence is a correct Warner screen, black, one brief corrupted Warner-like RGB/block frame, black and then the EA movie. A phone capture preserved the transient corruption when desktop capture represented the interval as black.

Bounded GP1 tracing places the display reconfiguration at frames 414–419, including the `0x08000002` to `0x08000011` transition into 24-bit scanout. The first MDEC trace event occurs only at frame 428. The resulting roughly ten-frame pre-MDEC interval explains why a two-present entry blank was insufficient: stale 15-bit VRAM could still be interpreted as packed RGB888 before a valid movie upload arrived.

The first presentation-only candidate held 24-bit output black until the runtime reported non-zero RGB888 upload coverage. Manual validation confirmed that the transient corruption disappeared, but the display stayed black throughout the audible EA movie and recovered at language selection. The MDEC path therefore does not publish the expected coverage signal. The follow-up also releases the wait on confirmed MDEC activity and then applies a two-present settling blank. It does not alter guest RAM, GPU commands or timing. Focused source-contract tests and the Release build pass. Manual validation confirms that the glitch is absent and EA remains visible and audible. A possible slight loading delay or audiovisual offset was uncertain in that single pass and is not confirmed evidence.

### Offline overlay cache boundary

The runtime's additive capture file contained three primary regions, including a `US.GAM` image spanning normalized addresses `0x00010000..0x0006B003`. The existing `compile_overlays.py --check` path successfully emitted and compiled all primary regions with MinGW64 GCC, reporting no unsupported instructions and no unknown/bad targets. The generated ignored cache was discovered by the Release runtime and its DLLs were indexed.

Two measured runs nevertheless reported zero native overlay activations while reproducing the interpreter-heavy slowdown. Recompiling the newly accumulated fragment variants increased the indexed inventory but did not change `native=0`. The exact cause is now CONFIRMED: `US.GAM` executes through KUSEG PCs (`0x000xxxxx`), whereas overlay capture and compilation produce KSEG0 entries (`0x800xxxxx`). `overlay_loader_dispatch` intentionally rejects a KUSEG/KSEG1 alias of a KSEG0 shard because its generated body bakes architectural PC values that affect `$ra`, EPC and instruction-cache tags. The framework's dedicated segment-gate regression test passes. This is therefore an unsupported execution-segment case, not C emission, compilation, cache discovery or CRC failure.

A later 49.5-minute play session added five executable-region captures, but comparison prevents misclassifying the two low-RAM regions as game overlays. The entry at `0x8000281C` exactly matches OpenBIOS ROM offset `0x76F4` and begins an exception-context save path. Entries at `0x8000357C` and `0x8000DFAC` exactly match `US.GAM` file offsets `0x5B184` and `0x5B140`; saved symbols place the source in the imported PsyQ `_patch_card` area, and `_patch_card` writes the continuation pointer at `0x0000DFFC`. These regions are BIOS and memory-card patch handlers copied into low RAM. A third capture at `0x80030000` is byte-identical to canonical `US.GAM`, while the remaining two lie inside the `US.GAM` window and contain live differences. None of the five is evidence for a newly discovered POTTER level overlay.

A bounded debug-runtime profile sampled an 8-second window with 38.9% of wall-time in the dirty-RAM interpreter, 10.0% in statically compiled boot code, 0% in native overlays and 50.7% in host/other work. A later sample after the heaviest interval measured 17.6% interpreter and 17.5% static, consistent with the observed recovery rather than a permanent stall.

The interpreted-entry table localized the largest chains to `0x000598AC` (3,714,260 attributed instructions), `0x0005C868` (1,525,790), `0x00067A38` (1,000,278), `0x0005C538` (775,914), `0x0005B638` (612,143), `0x0005BF2C` (527,518) and `0x0005C5CC` (525,820) in the bounded run. Read-only selected-function decompilation maps those addresses to or inside GPU environment setup, ISO9660 helpers, `_patch_gte`, `VSync` and formatted-output code. These are entry-chain totals: local-flow interpretation can continue far beyond the named function, so the numbers must not be read as per-function self time.

The selected design is a second statically generated provider whose code view preserves the observed KUSEG execution addresses. The original `US.GAM` header remains KSEG0 (`load=0x80010000`, `entry=0x8005B2C8`) and is not modified; only the recompiler's in-memory code-address view is rebased to KUSEG after header validation. The recompiler regression covers KUSEG `JAL` targets and link values, and a real ignored generation produced 2,091 entries over `0x00010000–0x00079000`. The boot and secondary providers now use independent dispatch namespaces behind one segment-aware selector, and the runtime retains separate exact-byte references for both images. A bounded headless run armed `0x00100000–0x0010D800` and `0x00010000–0x00079000`, completed two CD-read bursts and measured 65.82% static execution versus 6.33% interpretation over the final ten-second window. This confirms KUSEG static activation. Subsequent paced visible testing reached several rooms and durable save/reload; full-game performance and audiovisual stability remain Phase 6 work.

### Memory-card validation

CONFIRMED dynamically: the native runtime created 128 KiB card images, presented slot selection and continued normally into the opening sequence after card creation. The tested route crossed several rooms, supported conversations and automatically triggered story scenes before saving on the route to the common room. A later visible test on the linked KUSEG-provider build closed the process, restarted through the same launcher, detected the existing save, showed a loading screen with a moving progress bar and restored that later gameplay position. Brief sub-second pauses occurred during card checking and loading. This closes basic early-route transitions and durable save/restart/load; major level boundaries, corruption resistance and extended multi-slot use are not yet tested.
