# 📘 第三大脑与个人 AGI 系统：标准执行操作手册 (Standard Execution Manual)

> **版本**：V8.1 Transactional Gold-Standard Edition
> **核心架构**：LLM=CPU · Context=RAM · Storage=Obsidian Disk · Tools=System Calls · Skills=Programs · Harness=Kernel · Agent Teams=Processes
> **适用对象**：人类架构师、Claude Code、OpenAI Codex、Google Antigravity 及所有自主 Worker 智能体
> **核心宗旨**：确立每次执行的标准化作业流程（SOP）、严格完成标准（DoD）与不可触碰的系统红线。

---

## 🏛️ 一、 系统三位一体认知基准 (The Trinity Baseline)

在执行任何任务前，所有智能体必须明确三层解耦与职责边界：

1. **执行层 (Agent Surface / CPU)**：Claude Code / Codex / Antigravity 提供多模态推理算力与自主执行表面。
2. **协议层 (Skills Engine / Programs)**：`third-brain-v5-skills` 提供跨模型通用的 SOP 规范、流水线编排与治理测试。
3. **数据层 (Obsidian Vault / Disk)**：作为单一事实源（Single Source of Truth），存储不可变事实锚点、高维概念拓扑与交付物。

---

## ⚡ 二、 五阶段流水线标准作业程序 (5-Stage Worker SOP)

系统严格按照以下 5 个 Worker 角色流转，禁止跨阶段越级操作。

### Stage 1: 摄取与事实锚定 (Worker 1: Ingestion Specialist)
- **输入**：`Clippings/` 目录中的新文件，或用户提供的 URL。
- **SOP 动作**：
  1. 计算并保存完整的 64 位 SHA-256 校验和。
  2. 生成不可变来源文件 `sources/YYYY-MM/YYYY-MM-DD-kebab-case-title.md`（基于 `template-source-v8.1.md`）。
  3. 提炼 3~7 条关键事实，每条末尾必须打上显式块级锚点（如 `^core-insight-name`）。
  4. 只在候选通过治理、显式批准提交且 postcheck 成功后，将原始文件移入契约目录 `Clippings/Archive/`。
- **DoD (完成定义)**：来源卡完整、哈希与事实锚点有效、提交收据有效；归档是验证后的终结步骤。

### Stage 2: 认知编译与概念建模 (Worker 2: Cognitive Architect)
- **输入**：Stage 1 生成的来源事实锚点。
- **SOP 动作**：
  1. 提炼核心第一性原理，放入 `> [!NOTE]` 标注块作为 **Core Thesis**。
  2. 基于 `template-concept-gold-standard-v8.1.md` 撰写，必须包含：
     - **因果传导机制 (Causal Mechanism)**。
     - **证据边界 (Evidence Boundary)** 与 **反证条件 (Falsifiers)**。
     - **精确来源锚点 (Exact Locators)**（引用 `[[sources/...#^anchor]]`）。
  3. 绘制 **Mermaid 机制流程图**（`flowchart TD`）。
  4. 构建 **四维范式对比矩阵 (Paradigm Matrix)**。
- **DoD (完成定义)**：候选概念卡在 staging 中满足 V8.1 Schema、所有 `semantic.*` 已解决，并具备精确来源锚点；提交前不写入 canonical concept 路径。

### Stage 3: 图谱编织与导航对齐 (Worker 3: Graph Weaver)
- **输入**：Stage 2 生成的新概念卡片。
- **SOP 动作**：
  1. 识别概念所属的主领域，生成对应领域 MOC（`maps/domain-mocs/`）的类型化差异计划。
  2. 记录共享目标 preimage；由串行 integration owner 在验证后 compare-and-set 提交。
  3. 如涉及复杂系统架构，同步更新或创建 `maps/canvases/*.canvas` 可视化白板。
- **DoD (完成定义)**：图谱候选通过链接、歧义与 preimage 检查；不得在治理前直接更新 canonical MOC。

### Stage 4: 治理质检与门禁把关 (Worker 4: Governance Gatekeeper)
- **输入**：图谱变更事件。
- **SOP 动作**：
  1. 运行 `python -m tools.worker_flow.cli ... submit --run-id <run-id>` 检查 Schema、链接、全部锚点与时效性。
  2. 运行仓库声明的 `tools/`、`tests/` 与实验测试套件；Vault 内脚本不自动执行。
  3. 只有 `VERIFIED` 加显式提交批准才能进入串行 commit；失败时保留 staging 与证据。
- **DoD (完成定义)**：治理收据和测试退出码有效，postcheck 无回归，任何归档发生在成功提交之后。

### Stage 5: 行动转化与产出交付 (Worker 5: Deliverable Synthesizer)
- **当前能力边界**：仅提供 V8.1 输出模板与 Schema；交付物编写是独立、受审阅的任务，不由事务运行时自动生成。
- **输入**：用户的业务/战略决策请求。
- **SOP 动作**：
  1. 基于 `template-output-deliverable.md` 模板，调取 Vault 中多个概念节点进行跨学科逻辑合成。
  2. 明确输出 **实证依据与支撑概念 (Grounding Concepts & Evidence)** 表格。
  3. 明确输出 **风险防范与证伪条件 (Risks & Falsifiers)**。
  4. 经独立审阅和显式批准后，输出交付物至 `wiki/outputs/`。
- **DoD (完成定义)**：交付物具备支撑概念矩阵与行动清单，通过逻辑一致性校验。

---

## 🚫 三、 不可触碰的 10 大系统红线 (The 10 Inviolable Red Lines)

1. **严禁凭空伪造事实 (No Hallucinated Citations)**：所有核心论点必须有 `sources/` 下带 `^anchor` 的确切收据。
2. **严禁破坏不可变事实层 (No Mutating Immutable Sources)**：`sources/` 文件一旦生成且写入哈希，除非修复排版，否则严禁修改原始事实与日期。
3. **严禁制造知识孤岛 (No Orphan Nodes)**：新建任何概念必须挂载至至少一个 MOC、`Home.md` 与 `中央索引.md`。
4. **不得伪造 Inbox Zero**：空队列必须由只读 `scan` 的 `NO_OP` 与副作用数 0 证明；存在待审输入时不得为清零而提前归档。
5. **严禁陈旧无结构的空泛总结 (No Generic Summaries)**：严禁使用“本文介绍了...，具有重要意义”等废话，必须直接输出第一性原理与对比矩阵。
6. **严禁破坏 YAML Frontmatter 语法 (Strict YAML Compliance)**：英文冒号后必有空格，数组必须为行内 `[a, b]` 或缩进列表，日期必须加引号 `"YYYY-MM-DD"`。
7. **严禁产生死链与空链接 (Zero Broken Links)**：双链引用的文件名必须在 Vault 中真实存在。
8. **严禁违背 OCD 反 Cliché 设计准则 (No Cliché Tropes)**：严禁在 UI 或文档中使用无意义的发光边框、暗黑渐变与装饰性废话。
9. **严禁私自绕过单元测试 (No Bypassing Tests)**：每次技能或运行时代码修改后，运行 release playbook 声明的完整测试矩阵，并记录实际测试数量与退出码。
10. **严禁隐瞒单一来源声明 (Always Flag Single-Source)**：未经跨机构定量验证的访谈或供应商自述，必须显式标注 `WARNING: 单一来源声明 (Single source)`。

---

## 💻 四、 核心模板与 IPC 任务契约规范

### 1. Worker IPC 任务契约示例
所有子智能体任务必须遵循基于 JSON 的结构化回执：
```json
{
  "task_id": "run-20260817-1234",
  "worker_role": "Worker-Cognitive",
  "execution_time_ms": 1450,
  "exit_code": 0,
  "touched_files": ["wiki/concepts/ai-engineering/example.md"],
  "verification_passed": true,
  "evidence_summary": "Processed 3 anchors into Core Thesis"
}
```

### 2. 常用 CLI 命令速查
```bash
# 只读扫描（显式根目录）
python -B -m tools.worker_flow.cli --vault "<vault-root>" --repo "<repo-root>" scan
# 完整测试矩阵（数量以当次输出为准）
python -B -m unittest discover -s tools -p "test_*.py" -v
python -B -m unittest discover -s tests -p "test_*.py" -v
```
