[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet(
        "auto",
        "claude",
        "claude-code",
        "codex",
        "gemini",
        "cursor",
        "windsurf",
        "all",
        "bundle",
        "agentic-os"
    )]
    [string]$Target = "auto"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$SkillsDir = Join-Path $RepoRoot "skills"
$AdaptersDir = Join-Path $RepoRoot "adapters"
$ConfigFile = Join-Path $RepoRoot "system\config.md"
$InstallHelper = Join-Path $RepoRoot "tools\install_skills.py"
$PackageHelper = Join-Path $RepoRoot "tools\package_agentic_os.py"
$InstallHome = if ($env:THIRD_BRAIN_HOME) {
    [System.IO.Path]::GetFullPath($env:THIRD_BRAIN_HOME)
}
else {
    $HOME
}
$WorkspaceRoot = (Get-Location).Path

if (-not (Test-Path -LiteralPath $SkillsDir -PathType Container)) {
    throw "Skills directory does not exist: $SkillsDir"
}

function Copy-Skills {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    $Python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $Python) {
        throw "Python 3 is required for manifest-driven installation."
    }
    & $Python.Source $InstallHelper --source $SkillsDir --destination $Destination
    if ($LASTEXITCODE -ne 0) {
        throw "Skill installation or hash verification failed for $Destination"
    }
}

function Copy-Adapter {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    $parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

$Harness = $Target
if ($Harness -eq "auto") {
    if ((Get-Command codex -ErrorAction SilentlyContinue) -or (Test-Path -LiteralPath (Join-Path $InstallHome ".agents"))) {
        $Harness = "codex"
    }
    elseif ($env:CLAUDE_CODE -or (Test-Path -LiteralPath (Join-Path $InstallHome ".claude"))) {
        $Harness = "claude-code"
    }
    elseif (Get-Command gemini -ErrorAction SilentlyContinue) {
        $Harness = "gemini"
    }
    else {
        $Harness = "claude-code"
    }
}

Write-Host "=== Third Brain V8.1 Skills Installer ==="

switch ($Harness) {
    { $_ -in "bundle", "agentic-os" } {
        if (-not (Test-Path -LiteralPath $PackageHelper -PathType Leaf)) {
            throw "Agentic OS package helper is missing: $PackageHelper"
        }
        $BundleDir = if ($env:THIRD_BRAIN_BUNDLE_DIR) { [System.IO.Path]::GetFullPath($env:THIRD_BRAIN_BUNDLE_DIR) } else { Join-Path $InstallHome ".third-brain\bundles" }
        New-Item -ItemType Directory -Force -Path $BundleDir | Out-Null
        $Output = Join-Path $BundleDir "third-brain-agentic-os-v8.1.zip"
        $Python = Get-Command python -ErrorAction SilentlyContinue
        if (-not $Python) { throw "Python 3 is required for Agentic OS bundle packaging." }
        & $Python.Source $PackageHelper --output $Output
        if ($LASTEXITCODE -ne 0) { throw "Agentic OS bundle packaging failed." }
        & $Python.Source $PackageHelper --verify $Output
        if ($LASTEXITCODE -ne 0) { throw "Agentic OS bundle verification failed." }
        Write-Host "[OK] Created Codex Agentic OS bundle: $Output"
        return
    }
    { $_ -in "claude", "claude-code" } {
        $Destination = if ($env:CLAUDE_SKILLS_DIR) {
            $env:CLAUDE_SKILLS_DIR
        }
        else {
            Join-Path $InstallHome ".claude\skills"
        }
        Copy-Skills -Destination $Destination
    }
    "codex" {
        $Destination = Join-Path $InstallHome ".agents\skills"
        Copy-Skills -Destination $Destination
    }
    "gemini" {
        $Destination = Join-Path $InstallHome ".gemini\skills"
        Copy-Skills -Destination $Destination
    }
    "cursor" {
        $Destination = Join-Path $WorkspaceRoot ".cursor\rules\third-brain-skills.mdc"
        Copy-Adapter `
            -Source (Join-Path $AdaptersDir "cursor\third-brain-skills.mdc") `
            -Destination $Destination
    }
    "windsurf" {
        $Destination = Join-Path $WorkspaceRoot ".windsurf\skills"
        Copy-Skills -Destination $Destination
        Copy-Adapter `
            -Source (Join-Path $AdaptersDir "windsurf\third-brain-skills.md") `
            -Destination (Join-Path $WorkspaceRoot ".windsurf\rules\third-brain-skills.md")
    }
    "all" {
        Copy-Skills -Destination (Join-Path $InstallHome ".claude\skills")
        Copy-Skills -Destination (Join-Path $InstallHome ".agents\skills")
        Copy-Skills -Destination (Join-Path $InstallHome ".gemini\skills")
        Copy-Adapter `
            -Source (Join-Path $AdaptersDir "cursor\third-brain-skills.mdc") `
            -Destination (Join-Path $WorkspaceRoot ".cursor\rules\third-brain-skills.mdc")
        Copy-Skills -Destination (Join-Path $WorkspaceRoot ".windsurf\skills")
        Copy-Adapter `
            -Source (Join-Path $AdaptersDir "windsurf\third-brain-skills.md") `
            -Destination (Join-Path $WorkspaceRoot ".windsurf\rules\third-brain-skills.md")
    }
}

$SkillCount = @(Get-ChildItem -LiteralPath $SkillsDir -Directory).Count
if ($Harness -eq "cursor") {
    Write-Host "[OK] Installed Cursor rules adapter."
}
else {
    Write-Host "[OK] Installed $SkillCount skills for target '$Harness'."
}

if (Test-Path -LiteralPath $ConfigFile -PathType Leaf) {
    Write-Host "Path config template: $ConfigFile"
}
