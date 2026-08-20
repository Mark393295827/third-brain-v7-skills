# 3-Minute Quickstart: V8.1 Stage → Author → Submit → Approved Commit

This quickstart uses the canonical transactional flow. A browser command-centre action can inspect or verify; it does not bypass governance or perform a live Vault commit.

## 1. Stage an immutable source

```text
Use the V8.1 worker flow to stage this source.
Create an immutable source note under sources/YYYY-MM/, preserve metadata,
calculate SHA-256, and add block anchors. Do not rewrite an existing source.
```

## 2. Author a candidate

```text
Author a gold-standard concept candidate from the staged source.
Include evidence bounds, Mermaid relationships, and source block references.
Keep the result staged; do not write the live Vault.
```

## 3. Submit for governance

```text
Submit the staged source, concept candidate, and graph/navigation plan to the
V8.1 governance worker. Run schema, link, block-reference, and preimage checks.
Return a typed receipt and list any debt or unknowns.
```

## 4. Commit only after explicit approval

```text
Review the governance receipt. If the preimages and checks are acceptable,
explicitly approve the serial commit. Commit through python -m tools.worker_flow.cli,
then run post-checks and read the committed files back. Do not treat HTTP 2xx,
an animation, or a model message as success; require verifier evidence.
```

## Verification receipt

A successful run identifies the immutable source hash and anchors, candidate and graph plan, governance receipt, approval identity, commit preimages, post-check output, and any remaining unknowns. Without those artifacts the run is `VERIFY_FAILED` or `NEEDS_INPUT`, not complete.
