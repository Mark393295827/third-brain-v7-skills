# STOW Ingest Contract

Load this reference when writing notes or adapting the pipeline to a vault schema.

## Path Resolution

Read `system/config.md` when available. Otherwise use:

```text
SOURCES_DIR=sources/
CONCEPTS_DIR=wiki/concepts/
ENTITIES_DIR=wiki/entities/
MAPS_DIR=maps/
SYSTEM_DIR=system/
LOG_FILE=system/log.md
```

Never infer that a similarly named directory is the target vault without checking its root.

## Source Note Minimum

```yaml
source_id: "verified-or-generated-stable-id"
source_date: "YYYY-MM-DD-or-unknown"
source_title: "original title"
source_author: ""
source_type: article | book | video-transcript | pdf | clipping | mediated | local-synthesis
source_url: ""
input_class: external-fact | human-experience | internal-state | environment-signal
knowledge_stage: captured
evidence_level: single-source | multi-source | curated-map
trust_level: unverified | expert-source | primary-source
hash: "verified-hash-or-empty"
status: raw | ingested
```

Use 3-7 insight blocks such as `^ki-short-name`. A hash is optional; an invented hash is forbidden.

## Source Risk Defaults

| Source | Default caution |
|---|---|
| Official/primary | Check date, final/draft status, and omissions |
| Article/book/transcript | Preserve author perspective; mark single-source claims |
| Founder/company/investor interview | Treat metrics and roadmaps as self-reported |
| Mediated summary | State that the original is not fully archived |
| Local synthesis/source stack | Do not promote numbers without primary locators |
| Fast-changing claim | Add a current-source review item |

## Concept Minimum

```text
Thesis: current best understanding
Mechanism: what causes what
Boundary: what this evidence may establish
Counterpoint: what could make it wrong
Source: exact note/block locator
Connections: at least two meaningful wikilinks
Status: seed | growing | evergreen | stale
Knowledge stage: captured | stored | cross-checked | applied
```

Compiled truth may be revised with evidence. The evolution timeline below it is append-only.

## Promotion Gate

Promote a rule only with two durable supports, or one strong source plus local verification; a bounded Trigger -> Execute -> Verify -> State contract; preserved source/permission boundaries; and a cheap check. Otherwise add a governance candidate with target, evidence, unknowns, owner, and next test.

## Clipping Lifecycle

After verified ingest, move or mark the clipping according to local policy and update its queue/index. If archive authority is absent, leave it in place with a processed receipt. Never treat a trigger or scheduled snapshot as proof that ingest ran.
