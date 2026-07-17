# Third Brain V7 最大潜力使用手册

本手册适用于分支 `codex/v7-skill-contract-refactor`。目标不是让 19 个 skills 同时运行，而是把它们组合成一个可恢复、可验证、可持续改进的个人或团队操作系统。

最小闭环：

```text
明确目标 -> 选择一个主 skill -> 执行最小动作 -> 独立验证
        -> 写入持久状态 -> 回写 Obsidian -> 人工审核晋升
```

最大潜力的判断标准不是输出数量，而是：下一次运行是否能读取上一次的证据、错误和决策，并以更低成本做出更好的下一步。

## 1. 先理解 V7 改变了什么

V7 把每个 skill 从“长提示词”改造成执行契约。所有 skills 都包含：

- `intake`：确认目标、范围、权限、预算和验收标准。
- `unknowns_gate`：区分可查询、可实验、必须询问和无法访问的未知。
- `execute`：只执行最小、可逆、能产生证据的动作。
- `evaluate`：在宣布完成前运行新鲜检查。
- `state_contract`：多轮工作在返回前保存状态。
- `retry_policy`：只有诊断或策略发生变化时才重试。
- `Failure Protocol`：用标准错误码停止，不伪造成功。
- `Output Contract`：返回结果、证据、未知和下一步。

### 四种执行 Profile

| Profile | 数量 | 使用条件 | 你需要特别提供什么 |
|---|---:|---|---|
| `one-shot` | 3 | 一次转换即可完成，且有便宜检查 | 输入、输出格式、验收标准 |
| `stateful` | 7 | 跨多轮、多文件或多天运行 | 状态路径、负责人、复盘时间 |
| `loop` | 1 | 客观 verifier 能驱动有限纠错 | 最大迭代、时间/成本上限、停止与恢复 |
| `high-risk` | 8 | 涉及信任、生产、权限、外部用户或不可逆动作 | 独立验证、人工批准、回滚路径 |

不要把 profile 当质量等级。`one-shot` 不是低级模式，能够一次完成的任务不应承担 loop 或多代理成本。

## 2. 安装并确认使用的是 V7 分支

### 已有仓库

```powershell
git fetch origin
git switch codex/v7-skill-contract-refactor
git pull --ff-only
git status --short --branch
```

### 新克隆

```powershell
git clone --branch codex/v7-skill-contract-refactor `
  https://github.com/Mark393295827/third-brain-v5-skills.git
cd third-brain-v5-skills
```

### 安装到 Codex

```powershell
$target = Join-Path $HOME ".agents\skills"
New-Item -ItemType Directory -Force -Path $target | Out-Null
Copy-Item -Recurse -Force ".\skills\*" $target
```

其他运行时的默认位置：

| 运行时 | 目标位置 |
|---|---|
| Codex CLI | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Cursor | 使用 `adapters/cursor/third-brain-skills.mdc` |
| Windsurf | `.windsurf/skills/` 加对应 adapter |

安装后重新启动或新建任务，让运行时重新发现 skills。复制文件只证明安装动作发生，不证明当前会话已经加载它们。

### 安装验收

```powershell
python tools\lint-agent-skills.py
python -m unittest tools.test_lint_agent_skills -v
python skills\loop-engineering\scripts\validate_loop_contract.py `
  skills\loop-engineering\references\ci-repair-loop-example.md --strict
```

预期结果：19 个 skills lint 通过、测试通过、示例 loop contract 为 `PASS`。

## 3. 配置 Obsidian 为持久磁盘

V7 默认从 `system/config.md` 解析路径。把该文件复制到 Vault 的 `system/config.md`，再按实际目录修改。

核心目录职责：

| 变量 | 默认路径 | 职责 |
|---|---|---|
| `SOURCES_DIR` | `sources/` | 不可变来源与出处 |
| `CONCEPTS_DIR` | `wiki/concepts/` | 当前最佳理解、机制和边界 |
| `ENTITIES_DIR` | `wiki/entities/` | 人、公司、产品、项目 |
| `OUTPUTS_DIR` | `wiki/outputs/` | 报告、分析和可复用产物 |
| `DECISIONS_DIR` | `wiki/decisions/` | 决策、依据、替代方案和复审条件 |
| `SOPS_DIR` | `wiki/sops/` | 已验证的操作流程 |
| `MAPS_DIR` | `maps/` | 导航和主题地图 |
| `SYSTEM_DIR` | `system/` | 配置、日志、lint、治理和队列 |
| `LOG_FILE` | `system/log.md` | 追加式执行日志 |

三条不可破坏的存储规则：

1. `sources/` 保存证据，不被后续综合覆盖。
2. `wiki/` 保存可随新证据修订的当前理解。
3. `system/` 保存过程状态、审计收据和待审核晋升。

推荐额外建立：

```text
.agent-state/
  runs/               每次复杂运行的状态
  contracts/          loop 和 delegated-action 契约
  receipts/           测试、lint、审批、回滚收据
  review-queue.md      需要人判断的问题
```

`.agent-state/` 可以位于项目仓库；长期知识仍回写 Vault。不要只把关键状态留在聊天历史。

## 4. 每次调用都使用统一任务信封

自然语言仍然可以调用 skill，但复杂任务应提供下面的信封：

```text
使用：[skill-name]

目标：要改变的可观察状态
范围：允许读取和修改的文件、系统或主题
非目标：本次明确不处理什么
输入：路径、来源、已有状态或数据
验收：哪条命令、证据或指标证明成功
状态：持久状态写到哪里
预算：最大尝试、时间、工具调用或成本
权限：允许、需批准、禁止的动作
回写：结果进入哪个项目文件或 Obsidian 页面
```

高风险任务再增加：

```text
独立验证者：不能只由执行者自评
批准点：执行哪一步前必须由人确认
回滚：错误时恢复到哪个状态
```

### 标准输出收据

检查 agent 是否返回这五项：

```yaml
status: success | partial | blocked | failed
result: "实际完成的结果"
evidence: []
unknowns: []
next_action: "唯一或最优先的下一步"
```

缺少 `evidence` 的 success 不应被接受。

## 5. Skill 路由总表

### 知识系统

| 需求 | 主 skill | 典型下游 |
|---|---|---|
| 导入 PDF、网页、转录或 clipping | [wiki-ingest](../skills/wiki-ingest/SKILL.md) | `wiki-lint`、`knowledge-ops` |
| 多来源研究和证据比较 | [deep-research](../skills/deep-research/SKILL.md) | `wiki-ingest` |
| 把材料编译成决策模型 | [cognitive-compile](../skills/cognitive-compile/SKILL.md) | 概念页、决策页 |
| 去重、检索、同步、治理队列 | [knowledge-ops](../skills/knowledge-ops/SKILL.md) | `wiki-lint` |
| 检查链接、出处、生命周期和晋升条件 | [wiki-lint](../skills/wiki-lint/SKILL.md) | 修复或审核队列 |

### 每日执行与学习

| 需求 | 主 skill | 典型下游 |
|---|---|---|
| 设计或收尾每日知识闭环 | [daily-okr](../skills/daily-okr/SKILL.md) | 当日产物和下一日调整 |
| 管理任务状态、WIP、阻塞和完成 | [project-flow-ops](../skills/project-flow-ops/SKILL.md) | `verify-before-claim` |
| 从本次会话提取可复用增量 | [session-learn](../skills/session-learn/SKILL.md) | Wiki、SOP 候选、决策页 |
| 在宣布完成前验证 | [verify-before-claim](../skills/verify-before-claim/SKILL.md) | 完成收据或修复动作 |

### 行为、创意与操作系统

| 需求 | 主 skill | 典型下游 |
|---|---|---|
| 把目标变成可执行行为和复盘 | [behavior-design](../skills/behavior-design/SKILL.md) | `daily-okr` |
| 生成不同机制的方案和最小实验 | [creativity-engine](../skills/creativity-engine/SKILL.md) | 项目或行为实验 |
| 重构个人或团队工作系统 | [anthropic-os](../skills/anthropic-os/SKILL.md) | `loop-engineering`、`harness-engineering` |

### Agent 工程

| 需求 | 主 skill | 何时升级 |
|---|---|---|
| 设计 model-native 工程工作流 | [agentic-engineering](../skills/agentic-engineering/SKILL.md) | 出现重复任务时升级为 loop |
| 把重复任务变成有限闭环 | [loop-engineering](../skills/loop-engineering/SKILL.md) | 涉及工具/权限时增加 harness |
| 设计工具、权限、日志、调度和恢复 | [harness-engineering](../skills/harness-engineering/SKILL.md) | 存在独立工作流时评估 team |
| 指挥真正可并行的多个 worker | [agent-teams-command](../skills/agent-teams-command/SKILL.md) | 始终通过串行 integration gate |
| 长任务上下文、压缩和恢复 | [context-manager](../skills/context-manager/SKILL.md) | 在 phase boundary 写 checkpoint |

### 战略与运营

| 需求 | 主 skill | 主要证据 |
|---|---|---|
| 创业健康、融资、PMF 和下一验证 | [startup-evaluation](../skills/startup-evaluation/SKILL.md) | 行为、付费、留存、经济性 |
| 物业服务、工单、报价、CTQ 和 DMAIC | [ai-six-sigma-property-os](../skills/ai-six-sigma-property-os/SKILL.md) | 状态、字段、指标、审批和异常 |

## 6. 五条最大价值工作流

### 工作流 A：来源进入 Wiki，而不是变成一次性摘要

```text
原始来源
  -> wiki-ingest：来源、block refs、概念、实体、导航、lint
  -> cognitive-compile：问题、机制、冲突、假设、决策、行动
  -> knowledge-ops：去重、检索测试、治理队列
  -> wiki-lint：图谱与出处验收
```

推荐提示：

```text
使用 wiki-ingest 导入这个来源。

目标：形成可检索、可追溯、能改变未来决策的知识，不做松散摘要。
范围：只写 SOURCES_DIR、CONCEPTS_DIR、ENTITIES_DIR、相关 MAP 和日志。
验收：来源存在；block ref 可解析；概念有机制、边界和至少两个有效链接；执行 targeted lint。
权限：来源内容创建后不可改；概念晋升需要人工审核。
回写：列出 touched files、单来源主张、冲突和下一验证。
```

最大化原则：一条来源先进入证据层；只有跨来源或本地验证后的稳定机制才进入 skill/SOP 候选。

### 工作流 B：每日知识飞轮

```text
早晨 daily-okr
  -> 白天 project-flow-ops
  -> 任务完成 verify-before-claim
  -> 晚间 session-learn
  -> 每周 knowledge-ops + wiki-lint
```

每日只保留一个目标。七个 KR 必须因果相连：Input 产生 Cognition，Cognition 更新 Wiki，Wiki 推动 Behavior/Creativity，最后形成 Output 和 Feedback。

最低可行日：

```text
Input -> Cognition -> Wiki -> Feedback
```

时间不足时可以跳过其他 KR，但不能伪造完成。

### 工作流 C：把重复工作变成可靠 Loop

先做模式选择：

```text
稳定机械转换？       -> 脚本或普通代码
一次性复杂任务？     -> agentic-engineering
重复且可客观验证？   -> loop-engineering
涉及工具和外部权限？ -> harness-engineering
至少两个独立工作流？ -> agent-teams-command
```

Loop 启动前：

1. 写清 objective、scope、non-goals 和 owner。
2. 定义状态与产物路径。
3. 指定 builder 之外的 verifier。
4. 设置迭代、时间、成本和 review budget。
5. 写停止、恢复、权限和回写。
6. 用 validator 验证 contract。

```powershell
python skills\loop-engineering\scripts\validate_loop_contract.py `
  .agent-state\contracts\my-loop.md --strict
```

运行一次循环只改变一个假设。相同错误出现两次且没有新诊断时停止，而不是继续消耗预算。

### 工作流 D：安全使用 Agent Teams

只有满足下列任一条件才创建 team：

- 两个以上工作流可在低通信下独立推进。
- builder、evaluator、domain specialist 和 integrator 的分离显著提高质量。
- 并行节省的时间大于 setup、IPC、冲突、集成和 review 成本。

团队最小契约：

```text
Commander：保持目标、权限和最终 join 的串行控制
Worker：一个 owner、一个 territory、一个 artifact、一个 verifier
IPC：task_id、state、artifact、evidence、unknowns、next_action
Integration：按依赖顺序一次合入一个已验证产物
Cleanup：关闭 worker、清理 worktree、对齐任务和收据
```

不要让两个 worker 同时拥有同一文件。共享 schema 由 commander 先发布，再让 worker 只读消费。

### 工作流 E：Wiki 知识推动 Skill 演化

```text
来源 1 + 来源 2 或 来源 1 + 本地验证
  -> knowledge-ops 生成 promotion candidate
  -> agentic-engineering 写执行契约
  -> 独立 eval + lint/test
  -> 人工审核 diff
  -> 安装/合并
  -> session-learn 回写结果和失败
```

晋升为 skill、SOP、schema 或 automation 前必须满足：

- 至少两个持久页面支持，或一个高质量来源加本地验证。
- 能写成 `Trigger -> Execute -> Verify -> State`。
- 有 owner、预算、停止、恢复和回写。
- 不放松来源、权限、review queue 和人工批准边界。
- 有便宜检查，例如 skill lint、wiki lint、测试或 review receipt。

不满足时放入 `system/review-queue.md`，不要直接修改规则。

## 7. 正确处理失败，而不是要求“再试一次”

| 错误码 | 含义 | 用户的最佳响应 |
|---|---|---|
| `NEEDS_INPUT` | 缺少由用户拥有的关键决策 | 回答一个精确问题，不重发整段任务 |
| `INSUFFICIENT_EVIDENCE` | 证据不足以支持结论 | 提供来源或缩小主张 |
| `BLOCKED_PERMISSION` | 操作超出授权 | 批准、拒绝或提供只读替代 |
| `BLOCKED_DEPENDENCY` | 文件、服务或工具不可用 | 恢复依赖或接受降级路径 |
| `VERIFY_FAILED` | 产物存在但验收失败 | 查看失败证据，修复后重验 |
| `NO_PROGRESS` | 更换策略后仍重复失败 | 停止循环，重新定义问题或人工接管 |
| `BUDGET_STOP` | 时间、尝试、工具或成本到顶 | 从持久状态恢复，不把停止当成功 |

最差的回应是“继续直到成功”。最佳回应是补充一个能改变下一决策的事实、权限或验收标准。

## 8. 权限与自主性阶梯

按证据逐级扩权：

| 阶段 | Agent 能力 | 晋级证据 |
|---|---|---|
| Observe | 读取、检索、总结、建议 | 来源和假设可检查 |
| Co-drive | 草拟、模拟、准备变更 | 每个外部动作由人批准 |
| Scoped action | 执行低风险可逆动作 | 日志、回滚和后检查通过 |
| Supervised routine | 运行可逆定时流程 | 告警、收据、异常审核存在 |
| Audited autonomy | 高频低风险闭环 | 定期权限审计和失败复盘 |

权限必须由账号、路径、网络、工具和预算真实限制。提示词中的“不要误用”不能代替权限控制。

定时器、hook 或 scheduler 只证明触发。只有执行日志、状态更新和 verifier 收据才能证明任务完成。

## 9. 上下文和成本控制

用 [context-manager](../skills/context-manager/SKILL.md) 执行四分类：

- `KEEP`：目标、验收、权限、当前状态、新鲜证据、阻塞。
- `SUMMARIZE`：完成的探索、长日志、被替代的计划，但保留决策和 locator。
- `DROP`：重复、过时、无关和可重建内容。
- `RETRIEVE`：只在下一动作需要时加载 reference 或来源全文。

在这些边界创建 checkpoint：

- 探索转实施。
- 单 agent 转 loop/team。
- 即将压缩上下文。
- 即将执行外部或不可逆动作。
- 即将交接给另一个会话或负责人。

模型和价格从运行时发现。持久 skill 只记录能力需求，例如 reasoning、tool use、latency、context、multimodal 或 independent evaluator。

## 10. 日、周、月运行节奏

### 每日

| 时点 | 动作 | 证据 |
|---|---|---|
| 开始 | `daily-okr` 选择一个目标和预算 | 今日状态与七 KR |
| 执行中 | `project-flow-ops` 控制每人 1-2 个 ACTIVE | task transition 和 artifact |
| 完成前 | `verify-before-claim` | 新鲜测试、lint、read-after-write 或来源核对 |
| 结束 | `session-learn` 提取增量 | 写入路径、链接检查和 closure receipt |

### 每周

| 动作 | 目的 |
|---|---|
| `wiki-lint` | 清除 P0/P1 出处与链接问题 |
| `knowledge-ops` | 去重、检索测试、处理知识债务 |
| Review queue | 审核矛盾、单来源主张和晋升候选 |
| Loop review | 检查成功率、重复错误、预算和停止是否有效 |
| Permission review | 撤销不再需要的账号、路径和工具权限 |

### 每月

| 动作 | 目的 |
|---|---|
| `anthropic-os` | 复盘 Four-C、瓶颈和工作系统实验 |
| Skill diff review | 保留、修改、退役或合并规则候选 |
| Recovery drill | 验证 checkpoint、回滚和人工接管 |
| Context cleanup | 清理过期状态、空闲 worker 和不可检索产物 |

月度变化必须保留旧版本和证据，不进行无审核的自动退役。

## 11. 最小治理仪表盘

不要一开始追踪几十个指标。先使用五类：

| 维度 | 首选指标 | 反向信号 |
|---|---|---|
| 质量 | 有新鲜证据的完成主张比例 | “应该可以”或只有自评 |
| 知识 | 可从来源定位的核心主张比例 | 无出处概念、重复页面 |
| 流动 | 从 trigger 到 verified result 的时间 | WIP 增长、重复阻塞 |
| 恢复 | 能从 checkpoint 继续的复杂运行比例 | 依赖聊天重放 |
| 自主性 | 无越权且通过 guardrail 的受监督运行 | 回滚、异常或人工理解下降 |

建议把 `P0 broken source refs = 0`、`每个完成任务都有 receipt` 和 `每位 owner 的 ACTIVE 不超过 1-2` 作为初始本地政策。其他目标应从你的基线推导，不复制外部生产力倍数。

## 12. 30 天采用路径

### 第 1 周：可信输入和完成

- 只安装并深用 `wiki-ingest` 与 `verify-before-claim`。
- 配好 Vault 路径、来源不可变规则和日志。
- 目标：每个来源可追溯，每个完成主张有证据。

### 第 2 周：每日闭环

- 加入 `daily-okr`、`project-flow-ops`、`session-learn`。
- 每天只跑一个目标；晚上保存知识增量和下一步。
- 目标：下一会话不依赖重新解释上下文。

### 第 3 周：知识规模化

- 加入 `cognitive-compile`、`knowledge-ops`、`wiki-lint`。
- 建立矛盾、来源、重复、晋升和 stale review 队列。
- 目标：知识可检索、可核验、债务可见。

### 第 4 周：工程化自主性

- 先使用 `agentic-engineering`，再挑一个重复任务使用 `loop-engineering`。
- 只有涉及工具、调度和外部动作时加入 `harness-engineering`。
- 只有存在独立工作流和集成 owner 时加入 `agent-teams-command`。
- 目标：完成一次有限、可恢复、有 verifier 的自动化闭环。

行为、创意、创业和物业技能按真实需求加入，不按时间表强制启用。

## 13. 常见反模式

| 反模式 | 为什么失败 | 正确做法 |
|---|---|---|
| 一次加载全部 skills 和 Wiki | 占满上下文，稀释指令 | 一个主 skill，按需加载 reference |
| 把长上下文当长期记忆 | 压缩或换会话后丢失 | 使用 state path 和 Vault 回写 |
| 一次失败后原样重试 | 没有新信息，只增加成本 | 修改诊断、输入、工具或策略 |
| 用 agent team 做单文件任务 | 编排税大于收益 | 单 agent 加客观测试 |
| 定时触发等于任务成功 | executor 可能未运行或失败 | 要求执行和 verifier 收据 |
| 来源摘要直接晋升为规则 | 单来源偏差固化 | promotion gate 加人工审核 |
| 只优化主指标 | 可能破坏质量、安全和理解 | 同时定义 guardrail 与回滚 |
| Skill 内固定模型或价格 | 很快过时 | 运行时能力和当前计费表 |

## 14. 更新分支后的维护流程

```powershell
git switch codex/v7-skill-contract-refactor
git pull --ff-only
python tools\lint-agent-skills.py
python -m unittest tools.test_lint_agent_skills -v
```

验证通过后再同步到运行时 skills 目录。若你在安装目录做过本地修改，先保存 diff；不要用复制操作静默覆盖未审查的规则。

修改或新增 skill 时从 [Base Skill Template](skill-template.md) 开始，并遵守 [Agent Skills Standard](agent-skills-standard.md)。发布前至少运行：

```powershell
python tools\lint-agent-skills.py
python -m unittest tools.test_lint_agent_skills -v
git diff --check
```

## 15. 一页速查

```text
来源进入 Wiki          -> wiki-ingest
多来源研究             -> deep-research
材料变决策模型         -> cognitive-compile
知识去重/检索/治理      -> knowledge-ops
Wiki 健康检查          -> wiki-lint

每日闭环               -> daily-okr
项目 WIP 和阻塞        -> project-flow-ops
会话学习               -> session-learn
完成前证明             -> verify-before-claim

目标变行为             -> behavior-design
多机制创意和实验       -> creativity-engine
工作系统升级           -> anthropic-os

Agent 工作流设计       -> agentic-engineering
有限重复闭环           -> loop-engineering
工具/权限/调度/恢复     -> harness-engineering
真正独立的并行工作     -> agent-teams-command
长任务上下文恢复       -> context-manager

创业判断               -> startup-evaluation
物业工单和质量控制     -> ai-six-sigma-property-os
```

最终原则：先让一个闭环可靠，再增加 cadence；先让一个 owner 能解释和恢复系统，再增加 autonomy；先让知识通过证据和检查，再允许它修改未来的 agent 行为。
