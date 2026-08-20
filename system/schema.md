---
title: "Third Brain V8.1 Vault Frontmatter & Schema Specification"
type: system-schema
updated: "2026-08-18"
version: "8.1.0"
status: active
---

# Third Brain V8.1 Vault Frontmatter & Schema Specification

This document summarizes the machine-enforced schemas under `contracts/notes/`. The JSON schemas and `contracts/vault-contract.json` are authoritative; no personal Vault path is part of the contract.

---

## 1. Concept Note Schema (`wiki/concepts/<domain>/`)

Every concept note must strictly comply with the **V8.1 Gold Standard Concept Contract**:

```yaml
---
title: "概念英文/标准标题 (Concept Title)"
chinese_title: "概念中文全称 (Chinese Title)"
type: concept
contract_version: "8.1.0"
template_id: concept-gold-standard
template_version: "8.1.0"
author: "作者/主张者/机构"
date: "YYYY-MM-DD"
tags:
  - "domain/<domain-name>"
  - "topic/<topic-name>"
  - "type/concept"
aliases:
  - "英文/标准别名"
  - "中文别名"
  - "核心缩写/术语"
status: evergreen           # evergreen | growing | seed | stale | archived
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
knowledge_stage: stored     # captured | stored | cross-checked | applied
evidence_level: single-source  # single-source | multi-source | local-verified | curated-map
freshness_tier: stable      # snapshot | stable | slow | dynamic | volatile | realtime
valid_as_of: "YYYY-MM-DD"
last_verified: "YYYY-MM-DD"
next_review: "YYYY-MM-DD"
freshness_status: current   # current | due | stale | snapshot | unknown
source_ids:
  - "src-YYYYMMDD-slug"
run_id: "run-YYYYMMDD-upgrade"
---
```

### Mandatory Structural Sections (Gold-Standard V8.1):

1. **Title Header**: one canonical H1, `# chinese_title`.
2. **Core Thesis Callout (`> [!NOTE] Core Thesis`)**:
   - An authored thesis replacing the registered `semantic.core_thesis` token
   - `> (Source: [[sources/...#^anchor]])`
   - Explicit block anchor directly below: `^<concept-slug>-core-thesis`
3. **Temporal Scope Callout (`> [!INFO] Temporal Scope`)**:
   - `> Valid as of **YYYY-MM-DD** · freshness tier **tier-...** · next review **YYYY-MM-DD**.`
4. **Evidence Scope + Understanding Gates (`## 证据范围 (Evidence Scope) · 理解门 (Understanding Gates)`)**:
   - Three direct-evidence statements, each bound to an immutable source block anchor
   - `- **Interpretation:** ...`
   - `- **Evidence boundary:** ...`
   - `- **Falsifier / counterpoint:** ...`
   - Anti-pattern, understanding delta, and reusable action
5. **Core Mechanisms + Cognitive Topology (`## 核心机制与认知拓扑 (Core Mechanisms & Viking Mindmap)`)**:
   - Three required, evidence-linked mechanisms; a fourth only when supported
   - A four-stage Mermaid topology with an explicit feedback loop
6. **Paradigm Matrix (`## 范式对比矩阵 (Paradigm Matrix)`)** comparing legacy, intermediate, and new paradigms across six dimensions.
7. **Key Data & Evidence (`## 关键数据与实证 (Key Data)`)** with three anchored metrics and as-of dates.
8. **Agent Interface (`## Agent Interface`)** with role, context layer, tool mapping, input/output contracts, telemetry, stop condition, and machine-readable JSON.
9. **Implications & SOP (`## 应用与工程含义 (Implications & SOP)`)** with trigger, four staged actions, evaluation gate, and governance constraint.
10. **Connections (`## 关联 (Connections)`)** with annotated MOC, related concepts, optional entity, and immutable source.
11. **Evolution Timeline (`## 演化时间线 (Evolution Timeline)`)**:
    - Chronological list of emergence and upgrade milestones.
12. **Open Questions (`## 开放问题 (Open Questions)`)** for bounded uncertainty and future evidence work.

Optional mechanism, metric, SOP, entity, or timeline rows must be deleted when evidence does not support them; authored notes must never retain unresolved placeholders or invented filler.

Template path: `system/templates/template-concept-gold-standard.md` & `system/templates/template-concept-gold-standard-v8.1.md`

The canonical V8.1 template combines the strongest repeated structure observed in mature business-strategy cards—layered evidence, four-stage topology, three-paradigm comparison, operational metrics, staged SOP, annotated graph, and timeline—with stricter provenance, understanding, Agent Interface, uncertainty, and authoring-completeness gates. The authoring guide remains a reference for rationale and examples; it is not a separate runtime authority.

---

## 2. Source Note Schema (`sources/YYYY-MM/`)

Immutable source notes capture raw evidentiary receipts:

```yaml
---
title: "来源标题 (Source Title)"
type: source
contract_version: "8.1.0"
source_id: "src-YYYYMMDD-slug"
source_title: "原始标题"
source_author: "原始作者"
source_date: "YYYY-MM-DD"
source_type: clipping       # article | book | video-transcript | pdf | clipping | mediated | local-synthesis
source_url: "https://..."
source_identity: "canonical-url-or-local-identity"
prior_snapshots: []
input_class: external-fact
knowledge_stage: captured
evidence_level: single-source
trust_level: unverified     # unverified | expert-source | primary-source
hash: "sha256:<64 lowercase hex>"
status: ingested
captured_at: "YYYY-MM-DDTHH:MM:SSZ"
observed_at: "YYYY-MM-DDTHH:MM:SSZ"
valid_as_of: "YYYY-MM-DD"
freshness_tier: snapshot
freshness_status: snapshot
run_id: "run-..."
---
```

### Mandatory Structural Sections:
1. `# Source Title`
2. `## Provenance`
3. `## Evidence Blocks` with unique Obsidian block anchors
4. `## Raw Source` preserving the captured body

---

## 3. Entity Note Schema (`wiki/entities/<category>/`)

Categories: `people`, `companies`, `funds-investors`, `products`, `orgs`

```yaml
---
title: "实体名称 (Entity Name)"
type: entity
contract_version: "8.1.0"
entity_category: people     # people | companies | funds-investors | products | orgs
tags:
  - "entity/people"
  - "type/entity"
status: active              # active | stale | archived
updated: "YYYY-MM-DD"
freshness_tier: dynamic
valid_as_of: "YYYY-MM-DD"
last_verified: "YYYY-MM-DD"
next_review: "YYYY-MM-DD"
freshness_status: current
source_ids:
  - "src-YYYYMMDD-slug"
---
```

Entity notes are currently validate-only: the runtime does not claim an entity authoring renderer.

---

## 4. Map of Content (MOC) Schema (`maps/domain-mocs/`, `maps/`)

```yaml
---
title: "领域 MOC 名称"
type: map
contract_version: "8.1.0"
map_tier: domain-moc        # domain-moc | system-index | project-map | canvas
status: active              # active | stale | archived
updated: "YYYY-MM-DD"
generated_from_receipts: []
---
```

---

## 5. Output / Deliverable Note Schema (`wiki/outputs/`)

```yaml
---
title: "交付物标题 (Deliverable Title)"
type: output
contract_version: "8.1.0"
output_type: decision-memo  # gmail-digest | evaluation | compilation | decision-memo | daily-loop
status: draft               # draft | verified | superseded | archived
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
valid_as_of: "YYYY-MM-DD"
freshness_status: current
source_ids:
  - "src-YYYYMMDD-slug"
run_id: "run-..."
---
```

Output notes use the versioned `template-output-deliverable-v8.1.md`; `template-output-deliverable.md` is a byte-identical compatibility alias. The output lane is currently template-and-schema support, not an automatic authoring claim.
