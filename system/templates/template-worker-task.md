---
task_id: "{{task_id}}"
worker_role: "{{worker_role}}" # Worker 1 (Ingest) | Worker 2 (Concept) | Worker 3 (Graph) | Worker 4 (Lint/Test) | Worker 5 (Deliverable)
target_pipeline: "{{pipeline_name}}"
contract_version: "8.1.0"
template_id: worker-task-v8.1
status: pending # pending / in_progress / completed / failed
created: "{{timestamp}}"
assigned_to: "{{agent_id}}"
---

# Task Contract: {{task_name}} (Worker {{worker_role}} Pipeline)

> [!NOTE] 任务契约目标 (Task Contract Objective)
> **目标：** 严格遵循 V8.1.0 五阶段流水线（5-Stage Worker Assembly Pipeline）质量规范，完成不可变物料流转与零断链交付。

---

## 1. 任务目标与物料上下文 (Objective & Inputs Context)

- **执行目标 (Goal):** {{goal_statement}}
- **输入物料 (Inputs):** `{{input_paths_or_uris}}`
- **质量与工程约束 (Constraints):**
  - 必须满足对应 Schema 契约校验
  - 严禁产生悬空断链（Broken Links = 0）
  - 严格保持证据级别（Evidence Level）与来源收据绑定
  - 提示词缓存对齐（Prompt Caching 命中目标 $\ge 90\%$）

---

## 2. 完成标准 (Definition of Done — DoD Checklist)

- [ ] **契约完备**：产出物严格符合 V8.1 格式契约（含 Frontmatter、Mermaid、矩阵与 SOP）
- [ ] **双链闭环**：所有 Wikilinks 及块引用（`#^...`）精确可解析
- [ ] **边界标注**：单源/多源声明与反证条件完整齐备
- [ ] **回归测试**：声明的自动化测试套件与 Link Audit 全部通过，并记录当次测试数与退出码

---

## 3. 产出物清单 (Expected Output Artifacts)

| 产出类型 | 物理文件路径 | 状态 |
|:---|:---|:---:|
| **主产出卡片** | `{{primary_artifact_path}}` | `[ ]` |
| **中央索引回挂** | `{{moc_or_index_path}}` | `[ ]` |
| **验证与执行收据** | `{{receipt_path}}` | `[ ]` |

---

## 4. 自动化执行收据 (Execution Receipt — Auto-filled on Done)

```json
{
  "task_id": "{{task_id}}",
  "worker_role": "{{worker_role}}",
  "pipeline": "{{pipeline_name}}",
  "execution_time_ms": 0,
  "exit_code": 0,
  "touched_files": [],
  "verification_passed": true,
  "evidence_summary": ""
}
```
