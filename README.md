# computer-model-patent-mining

计算机模型 / AI 算法类发明专利的**挖掘与说明书核心内容撰写**技能，适用于 WorkBuddy / Claude 类 Agent。

基于用户提供的**项目申请书、中英文论文、技术文档、背景技术资料**，挖掘可授权的计算机模型类发明专利点，严格实现「**技术问题 → 必要技术特征 → 技术效果**」三维一一映射，输出符合中国发明专利审查标准的说明书核心内容。

## 核心机制

1. **三维一一映射（强制）**：每个痛点 `P1-1…P3-n` 必须有对应的必要技术特征与专属技术效果，由 `scripts/check_draft.py` 强制校验，覆盖率不足即 FAIL。
2. **禁止凭空捏造**：全部技术内容须可追溯至用户资料；合理外推部分必须标注「（推定）」并登记《推定与待确认清单》。
3. **三级递进技术问题**：行业通用缺陷 → 场景化短板 → 核心技术瓶颈，字数严格 300–500。
4. **客体合规**：针对《专利法》第 25 条，将算法处理与外部技术数据 / 物理过程绑定。

## 目录结构

```
computer-model-patent-mining/
├── SKILL.md                          # 主入口：硬规则、交付契约、七步工作流
├── prompts/
│   ├── 01_material_fusion.md         # 资料融合与技术要素抽取
│   ├── 02_innovation_mining.md       # 创新点挖掘与公知/创新分离
│   ├── 03_technical_problem.md       # 技术问题（三级递进 300-500 字）
│   ├── 04_technical_solution.md      # 技术方案（必要技术特征）
│   ├── 05_technical_effect.md        # 技术效果（逐条对应）
│   ├── 06_drawings.md                # 附图方案（框架图 + 流程图）
│   └── 07_assembly_qc.md             # 组装成稿与闭环自检
├── references/
│   ├── drafting_spec.md              # 法条速查、禁用词表、客体合规改造手法
│   ├── innovation_playbook.md        # 八大切入面 40+ 创新点挖掘套路
│   ├── drawing_spec.md               # 专利制图规范与附图说明模板
│   └── domain_taxonomy.md            # 10 类模型技术归类与评测指标
├── assets/
│   ├── output_template.md            # 成稿骨架模板
│   ├── mapping_matrix.csv            # 三维映射表
│   └── example_bearing_fault.md      # 完整示例（自检全 PASS）
└── scripts/
    └── check_draft.py                # 9 项自动自检
```

## 使用方法

```bash
# 成稿后必跑自检（FAIL 项须修稿后重跑）
python scripts/check_draft.py <成稿.md> --matrix mapping_matrix.csv

# 仅统计技术问题字数
python scripts/check_draft.py <成稿.md> --count-only
```

自检项目：章节完整性、技术问题字数、痛点→特征覆盖、痛点→效果覆盖、孤儿特征、禁用词、术语一致性、附图标记一致性、数值出处核对。

## 示例

`assets/example_bearing_fault.md` 为完整示例（滚动轴承故障诊断方向），自检 9 项全 PASS：
技术问题 461 字、5 个痛点 100% 覆盖、8 条必要技术特征、图 1 系统框架图（8 个标记）+ 图 2 方法流程图。

## 与相邻专利技能的边界

| 技能 | 职责 |
|------|------|
| 本技能 | 计算机模型 / 算法类发明专利的挖掘 + 说明书核心内容撰写 |
| `patent-disclosure-skill` | 通用交底书（发明/实用/外观）、通俗解读、审查答复 |
| `mech-ctrl-patent-valuation` | 机械 + 控制组合专利价值评估 |
| `mech-ctrl-patent-interpret` | 机械 + 控制组合专利结构化解读 |
