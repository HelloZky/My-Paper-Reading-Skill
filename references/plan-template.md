# plan.md 模板(外化状态 = 这篇论文的唯一真相来源)

把下面整段复制到 `[Primary Research Area]/[File Stem]/plan.md`,边做边填、边做边把任务状态更新为对应枚举值(`pending/running/done/blocked/skipped`)。
任何新会话只要读这个文件,就能无损接手——这是 harness "外化状态、对抗失忆" 的落点。

```markdown
# Plan — <Display Title>

## 输入与源文件(provenance)

- input_path: "<用户给的绝对路径>"
- tex_main: "<main.tex 绝对路径 | 无>"
- pdf: "<origin.pdf 绝对路径 | 无>"
- full_md: "<full.md 绝对路径 | 无>"
- html: "<主 html/htm 绝对路径 | 无>"
- images_dir: "<images/ 绝对路径 | 无>"

## 进度指针(中断后新会话先看这两行)

- current_step: "<Step1..Step9 | done>"
- next_action: "<下一步具体要做什么>"
- updated_at: "<YYYY-MM-DD HH:MM>"

## 元数据

- display_title: "<原始标题>"
- file_stem: "<清洗后的文件名主干>"
- authors: "<...>"
- year: "<...>"
- venue: "<... | 论文未报告>"
- doi: "<DOI | 未提供公开链接>"
- paper_url: "<论文链接 | 未提供公开链接>"
- code_url: "<代码链接 | 未提供公开链接>"
- supplementary: "<补充材料链接 | 未提供公开链接>"
- zotero_key: "<key | 无>"
- selected_attachments: "<本次实际采用的附件文件名列表 | 无>"
- paper_type: "<regular | survey | ambiguous>"
- paper_type_evidence: "<1–2 句判断依据>"
- primary_research_area: "<研究方向目录名>"
- secondary_areas: "<次要领域 | 无>"
- keywords: "<关键词/技术点 | 无>"
- category_path: "<领域内分类 | 无>"
- method_category: "<方法范式 | 无>"

## 关键字段采信来源(冲突时谁胜出)

- 标题: <tex|full.md|html|pdf>
- 公式/算法/符号: <tex|...>
- 正文结构/段落: <full.md+html|...>
- 实验数字/表格: <tex|pdf|...>
- 图号/caption: <pdf|...>
- 冲突记录: "<哪个字段有冲突、最终采信了什么、为什么 | 无冲突>"

## 环境探测

- output_root: "<来自配置解析 | 回退到当前工作目录>"
- python: "<resolve_config 解析到的 python 路径>"
- python_version: "<`python3 --version` 输出 | 无法执行>"
- config_provenance: "<resolve_config 的 _provenance:每字段来自 global/cwd/explicit/env/fallback 的哪一层>"
- config_warnings: "<resolve_config 的 _warnings:如 output_root 回退告警、损坏配置文件告警 | 无>"
- paper_py: "<可用路径 | 不可用>"
- notebooklm_cli: "<可用 | 不可用>"
- notebook_id: "<本论文使用的 NotebookLM notebook_id(报告与视觉共用,所有命令内联 -n)| 无>"
- gpt_image_mcp: "<可用 | 不可用>"
- ai_diagrams: "<已生成的 AI 示意图列表(assets/...)| 无>"
- visuals_command: "<将要执行的完整 paper.py 命令 | 不可用,见失败日志>"

## 任务状态(状态枚举:`pending` / `running` / `done` / `blocked` / `skipped`)

> `done` = 产物已实际存在并通过校验的"声称",不是"应该做了"。`blocked` 必须在失败日志写明原因。

| 任务 | 状态 | 备注 |
|---|---|---|
| main note | pending | |
| brief | pending | |
| method | pending | |
| experiments | pending | |
| review | pending | |
| ideas | pending | |
| marp | pending | |
| markdown_done(前 7 个文件已写 + Step 6 QA 门禁通过) | pending | |
| notebooklm_reports_started | pending | |
| notebooklm_reports_done | pending | |
| visuals_started | pending | |
| visuals_done | pending | |

## 失败日志(harness 信号:缺什么、怎么兜底)

<!-- 每条格式:- [步骤] 现象 | 缺失类型: 工具/源文件/信息/约束 | 兜底动作: ... -->
- (暂无)
```

## 使用要点

- **provenance 不是装饰**:当三种来源冲突时,这里写清楚"采信了谁",日后复查或被质疑数字来源时一眼可查。
- **状态是声称,不是愿望**:只有在产物**实际存在并通过校验**后才把状态置为 `done`;`*_started` 与 `*_done` 永远分开。
- 口径:本 skill 流程文里说的"勾选 X" = "把任务 X 的状态置为 `done`"。
- **失败日志要积累**:每次缺工具/缺源文件/判不准类型都追加一条。攒多了,用户就知道该给这套 harness 补哪块短板。
