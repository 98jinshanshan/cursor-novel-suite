# Shared helpers for Novel Suite platform scripts (dot-source from platforms/*.ps1)

function Get-SuiteRoot {
    param([string]$StartDir)
    $current = (Resolve-Path $StartDir).Path
    for ($i = 0; $i -lt 12; $i++) {
        if (Test-Path (Join-Path $current ".novel-suite-root")) {
            $writerCli = Join-Path $current "cursor-novel-writer\engine\novel_cli.py"
            if (Test-Path $writerCli) { return $current }
        }
        $parent = Split-Path -Parent $current
        if ($parent -eq $current) { break }
        $current = $parent
    }
    throw "Cannot find Novel Suite root (need .novel-suite-root + cursor-novel-writer/engine/novel_cli.py)."
}

function Test-RobocopyOk {
    param([int]$ExitCode)
    return ($ExitCode -ge 0 -and $ExitCode -le 7)
}

# User data preserved during sync (zip / local mirror)
$script:SuitePreserveDirNames = @(
    "novels",
    "intel",
    ".trae",
    ".agents",
    ".qoder",
    ".cursor"
)

function Get-SuiteRobocopyExcludeDirs {
    return $script:SuitePreserveDirNames + @(".git", "tmp", "__pycache__", ".pytest_cache", "node_modules")
}
