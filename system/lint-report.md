---
title: "Obsidian Vault Health Report Placeholder"
type: system-lint-report
version: "8.1.0"
status: template
scanned: null
---

# Obsidian Vault Health Report

> `NO_SCAN_EVIDENCE` — this repository file is a report template, not a health receipt.

Do not infer Vault compliance, link health, test counts, Inbox Zero, or deployment state from this file. A valid run must record the explicit Vault root, contract version, scan timestamp, command, inventory counts, findings, side-effect count, and receipt/artifact hashes.

## Required Receipt Fields

- Vault path and runtime fingerprint
- Contract and template hashes
- Inventory baseline and observed counts
- P0/P1 findings with exact paths
- Verification commands and exit codes
- Side-effect count and protected-tree pre/post hashes

Generated receipts belong under `system/runs/<run-id>/` or the repository audit-artifact directory; they must not overwrite this template with unverified prose.
