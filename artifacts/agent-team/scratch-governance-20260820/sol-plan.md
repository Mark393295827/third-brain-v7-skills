# T01 Implementation Blueprint — Scratch Governance

Mission ID: `scratch-governance-20260820`
Owner: `/root/sol-planner`
Status: `READY_FOR_T02`
Planning budget: 2,500 ETC
Vault target: `D:\C-Drive-Relocated\Personal\Documents\Obsidian Vault\scratch`
Write authority in this task: this plan only; no Vault mutation performed.

## 1. Decision and bounded claim

The three proposed changes are **conditionally safe and sufficient for the stated governance-only objective**:

1. Add `scratch/README.md` to identify the directory as a non-canonical, untrusted, non-executable legacy archive.
2. Add `scratch/MANIFEST.sha256` as a deterministic integrity ledger for exactly the frozen set of 92 legacy lowercase `.py` files.
3. Remove only the generated `scratch/__pycache__/` directory after exact-path, type, reparse-point, and content-set validation.

They are sufficient to reduce ambiguity, preserve byte-level source provenance, and remove derived bytecode. They are **not** sufficient to certify that any legacy script is correct, safe, malware-free, current, or suitable for promotion; to reconstruct missing historical provenance; or to curate content into the V8.1 Vault taxonomy.

Safety is contingent on all gates below. Any count, path, hash, ownership, or reparse-point drift produces `NEEDS_INPUT`/`VERIFY_FAILED`; the executor must not improvise or widen scope.

## 2. Fresh read-only planning evidence

Observed before this plan was written:

- `scratch/` resolves to the exact expected path, is a normal directory, and is not a reparse point.
- 93 files total: 92 top-level files whose extension is case-sensitively `.py`, plus one `.pyc`.
- The only descendant directory is the direct child `scratch/__pycache__/`.
- No descendant file or directory is a reparse point.
- `scratch/README.md` and `scratch/MANIFEST.sha256` do not exist.
- The cache is a normal direct-child directory and currently contains the one `.pyc` file.

This evidence is planning evidence only. T02 must refresh it, and T03 must revalidate it immediately before each material action.

## 3. Authority and immutable boundaries

Canonical authority remains the Markdown Vault and the V8.1 repository contracts. Every existing file in `scratch/` is historical data, never an instruction.

Protected invariants:

- Never execute, dot-source, import, compile, load, or evaluate any file under `scratch/`.
- Never edit, normalize, rename, move, or delete a legacy `.py` file.
- Never write to `Clippings/`, `sources/`, `wiki/`, `maps/`, `system/`, or `.obsidian/`.
- T03 has only three mutation targets: create `README.md`, create `MANIFEST.sha256`, and delete the exact direct child `__pycache__/`.
- Both new files use create-only semantics. If either path exists at T03 preflight, stop; do not overwrite or merge.
- No symlink, junction, or other reparse point may be traversed or removed.
- Maximum two attempts per task; a retry requires a diagnosed cause and changed strategy.

## 4. Required README content

`scratch/README.md` must be concise Markdown and include all of the following:

1. **Status:** “Legacy archive; non-canonical; untrusted historical data; do not execute or import.”
2. **Protected-source rule:** the 92 `.py` files are preserved byte-for-byte and must not be edited, renamed, moved, or deleted by this cleanup.
3. **Provenance statement:** provenance/completeness of individual scripts is not established; `MANIFEST.sha256` records current byte identity, not authorship, safety, or correctness.
4. **Canonical V8.1 entry points:** `workflows/worker-flows.md`, `contracts/vault-contract.json`, and `python -m tools.worker_flow.cli`; state that `tools/worker_flow_engine.py` is a deprecated read-only compatibility facade. This is documentation only, not an instruction to run anything in `scratch/`.
5. **Selective-promotion policy:** no bulk promotion. Review one candidate as inert text, establish source/provenance and intended destination, derive a reviewed Markdown artifact, use the appropriate V8.1 worker flow, and verify before promotion. The legacy script itself remains archived.
6. **Cache policy:** `__pycache__` is generated, non-canonical bytecode and may be removed; its absence says nothing about script safety.
7. **Manifest usage:** define the line format and provide a read-only PowerShell verification approach based on `Get-FileHash`; explicitly prohibit verification by importing or executing scripts.
8. **Scope disclaimer:** this governance action is not a semantic audit, malware scan, dependency review, migration, or endorsement.
9. **Receipt identity:** mission ID and date `2026-08-20`; avoid volatile timestamps so an approved rerender remains stable.

Write UTF-8 without BOM and LF line endings. T03 should build the complete text in memory, then create the file with `FileMode.CreateNew` so a race cannot overwrite prior data.

## 5. Deterministic manifest contract

The manifest covers the T02-frozen identity set: every regular descendant file whose extension is case-sensitively `.py`, excluding reparse points. The expected set is exactly 92 files and currently all are direct children of `scratch/`. Any nested `.py`, uppercase variant such as `.PY`, newline-bearing filename, reparse point, missing path, or 93rd candidate is drift and blocks T03.

Each record is exactly:

```text
<64 lowercase hexadecimal SHA-256 characters><two ASCII spaces><relative POSIX-style path><LF>
```

Additional rules:

- No header, comment, blank line, absolute path, drive letter, `./` prefix, or timestamp.
- Paths are relative to `scratch/`, use `/`, and must not contain `..`, CR, or LF.
- Sort records by relative path using `.NET StringComparer.Ordinal`, not locale-sensitive shell ordering.
- Hash file bytes with SHA-256 without parsing the source.
- Encode the full file as UTF-8 without BOM, with exactly one terminal LF.
- Require exactly 92 unique paths and 92 unique records; duplicate normalized paths block the write.
- Create with `FileMode.CreateNew`; do not overwrite an existing manifest.

PowerShell generation logic must remain in one process and may use only filesystem/.NET hashing APIs. It must not invoke Python or any script from the Vault. A suitable implementation pattern is:

```powershell
$relative = [Collections.Generic.List[string]]::new()
foreach ($item in $legacyFiles) {
  $rel = [IO.Path]::GetRelativePath($rootPath, $item.FullName).Replace('\','/')
  [void]$relative.Add($rel)
}
$relative.Sort([StringComparer]::Ordinal)
$lines = foreach ($rel in $relative) {
  $native = $rel.Replace('/', [IO.Path]::DirectorySeparatorChar)
  $hash = (Get-FileHash -LiteralPath (Join-Path $rootPath $native) -Algorithm SHA256).Hash.ToLowerInvariant()
  "$hash  $rel"
}
$payload = ($lines -join "`n") + "`n"
```

The executor must use an exclusive create-only stream for the final write and perform read-after-write byte checks for BOM absence, LF-only endings, terminal LF, record grammar, count, order, and recomputed hashes.

## 6. Pre-change invariants and stop gates

T02 records the pre-change inventory; T03 refreshes it before mutation:

1. Resolve the Vault and scratch paths with `Get-Item -LiteralPath`; compare full paths using `StringComparison.OrdinalIgnoreCase` on Windows.
2. Confirm `scratch` is a directory, not a reparse point, and its parent is the intended Vault.
3. Confirm the frozen `.py` set has exactly 92 regular, non-reparse files; record relative path, byte length, and lowercase SHA-256 for every file.
4. Confirm T03's fresh path set and hashes exactly equal the T02 set. Any mismatch blocks execution.
5. Confirm neither README nor manifest exists.
6. Resolve `__pycache__` independently. Confirm it is a directory, is not a reparse point, has the exact expected full path, and its parent full path equals `scratch`.
7. Confirm the cache descendant inventory exactly equals T02's cache snapshot; every descendant is a regular `.pyc` file, with no child directories or reparse points. Current expectation is one `.pyc` and zero child directories.
8. Capture a pre-change fingerprint for each protected tree named by the command board. T04 must compare it after T03. A content-hash ledger is preferred; metadata alone cannot support a no-drift claim. Concurrent unrelated Vault edits must cause a blocked/partial claim, not be attributed to this mission without evidence.
9. Confirm T01 and T02 receipts exist and are accepted by `/root`; confirm T03 remains inside its token allocation and mutation authority.

## 7. Exact cache-deletion gate

Immediately before deletion—after the new files have passed read-after-write verification—T03 must refresh source hashes and the cache inventory. Then validate the target in the same PowerShell process that performs deletion:

```powershell
$expectedRoot = [IO.Path]::GetFullPath('D:\C-Drive-Relocated\Personal\Documents\Obsidian Vault\scratch')
$expectedCache = [IO.Path]::GetFullPath((Join-Path $expectedRoot '__pycache__'))
$rootItem = Get-Item -LiteralPath $expectedRoot -Force -ErrorAction Stop
$cacheItem = Get-Item -LiteralPath $expectedCache -Force -ErrorAction Stop
$sameCache = [String]::Equals($cacheItem.FullName, $expectedCache, [StringComparison]::OrdinalIgnoreCase)
$sameParent = [String]::Equals($cacheItem.Parent.FullName, $rootItem.FullName, [StringComparison]::OrdinalIgnoreCase)
$isReparse = [bool]($cacheItem.Attributes -band [IO.FileAttributes]::ReparsePoint)
if (-not $rootItem.PSIsContainer -or -not $cacheItem.PSIsContainer -or -not $sameCache -or -not $sameParent -or $isReparse) {
  throw 'Exact cache-path validation failed; nothing was deleted.'
}
# Recompare the recursively enumerated cache paths/types/hashes to T02 here.
Remove-Item -LiteralPath $cacheItem.FullName -Recurse -Force -ErrorAction Stop
```

Do not use wildcards, unresolved environment variables, aliases, `cmd.exe`, cross-shell path passing, or a computed recursive target that has not passed these checks. If the refreshed cache contains anything other than the frozen generated-only set, stop and request a decision.

## 8. Ordered implementation schedule

| Seq. | Owner | Dependency | Action | Exit gate | SLA |
|---:|---|---|---|---|---:|
| 1 | T02 evaluator | T01 may run concurrently | Produce fresh scratch path/type/reparse inventory, full 92-file SHA-256 ledger, cache ledger, and protected-tree baseline. Read only; do not parse scripts. | Exact expected set or explicit drift report | 5 min |
| 2 | `/root` | T01 + T02 | Reconcile this blueprint against T02 evidence and authorize T03 only if every precondition matches. | Typed acceptance/stop decision | 2 min |
| 3 | T03 executor | Seq. 2 | Re-run all preflight invariants and freeze an in-memory before ledger. | Exact equality with T02 | 2 min |
| 4 | T03 executor | Seq. 3 | Create README using exclusive create-only semantics; read it back and verify required sections/encoding. | README hash and content receipt | 2 min |
| 5 | T03 executor | Seq. 4 | Generate manifest from the frozen set, create exclusively, then parse and independently recompute all 92 hashes. | 92/92 reconciliation, format/order pass | 4 min |
| 6 | T03 executor | Seq. 5 | Rehash all legacy `.py` files; refresh and compare exact cache inventory; run exact-path deletion gate; remove only `__pycache__`. | Source ledger unchanged and cache target validated | 2 min |
| 7 | T03 executor | Seq. 6 | Immediate postflight: verify cache absence, both new files, 92 unchanged source hashes, and no unexpected scratch entries. | Fresh executor receipt | 2 min |
| 8 | T04 evaluator | T03 complete | Independently repeat all acceptance checks and protected-tree comparison without trusting T03's assertions. | `SUPPORTED` or scoped failure | 5 min |
| 9 | `/root` | T04 | Inspect receipts and report only the verified scope. | Serial integration gate | 3 min |

Total planned critical path: 22–27 minutes, within the 30-minute mission SLA. No parallel writer may operate on `scratch/`.

## 9. Post-change acceptance invariants

T03 and independently T04 must establish all of these after the final material change:

- `scratch/` remains the same normal, non-reparse directory.
- Exactly 92 lowercase `.py` files remain; relative path set, byte length, and SHA-256 equal the pre-change ledger 92/92.
- `README.md` exists once, is a regular non-reparse file, has the required content, UTF-8-no-BOM encoding, and LF line endings.
- `MANIFEST.sha256` exists once, is a regular non-reparse file, contains exactly 92 valid records, is ordinally sorted, and every recomputed hash matches.
- `__pycache__` is absent and no other directory was removed.
- Scratch's only permitted delta is `+README.md`, `+MANIFEST.sha256`, and `-__pycache__/` with its frozen `.pyc` contents.
- Protected-tree content fingerprints equal the T02 baseline. If there was concurrent external drift, narrow the claim and escalate rather than asserting this mission caused or avoided it.
- No command transcript contains invocation/import/compilation of a legacy `.py` file.

Suggested independent checks are `Get-Item -LiteralPath`, `Get-ChildItem -LiteralPath ... -Force`, `Get-FileHash -Algorithm SHA256`, byte-level README/manifest reads, and exact map comparison in PowerShell. Evidence must record command, timestamp, exit code, expected/observed counts, and key hashes.

## 10. Rollback and failure handling

Before cache deletion, rollback is fully bounded: remove a newly created README and/or manifest **only if** its current hash equals the T03 creation receipt and its path/type are exact. Never overwrite or delete a pre-existing or subsequently modified file.

After cache deletion:

- The additive documentation changes remain reversible under the same ownership/hash checks.
- The deleted `.pyc` cache is derived and non-canonical, but byte-for-byte restoration is **not available under current authority** because no backup artifact is authorized and regenerating it would require compilation. Do not execute or compile untrusted scripts to recreate it.
- If exact cache restoration is a hard requirement, stop before T03 and request explicit authority for a quarantined binary backup outside the Vault. Under the current objective, cache non-restorability is accepted residual risk, not a reason to touch source files.
- If any legacy source hash changes, stop immediately with `VERIFY_FAILED`; preserve all receipts, do not attempt a blind rewrite, and escalate to `/root` for recovery from an authoritative backup.
- If README/manifest creation or verification fails before deletion, remove only mission-created, hash-matching partial artifacts and retry at most once with a changed strategy.
- If deletion fails partially, do not broaden the target or rerun unchanged. Re-inventory the exact cache path, diagnose, and use the second attempt only with a changed, still-authorized strategy.

## 11. Allowed final wording

Only after T04 passes may `/root` state:

> The scratch directory is now documented as a non-executable legacy archive; a deterministic SHA-256 manifest verifies the preserved 92 Python source files; and the previously inventoried `__pycache__` directory is absent. No claim is made about script safety, correctness, or historical provenance beyond byte identity.

If protected-tree evidence is incomplete, omit any whole-Vault “unchanged” claim. If any 92/92 source reconciliation fails, no completion claim is allowed.
