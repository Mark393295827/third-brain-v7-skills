[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        "scan",
        "prepare",
        "prepare-local",
        "prepare-retrofit",
        "prepare-system",
        "stage-candidate",
        "submit",
        "commit",
        "status",
        "freshness-scan",
        "inventory"
    )]
    [string]$Action,

    [string]$VaultPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path,

    [string]$RepoPath = $env:THIRD_BRAIN_SKILLS_REPO,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$WorkerArguments
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoPath)) {
    throw "RepoPath is required. Pass -RepoPath or set THIRD_BRAIN_SKILLS_REPO."
}

$resolvedVault = (Resolve-Path -LiteralPath $VaultPath).Path
$resolvedRepo = (Resolve-Path -LiteralPath $RepoPath).Path
$python = Get-Command python -ErrorAction Stop

& $python.Source -m tools.worker_flow.cli --vault $resolvedVault --repo $resolvedRepo $Action @WorkerArguments
exit $LASTEXITCODE
