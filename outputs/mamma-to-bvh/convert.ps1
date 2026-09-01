param(
    [Parameter(Mandatory = $true)] [string]$InputNpz,
    [Parameter(Mandatory = $true)] [string]$OutputBvh,
    [string]$Blender = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [int]$Fps = 30,
    [double]$RotateZ = 0,
    [switch]$Validate,
    [string]$SaveBlend = "",
    [string]$SaveAmass = ""
)

$ErrorActionPreference = "Stop"
$convertScript = Join-Path $PSScriptRoot "01_convert_mamma_to_amass.py"
$exportScript = Join-Path $PSScriptRoot "02_amass_to_bvh_blender.py"
$validateScript = Join-Path $PSScriptRoot "03_validate_bvh_blender.py"

if (-not (Test-Path -LiteralPath $Blender -PathType Leaf)) { throw "Blender executable not found: $Blender" }
if (-not (Test-Path -LiteralPath $InputNpz -PathType Leaf)) { throw "Input NPZ not found: $InputNpz" }

$resolvedOutput = [System.IO.Path]::GetFullPath($OutputBvh)
$amassPath = if ($SaveAmass) {
    [System.IO.Path]::GetFullPath($SaveAmass)
} else {
    [System.IO.Path]::ChangeExtension($resolvedOutput, ".amass.npz")
}

& $Blender --background --factory-startup --python $convertScript -- $InputNpz $amassPath --fps $Fps
if ($LASTEXITCODE -ne 0) { throw "MAMMA-to-AMASS conversion failed with exit code $LASTEXITCODE" }

$exportArgs = @(
    "--background", "--python", $exportScript, "--",
    $amassPath, $resolvedOutput, "--fps", $Fps, "--rotate-z", $RotateZ
)
if ($SaveBlend) { $exportArgs += @("--save-blend", $SaveBlend) }
& $Blender @exportArgs
if ($LASTEXITCODE -ne 0) { throw "AMASS-to-BVH export failed with exit code $LASTEXITCODE" }

if ($Validate) {
    & $Blender --background --factory-startup --python $validateScript -- $resolvedOutput --fps $Fps
    if ($LASTEXITCODE -ne 0) { throw "BVH validation failed with exit code $LASTEXITCODE" }
}
