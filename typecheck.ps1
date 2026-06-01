param(
    [switch]$SkipInstall,
    [switch]$ChangedOnly,
    [string]$BaseRef = "HEAD"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $RepoRoot ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

Set-Location $RepoRoot

if (-not (Test-Path $VenvPython)) {
    Write-Host "[typecheck] Creating virtual environment at .venv"
    py -m venv "$VenvDir"
}

if (-not $SkipInstall) {
    Write-Host "[typecheck] Installing dependencies"
    & "$VenvPython" -m pip install -r requirements-dev.txt
    & "$VenvPython" -m pip install -r cursor-novel-writer/requirements.txt
    & "$VenvPython" -m pip install -r cursor-novel-video/requirements.txt
}

Write-Host "[typecheck] Running pyright with repo config"
$pyrightArgs = @("-p", "pyrightconfig.json")

if ($ChangedOnly) {
    $changedTracked = @(git diff --name-only --diff-filter=ACMRTUXB "$BaseRef" --)
    $changedUntracked = @(git ls-files --others --exclude-standard)
    $changedAll = @($changedTracked + $changedUntracked | Sort-Object -Unique)

    $checkWriter = $false
    $checkVideo = $false
    foreach ($f in $changedAll) {
        if ($f.StartsWith("cursor-novel-writer/engine/") -and $f.EndsWith(".py")) {
            $checkWriter = $true
        }
        elseif ($f.StartsWith("cursor-novel-video/engine/") -and $f.EndsWith(".py")) {
            $checkVideo = $true
        }
    }

    if (-not $checkWriter -and -not $checkVideo) {
        Write-Host "[typecheck] No changed Python files in engine paths. Skip pyright."
        exit 0
    }

    if ($checkWriter) {
        $pyrightArgs += "cursor-novel-writer/engine"
    }
    if ($checkVideo) {
        $pyrightArgs += "cursor-novel-video/engine"
    }
}

npx --yes pyright @pyrightArgs
