---
title: "{{source_title}}"
type: source
contract_version: "8.1.0"
source_id: "{{source_id}}"
source_title: "{{source_title}}"
source_author: "{{source_author}}"
source_date: "{{source_date}}"
source_type: "{{source_type}}"
source_url: "{{source_url}}"
source_identity: "{{source_identity}}"
prior_snapshots: {{prior_snapshots}}
input_class: "{{input_class}}"
knowledge_stage: captured
evidence_level: "{{evidence_level}}"
trust_level: "{{trust_level}}"
hash: "sha256:{{sha256}}"
status: ingested
captured_at: "{{captured_at}}"
observed_at: "{{observed_at}}"
valid_as_of: "{{valid_as_of}}"
freshness_tier: snapshot
freshness_status: snapshot
run_id: "{{run_id}}"
---

# {{source_title}}

> [!INFO] Source Snapshot
> Immutable evidence captured at `{{captured_at}}`. It records what the source contained as of `{{valid_as_of}}`; it is not automatically a current claim.

## Provenance

- URL: {{source_url_or_unknown}}
- Author: {{source_author_or_unknown}}
- Source date: {{source_date}}
- Content hash: `sha256:{{sha256}}`

## Evidence Blocks

{{evidence_blocks}}

## Raw Source

{{raw_content}}
