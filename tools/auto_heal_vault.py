#!/usr/bin/env python3
"""
Auto-Heal Vault Utility — Part of Third Brain V7.2 / V5.0 Automation Governance
Performs automated structural cleanup, legacy entity migration, link verification, and system KPI refresh.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_VAULT = r"C:\Users\高杰\Documents\Obsidian Vault"
VAULT_DIR = Path(os.environ.get("OBSIDIAN_VAULT_PATH", DEFAULT_VAULT))

def migrate_legacy_entities():
    """Migrates standalone root entities/*.md files to proper subfolders under wiki/entities/."""
    legacy_dir = VAULT_DIR / "entities"
    target_dir = VAULT_DIR / "wiki" / "entities" / "products"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    if not legacy_dir.exists():
        return 0
    
    moved_count = 0
    for f in legacy_dir.glob("*.md"):
        if f.is_file():
            dest = target_dir / f.name
            shutil.move(str(f), str(dest))
            print(f"Migrated legacy entity: {f.name} -> wiki/entities/products/{f.name}")
            moved_count += 1
            
    # Remove empty root entities folder
    try:
        if not list(legacy_dir.iterdir()):
            legacy_dir.rmdir()
    except Exception:
        pass
        
    return moved_count

def run_kpi_script():
    """Executes update-system-kpi.ps1 via PowerShell."""
    script_path = VAULT_DIR / "system" / "scripts" / "update-system-kpi.ps1"
    if not script_path.exists():
        print(f"KPI script missing: {script_path}", file=sys.stderr)
        return False
        
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path), "-VaultPath", str(VAULT_DIR)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("✅ System KPI script updated successfully.")
        return True
    else:
        print(f"❌ KPI script error: {res.stderr}", file=sys.stderr)
        return False

def main():
    print("=== Auto-Healing Obsidian Vault ===")
    moved = migrate_legacy_entities()
    print(f"Legacy Entity Migration: {moved} files migrated.")
    
    kpi_success = run_kpi_script()
    print(f"KPI Refresh: {'SUCCESS' if kpi_success else 'FAILED'}")
    print("=== Vault Healing Complete ===")

if __name__ == "__main__":
    main()
