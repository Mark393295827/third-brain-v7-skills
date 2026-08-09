---
title: "Third Brain V7.2 / V5.0 Vault Frontmatter & Schema Specification"
type: system-schema
updated: "2026-07-31"
version: "7.2.0"
status: active
---

# Third Brain V7.2 / V5.0 Vault Frontmatter & Schema Specification

This document defines the strict schema, metadata fields, and tag requirements for all note types inside the Obsidian Vault (`C:\Users\高杰\Documents\Obsidian Vault`).

---

## 1. Concept Note Schema (`wiki/concepts/<domain>/`)

Every concept note must include the following YAML frontmatter and structural sections:

```yaml
---
title: "概念英文标题 (Concept English Title)"
url: "https://..."
author: "作者/机构"
date: "YYYY-MM-DD"
tags: [domain/<domain-name>, type/concept]
aliases: ["英文标题", "中文译名标题", "简短别名"]
status: growing            # growing | active | seed | archived
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
---
```

### Mandatory Structural Sections (Gold-Standard Concept Template):
1. **Title Header**: `# Title (中文副标题)`
2. **Core Thesis Callout (`> [!NOTE]`)**: Highlighting the primary thesis and paradigm shift.
3. **Core Mechanisms (`## 核心机制 (Core Mechanisms)`)**: 3 detailed sub-mechanisms with explicit `(Source: [[sources/...]])` block citations.
4. **Mermaid Process/Architecture Diagram (`mermaid`)**: Visualizing flow from input state to autonomous execution and leveraged result.
5. **Vertical Matrix Table (`## 传统范式 vs. 金牌 Agent 范式对比`)**: 4-dimension comparative matrix.
6. **Key Data & Evidence (`## 关键数据与实证`)**: Quantitative metrics.
7. **Graph Connections (`## 关联`)**: Links to related concepts, entities, and immutable sources.
8. **Evolution Timeline (`## 演化时间线`)**: Dated record of paradigm emergence.

Template path: `system/templates/template-concept-gold-standard.md`

---

## 2. Entity Note Schema (`wiki/entities/<category>/`)

Every entity note must include:

```yaml
---
title: "实体名称 (Entity Name)"
type: entity
entity_category: people    # people | companies | funds-investors | products | orgs
tags:
  - entity/<category>     # e.g. entity/people, entity/companies
  - type/entity
status: active
updated: "YYYY-MM-DD"
---
```

---

## 3. Source Note Schema (`sources/<pool>/`)

Immutable source notes MUST follow this layout:

```yaml
---
title: "来源标题 (Source Title)"
type: source
tags:
  - source/article        # source/article | source/transcript | source/book | source/pdf
  - type/source
source_url: "https://..."
captured_date: "YYYY-MM-DD"
author: "作者/机构"
reliability: primary      # primary | secondary | mediated
---
```

---

## 4. SOP Note Schema (`wiki/sops/`)

Standard Operating Procedure notes MUST include:

```yaml
---
title: "SOP — 流程名称"
type: sop
tags:
  - sop
  - skill-adaptation
status: active
updated: "YYYY-MM-DD"
evidence_level: skill-adapted
---
```

---

## 5. Map of Content (MOC) Schema (`maps/<tier>/`)

```yaml
---
title: "MOC 名称"
type: map
map_tier: domain-moc       # domain-moc | system-index | project-map | canvas
tags:
  - map/<tier>
status: active
updated: "YYYY-MM-DD"
---
```
