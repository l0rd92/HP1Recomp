param(
    [string]$Version = "",
    [string]$BuildDir = "build-release",
    [int]$Jobs = 8
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
if (-not $Version) {
    $Version = "v" + (Get-Content (Join-Path $Root "VERSION") -Raw).Trim()
}
$GameVersion = $Version -replace '^v', ''
$BuildPath = Join-Path $Root $BuildDir
$StageRoot = Join-Path $Root "release-stage"
$Stage = Join-Path $StageRoot "HP1Recomp-windows-x64"
$ZipPath = Join-Path $Root ("HP1Recomp-{0}-windows-x64.zip" -f $Version)
$MingwBin = "C:\msys64\mingw64\bin"
$Cmake = Join-Path $MingwBin "cmake.exe"
$Objdump = Join-Path $MingwBin "objdump.exe"

function Invoke-Native {
    param([scriptblock]$Command, [string]$Description)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $Command 2>&1 | Out-Host
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $oldPreference
    if ($exitCode -ne 0) {
        throw "$Description failed (exit $exitCode)"
    }
}

foreach ($required in @($Cmake, $Objdump)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Required build tool is missing: $required"
    }
}

$BootDispatch = Join-Path $Root "generated\SLUS_014.15_dispatch.c"
$SecondaryDispatch = Join-Path $Root "generated\secondary\US.GAM_dispatch.c"
if (-not (Test-Path -LiteralPath $BootDispatch) -or
    -not (Test-Path -LiteralPath $SecondaryDispatch)) {
    throw "Generated boot and US.GAM providers are required. Follow docs/build.md with your legal disc before packaging."
}

$env:PATH = "$MingwBin;$env:PATH"
Invoke-Native {
    & $Cmake -S $Root -B $BuildPath -G Ninja `
        -DCMAKE_BUILD_TYPE=Release `
        -DPSX_DEBUG_TOOLS=OFF `
        -DPSX_RECOMP_UI=OFF `
        "-DPSX_GAME_VERSION=$GameVersion"
} "release configure"
Invoke-Native {
    & $Cmake --build $BuildPath --target psx-runtime -j $Jobs
} "release build"

if (Test-Path -LiteralPath $StageRoot) {
    $resolvedStage = [System.IO.Path]::GetFullPath($StageRoot)
    $expectedStage = [System.IO.Path]::GetFullPath((Join-Path $Root "release-stage"))
    if ($resolvedStage -ne $expectedStage) {
        throw "Unsafe release stage path: $resolvedStage"
    }
    Remove-Item -LiteralPath $StageRoot -Recurse -Force
}
New-Item -ItemType Directory -Force $Stage | Out-Null
New-Item -ItemType Directory -Force (Join-Path $Stage "saves") | Out-Null

$ExeNameFile = Join-Path $BuildPath "psxrecomp_exe_name-psx-runtime.txt"
if (-not (Test-Path -LiteralPath $ExeNameFile)) {
    throw "Runtime executable-name manifest is missing: $ExeNameFile"
}
$BuiltStem = (Get-Content $ExeNameFile -Raw).Trim()
$BuiltExe = Join-Path $BuildPath ($BuiltStem + ".exe")
if (-not (Test-Path -LiteralPath $BuiltExe)) {
    throw "Built runtime executable is missing: $BuiltExe"
}
Copy-Item -LiteralPath $BuiltExe -Destination (Join-Path $Stage "HP1Recomp.exe")
Copy-Item -LiteralPath (Join-Path $Root "game.toml") -Destination $Stage
Copy-Item -LiteralPath (Join-Path $Root "README.md") -Destination $Stage
Copy-Item -LiteralPath (Join-Path $Root "RELEASE_NOTES.md") -Destination $Stage
Copy-Item -LiteralPath (Join-Path $Root "packaging\release\START_HERE.txt") -Destination $Stage
Copy-Item -LiteralPath (Join-Path $Root "packaging\release\input.ini") -Destination $Stage

$BiosSource = Join-Path $BuildPath "bios"
$BiosDestination = Join-Path $Stage "bios"
New-Item -ItemType Directory -Force $BiosDestination | Out-Null
Copy-Item -LiteralPath (Join-Path $BiosSource "openbios.bin") -Destination $BiosDestination
Copy-Item -LiteralPath (Join-Path $BiosSource "OpenBIOS.LICENSE") -Destination $BiosDestination
if ((Get-Item (Join-Path $BiosDestination "openbios.bin")).Length -ne 524288) {
    throw "Staged OpenBIOS image is not exactly 512 KiB"
}

$LicensesDestination = Join-Path $Stage "licenses"
Copy-Item -LiteralPath (Join-Path $Root "psxrecomp\runtime\licenses") `
    -Destination $LicensesDestination -Recurse
if (@(Get-ChildItem -LiteralPath $LicensesDestination -File).Count -lt 1) {
    throw "No third-party notices were staged"
}

$imports = & $Objdump -p (Join-Path $Stage "HP1Recomp.exe") |
    Select-String "DLL Name: (.+)" |
    ForEach-Object { $_.Matches[0].Groups[1].Value.Trim() }
$systemDlls = @(
    "kernel32.dll", "user32.dll", "gdi32.dll", "shell32.dll", "msvcrt.dll",
    "advapi32.dll", "ws2_32.dll", "comdlg32.dll", "dbghelp.dll", "ole32.dll",
    "oleaut32.dll", "winmm.dll", "imm32.dll", "version.dll", "setupapi.dll",
    "dinput8.dll", "rpcrt4.dll", "hid.dll", "cfgmgr32.dll", "opengl32.dll",
    "d2d1.dll", "dwrite.dll", "ucrtbase.dll"
)
$nonSystem = $imports | Where-Object {
    $systemDlls -notcontains $_.ToLower() -and $_ -notlike "api-ms-win-crt-*.dll"
}
if ($nonSystem) {
    throw "Release executable imports non-system DLLs: $($nonSystem -join ', ')"
}

$forbiddenPatterns = @(
    "SCPH*.BIN", "*.cue", "*.iso", "*.img", "*.chd", "*.mcd",
    "disc.cfg", "bios.cfg", "settings.toml", "keybinds.ini",
    "overlay_captures.json", "psx_freeze_dump_*.json", "psx_last_run_report.json"
)
$forbidden = foreach ($pattern in $forbiddenPatterns) {
    Get-ChildItem -LiteralPath $Stage -Recurse -File -Filter $pattern -ErrorAction SilentlyContinue
}
$forbidden += Get-ChildItem -LiteralPath $Stage -Recurse -File -Filter "*.bin" `
    -ErrorAction SilentlyContinue | Where-Object {
        $_.FullName -ne (Join-Path $BiosDestination "openbios.bin")
    }
if ($forbidden) {
    throw "Release stage contains private or retail files: $(($forbidden | ForEach-Object FullName) -join '; ')"
}
if (Get-ChildItem -LiteralPath (Join-Path $Stage "saves") -Recurse -File -ErrorAction SilentlyContinue) {
    throw "Release saves directory is not empty"
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    throw "Python is required to create a portable ZIP"
}
$ZipHelper = Join-Path $Root "psxrecomp\tools\create_release_zip.py"
if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}
Invoke-Native {
    & $Python.Source $ZipHelper --source $Stage --output $ZipPath
} "portable release ZIP"

$zipHash = (Get-FileHash -LiteralPath $ZipPath -Algorithm SHA256).Hash.ToLowerInvariant()
"$zipHash  $([System.IO.Path]::GetFileName($ZipPath))" |
    Set-Content -Encoding ASCII -LiteralPath "$ZipPath.sha256"

Write-Host "Verified self-contained executable with $($imports.Count) system DLL import(s)"
Write-Host "Wrote $ZipPath"
Write-Host "SHA256 $zipHash"
