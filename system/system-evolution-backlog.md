---
title: "System Evolution Backlog"
type: system-evolution-backlog
status: active
version: "8.1.0"
created: "2026-06-27"
updated: "2026-08-18"
knowledge_stage: recorded
evidence_level: local-scan
---

# Third Brain V8.1 — 系统演进与规则积压待办 (Evolution Backlog)

> 本待办台账记录第三大脑在 **个人 AGI 与知识操作系统** 方向的核心演进路线、架构规则候选与前瞻研究主题。

---

## 1. 核心架构演进路线 (Architecture Roadmap)

```mermaid
flowchart TD
    subgraph Phase1 ["Phase 1: V8.1 Baseline (已达成)"]
        A1["13 领域概念分类与不可变来源收据"]
        A2["V8.1 黄金标准十段式概念卡片"]
        A3["5-Stage Worker 流水线与动态测试门禁"]
        A1 --> A2 --> A3
    end

    subgraph Phase2 ["Phase 2: Agent Autonomy (进行中)"]
        B1["多智能体并行摄取与冲突检测 (IPC)"]
        B2["全自动断链检测与实体自动打桩"]
        B3["存量概念自动化批量升级至 V8.1"]
        B1 --> B2 --> B3
    end

    subgraph Phase3 ["Phase 3: Cognitive Flywheel (前瞻规划)"]
        C1["跨领域概念演化拓扑动态图谱"]
        C2["基于事实收据的投资/战略前瞻推演引擎"]
        C3["个人 AGI 知识共生体自适应优化"]
        C1 --> C2 --> C3
    end

    A3 --> B1
    B3 --> C1

    style Phase1 fill:#f0f5ff,stroke:#2f54eb
    style Phase2 fill:#f6ffed,stroke:#52c41a
    style Phase3 fill:#fffbe6,stroke:#faad14
```

---

## 2. 结构化系统规则候选 (Candidate Rules)

### 1. [agent-loop] Loop Engineering & 硬预算控制
- **候选规则**：所有重复性智能体任务必须显式声明 `Trigger -> Execute -> Verify -> State`，并附带硬 Token/步数预算、停止条件与回滚路径。
- **状态**：`APPROVED`（已在 `third-brain-v5-skills` 全面落地）。

### 2. [harness-boundary] 权限与工具沙箱边界
- **候选规则**：智能体执行外部工具调用或写回系统状态时，必须具备严格的权限边界、不可变审计记录与失败补偿机制。
- **状态**：`APPROVED`。

### 3. [gold-standard-contract] V8.1 概念卡片强类型门禁
- **候选规则**：所有新创建概念卡片必须具备 Core Thesis 块锚点、3 阶段彩色 Mermaid 流程图与范式对比矩阵。
- **状态**：`ACTIVE`（已正式成为系统宪法级标准）。
