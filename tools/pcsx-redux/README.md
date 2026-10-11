# PCSX-Redux runtime observers

These tools perform focused runtime validation without modifying emulated RAM or
retail game data.

## HP1 Strategy audio/zone observer

`trace_hp1_strategy.lua` installs eleven execution breakpoints for the HP1 USA
`US.GAM`: eight Strategy handlers used by `MusicStreamer` and `StreamBox`, plus
three checkpoints around the two initialization-time instruction writes. It
reports only distinct snapshots and disables itself after 200 events to keep
output bounded. The patch checkpoints capture both destination words before,
between and after the stores without suppressing or replacing either write.

Requirements:

- PCSX-Redux debugger enabled
- interpreter CPU selected (breakpoints are not reliable with the recompiler)
- exact HP1 USA build documented by the project

Load it from **Debug > Lua > Lua Console**:

```lua
dofile([[C:\path\to\HP1Recomp\tools\pcsx-redux\trace_hp1_strategy.lua]])
```

The observer prints to the Lua console and PCSX-Redux's general log. Use
`HP1Trace.status()` to display its bounded event count and `HP1Trace.stop()` to
remove all eleven breakpoints. Runtime output is provisional local evidence and
must not be committed without review for embedded retail-derived data.

The same script can run unattended with PCSX-Redux's `-interpreter`,
`-debugger`, `-dofile`, `-iso` and `-run` options. Use one local `-logfile`
under the provisional export directory and replace it on the next run. The
observer was verified with PCSX-Redux build 445 on 2026-09-30.

For an explicitly automated title-screen pass, set the process environment
variable `HP1_TRACE_AUTO_START=1`. The observer then issues the bounded sequence
`Start`, `Start`, `Cross`, `Cross`, spaced by 120 observed handler hits; each
tap is released after 12 hits. This opt-in mode changes controller input only;
it does not write emulated RAM. Without the variable, the observer remains
strictly observational.
