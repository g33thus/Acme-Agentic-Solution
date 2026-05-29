#requires -Version 5.1
<#
.SYNOPSIS
  PostToolUse hook. Reminds the agent to keep specs in sync after edits.

.DESCRIPTION
  Reads the hook payload from stdin (JSON), extracts the edited file path,
  and prints a reminder unless the edit was itself under specs/.
  Always exits 0 so it never blocks an edit.
#>

$ErrorActionPreference = 'SilentlyContinue'

try {
    $raw = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($raw)) { exit 0 }

    $payload = $raw | ConvertFrom-Json
    $path = $payload.tool_input.file_path
    if (-not $path) { exit 0 }

    # Normalise to forward slashes for a simple, OS-agnostic check.
    $norm = ($path -replace '\\', '/')

    # Skip when editing the specs themselves, the plan file, or the hook.
    if ($norm -match '/specs/' -or
        $norm -match '/\.claude/' -or
        $norm -match '/plans/') {
        exit 0
    }

    $msg = @'
SPEC SYNC: This edit touched non-spec files. Per constitution principle VIII, if it changed behaviour, architecture, the data model, or the API, update the matching spec in the SAME change before finishing:
  - requirements -> specs/spec.md
  - design/components -> specs/plan.md
  - a major decision -> a new or updated specs/adr/NNNN-*.md
  - API shape -> specs/api/openapi.yaml
  - and tick the related item in specs/tasks.md
If the edit was cosmetic (formatting, comments), no spec change is needed.
'@

    Write-Output $msg
}
catch {
    # Never block an edit on hook failure.
}

exit 0
