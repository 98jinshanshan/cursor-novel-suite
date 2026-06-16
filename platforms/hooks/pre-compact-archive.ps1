# Cursor user hook: archive transcript to workspace docs/audit before compaction.
# Installed to: %USERPROFILE%\.cursor\hooks\pre-compact-archive.ps1

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ArchivePy = Join-Path $ScriptDir "session-archive.py"

if (-not (Test-Path $ArchivePy)) {
    Write-Error "session-archive.py not found beside hook: $ArchivePy"
    exit 0
}

$inputJson = [Console]::In.ReadToEnd()
if ([string]::IsNullOrWhiteSpace($inputJson)) {
    exit 0
}

$event = "preCompact"
try {
    $obj = $inputJson | ConvertFrom-Json
    if ($obj.hook_event_name) { $event = $obj.hook_event_name }
} catch {
    # keep default event name
}

$inputJson | & py -3 $ArchivePy hook --event $event
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: session-archive hook failed exit $LASTEXITCODE" -ForegroundColor Yellow
}

$userMsg = @{
    user_message = "对话已归档到当前工作区 docs/audit/session-archives/（压缩前快照）。可说「整理压缩对话」触发 session-retrospect。"
} | ConvertTo-Json -Compress
Write-Output $userMsg
exit 0
