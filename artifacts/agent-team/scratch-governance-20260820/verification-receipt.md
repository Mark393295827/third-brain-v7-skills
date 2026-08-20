# T04 independent verification receipt

- Mission: `scratch-governance-20260820`
- Timestamp: `2026-08-20T18:46:17.7976225+08:00` (Asia/Shanghai)
- Target: `D:\C-Drive-Relocated\Personal\Documents\Obsidian Vault\scratch`
- Decision: `SUPPORTED` for the scoped post-change acceptance checks.
- Scope boundary: read-only verification; no Vault file was modified, and no `.py` was imported, executed, compiled, or parsed.

## Commands and observed results

Independent PowerShell checks used `Get-Item -LiteralPath`, recursive `Get-ChildItem -Force`, `Get-FileHash -Algorithm SHA256`, byte-level `[IO.File]::ReadAllBytes`, strict UTF-8 decoding, and .NET `StringComparer.Ordinal` sorting. Protected-tree fingerprints were recomputed from ordinal relative-POSIX-path + TAB + lowercase per-file SHA-256 + LF records, then SHA-256 hashed.

| Check | Expected | Observed | Result |
|---|---|---|---|
| Scratch identity/type | Exact target, normal directory, non-reparse | Exact path; directory; non-reparse | PASS |
| Legacy source set | 92 top-level lowercase `.py`; unchanged paths, bytes, hashes | 92 files; aggregate 1,345,412 bytes; corrected T02 hashes 92/92; no unexpected files/dirs | PASS |
| README | Required governance content; UTF-8 no BOM; LF-only; terminal LF | Required status, provenance, canonical-entry-point, selective-promotion, cache, manifest-verification, scope, mission/date content present; encoding/line endings pass | PASS |
| `MANIFEST.sha256` | Exactly 92 lowercase SHA-256 records, two spaces, ordinal paths, LF/no BOM/terminal LF | 8,263 bytes; 92 records; 92 unique paths; grammar/order/encoding pass; recomputed hashes 92/92 | PASS |
| Cache removal | `scratch/__pycache__/` absent | Absent | PASS |
| Quarantine preimage | Exactly one expected `.pyc`, 15,612 bytes, recorded SHA-256 | `parallel_gold_standard_compiler.cpython-313.pyc`; 15,612 bytes; SHA-256 `1510a61384881f0aa45da410558eaf2f3cd45ba17f4d11e791b51412b195d32e` | PASS |
| Durable protected trees | Clippings/sources/wiki/maps/system equal baseline | All five fingerprints, file counts, and byte totals equal baseline | PASS |

Protected-tree reconciliation:

- `Clippings`: 1,023 files / 43,715,321 bytes / `88d54dd7a1a0335c63873e84af6345261c6b4167e8ecf588cc13eb59931c6d80`
- `sources`: 1,358 / 23,770,182 / `ffc2dcacf1420468863a21054bc2b2c259778e5b14461eb136f910fbf1b00514`
- `wiki`: 2,766 / 16,146,042 / `a0825ae6dd1d6fbedb23a82fa639bac71f92d86976a610ba2c4139b7f2b37a55`
- `maps`: 39 / 805,222 / `25e9552cbf4fdb5e577caf6660ac559a0483f33b0f3dce7811b631c136f6f468`
- `system`: 187 / 9,656,343 / `4583b701e55056e4387ce8d49e331c93cdb4c95ac3d1357183948e7aa7805847`

## `.obsidian` boundary

The supplied `protected-tree-drift-event.md` records concurrent pre-existing `.obsidian/` drift before mission mutation. Per scope, this verification does not require or claim `.obsidian` stability. The reviewed execution boundary and commands did not target `.obsidian/`.

## Residual risk and rollback

This receipt supports byte identity, governance documentation, manifest integrity, cache absence, quarantine recoverability, and the five durable-tree no-drift checks only. It does not establish legacy script safety, correctness, authorship, provenance completeness, or semantic validity. Rollback of the additive README/manifest is permitted only by the owner after verifying their creation hashes and exact paths; the removed generated cache can be restored from the quarantined one-file preimage without touching legacy source files.
