# T03 Execution Receipt — Scratch Governance

- Mission: `scratch-governance-20260820`
- Owner: `scratch-executor` (T03)
- Attempt: `1`
- Timestamp: `2026-08-20T18:31:15.8562711+08:00` (Asia/Shanghai)
- Result: `VERIFY_FAILED` / stopped before mutation

## Scope and authority

Target was exactly `D:\C-Drive-Relocated\Personal\Documents\Obsidian Vault\scratch`.
No legacy `.py` file was executed, imported, compiled, edited, renamed, moved, or deleted. No `README.md`, `MANIFEST.sha256`, or `__pycache__` mutation was performed.

## Checks

1. Read-only preflight resolved `scratch` as the expected normal directory, non-reparse, with the intended parent; `README.md` and `MANIFEST.sha256` were absent; exactly 92 top-level lowercase `.py` files were present.
2. The T02 inventory ledger was parsed as 92 records and each current source was rehashed with `Get-FileHash -Algorithm SHA256` without parsing or loading scripts.
3. The preflight stopped because two frozen inventory hashes did not match current bytes:

| Relative path | T02 inventory SHA-256 | Fresh SHA-256 | Bytes |
|---|---|---|---:|
| `fast_audit_ks.py` | `c1af2287a0781e9fc6c9ad5d538e7a099a3f2af94534f1f5db35950d852135d0` | `c1af2287a0781e9fc6c9ad5d538e7a099f3a2af94534f1f5db35950d852135d0` | 2570 |
| `upgrade_knowledge_ops_card.py` | `88ed2d9460aeed77e04df5fd55b2e62f9931fd581f48db120bfbde6518879313` | `88ed2d9460aeed77e04df5fd55b2e62f9931fd581f48db120bfbde651887931e` | 14596 |

4. Because the frozen 92-path/hash identity set was not equal, the plan's drift gate required stopping without widening scope. The cache was not deleted and no protected-tree mutation was attempted.

## Evidence

- Fresh observed source count: 92
- Fresh observed cache: direct-child `__pycache__` directory containing one `parallel_gold_standard_compiler.cpython-313.pyc` of 15,612 bytes; no deletion performed.
- Vault scratch additive files after stop: `README.md` absent; `MANIFEST.sha256` absent.
- No Vault delta was made by T03.

## Next action

`/root` must reconcile the stale or drifted T02 ledger with an authoritative fresh inventory and decide whether to authorize a new attempt. T03 must not create the manifest or remove the cache until all frozen path/type/content/hash gates pass.

## Attempt 2 continuation — additive files verified; deletion blocked

- Timestamp: `2026-08-20T18:42:21.2378190+08:00` (Asia/Shanghai)
- Repaired T02R ledger independently reconciled `92/92` current top-level lowercase `.py` files; no source hash drift was observed.
- `README.md` was created with `apply_patch`, read back as UTF-8 without BOM and LF-only, and verified against the required governance content. SHA-256: `7bef45aa0e545f0198ae18ef79794d3ce627eba86cff087ad11b8b05f039a2ee`.
- `MANIFEST.sha256` was created with `apply_patch`, read back as UTF-8 without BOM and LF-only, and verified as 92 ordinally sorted records with two-space separators; all 92 hashes reconcile to the repaired ledger. Size: 8,263 bytes. SHA-256: `716267d1e571fe67b15f3714e05f9f189a80749b30d48e0cf4fad33b56f66524`.
- The exact cache preimage still matched: direct-child `__pycache__`, one regular non-reparse `.pyc`, 15,612 bytes, SHA-256 `1510a61384881f0aa45da410558eaf2f3cd45ba17f4d11e791b51412b195d32e`.
- The authorized native PowerShell `Remove-Item -LiteralPath <validated exact cache path> -Recurse -Force` command was rejected by the host policy before PowerShell execution. No deletion occurred; `__pycache__` remains present. No alternate deletion method was attempted.
- Post-addition checks found the five in-scope durable protected-tree fingerprints unchanged: Clippings `88d54dd7a1a0335c63873e84af6345261c6b4167e8ecf588cc13eb59931c6d80`, sources `ffc2dcacf1420468863a21054bc2b2c259778e5b14461eb136f910fbf1b00514`, wiki `a0825ae6dd1d6fbedb23a82fa639bac71f92d86976a610ba2c4139b7f2b37a55`, maps `25e9552cbf4fdb5e577caf6660ac559a0483f33b0f3dce7811b631c136f6f468`, and system `4583b701e55056e4387ce8d49e331c93cdb4c95ac3d1357183948e7aa7805847`.
- `.obsidian/` was not targeted by any T03 command; its pre-existing drift remains out of scope and is excluded from the final unchanged claim.

Result remains `PARTIALLY_SUPPORTED` pending the authorized cache deletion. No completion claim is permitted while `__pycache__` remains.
