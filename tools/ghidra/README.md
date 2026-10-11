# Ghidra structural export

`ExportProgramFacts.java` exports structural information from an already analyzed Ghidra program without decompiling functions or starting Auto Analysis.

## Safety requirements

- Close the desktop Ghidra project before running the headless exporter. A local Ghidra project cannot be opened concurrently by the desktop and headless processes, even with `-readOnly`.
- Always use both `-readOnly` and `-noanalysis`.
- Write generated output outside the Git checkout. The reference workstation uses `C:\path\to\HP1-work\exports`.
- Do not point the output directory at retail data or the Ghidra project directory.

## Invocation

Run one program at a time. Example for the boot executable:

```powershell
& 'C:\path\to\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat' `
    'C:\path\to\HP1-work\ghidra' 'HP1-USA' `
    -process 'SLUS_014.15' `
    -readOnly -noanalysis `
    -scriptPath 'C:\path\to\HP1Recomp\tools\ghidra' `
    -postScript ExportProgramFacts.java 'C:\path\to\HP1-work\exports\latest\SLUS_014.15' `
    -log 'C:\path\to\HP1-work\exports\logs\<run>-headless.log' `
    -scriptlog 'C:\path\to\HP1-work\exports\logs\<run>-script.log'
```

Use `US.GAM` as both the `-process` value and final output-directory name for the secondary executable.

## Outputs

Each program directory contains:

- `program.json` — program identity, hashes, language and counts
- `memory-map.csv` — blocks, ranges and permissions
- `functions.csv` — function entries, names, ranges, signatures and symbol sources
- `symbols.csv` — all saved non-dynamic symbols and labels, including imported debug symbols
- `calls.csv` — recorded call references with callers and resolved target functions where available
- `references.csv` — all recorded references with containing functions where available
- `summary.md` — compact human-readable counts

The export reflects the saved Ghidra database. Indirect targets that Ghidra has not resolved remain absent or unresolved; the exporter does not infer them.

## PsyQ linker-map import

`ImportLinkerMap.java` imports the simple `address name` records present in PsyQ-style linker MAP files. It renames an existing function when a record matches its entry point; otherwise it creates an imported label. Duplicate records, already-present symbols and addresses outside the loaded program memory are skipped and counted, making repeated seed application idempotent. Pass the MAP path as the script's first argument when running headless, or select it in the file dialog when running from Ghidra's Script Manager.

Use a map only with the exact executable build that produced it. Addresses or names must not be transferred to another build without independent matching evidence.

## Bounded decompiler export

`ExportSelectedFunctions.java` writes decompiler output only for the function entry addresses explicitly supplied after its output-file argument. If an address is currently only a label, the script disassembles it and creates a temporary in-memory function for decompilation; run with `-readOnly -noanalysis` so this never changes the saved project. Use it for focused comparison rather than exporting or manually copying an entire program. Generated decompiler text is local working material and must not be committed when it contains game code.

## Retention

Replace the contents under `exports\latest` on the next accepted provisional export. Keep headless and script logs for the latest three executions. Preserve a run separately before rotation only when it contains unique or decision-relevant evidence. Retention cleanup is not automated yet.
