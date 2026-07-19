# 可选分支:为笔记生成 AI 示意图 / 流程图(gpt-image-2 MCP)

> 何时读本文件:**仅当当前环境注册了 gpt-image-2 MCP**(工具 `mcp__gpt-image-2__generate_image` 可用)且打算给笔记配示意图时。这是 process.md Step 4A 的展开层;MCP 不可用则整段跳过,不影响任何笔记产出。

可在写笔记时为少数高价值位置生成**示意图 / 流程图 / 概念图**辅助理解。

> ⛔ **不可逾越的红线(等同"不编造")**:
> - 只能画**示意 / 流程 / 概念 / 类比**图,内容必须**忠于论文文字描述**(如方法 pipeline 按论文步骤画),不臆造模块。
> - **严禁**生成看起来像论文**真实实验结果**的图:性能曲线、定量柱状/折线图、数据表截图、或冒充论文原图(Fig. X)的图像——那等于伪造证据。
> - **严禁**在 `实验结果` 笔记里生成任何"结果图"。
> - 每张 AI 图**必须**紧跟一行图注,**明确标注**:`> 🤖 AI 生成示意图(非论文原图),仅辅助理解,以原文为准。`

执行细则:

1. **能力探测**:仅当 `mcp__gpt-image-2__generate_image` 工具实际可用时才执行;否则在 `plan.md` 失败日志记一条(缺失类型: 工具)并跳过。
2. **数量克制**:每篇 **1–3 张**高价值图,典型分配:
   - `方法介绍`:1 张**方法流程图**(按第 2.1 节的文字版流程画,常规论文最值得做)。
   - `主笔记` 或 `简报`:可选 1 张**核心概念 / 定位示意图**。
   - 综述类:可选 1 张**分类体系(taxonomy)树状示意图**。
3. **保存位置**:存到该论文目录的 **`assets/`** 子目录(与 `images/`=论文原图严格区分)。调用时传 `output_dir=<论文目录>/assets`、`filename_prefix=<File Stem 简写>-<图类型>`(如 `-method-flow`),从返回的 `structuredContent.images[].file_path` 取实际文件名。
4. **嵌入**:用 `![[assets/<实际文件名>]]` 嵌入对应笔记,**紧跟强制图注**(见红线)。注意 gpt-image-2 不支持透明背景,示意图用白底即可;尺寸建议预设 `1536x1024`(横版流程图)或 `1024x1024`。
5. **提示词写法**:用论文方法的真实步骤/模块名构造 prompt(英文或中文均可),要求"clean schematic diagram / flowchart, labeled boxes and arrows, no fake numbers, white background";不要让模型自由发挥成"看起来像真实结果"的图。
6. **同步即用**:生成是同步的——拿到 `file_path` 确认文件已存在后再写嵌入,使其在 Step 6 QA 时即存在(`validate_notes.py` 会校验 `assets/` 嵌入存在性,无需延迟回填)。
7. 把生成了哪些图记入 `plan.md` 的 `ai_diagrams`(便于复查与避免重复生成)。

## 降级分支:NotebookLM 视觉不可用时,用 gpt-image-2 生成"杂志风信息图"(2026-07 实测可行)

> 触发条件:Step 8 的 NotebookLM 视觉任务 `blocked`(订阅到期/配额/CLI 不可用)**且** gpt-image-2 MCP 可用。此时可用 gpt-image-2 生成一张**NotebookLM 风格的中文信息图**,替代 `_infographic_zh.png` 的角色(slide-deck 无替代,维持 blocked)。

执行要点(在上面红线全部适用的前提下):

1. **风格要求(与"流程图"划清界限,这是本分支的核心)**:NotebookLM 信息图是**杂志式海报**,不是 boxes-and-arrows 流程图。prompt 必须指定:浅色渐变背景、大标题 + 2–4 行中文导语段、中央大幅光泽插画(hero illustration,主题化比喻论文核心)、左右两栏"问题/方法"图标条目(各 3 条,小图标 + 粗体标题 + 两行描述)、底部圆角面板放 2–3 张数据卡片、右下角角标。风格词:"polished tech magazine / NotebookLM-style summary graphic, soft light gradient background, glossy semi-3D detailed icons, dense but organized magazine layout, no flowchart arrows between sections"。
2. **数字纪律**:数据卡片**只允许使用已通过 Step 6/6B 核对回原文的真实指标**(如 EER/ACC 组合值),且必须是文字数字,不画性能曲线/柱状图——伪造数据的红线不变。没把握的数字宁可不放。
3. **参数**:竖版 `1024x1536`(或更接近 NotebookLM 比例的 `1536x2720`,更贵更慢),`quality: high`(中文小字多时必须 high),`filename_prefix=<简写>-infographic`。实测成本约 $0.03(1024x1536)–$0.12(1536x2720)。
4. **落位与 banner**:存 `assets/`,嵌入主笔记"视觉框架图"节与简报第 0 节,紧跟强制 AI 图注;**主笔记 `banner` 可指向该图的文件名**(裸文件名,Obsidian 按文件名解析),等价于 NotebookLM infographic 的 banner 角色。
5. **记录**:`plan.md` 的 `ai_diagrams` 写明"替代 blocked 的 NotebookLM infographic";失败日志保留 NotebookLM blocked 的原因条目,不因有替代品而删除。
6. 角标建议含"AI 生成示意图"字样(与图注双保险)。

可直接套用的 prompt 骨架(替换【】内容):

```text
Vertical infographic poster in the style of a polished tech magazine / NotebookLM-style
summary graphic. Soft light-blue gradient background, cool blue-purple-teal palette,
glossy semi-3D detailed icons, dense but organized magazine layout. All body text in
Simplified Chinese, rendered accurately.
TOP: bold Chinese headline "【论文中文题】", then a 3-line Chinese intro paragraph: "【导语】".
HERO ILLUSTRATION (center, large): 【论文核心的主题化比喻场景,如雷达扫描两种波形】.
MIDDLE: two side-by-side columns. Left header "【问题栏标题】" with 3 entries
(icon + bold title + 2-line description): 【三条】. Right header "【方法栏标题】" with 3 entries: 【三条】.
BOTTOM: rounded panel header "【指标面板标题】", three glossy stat cards, each icon +
gradient pill number + caption: 【仅用已核实的真实数字】.
FOOTER small text bottom-right: "【会议年份】 · AI 生成示意图".
No flowchart arrows between sections. No fake data charts.
```
