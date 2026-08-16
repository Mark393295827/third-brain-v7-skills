---
task_id: "{{task_id}}"
worker_role: "{{worker_role}}"
target_pipeline: "{{pipeline_name}}"
status: pending
created: "{{timestamp}}"
assigned_to: "{{agent_id}}"
---

# Task Contract: {{task_name}}

## 1. 任务目标与上下文 (Objective & Context)
- **目标 (Goal)**：{{goal_statement}}
- **输入物料 (Inputs)**：{{input_paths_or_uris}}
- **约束条件 (Constraints)**：{{constraints}}

## 2. 完成标准 (Definition of Done - DoD)
- [ ] 产出物符合 OCD 规范与指定 schema
- [ ] 链接与块引用精确可解析（无断链）
- [ ] 单源声明/证据边界完整标注
- [ ] 验收测试或静态检查 100% 通过

## 3. 产出物清单 (Expected Artifacts)
- **主产出物**：`{{primary_artifact_path}}`
- **回挂索引**：`{{moc_or_index_path}}`
- **验证收据**：`{{receipt_path}}`

## 4. 执行收据与证据 (Execution Receipt)
```json
{
  "task_id": "{{task_id}}",
  "worker_role": "{{worker_role}}",
  "execution_time_ms": 0,
  "exit_code": 0,
  "touched_files": [],
  "verification_passed": true,
  "evidence_summary": ""
}
```
