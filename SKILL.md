---
name: computer-model-patent-mining
description: "计算机模型 / AI 算法类发明专利挖掘与说明书撰写：基于用户提供的项目申请书、中英文论文、技术文档、背景资料，挖掘可授权的计算机模型发明专利点，严格实现「技术问题—必要技术特征—技术效果」三维一一映射，输出技术问题（300-500 字三级递进）、完整技术方案、逐条对应技术效果，以及系统框架图 + 核心方法流程图的专利制图说明。| Trigger on 专利挖掘 / 发明专利 / 算法专利 / 模型专利 / AI 专利 / 论文转专利 / 项目书转专利 / 技术问题技术方案技术效果 / 说明书附图方案 / 专利交底书（计算机类）。"
version: "1.0.0"
display_name: 计算机模型类发明专利挖掘与撰写
display_name_en: Computer-Model Invention Patent Mining & Drafting
description_zh: 基于项目申请书 / 中英文论文 / 技术文档 / 背景技术资料，挖掘全新可授权的计算机模型类发明专利，严格遵循专利撰写规范，实现技术问题、必要技术特征、技术效果三维一一对应，输出技术问题（300-500 字三级递进）、可落地技术方案、逐条对应技术效果与专利附图方案（系统框架图 + 核心方法流程图）。
description_en: Mines patentable computer-model (AI/algorithm) invention patents from project proposals, papers and technical documents; enforces a strict three-way mapping of technical problem, essential technical features and technical effect, and produces a 300-500 character three-tier technical problem, an implementable solution, item-by-item effects, and patent drawing specs.
agent_created: true
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch
---

# 计算机模型类发明专利 · 挖掘与说明书核心内容撰写

## Overview

面向**计算机模型 / 人工智能算法类**发明专利（神经网络模型、机器学习方法、数据处理与预测模型、模型压缩与部署方法、模型与硬件/控制联动方案等），从用户提供的**原始技术资料**中挖掘具备新颖性、创造性的可授权发明点，并输出符合中国发明专利审查标准的**说明书核心内容**：技术问题、技术方案、技术效果、附图方案。

与相邻专利技能的边界：

| 技能 | 职责 | 何时不选本技能 |
|------|------|----------------|
| 本技能 | 计算机模型/算法类发明专利的**挖掘 + 说明书核心内容撰写** | 需要写机械/实用新型/外观交底书 |
| `patent-disclosure-skill` | 通用交底书（发明/实用/外观）编写、通俗解读、政策嗅探、审查答复 | —— |
| `mech-ctrl-patent-valuation` | 机械+控制组合专利**价值评估** | 只做估值不做撰写 |
| `mech-ctrl-patent-interpret` | 机械+控制组合专利**结构化解读** | 只做解读不做撰写 |

## 四条不可逾越的硬规则（Hard Rules）

1. **资料融合规则（禁止凭空捏造）**：全部技术内容必须可从用户提供的原始资料（模型架构、算法逻辑、实验数据、应用场景、现有技术缺陷）追溯或由其合理外推。凡属合理外推/补充的，必须在文中以「（推定）」标注并单列《推定与待确认清单》。
2. **三维一一映射规则**：技术问题中的**每一个**痛点（含每一层级）→ 必须有对应的**必要技术特征** → 必须有对应的**专属技术效果**。交付前必须填写 `assets/mapping_matrix.csv` 并跑通 `scripts/check_draft.py`。
3. **撰写规范规则**：符合《专利法》第 2 条（技术方案三要素）、第 22 条（新颖性/创造性）、第 25 条（智力活动规则排除）、第 26 条第 3/4 款（清楚完整、得到说明书支持），以及《专利审查指南》第二部分第九章（涉及计算机程序的发明专利申请）。区分**公知技术**与**创新技术**，创新点单独成块。
4. **篇幅规则**：技术问题严格 **300–500 字**（中文字符），采用**三级递进**：行业通用缺陷 → 场景化短板 → 核心技术瓶颈与落地问题。

## 交付物契约（Output Contract）

最终必须产出**四个部分，顺序固定**：

1. **一、技术问题**（300–500 字，三级递进，末尾标注实际字数）
2. **二、技术方案**（系统整体架构 / 核心模块组成 / 各模块执行步骤 / 算法优化逻辑 / 数据处理流程 / 参数配置规则 / 训练与推理方式 / 交互联动关系；必要技术特征以「必要技术特征 N：」编号并加粗）
3. **三、技术效果**（逐条对应，每条注明「对应技术问题层级 X / 对应必要技术特征 N」）
4. **四、专利说明书附图方案**（图 1 系统框架图 + 图 2 核心方法流程图；含构图说明 + 可直接写入说明书的附图说明文字）

另附：`mapping_matrix.csv` 填写结果 + `scripts/check_draft.py` 自检报告 + 《推定与待确认清单》。

模板：`assets/output_template.md`。

## Workflow（分步执行，逐步提示进度）

**步骤 0｜资料接收与澄清（仅在资料明显不足时提问，最多 1 轮）**
- 收集：项目申请书 / 论文（中英文）/ 技术文档 / 背景技术资料 / 实验数据。
- 判断模型技术类型（见 `references/domain_taxonomy.md` 快速归类）。
- 缺省字段**由 AI 依缺省规则补齐**并标「（推定）」，不反复追问用户。只有缺失**决定发明点成立与否**的关键信息（如：模型到底解决什么技术问题、有何量化效果）时才提问，且一次问完。

**步骤 1｜资料融合与技术要素抽取** → `Read prompts/01_material_fusion.md`

**步骤 2｜创新点挖掘与公知/创新分离** → `Read prompts/02_innovation_mining.md`
- 挖掘套路库见 `references/innovation_playbook.md`（八大切入面、40+ 具体切入点）。

**步骤 3｜撰写技术问题（三级递进 300–500 字）** → `Read prompts/03_technical_problem.md`

**步骤 4｜撰写技术方案（必要技术特征）** → `Read prompts/04_technical_solution.md`

**步骤 5｜撰写技术效果（逐条对应）** → `Read prompts/05_technical_effect.md`

**步骤 6｜输出附图方案** → `Read prompts/06_drawings.md`
- 制图规范见 `references/drawing_spec.md`。

**步骤 7｜组装成稿与闭环自检** → `Read prompts/07_assembly_qc.md`
- 撰写语言规范（术语、句式、禁用词）见 `references/drafting_spec.md`。
- 必跑：`python scripts/check_draft.py <成稿.md> [--matrix mapping.csv]`。

## 关键引用与规范

- 撰写语言与禁用词规范：`references/drafting_spec.md`
- 计算机模型创新点挖掘套路库：`references/innovation_playbook.md`
- 专利附图制图规范与附图说明模板：`references/drawing_spec.md`
- 模型技术类型归类速查：`references/domain_taxonomy.md`
- 三维映射表模板：`assets/mapping_matrix.csv`
- 成稿模板：`assets/output_template.md`
- 完整示例（滚动轴承故障诊断，自检全 PASS）：`assets/example_bearing_fault.md`
- 自检脚本：`scripts/check_draft.py`

## 使用注意

- 输出语言跟随用户；专利正文一律使用**规范技术撰写语言**，杜绝论文式抒情、口语化、营销化表述（如"极大地""革命性""显著优于一切"）。
- 效果可量化时**必须给出量化口径**（提升百分比、FLOPs 下降、时延、参数量、显存、功耗、准确率/召回率/F1），量化数据须来自用户提供资料或明确标注为「（推定，待实验验证）」。
- 涉及算法本身时，务必将模型处理与外部**技术数据/物理过程**绑定，规避《专利法》第 25 条客体风险。
- 本申请为**国内发明专利**导向，不套用 US/EPO 体例。
