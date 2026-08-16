---
title: "Live Vault V8.1 Migration Baseline — 2026-08-16"
type: audit-baseline
status: verified-read-only
contract_version: "8.1.0"
created: "2026-08-16"
updated: "2026-08-16"
evidence_level: local-scan
---

# Live Vault V8.1 Migration Baseline — 2026-08-16

> Read-only inventory produced by `python -m tools.worker_flow.cli ... inventory`. No live-vault file was changed by this scan.

## Scope and identity

- Vault fingerprint: `a96a02d325605715506f805f9241735667731751e3f834c5f5f749ace269a9bf`
- Scan timestamp: `2026-08-16T09:33:14Z`
- Scope: `maps/**/*.md`, `sources/**/*.md`, `system/**/*.md`, `wiki/**/*.md`

## Layer counts

| Layer | Markdown files | V8.1 contract state |
|---|---:|---|
| `maps/` | 31 | 31 pre-V8.1 maps |
| `sources/` | 1,231 | 1,231 require migration metadata or an immutable overlay strategy |
| `system/` | 87 | 7 files at V7.0, 3 at V7.2, 77 unversioned |
| `wiki/` | 2,502 | 2,502 unversioned for V8.1 purposes |

## Migration debt

| Finding | Count | Boundary |
|---|---:|---|
| Concepts with anchored evidence and potential semantic restoration | 1,196 | Supervised retrofit batches |
| Concepts without anchored support | 473 | `INSUFFICIENT_EVIDENCE`; do not synthesize Gold-Standard prose |
| Wiki pages with unknown/due freshness state | 2,450 | Add temporal metadata by evidence-bearing migration, not mechanical “current” labels |
| Sources missing at least one V8.1 provenance/temporal field | 1,231 | Preserve source bodies; use overlays/new snapshots where needed |
| Legacy invalid/dummy source hashes | 601 | Do not treat as SHA-256 or deduplication evidence |
| Valid duplicate SHA-256 source groups | 0 | No hash-proven duplicate group established by this scan |
| Canonical URL identity threads with multiple captures | 6 | Review as temporal snapshot threads, not automatic duplicates |
| Missing frontmatter: maps / sources / system / wiki | 0 / 3 / 37 / 8 | Repair writable derived pages; report immutable-source defects |
| Duplicate `Daily Knowledge Loop Snapshot` sections | 9 in one dashboard | Replace with one marker-bounded machine block after backup |

## Canary selection

Selected retrofit candidate:

- `wiki/concepts/knowledge-systems/LLM知识图谱溯源.md`
- Evidence: six distinct anchors in `sources/2026-07/2026-07-23-citation-needed-provenance-llm-knowledge-graphs.md`
- Graph owner: `maps/domain-mocs/AI 知识工作流.md`
- Preimage at selection: `8a80abffab327f5f43a6f8ec2f913e980ab6a4011f40611e407dc818f27beac0`
- Required repair: V8.1 frontmatter/sections, temporal scope, canonical monthly source links, adaptable Mermaid, comparison matrix, implications, and verified graph write-back.
- Source rule: source bytes remain unchanged; only the concept and its map delta may be committed.

## Promotion rule

The canary may proceed only after isolated tests pass, staging produces a reviewable diff, the selected source anchors resolve, source/MOC/concept preimages remain unchanged, and post-commit checks show no new P0/P1 defect.

