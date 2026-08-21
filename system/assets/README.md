---
title: "Third Brain V8.1 — 媒体与系统资产索引 (Assets Index)"
type: system-assets-index
version: "8.1.0"
updated: "2026-08-18"
status: active
tags:
  - "type/system"
  - "domain/knowledge-systems"
---

# Third Brain V8.1 — 媒体与系统资产索引 (Assets Index)

> 本目录（`system/assets/`）集中持久化 Obsidian Vault 中被来源卡片、概念笔记和 MOC 引用的结构图、截图与媒体资产。

---

## 1. 资产组织规范 (Organization Rules)

```
system/assets/
├── README.md         ← 本资产索引清单 (V8.1)
├── diagrams/         ← 流程图、架构图与第一性原理拓扑图 (PNG / SVG)
├── screenshots/      ← 系统运行截图、CLI 输出与应用界面
└── (media files)     ← 麦肯锡/贝恩研究图表与历史来源嵌入图
```

### 规范使用要求：
1. **命名规范**：遵循 `YYYY-MM-DD-description.png` 或来源对应前缀。
2. **嵌入方式**：优先使用 Vault 相对嵌入：`![[system/assets/filename.png]]` 或 `![caption](system/assets/filename.png)`；不要把个人绝对路径写入可分发文档。
3. **体积限制**：优先使用压缩优化格式，单张图片原则上不超过 5MB。
4. **不可变保护**：已被 `sources/` 卡片引用的图像文件作为不可变证据链一部分，严禁随意删除。

---

## 2. 当前全量媒体资产清单 (Asset Inventory)

| 资产文件名 | 相对位置 | 格式 | 引用来源笔记 | 资产内容与说明 |
| :--- | :--- | :---: | :--- | :--- |
| **`2026-04-22-10x-thinking-structure.png`** | `diagrams/` | PNG | [[sources/2026-04/2026-04-22-10x-thinking-notebooklm]] | 10倍思维认知结构与飞轮架构图 |
| **`mck_bain_team_p1.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 麦肯锡/贝恩咨询团队组织架构分析图 (p1) |
| **`mck_bain_team_p11.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 麦肯锡/贝恩咨询团队协同与分工图 (p11) |
| **`mck_bain_team_p2.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 咨询项目交付与人员配置图 (p2) |
| **`mck_bain_team_p21.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 团队绩效与能力矩阵模型图 (p21) |
| **`mck_bain_team_p3.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 咨询组织能力梯队图 (p3) |
| **`mck_bain_team_p41.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 组织敏捷化与跨部门协作图 (p41) |
| **`mck_bain_team_page1.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 咨询团队核心方法论封面图 |
| **`mck_marketing_p1.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 营销战略与客户增长漏斗图 (p1) |
| **`mck_marketing_p11.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 营销转化与 ROI 评估图 (p11) |
| **`mck_marketing_p2.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 客户全生命周期管理图 (p2) |
| **`mck_marketing_p21.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 数字化营销与渠道矩阵图 (p21) |
| **`mck_marketing_p3.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 品牌溢价与增长飞轮图 (p3) |
| **`mck_marketing_page1.png`** | 根目录 | PNG | [[sources/2026-05/2026-05-14-input-skills-obsidian]] | 营销方法论核心概览图 |
| **`factor_investing_quotes.txt`** | 根目录 | TXT | `system/references/` 候选 | 因子投资与 Smart Beta 原书重点引文摘录 |
| **`geb_extracted_quotes.txt`** | 根目录 | TXT | `system/references/` 候选 | 《哥德尔、艾舍尔、巴赫 (GEB)》核心引文摘录 |

---

## 3. 维护与清理指南

- **无引用孤立大文件检测**：使用自动化扫描脚本定期检测未在任何 `.md` 文件中引用的媒体资产。
- **保留原则**：只要存在 1 处有效嵌入，必须保留；确系废弃且无历史来源关联的临时截图可由架构师确认后删除。
