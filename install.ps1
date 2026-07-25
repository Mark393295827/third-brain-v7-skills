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
        "all"
    )]
    [string]$Target = "auto"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$SkillsDir = Join-Path $RepoRoot "skills"
$AdaptersDir = Join-Path $RepoRoot "adapters"
$ConfigFile = Join-Path $RepoRoot "system\config.md"
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

    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    foreach ($skill in Get-ChildItem -LiteralPath $SkillsDir -Directory -Force) {
        $skillDestination = Join-Path $Destination $skill.Name
        New-Item -ItemType Directory -Force -Path $skillDestination | Out-Null

        foreach (
            $file in Get-ChildItem -LiteralPath $skill.FullName -File -Recurse -Force |
                Where-Object {
                    $_.Extension -notin ".pyc", ".pyo" -and
                    $_.FullName -notmatch "(?i)(^|[\\/])__pycache__([\\/]|$)"
                }
        ) {
            $relative = $file.FullName.Substring($skill.FullName.Length)
            $relative = $relative.TrimStart([char[]]@("\", "/"))
            $targetFile = Join-Path $skillDestination $relative
            $targetParent = Split-Path -Parent $targetFile
            New-Item -ItemType Directory -Force -Path $targetParent | Out-Null
            Copy-Item -LiteralPath $file.FullName -Destination $targetFile -Force
        }
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
    if ($env:CLAUDE_CODE -or (Test-Path -LiteralPath (Join-Path $InstallHome ".claude"))) {
        $Harness = "claude-code"
    }
    elseif (Get-Command codex -ErrorAction SilentlyContinue) {
        $Harness = "codex"
    }
    elseif (Get-Command gemini -ErrorAction SilentlyContinue) {
        $Harness = "gemini"
    }
    else {
        $Harness = "claude-code"
    }
}

Write-Host "=== Third Brain V7.1 Skills Installer ==="

switch ($Harness) {
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
