# Invoke-PytestCollectionCleanup.ps1
# 默认 dry-run；禁止无确认删除；优先 quarantine。
# 依据：《向量化索引治理规范_V1》第 8 节 pytest 自动清理（测试结束即删 + 24h 兜底）
# 审计背景：OpenClaw Batch 01 — 47/47 collection 为 novel__pytest-*，约 16.93GB
#
# 用法（仅示例，执行清理须用户单独授权）：
#   powershell -File tools/maintenance/Invoke-PytestCollectionCleanup.ps1
#   powershell -File tools/maintenance/Invoke-PytestCollectionCleanup.ps1 -IncludeSize
#   powershell -File tools/maintenance/Invoke-PytestCollectionCleanup.ps1 -Mode Quarantine -ConfirmToken PLEASE_CLEAN_PYTEST_COLLECTIONS_20260620

[CmdletBinding()]
param(
    [string]$RootPath = "G:\CURSOR\platforms\data\qdrant_storage\collections",
    [ValidateSet("DryRun", "Quarantine", "Delete")]
    [string]$Mode = "DryRun",
    [int]$OlderThanHours = 24,
    [string]$ConfirmToken = "",
    [switch]$IncludeSize
)

$ErrorActionPreference = "Stop"
$RequiredConfirmToken = "PLEASE_CLEAN_PYTEST_COLLECTIONS_20260620"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptDir "_cleanup_logs"
$LogStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogPath = Join-Path $LogDir "cleanup_$LogStamp.log"
$DryRunCsvPath = Join-Path $LogDir "dryrun_$LogStamp.csv"
$QuarantineDateSuffix = Get-Date -Format "yyyyMMdd"
$PythonProcessNamePattern = '^(python|python3|python3\.13|pythonw|py)(\.exe)?$'
$PythonCommandLinePattern = 'pytest|qdrant|novel_suite\.memory'

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$Level] $Message"
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    Add-Content -Path $LogPath -Value $line -Encoding UTF8
    switch ($Level) {
        "WARN" { Write-Warning $Message }
        "ERROR" { Write-Error $Message }
        default { Write-Host $Message }
    }
}

function Get-DirectorySizeBytes {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return 0 }
    $measure = Get-ChildItem -LiteralPath $Path -Recurse -File -Force -ErrorAction SilentlyContinue |
        Measure-Object -Property Length -Sum
    if ($null -eq $measure.Sum) { return [int64]0 }
    return [int64]$measure.Sum
}

function Format-SizeHuman {
    param([int64]$Bytes)
    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    return "$Bytes B"
}

function Test-IsPytestCollection {
    param([string]$Name)
    if ($Name -match '^(prod|stage|scratch)__') { return $false }
    if ($Name -like "novel__pytest-*") { return $true }
    if ($Name -match 'pytest') { return $true }
    return $false
}

function Get-SuggestedAction {
    param([bool]$IsExpired, [string]$RunMode)
    if (-not $IsExpired) { return "skip (within ${OlderThanHours}h TTL)" }
    switch ($RunMode) {
        "DryRun" { return "quarantine (preferred) or delete after user confirm" }
        "Quarantine" { return "quarantine" }
        "Delete" { return "delete" }
        default { return "review" }
    }
}

function Test-IsBlockingPythonProcess {
    param($ProcessRow)
    $name = [string]$ProcessRow.Name
    if ($name -notmatch $PythonProcessNamePattern) { return $false }
    $cmd = [string]$ProcessRow.CommandLine
    return $cmd -match $PythonCommandLinePattern
}

function Assert-SafeToMutate {
    $blockers = @()
    $cursor = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
    if ($cursor) { $blockers += "Cursor ($($cursor.Count) process(es))" }

    $qdrant = Get-Process -Name "qdrant*" -ErrorAction SilentlyContinue
    if ($qdrant) { $blockers += "qdrant ($($qdrant.Count) process(es))" }

    $pythonHits = @()
    try {
        $pythonHits = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
            Test-IsBlockingPythonProcess -ProcessRow $_
        })
    } catch {
        Write-Log "Win32_Process query failed (non-fatal for dry-run): $_" "WARN"
    }
    if ($pythonHits.Count -gt 0) {
        $blockers += "python test ($($pythonHits.Count) process(es))"
    }

    if ($blockers.Count -gt 0) {
        $msg = "Abort $($Mode): active process(es) detected — " + ($blockers -join "; ")
        Write-Log $msg "ERROR"
        throw $msg
    }
    Write-Log "Pre-check passed: no Cursor / qdrant / pytest python processes."
}

function Confirm-TokenIfRequired {
    if ($Mode -eq "DryRun") { return }
    if ($ConfirmToken -ne $RequiredConfirmToken) {
        $msg = "Mode '$Mode' requires -ConfirmToken '$RequiredConfirmToken'."
        Write-Log $msg "ERROR"
        throw $msg
    }
    Write-Log "ConfirmToken accepted for Mode=$Mode."
}

function Export-DryRunCsv {
    param([array]$Rows, [string]$CsvPath)
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    $Rows | Select-Object Collection, Path, SizeHuman, LastModified, OlderThanHours, IsExpired, SuggestedAction |
        Export-Csv -Path $CsvPath -NoTypeInformation -Encoding UTF8
    Write-Log "DryRun CSV written: $CsvPath"
}

Write-Log "=== Invoke-PytestCollectionCleanup start ==="
Write-Log "Mode=$Mode RootPath=$RootPath OlderThanHours=$OlderThanHours IncludeSize=$IncludeSize LogPath=$LogPath"

if (-not (Test-Path -LiteralPath $RootPath)) {
    Write-Log "RootPath not found: $RootPath" "WARN"
    Write-Log "No collections to scan. Exiting."
    exit 0
}

$cutoff = (Get-Date).AddHours(-$OlderThanHours)
$candidates = @()

Get-ChildItem -LiteralPath $RootPath -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object {
    $name = $_.Name
    if (-not (Test-IsPytestCollection -Name $name)) {
        Write-Log "Skip (not pytest / excluded prefix): $name"
        return
    }

    $sizeBytes = [int64]0
    $sizeHuman = "n/a (pass -IncludeSize to compute)"
    if ($IncludeSize) {
        $sizeBytes = Get-DirectorySizeBytes -Path $_.FullName
        $sizeHuman = Format-SizeHuman -Bytes $sizeBytes
    }

    $lastWrite = $_.LastWriteTime
    $isExpired = $lastWrite -lt $cutoff
    $suggested = Get-SuggestedAction -IsExpired $isExpired -RunMode $Mode

    $row = [ordered]@{
        Collection      = $name
        Path            = $_.FullName
        SizeBytes       = $sizeBytes
        SizeHuman       = $sizeHuman
        LastModified    = $lastWrite.ToString("yyyy-MM-dd HH:mm:ss")
        OlderThanHours  = $OlderThanHours
        IsExpired       = $isExpired
        SuggestedAction = $suggested
    }
    $candidates += [pscustomobject]$row
}

Write-Log "Matched pytest collections: $($candidates.Count)"
Write-Host ""
Write-Host "== Pytest Collection Cleanup ($Mode) ==" -ForegroundColor Cyan
Write-Host "Root: $RootPath"
Write-Host "Cutoff: $($cutoff.ToString('yyyy-MM-dd HH:mm:ss')) (older than ${OlderThanHours}h)"
Write-Host "IncludeSize: $IncludeSize"
Write-Host "Log:  $LogPath"
Write-Host ""

if ($candidates.Count -eq 0) {
    Write-Log "No pytest collections matched. Done."
    exit 0
}

if ($IncludeSize) {
    $candidates | Format-Table -AutoSize Collection, SizeHuman, LastModified, IsExpired, SuggestedAction
} else {
    $candidates | Format-Table -AutoSize Collection, Path, LastModified, IsExpired, SuggestedAction
}

foreach ($c in $candidates) {
    Write-Log ("DRY-LIST | {0} | {1} | {2} | expired={3} | action={4}" -f `
        $c.Collection, $c.Path, $c.SizeHuman, $c.IsExpired, $c.SuggestedAction)
}

$expired = @($candidates | Where-Object { $_.IsExpired })
Write-Log "Expired (>${OlderThanHours}h): $($expired.Count) / $($candidates.Count)"

if ($Mode -eq "DryRun") {
    Export-DryRunCsv -Rows $candidates -CsvPath $DryRunCsvPath
    Write-Host ""
    Write-Host "DryRun CSV: $DryRunCsvPath" -ForegroundColor Green
    Write-Host "DryRun only — no files modified." -ForegroundColor Green
    Write-Log "DryRun complete. No mutations."
    exit 0
}

Confirm-TokenIfRequired
Assert-SafeToMutate

$targets = $expired
if ($targets.Count -eq 0) {
    Write-Log "No expired collections to process in Mode=$Mode." "WARN"
    exit 0
}

Write-Host ""
Write-Host "== Pre-mutation dry-run summary (required before $Mode) ==" -ForegroundColor Yellow
if ($IncludeSize) {
    $targets | Format-Table -AutoSize Collection, SizeHuman, LastModified, SuggestedAction
} else {
    $targets | Format-Table -AutoSize Collection, Path, LastModified, SuggestedAction
}
Write-Log "Pre-mutation summary logged for $($targets.Count) target(s)."

if ($Mode -eq "Quarantine") {
    foreach ($t in $targets) {
        $newName = "{0}_QUARANTINE_{1}" -f $t.Collection, $QuarantineDateSuffix
        $dest = Join-Path (Split-Path -Parent $t.Path) $newName
        if (Test-Path -LiteralPath $dest) {
            Write-Log "Quarantine skip (dest exists): $dest" "WARN"
            continue
        }
        Rename-Item -LiteralPath $t.Path -NewName $newName
        Write-Log "QUARANTINE | $($t.Collection) -> $newName"
        Write-Host "Quarantined: $($t.Collection) -> $newName" -ForegroundColor Yellow
    }
    Write-Log "Quarantine complete."
    exit 0
}

if ($Mode -eq "Delete") {
    Write-Host ""
    Write-Host "DELETE will permanently remove $($targets.Count) expired collection(s)." -ForegroundColor Red
    foreach ($t in $targets) {
        Remove-Item -LiteralPath $t.Path -Recurse -Force
        Write-Log "DELETE | $($t.Path) ($($t.SizeHuman))"
        Write-Host "Deleted: $($t.Collection)" -ForegroundColor Red
    }
    Write-Log "Delete complete."
    exit 0
}
