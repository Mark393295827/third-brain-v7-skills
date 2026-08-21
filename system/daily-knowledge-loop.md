---
title: "Daily Knowledge Loop — 每日知识复利闭环"
type: system-daily-knowledge-loop
status: active
version: "8.1.0"
created: "2026-06-27"
updated: "2026-08-18"
knowledge_stage: recorded
evidence_level: local-scan
tags:
  - "system/automation"
  - "daily-okr"
  - "knowledge-loop"
---

# Daily Knowledge Loop — 每日知识复利闭环 (V8.1)

> **核心目标**：每日驱动一次最小知识复利闭环，将剪报摄取、不可变收据生成、V8.1 黄金标准概念建模、图谱回挂与 7-KR Daily OKR 融合为高确定性的执行流。

---

## 1. 闭环契约规范 (Loop Contract)

| 字段 | 契约标准 |
| :--- | :--- |
| **触发机制** | 每日定时触发或主动调度执行 |
| **流水线引擎** | V8.1 transactional runtime (`python -m tools.worker_flow.cli`) |
| **产出路径** | `system/daily/YYYY-MM-DD-daily-knowledge-loop.md` 与 `wiki/outputs/` |
| **底层证据** | `sources/YYYY-MM/` (SHA-256 + `^anchor`)、[[system/governance-dashboard]]、[[system/lint-report]] |
| **执行范围** | `Clippings/`, `sources/`, `wiki/concepts/<domain>/`, `wiki/entities/`, `maps/`, `system/` |
| **完成定义 (DoD)** | 剪报 Inbox Zero、新增概念卡片 100% 黄金标准、0 悬空断链、测试套件通过 |

---

## 2. 每日 7-KR 执行标准 (Daily 7-KR Gate)

```
KR1: 外部摄取 ──> 1-3 条剪报转化为 sources 不可变收据 (Worker 1)
KR2: 认知编译 ──> 强制提炼 Core Thesis、因果机制与反证条件 (Worker 2)
KR3: Wiki沉淀 ──> 按 V8.1 黄金标准生成/更新 1 个概念卡片 (Worker 2)
KR4: 图谱挂载 ──> 回挂领域 MOC 与中央索引，建立实体桩 (Worker 3)
KR5: 治理自检 ──> 校验 YAML 语法与测试套件通过率 (Worker 4)
KR6: 成果交付 ──> 在 wiki/outputs/ 留下 1 个可复用业务/投资成果 (Worker 5)
KR7: 反馈复盘 ──> 3 行总结反思，追加记录至 system/log.md
```

---

## 3. 5-Stage 流水线分工

```mermaid
flowchart LR
    A["Clippings/ 剪报"] --> B["Worker 1: 事实收据"]
    B --> C["Worker 2: 黄金概念"]
    C --> D["Worker 3: 图谱编织"]
    D --> E["Worker 4: 治理质检"]
    E --> F["Worker 5: 交付物"]

    style A fill:#f0f5ff,stroke:#2f54eb
    style B fill:#f6ffed,stroke:#52c41a
    style C fill:#fffbe6,stroke:#faad14
    style D fill:#fff1f0,stroke:#f5222d
    style E fill:#f9f0ff,stroke:#722ed1
    style F fill:#e6fffb,stroke:#13c2c2
```

---

## 4. 自动化与人工边界 (Automation Boundary)

- **完全自动化 (Fully Automated)**：剪报文件扫描、SHA-256 哈希计算、YAML 语法格式检查、断链扫描、单元测试套件运行。
- **人机共生决策 (Human-AI Supervised)**：核心论点提炼、因果机制图谱建模、范式矩阵对比、投资/战略决策落地。
