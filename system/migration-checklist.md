---
title: "Third Brain V8.1 — 迁移与系统健康检查清单"
tags:
  - "type/system"
  - "domain/knowledge-systems"
aliases:
  - "migration guide"
  - "health checklist"
  - "健康检查清单"
status: active
version: "8.1.0"
created: "2026-04-06"
updated: "2026-08-18"
---

# Third Brain V8.1 — 迁移与系统健康检查清单

> 本清单用于指导从旧版本（V5.x / V7.x）向 **V8.1.0 黄金标准架构** 的迁移验证与日常系统健康检查。

---

## 1. 基础环境与配置就绪检查

- [ ] **工作区对齐**：在运行收据中记录显式 Vault 根目录、解析后路径与 runtime fingerprint。
- [ ] **插件支持**：按实际 `.obsidian` 状态记录；插件不是 V8.1 事务运行时的前置条件，不得为通过清单而安装。
- [x] **内部链接自动更新**：设置 `Settings > Files & Links > Automatically update internal links` 为开启。
- [ ] **模板目录配置**：如使用 Obsidian Templates/Templater，再单独验证其目录指向 `system/templates/`；未配置时保持未勾选。

---

## 2. V8.1 目录结构与分类学验证

- [ ] **`Clippings/`**：验证归档目录大小写与 `Clippings/Archive` 契约一致；Inbox Zero 以 `scan` 的 `NO_OP` 收据为准。
- [x] **`sources/`**：按月归档 (`2026-08/`, `2026-07/`...), 包含 `pre-2026/` 与 `books/`。
- [x] **`wiki/concepts/`**：严格包含 13 个领域子目录 (`ai-engineering`, `investing-vc`, `general-concepts` 等)。
- [x] **`wiki/entities/`**：严格包含 5 个实体类别 (`people`, `companies`, `funds-investors`, `products`, `orgs`)。
- [x] **`wiki/outputs/`**：包含 `gmail-digests/`, `evaluations/`, `compilations/`。
- [x] **`maps/`**：包含 `domain-mocs/` (13 个领域 MOC), `system-indexes/`, `project-maps/`, `canvases/`，根部包含 `Home.md` 与 `中央索引.md`。
- [x] **`system/`**：包含 `templates/`, `scripts/`, `contracts/`, `runs/`, `logs/`。

---

## 3. 模板与契约就绪验证

核对 `system/templates/` 目录下的核心模板：
- [x] `template-concept-gold-standard.md` (V8.1.0 黄金标准概念卡片模板)
- [x] `template-concept-gold-standard-v8.1.md` (V8.1.0 版本化契约模板)
- [x] `template-source-v8.1.md` (V8.1.0 不可变来源事实收据模板)
- [x] `contracts/vault-contract.json` (契约签名与 SHA-256 校验一致)

---

## 4. 概念卡片 V8.1 黄金标准达标检查 (DoD)

随机抽检概念卡片，核实以下 10 项结构是否完备：
- [x] **Frontmatter**：包含 `contract_version: "8.1.0"`, `template_id: concept-gold-standard`, `tags`, `aliases`, `status`, `knowledge_stage`, `evidence_level`, `freshness_tier`。
- [x] **Core Thesis**：包含 `> [!NOTE] Core Thesis` 标注块与块级锚点 `^<concept-slug>-core-thesis`。
- [x] **Temporal Scope**：包含 `> [!INFO] Temporal Scope` 标注有效时间与审阅周期。
- [x] **证据范围**：包含直接证据、主观解释、证据边界、反证条件四要素。
- [x] **核心机制**：包含 3 阶段彩色 Mermaid TD 流程图 (`#f0f5ff`, `#f6ffed`, `#fffbe6`) 及原理拆解。
- [x] **范式对比矩阵**：包含多维 Markdown 表格对比。
- [x] **关键数据与实证**：包含可验证指标与来源引用。
- [x] **落地与实践指南 (SOP)**：包含具体有序步骤。
- [x] **概念网络连接**：包含 领域 MOC、关联人物、企业、概念与不可变来源。
- [x] **演化时间线**：包含时间演化里程碑。

---

## 5. 治理与测试门禁

- [ ] 运行 `tools/`、`tests/` 与实验测试套件，记录当次测试数、退出码与最终仓库哈希；不使用写死的测试数量。
- [ ] `system/lint-report.md` 只是无证据模板；健康结论必须来自新的 run receipt。检查 dashboard 是否引用该收据，而非自我声明。
