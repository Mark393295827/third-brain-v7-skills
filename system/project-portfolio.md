---
title: "Project Portfolio — 项目组合执行台账"
type: project-portfolio
status: active
owner: vault-owner
wip_limit: 2
version: "8.1.0"
created: "2026-07-19"
updated: "2026-08-18"
tags:
  - "domain/knowledge-systems"
  - "type/system"
  - "type/project-portfolio"
---

# Project Portfolio — 项目组合执行台账 (V8.1)

> **金字塔聚焦原则**：严格控制并发在制品（WIP Limit ≤ 2）。一次只推进具备明确负责人、可交付产物与确定性验证收据的高杠杆项目。

---

## 1. 项目生命周期契约 (State Contract)

```
BACKLOG (待办池) ──> ACTIVE (进行中，限额 ≤ 2) ──> BLOCKED (阻塞挂起) ──> COMPLETED (交付归档)
```

- **BACKLOG**：通过初步价值评估但未启动的项目。
- **ACTIVE**：具备明确 Owner、交付截止日、资源预算与 DoD 验收标准的活跃项目。
- **BLOCKED**：因外部依赖或关键未知而暂时阻塞的项目。
- **COMPLETED**：已在 `wiki/outputs/` 输出最终成果，并通过验证收据验收的项目。

---

## 2. MECE 工作类别定义 (Work Classes)

| 工作类别 (Work Class) | 独占性定义 | 强制交付物 | 当前典型案例 |
| :--- | :--- | :--- | :--- |
| **`PROJECT`** | 有明确终点和高价值产出的交付承诺 | Reviewable Output + 验证收据 | V8.1 黄金标准全库演进计划 |
| **`EXPERIMENT`** | 为消除关键不确定性而运行的有界测试 | Hypothesis + Observation + Decision | 多智能体并行写入 IPC 测试 |
| **`AREA`** | 无明确终点、需持续维持标准的治理责任域 | Health Metric + 周期性 Review | 知识库治理与断链清零 (`system/lint-report.md`) |
| **`RESOURCE`** | 供未来参考的静态素材与背景知识 | Retrievable Note | 不可变事实层 (`sources/`) |
| **`ARCHIVE`** | 已完成或废弃的历史记录 | Closure Receipt | 历史归档 (`system/logs/`) |

---

## 3. 当前活跃项目与在制品追踪 (Active WIP Tracking)

| 项目名称 | 负责人 | 目标与交付物 | 预计完成 | 当前状态 |
| :--- | :--- | :--- | :---: | :---: |
| **V8.1 黄金标准全库规范落地** | Antigravity / Vault Owner | 完成 `system/` 全量文档升级与概念卡片模板重构 | 2026-08-18 | 🟢 **COMPLETED** |
| **存量概念卡片 V8.1 渐进升级** | AI Worker Teams | 按 13 领域 MOC 逐批将存量概念卡升级为黄金标准格式 | 持续推进 | 🔵 **ACTIVE** (WIP: 1/2) |

---

## 4. 执行守则

1. **拒绝无主的“标签式活跃”**：所有进入 `ACTIVE` 的项目必须有明确交付定义。
2. **完工必有成果**：项目完成必须在 `wiki/outputs/` 沉淀结构化文档并同步回写知识库。
