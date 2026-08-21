---
title: "Third Brain V8.1 — Dataview 查询合集 (Dataview Queries)"
type: system-dataview-queries
version: "8.1.0"
updated: "2026-08-18"
status: active
tags:
  - "type/system"
  - "domain/knowledge-systems"
aliases:
  - "dataview queries"
  - "search queries"
  - "数据视图查询"
---

# Third Brain V8.1 — Dataview 实用查询合集

> 本文档汇集了面向 **V8.1 黄金标准知识库** 的常用 Dataview 与 DataviewJS 聚合查询语句，支持实时监控 13 领域概念、事实收据、实体索引与治理健康度。

---

## 1. 13 领域概念分布与统计 (Concept Count by Domain)

```dataview
TABLE length(rows) as "概念总数", rows.file.link as "概念索引"
FROM "wiki/concepts" AND #type/concept
GROUP BY file.folder as "领域目录"
SORT length(rows) DESC
```

---

## 2. V8.1 黄金标准概念卡片 (Gold-Standard Concepts)

```dataview
TABLE chinese_title as "中文全称", contract_version as "契约版本", evidence_level as "证据级别", freshness_tier as "时效层级", dateformat(file.mtime, "yyyy-MM-dd") as "更新时间"
FROM "wiki/concepts" AND #maturity/gold
SORT file.mtime DESC
```

---

## 3. 最新摄取不可变事实收据 (Latest Sources Ingested)

```dataview
TABLE source_author as "作者/机构", source_type as "来源类型", dateformat(file.cday, "yyyy-MM-dd") as "摄取日期", file.link as "来源收据"
FROM "sources"
SORT file.cday DESC
LIMIT 15
```

---

## 4. 实体库按类别索引 (Entities by Category)

```dataview
TABLE length(rows) as "实体总数"
FROM "wiki/entities"
GROUP BY file.folder as "实体分类"
SORT length(rows) DESC
```

### 4.1 顶级科技企业与创业团队
```dataview
TABLE aliases as "别名/全称", status as "状态", dateformat(file.mtime, "yyyy-MM-dd") as "更新时间"
FROM "wiki/entities/companies"
SORT file.mtime DESC
LIMIT 10
```

### 4.2 核心人物与思想家
```dataview
TABLE aliases as "别名/职务", status as "状态"
FROM "wiki/entities/people"
SORT file.mtime DESC
LIMIT 10
```

---

## 5. 孤岛检测：未入网概念 (Orphaned Concepts with 0 Links)

```dataview
TABLE file.folder as "所在领域", dateformat(file.cday, "yyyy-MM-dd") as "创建时间"
FROM "wiki/concepts"
WHERE length(file.outlinks) = 0 AND length(file.inlinks) = 0
SORT file.cday DESC
```

---

## 6. 时效预警：待审阅与过期概念 (Concepts Due for Review)

```dataview
TABLE next_review as "审阅截止日", freshness_tier as "时效性", evidence_level as "证据级别"
FROM "wiki/concepts"
WHERE next_review != null AND next_review <= date(today) + dur(7 days)
SORT next_review ASC
```

---

## 7. 待升级存量概念 (Seed / Staged Concepts Awaiting V8.1 Upgrade)

```dataview
TABLE status as "状态", dateformat(file.mtime, "yyyy-MM-dd") as "最后修改"
FROM "wiki/concepts"
WHERE !contains(tags, "maturity/gold")
SORT file.mtime ASC
LIMIT 15
```

---

## 8. 近 7 天新增知识流转 (Weekly Knowledge Influx)

```dataview
TABLE type as "笔记类型", file.folder as "目录", dateformat(file.cday, "yyyy-MM-dd HH:mm") as "创建时间"
WHERE file.cday >= date(today) - dur(7 days)
SORT file.cday DESC
```

---

## 9. 交付成果与战略简报 (Deliverables & Outputs)

```dataview
TABLE status as "状态", grounding_concepts as "支撑概念", dateformat(file.mtime, "yyyy-MM-dd") as "交付日期"
FROM "wiki/outputs"
SORT file.mtime DESC
```

---

## 10. 系统全量类型 KPI 快照 (System-Wide Note KPI)

```dataview
TABLE length(rows) as "卡片总数"
GROUP BY type as "系统定义类型"
WHERE type != null
SORT length(rows) DESC
```
