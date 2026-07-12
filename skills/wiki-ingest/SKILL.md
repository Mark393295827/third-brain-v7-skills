---
name: wiki-ingest
description: Use when a PDF, URL, transcript, clipping, or raw note must become source-grounded, linked, governed knowledge in an Obsidian vault.
metadata:
  version: "7.0.0"
  updated: "2026-07-11"
  profile: "high-risk"
  assumes: "The source is accessible and the vault root plus write boundaries can be resolved."
  conflicts_with: "Invented provenance, modified immutable sources, unsupported concept promotion, or success claims without post-ingest checks."
---

# Wiki Ingest

<skill_contract>

Use STOW: **Source -> Transform -> Organize -> Write-back**. The source is evidence, the concept page is current understanding, and the log is the receipt. Load `references/stow-contract.md` for schemas and lifecycle details.

## Usage Template

Provide: source path/URL/note, vault root, intended topic, permissions, and whether the item came from a clipping queue. Optional: path config, prior canonical source, and desired behavior/skill candidate.

## Workflow

<intake>

1. Verify source existence, type, accessibility, date, and vault identity.
2. Resolve configured directories; record defaults only when no config exists.
3. Classify input as external fact, human experience, internal state, or environment signal.
4. Assign source risk based on primary/secondary/mediated/self-reported status and freshness.
5. Search for canonical source, concepts, and entities before creating files.

</intake>

<unknowns_gate>

If the source cannot be read, the vault is ambiguous, or provenance cannot be distinguished from mediation, return `NEEDS_INPUT` or `INSUFFICIENT_EVIDENCE`. Never fabricate author, date, URL, hash, source id, transcript text, or primary-source confidence.

</unknowns_gate>

<execute>

1. **Source:** create or identify one immutable source note; preserve raw content and archive locators. Extract 3-7 key insights with stable block references.
2. **Transform:** separate direct claims, interpretations, contradictions, unknowns, and fast-changing facts. Mark single-source and self-reported claims.
3. **Organize:** update existing entity/concept pages when possible. New concepts require a thesis, mechanism, boundary, counterpoint, source locator, and at least two meaningful links.
4. **Understand:** answer what changed, what causes what, what this source may prove, what could make it wrong, and what reusable action follows. Raw summaries fail this gate.
5. **Navigate:** update the relevant index/map and clipping lifecycle. Machine-owned snapshot blocks remain untouched.
6. **Convert:** queue behavior, creativity, SOP, or skill candidates; apply the promotion gate before changing governed rules.
7. **Write-back:** append evolution timeline and ingest log entries; never rewrite historical provenance.
8. **Verify:** run targeted link, source-ref, frontmatter, block-ref, empty-file, and navigation checks over touched files.

For material promotion or source ambiguity, require independent review and human approval. Prepare a rollback as a file-level diff; rollback may remove derived writes but must not erase original source evidence or logs.

</execute>

<evaluate>

Read touched files after write. Confirm the source exists, locators resolve, concepts pass the understanding gate, links are meaningful, clipping status is accurate, and logs match actual writes. Downgrade the result to partial when any required check is unavailable.

</evaluate>

<retry_policy>

`max_attempts: 2`. Retry only the failed stage after diagnosing path, parser, schema, or link cause. Change strategy before retry; stop on the same signature or `NO_PROGRESS`. Never duplicate source notes as a retry mechanism.

</retry_policy>

<state_contract>

Persist `{run_id, status, attempt, budget, evidence, unknowns, last_error, next_action}` plus source identity/risk, vault fingerprint, resolved paths, touched-file ledger, created block refs, contradictions, candidates, approval, clipping transition, and verification receipts. Source and log history are append-only.

</state_contract>

## Failure Protocol

- `NEEDS_INPUT`: source or vault identity is ambiguous; ask one minimal probe.
- `INSUFFICIENT_EVIDENCE`: the material cannot support the requested claim or concept.
- `BLOCKED_PERMISSION`: return proposed writes and paths without claiming mutation.
- `VERIFY_FAILED`: a post-ingest check fails; preserve evidence and repair only the failed stage.
- `NO_PROGRESS`: repeated failure signature after changed strategy; stop and queue review.
- `BUDGET_STOP`: persist coverage and remaining items. `max_attempts: 2`.

## Output Contract

Return `status`, `result` (created/updated/queued files and understanding delta), `evidence` (source and lint receipts), `unknowns`, and `next_action` including approval or rollback when relevant.

## Edge Cases

- A clipping duplicates an existing source: link/archive it and add only new provenance or block locators; do not create a parallel canonical source.
- A mediated summary contains a precise changing number: preserve the summary, flag the number, and queue primary/current verification before promotion.

## Success Metrics

- Every derived claim traces to an immutable source locator.
- Concepts add mechanism and boundary, not only summary.
- Touched files pass targeted lint and appear in navigation or an explicit queue.

## Quality Gates

- [ ] Vault, source, and permissions were verified before write.
- [ ] No provenance field or source content was invented.
- [ ] Understanding and promotion gates were applied.
- [ ] Independent/approval/rollback controls match the change risk.
- [ ] Post-ingest receipt matches actual filesystem state.

</skill_contract>
