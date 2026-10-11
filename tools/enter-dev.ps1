# Dot-source from PowerShell: . .\tools\enter-dev.ps1
$mingwRoot = if ($env:HP1_MINGW_ROOT) { $env:HP1_MINGW_ROOT } else { "C:\msys64\mingw64" }
$mingwBin = Join-Path $mingwRoot "bin"
foreach ($name in @("gcc.exe", "g++.exe", "cmake.exe", "ninja.exe")) {
    if (-not (Test-Path (Join-Path $mingwBin $name))) { throw "Missing tool: $mingwBin\$name" }
}
$pythonExe = & py -3.12 -c "import sys; print(sys.executable)"
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $pythonExe)) { throw "Python 3.12 is required." }
$gitCommand = Get-Command git -ErrorAction Stop
$gitRoot = Split-Path (Split-Path $gitCommand.Source -Parent) -Parent
$gitBin = Join-Path $gitRoot "bin"
if (-not (Test-Path (Join-Path $gitBin "bash.exe"))) { throw "Git Bash not found under $gitRoot" }
$env:Path = "$mingwBin;$(Split-Path $pythonExe -Parent);$gitBin;$env:Path"
Write-Host "HP1Recomp development environment activated for this session."
Get-Command python, gcc, g++, cmake, ninja, bash | Select-Object Name, Source
