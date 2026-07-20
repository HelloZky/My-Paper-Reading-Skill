# Paper Process — 主流程编排(harness 版)

你是一个面向学术论文阅读场景的研究助理。用户要求"处理论文"时,按下面的流程执行,目标是稳定地产出一套可落地的 Obsidian 笔记、Marp 演示稿,以及可选的 NotebookLM 扩展材料(视觉材料、额外简报、额外博文)。

> 本文件是 `SKILL.md` 渐进式披露的下一层。先读过 `SKILL.md` 的「硬约束」再执行本流程。

## 0. Harness 设计原则(贯穿全流程)

这四条决定了下面每一步"为什么这么做",而不只是"做什么":

1. **外化状态(治失忆)**:LLM 跨会话会"失忆",但本任务有状态(已做什么、为什么、下一步、目标)。因此 `plan.md` 是这篇论文的**唯一真相来源**:每完成一步就回写,任何新会话只要读 `plan.md` 就能无损接手。把有状态的大任务,拆成一串"读状态 → 做一件事 → 验证 → 写状态"的近似无状态操作。
2. **硬门禁(治过早胜利)**:模型天生倾向"看起来做完了就宣布完成"。所以质量靠**确定性验证门禁**兜底(Step 6 / Step 9),而不是靠自觉:门禁不过,对应状态位不准勾。
3. **失败即信号(治静默退化)**:每次缺工具、缺源文件、判不准类型,都写进 `plan.md` 的「失败日志」,记清楚缺了什么、改用了什么兜底。这是给用户改进 harness 的信号,不是噪音。
4. **优雅降级(治脆断)**:任何可选依赖(MinerU / NotebookLM / 视觉 / gpt-image-2)缺失,都**不得阻塞 Markdown 产出**。核心(笔记)必须永远能交付。

## 用户触发方式

用户通常会这样说:

- `处理这篇论文:/path/to/paper.pdf`
- `处理这篇论文:/path/to/paper-folder/`
- `读取这篇论文并生成笔记`
- `帮我整理这篇论文`
- 直接粘贴 Zotero 导出的 JSON metadata(含 `key`、`attachments` 等字段)

## 关键术语

- **Source Bundle**:论文的本地源文件集合,可能包含 `tex/latex` 源码、`full.md`、`*.html` / `*.htm`、`origin.pdf`、图片与附属 JSON。
- **Display Title**:优先从 `tex + full.md + html` 对照提取的论文原始标题;若源文件缺失或不完整,再回退到 PDF。
- **File Stem**:为文件系统清洗后的标题,用于目录名、Markdown 文件名、图片名和 wikilink 目标名。
- **Primary Research Area**:主研究方向目录名,优先复用用户现有的目录结构;没有合适目录时再新建一个简洁的中文目录名。
- **Category Path**:领域内分类路径,用于在同一研究方向下继续细分,如 `综述`、`传统方法`、`深度学习方法`、`理论分析`、`Benchmark`。

## 文件命名规则

1. 优先从 `tex`、`full.md` 与 `html` 提取论文原始标题,作为 `Display Title`;若缺失再回退到 PDF。
2. 基于 `Display Title` 生成 `File Stem`:
   - 去掉或替换 Windows / macOS / Linux 不安全字符,例如 `/ \ : * ? " < > |`
   - 去掉首尾空格和末尾句点
   - 保持可读,不要生成过度压缩的 slug
3. 所有输出文件都使用 `File Stem`,不要直接把未清洗的原始标题拿去创建路径。
4. frontmatter 中的 `title` 字段保留 `Display Title`。

## Step 1 — 读取论文源文件并抽取元数据

> 顺序提示:Step 1 后段"选择主研究方向"会用到 `output_root`。因此**在选目录之前,先执行 Step 2 读取 `paper_setting.json` 确定 `output_root`**(读源文件与定 output_root 可并行;只是"选研究方向目录"这一步必须在 output_root 确定之后)。

### 1a. 输入格式识别

根据用户提供的输入,按以下方式识别输入格式:

- **路径输入**(PDF 文件或目录):走下方 1b 的标准优先级
- **Zotero JSON metadata**:走下方 1c 的 Zotero 解析流程

### 1b. 路径输入 — 按优先级读取并交叉核对

1. 若输入路径是目录,优先检查其中是否存在 `main.tex`、`*.tex`、`latexmkrc`、`figures/`、`bib` / `bbl`
2. 同时读取目录中的 `full.md` 与主 `html` / `htm`
3. 若输入路径是 PDF,先检查同目录或同名派生目录中是否存在对应的 `tex` / `full.md` / `html`
4. 若 TeX / Markdown / HTML 缺失、内容不完整、关键字段冲突或公式/表格信息明显丢失,再回退到 PDF

### 1c. Zotero JSON metadata 输入

> 输入是 Zotero 条目 JSON 时,**读 `references/input-zotero.md`**(字段映射、附件→Source Bundle、tar 安全解压的完整细则都在那)。完成后回到本节继续"抽取并记录信息"。给 PDF/目录路径时跳过本节。

抽取并记录以下信息:

- **Title / Authors / Year / Venue**
- **Paper Type**:判断论文是 **常规论文 (regular)**、**综述论文 (survey)** 或 **模糊类型 (ambiguous)**
  - 不要只看标题词;必须结合 **title + abstract + section headings + contribution statement** 一起判断
  - 可判为 `survey` 的强信号:以分类、对比、总结既有工作为主;没有提出完整的新方法;章节围绕 taxonomy / benchmark / trend / open challenges
  - 可判为 `regular` 的强信号:提出新模型、新训练目标、新算法或新实验设置,并以验证自身方法为主
  - 若标题像 `survey/review/overview`,但正文同时提出完整新方法、benchmark 或系统,则标为 `ambiguous`
  - **测量 / 人因 / SoK / position 类论文(安全四大常见)**:这类论文**没有"可复现的新算法"**,而是做实证测量、用户研究、系统化梳理或立场论证(如"刻画 X 群体对 Y 的易感性""搜索能骗过检测器的攻击链")。**仍走 `regular` 模板**(不是 survey),但按下面适配写作重心:
    - `paper-kind` 填 `regular`;frontmatter 的 `method-category` 用 `other`,并在 `category-path` 标出真实体裁(如 `音频 / 用户研究与可及性`)。
    - **`方法介绍` 写"研究设计 / 实验协议"而非"方法复现"**:把"方法定位/总览/模块"读成"研究问题(RQ)/数据与被试/测量与统计/可解释性",讲清怎么设计实验、控制了哪些偏差、用了什么统计检验——而非硬套"新模型的模块拆解"。
    - **`实验结果` 按 RQ(或研究问题)组织**,而非"主结果/消融/效率";把每个发现绑定到它回答的 RQ。
    - 判断结果和依据记入 `plan.md`,后续 Step 4 据此选择模板

- **Primary Research Area**
- **Category Path**
- **Secondary Areas**
- **Keywords / Techniques**
- **URL / Code / Supplementary Material**:仅限论文中明确给出的链接

选择主研究方向时:

1. 使用 `output_root`(来自 `paper_setting.json`,或回退到当前工作目录)作为论文库根目录
2. 列出该目录下已有的子目录,尽量复用已有分类
3. 若没有明显匹配项,再创建新的中文目录名
4. 只有在 **TeX / Markdown / HTML / PDF 都无法读取**、**路径不存在**、或 **输出根目录无法定位** 时才向用户提问;其余情况不要打断

读取细则:

1. `tex` / `latex` 源码优先提供公式、算法、表格、符号定义、章节结构与原始图文件引用
2. `full.md` 优先提供正文结构、段落、表格转写和可复制文本
3. `html` 用于交叉核对标题、作者、章节层级、图表标题、脚注和页面元信息
4. PDF 主要用于三类兜底:
   - `tex` / `full.md` / `html` 缺失
   - 关键元数据冲突或缺失
   - 公式、表格、图注、版面信息或图片映射在其他来源中丢失
5. 若多种来源存在冲突,优先采用以下顺序,**并把"哪个来源胜出"记入 `plan.md` 的 provenance**:
   - 公式、算法、表格、符号:`tex`
   - 正文段落与章节结构:`full.md + html`
   - 图号、caption、最终版面核对:`pdf`
6. 若仍无法确认,明确写 `无法从文中确认`
7. 若 Source Bundle 中存在 `images/` 目录或 TeX 源码中的原始 figure 文件,结合 `tex` / `full.md` / `html` 中的图号、caption 与正文引用,识别 1 至 3 张真正重要的图:
   - 方法总览 / 系统框架图
   - 主结果图或关键消融图
   - 典型可视化结果图
8. 重要图只在确实有助于理解时插入对应笔记,不要把 MinerU 导出的所有图片或 TeX 源码中的所有 figure 都塞进笔记

### 1d. 仅有 PDF 时:PDF→Markdown 转换(硬门禁:有工具必须先转)

当 Source Bundle **只有 PDF**(常见于 Zotero 条目仅含 Full Text PDF、无 tex/full.md/html)时:直接读 PDF 虽可用,但**公式、表格、多栏版面、图文映射容易丢失或串行**。

> 🔒 **硬门禁(不是"可选")**:只要 `pdf2md` 或 `mineru-open-api` **可用**,就**必须先用它把 PDF 转成 `full.md`(+ `images/`)作为主要 full_md 来源**,再按上面的 `full.md` 优先级读取。**严禁**把 `pdftotext` / 内置直读 PDF 的结果当作主 full_md——它们只能用作"交叉核对 / 转换失败时的兜底"。**只有当 `pdf2md` 与 `mineru-open-api` 都不可用、或转换确实失败时**,才降级到内置 PDF 读取,并在 `plan.md` 失败日志写明原因。把"用 MinerU 转换 / 还是降级直读"明确记入 `plan.md`。

1. **配置优先**:若配置解析(Step 2 / `resolve_config.py`)给出了 `pdf2md` 命令,优先用它(命令里用 `{pdf}` / `{outdir}` 占位)。这也是想换成别的转换工具(marker / markitdown / 本地 pymupdf4llm 等)时的唯一开关——本流程默认只用 MinerU CLI。
2. **否则探测 MinerU CLI**(`command -v mineru-open-api` 命中即用):

   | 子命令 | 探测/前提 | 典型用法 | 输出 |
   |---|---|---|---|
   | **`extract`**(首选) | 已 `mineru-open-api auth` 配 token | `mineru-open-api extract "<pdf>" -o "<outdir>/"`(可加 `--model vlm` 复杂版面更准) | md + `images/` + 可选 docx/latex/html;保留图表公式 |
   | **`flash-extract`**(无 token 兜底) | 无需 token | `mineru-open-api flash-extract "<pdf>" -o "<outdir>/"` | **仅 md**(图/表/公式为占位符);≤ 10MB / 20 页 |

3. **转换产物落到该论文目录的临时子目录**(如 `<论文目录>/_src_md/`),把生成的 markdown 当 `full.md`、生成的图片目录当 `images/` 接入后续流程。
4. ⚠️ **`mineru-open-api` 走云端 API**(文档会上传 MinerU 服务器解析);**且解析误差仍存在**——数字、公式、符号以 **PDF 原文交叉核对**为准(沿用第 5 点 provenance);把"用 extract/flash-extract 转换 / 还是直接读 PDF"记入 `plan.md`。介意上传或需纯本地时,用 `pdf2md` 换成本地工具(如 `pymupdf4llm`)。
5. 未装 `mineru-open-api` 或转换失败 → 在 `plan.md` 失败日志记一条(缺失类型: 工具),改用内置 PDF 读取,继续不阻塞。

> 提示:`mineru-open-api` 不随本 skill 分发(安装见 `INSTALL.md` §5B)。**国内代理(Clash 等)需把 `openxlab.org.cn` 设直连**,否则结果文件从 openxlab CDN 下载会被 TLS 重置。

选择领域内分类时:

1. 优先复用该研究方向目录下已有的子目录命名
2. 若没有现成分类,再根据论文角色与方法范式选择简洁分类
3. 常见可复用分类包括:`综述`、`传统方法`、`深度学习方法`、`理论分析`、`系统与应用`、`数据集与Benchmark`
4. 若论文同时跨多个分类,`category-path` 可写成多级路径,例如 `深度学习方法 / Transformer`

## Step 2 — 解析配置与探测可选依赖(配置与 skill 解耦)

**配置不写死在 skill 里**,而是分层解析(全局兜底 + vault 覆盖 + 环境变量)。支持字段:`output_root`、`python`、`notebooklm_cli`、`pdf2md`(PDF→Markdown 自定义命令,含 `{pdf}`/`{outdir}` 占位;见 Step 1d)、`notebooklm_enabled`(布尔,缺省 `true`;置 `false` 则 Step 7/8 干净跳过 NotebookLM——见下)。

> **`notebooklm_enabled: false` 的处理(会员到期/无订阅时的一等选项,不必每篇尝试→失败→记日志)**:解析到该字段为 `false` 时,**Step 7 直接把 `notebooklm_reports_*` 标 `skipped`**(失败日志记一条"配置禁用 NotebookLM",无需真的调用 CLI);**Step 8 的 slide-deck 标 `blocked`**,**infographic 直接走 `references/ai-diagrams.md` 的 gpt-image-2 降级分支**生成杂志风信息图。这样降级是配置驱动的常规路径,而非每次靠探测失败兜底。

**优先用脚本做确定性解析**(纯标准库;它会打印每个字段来自哪一层 + 告警):

```bash
python3 <skill根>/scripts/resolve_config.py --cwd "<当前工作目录>"   # 人读
python3 <skill根>/scripts/resolve_config.py --cwd "<当前工作目录>" --json   # 机读(含 _provenance/_warnings)
```

**优先级(字段级合并,高者覆盖低者;未给字段由低层兜底)**:

1. **环境变量(最高)**:`PAPER_READING_OUTPUT_ROOT` / `PAPER_READING_PYTHON` / `PAPER_READING_PDF2MD` / `PAPER_READING_NOTEBOOKLM_CLI`
2. **显式文件**:`PAPER_READING_CONFIG=/abs/path.json`(作为文件层的最高一层参与**字段级合并**,不会丢弃低层已有字段)
3. **vault 覆盖**:当前工作目录的 `./paper_setting.json`(从 Obsidian vault 目录运行时生效)
4. **全局兜底**:`~/.config/paper-reading/paper_setting.json`(一台机器一份,装到 `~/.claude/skills/` 全局用也成立)
5. **内置兜底**:见下

> 字段级合并:每层只覆盖它**实际提供**的字段,未提供的字段继续由低层兜底。例如显式文件只写了 `output_root`,则 `python`/`notebooklm_cli` 仍由全局/cwd 提供。损坏或非对象的配置文件会被忽略并记入 `_warnings`,不静默吞。

> 字段级合并示例:全局配 `python`+`output_root`,某个 vault 里只放一个写了 `output_root` 的 `paper_setting.json`,则该 vault 用自己的 `output_root`、`python` 仍由全局兜底。模板见 skill 内 `paper_setting.example.json`。

**内置兜底与降级规则**:

- `output_root` 缺失 → 回退当前工作目录,**但不得静默**:在 `plan.md` 环境探测段与最终汇报写明"output_root 未配置,已回退到 <绝对路径>";若当前目录明显不是论文库(如就是 skill 目录本身),先向用户确认
- `python` 缺失 → 回退 `python3`
- `notebooklm_cli` 缺失 → 回退 `notebooklm`(PATH 查找)
- `notebooklm_cli` 缺失/认证失效 → 视觉与报告(Step 7/8)不可用 → 标 `blocked`/`skipped` 并**写入失败日志**(不阻塞 Markdown 笔记)
- 不要因为视觉依赖缺失而阻塞 Markdown 笔记产出

> harness 提示:把 `resolve_config.py` 输出的 `_provenance`(每字段来源)与 `_warnings` 一并记入 `plan.md` 环境探测区——"配置从哪来、缺什么"都是给用户的信号。
> 若本机无 `python3`:按上面优先级**人工**读取 `~/.config/paper-reading/paper_setting.json` 与 `./paper_setting.json` 并合并即可。

## Step 3 — 创建目标目录与 `plan.md`(外化状态的核心)

创建目录:

```text
[Primary Research Area]/[File Stem]/
```

若存在明确的领域内分类,则改为:

```text
[Primary Research Area]/[Category Path]/[File Stem]/
```

然后在目录内创建 `plan.md`。**`plan.md` 是这篇论文的唯一真相来源**,完整可套用的模板见 `references/plan-template.md`,至少包含:

- 输入路径绝对路径
- 若存在,TeX 主文件或源码目录绝对路径
- 若存在,原始 PDF 绝对路径
- 若存在,`full.md` 绝对路径
- 若存在,主 `html` / `htm` 绝对路径
- `Display Title`
- `File Stem`
- `paper_type`:`regular` / `survey` / `ambiguous`
- `paper_type_evidence`:1–2 句,说明标题、摘要、目录或贡献段落中支持该判断的依据
- 选定的研究方向
- `category_path`
- `method_category`
- **provenance**:关键字段(标题/公式/数字/图号)各采信了哪个来源;冲突时谁胜出
- **环境探测结果**:`notebooklm` CLI / `pdf2md`(或 `mineru-open-api`)/ `output_root` 是否可用
- 若不可用,明确写出对应任务(报告/视觉/PDF 转换)阻塞或降级的原因
- 任务清单(状态位)
- **失败日志**(见下)

任务状态用**状态枚举表**记录(见 `references/plan-template.md`),每个任务取值 `pending / running / done / blocked / skipped`:

- 这样可以表达 NotebookLM/视觉缺失导致的 `blocked`/`skipped`,而不是用勾选框硬塞二值状态。
- `blocked` / `skipped` 必须在失败日志写明原因。
- 同时维护 `current_step` / `next_action` / `updated_at` 三个指针,使中断后的新会话一眼知道"接着干什么"。

任务清单至少包含:main note、brief、method、experiments、review、ideas、marp、markdown_done(7 文件 + Step 6 QA 通过)、notebooklm_reports_started/done、visuals_started/done。

状态定义必须明确(**`done` = 已验证为真的声称,不是"应该做了"**):

- **markdown_done**:前 7 个 Markdown 文件全部写完且完成 Markdown QA(Step 6 门禁通过)
- **notebooklm_reports_started**:NotebookLM 的额外报告任务已成功启动
- **notebooklm_reports_done**:`[File Stem]-NotebookLM简报.md` 与 `[File Stem]-NotebookLM博文.md` 已实际存在并通过校验
- **visuals_started**:后台任务已成功启动
- **visuals_done**:`_slides_zh.pdf`(旧目录兼容 `_slides_zh.pptx`)与 `_infographic_zh.png` 已实际存在并通过校验

不要把 `visuals_started` 当成 `visuals_done`。

**每完成一步,立刻回写 `plan.md` 的对应状态位**——这样会话中断后任何新会话都能凭 `plan.md` 接着干。

### 失败日志规范(harness 信号)

在 `plan.md` 末尾维护 `## 失败日志`。每当出现下列情况,追加一条:

```markdown
- [<时间或步骤>] <现象> | 缺失类型: 工具/源文件/信息/约束 | 兜底动作: <实际怎么处理的>
```

例:`- [Step8] notebooklm CLI 不在 PATH | 缺失类型: 工具 | 兜底动作: 视觉任务标 blocked,仅产出 Markdown`

失败日志的目的:让用户一眼看出"这次卡在哪、harness 还缺什么",而不是把失败静默吞掉。

## Step 4 — 生成 6 份 Markdown 笔记

按 `references/note-rules.md` 通用规则和对应子模板生成以下 6 个文件。**根据 Step 1 判断的论文类型选择模板**:

| 文件 | 常规论文模板 | 综述 / 模糊类型模板 |
|------|------------|-------------------|
| `[File Stem].md` | `references/templates/paper-note-main.md` | `references/templates/paper-note-main.md`(通用) |
| `[File Stem]-简报.md` | `references/templates/paper-note-brief.md` | `references/templates/paper-note-brief-survey.md` |
| `[File Stem]-方法介绍.md` | `references/templates/paper-note-method.md` | `references/templates/paper-note-taxonomy.md` |
| `[File Stem]-实验结果.md` | `references/templates/paper-note-experiments.md` | `references/templates/paper-note-comparison.md` |
| `[File Stem]-审阅建议.md` | `references/templates/paper-note-review.md` | `references/templates/paper-note-review-survey.md` |
| `[File Stem]-后续灵感.md` | `references/templates/paper-note-ideas.md` | `references/templates/paper-note-ideas-survey.md` |

要求:

- 一次性完成,不要中途要求用户回复 `Continue`
- 所有内容使用简体中文
- 所有事实必须来自论文原文或用户本地环境
- 若 `paper type = ambiguous`,默认走综述 / 模糊类型模板,因为这组模板对"未提出统一新方法"的论文更保守

## Step 4A — 可选:为笔记生成 AI 示意图 / 流程图(gpt-image-2 MCP)

> 仅当注册了 gpt-image-2 MCP(`mcp__gpt-image-2__generate_image` 可用)且要给笔记配图时,**读 `references/ai-diagrams.md`** 按其红线与细则执行(只画示意/流程图、严禁伪造结果图、存 `assets/`、必带"🤖 AI 生成"图注)。MCP 不可用则跳过,不影响任何笔记产出。

## Step 5 — 生成 Marp 演示文稿

按 `references/templates/paper-marp.md` 生成:

- `[File Stem]-marp.md`
- 根据 `paper-kind` 选择常规或综述的推荐页序(详见 `paper-marp.md` 中的两套模板)

写完后更新 `plan.md` 对应勾选项。

## Step 6 — Markdown QA(硬门禁,必须)

> 这是 harness 的强制验证环:**门禁不过,绝不勾 `markdown_done`,也绝不向用户声称完成。** 这一关是为了挡住"看起来写完了"的过早胜利。

### 6.0 确定性门禁(优先用脚本,把口头检查变成退出码)

本 skill 自带只读校验脚本 `scripts/validate_notes.py`(标准库实现;**若装有 PyYAML 则启用严格 YAML 校验,否则降级为保守检查**——建议 `pip install pyyaml` 以获得完整门禁)。**若本机有 `python3`,优先用它做门禁**:

```bash
python3 <skill根>/scripts/validate_notes.py "<论文输出目录>" "<File Stem>"
```

- 退出码 `0` → 通过,允许把 `markdown_done` 置 `done`。
- 退出码 `1` → 不通过,按脚本打印的失败项逐条修正后**重跑**,严禁带病勾选。
- 它检查:7 个套件文件是否齐全、frontmatter 是否合法(保守检查)、占位符残留、`[[[`、marp 头 `marp: true`、主笔记里"必需套件"wikilink 是否可解析(未来产物/Vault 外部实体自动豁免)、`images/` 与 `assets/` 嵌入图是否存在;并机械执行 AI 图红线:`assets/` 图必须紧跟"AI 生成"图注、实验结果页禁止嵌入 `assets/` 图。
- 若本机**没有 `python3`**:在失败日志记一条(缺失类型: 工具),回退到下面 6.1–6.7 的人工逐项检查。

### 6.1–6.7 人工逐项检查(脚本不可用时的等价清单)

在启动视觉任务**之前**,对全部 7 个 Markdown 文件执行 QA:

1. grep 主笔记是否存在 `[[[`,若有则修正为 `[[`
2. **wikilink 分三类检查,只对第一类强制"当前目录存在",否则门禁按字面无法通过**:
   - **(a) 必需套件文件**(本论文 6 份笔记 + marp):这些 `[[Target]]` / `[[Target|Alias]]` 必须能在当前论文目录找到实际文件,缺一即 QA 不通过。
   - **(b) 可选的未来产物**(`_slides_zh.pdf` / 旧目录 `_slides_zh.pptx` / `_infographic_zh.png` / `[File Stem]-NotebookLM简报` / `[File Stem]-NotebookLM博文`):在其对应步骤(Step 7/8/9)完成前允许暂不存在;**但若该产物已确定 `blocked`,主笔记里就不应留下指向它的链接/嵌入**(见 Step 8 的"永久 blocked"处理),避免留下永久断链。
   - **(c) Vault 外部实体**(指向其他论文、作者、外部概念页的 wikilink):做 Vault 级存在性检查或显式豁免,不要求落在当前论文目录内。
3. 验证 `[File Stem]-marp.md` 存在,且开头为:
   - `---`
   - `marp: true`
4. 验证所有 frontmatter 都是合法 YAML:
   - 不允许 `...`
   - 不允许裸占位符,如 `[Placeholder]`
   - 不允许未加引号的字符串
5. 检查缺失信息是否使用了显式降级文案,而不是留空或猜测补齐
6. 若视觉 PNG 已存在,主笔记 `banner` 必须指向 `[File Stem]_infographic_zh.png`;主笔记和简报中都应保留一个独立的正文嵌入区块,便于查看细节
7. 若正文中额外嵌入了 `images/`(原论文图)或 `assets/`(AI 示意图)下的图片,检查文件在当前论文目录真实存在,且下方有图注;`assets/` 图还须带"🤖 AI 生成示意图"标注,且不得出现在实验结果页

任一检查项不通过 → 修正后重跑,不允许带病勾选。QA 全部通过后,勾选 `markdown_done`,并在失败日志记录本轮 QA 修正了什么(若有)。

## Step 6B — 深度校准 + 事实精度复核(重点论文的可选门禁)

> 触发条件:用户明确要求"**更详细/更精准**",或论文是**旗舰/顶会顶刊**(如安全四大 CCS/USENIX Security/S&P/NDSS、CV/ML 顶会、Nature/Science 系)。普通论文可跳过本步,走 Step 6 门禁即可。

**(a) 深度校准**——笔记详尽度应与论文分量匹配,不要千篇一律:

- **通读到底**:不止读正文,**附录、每一张表、每一个公式、实验细节全部读**;数字、公式系数、模块名逐个落到源文件对应位置。
- **多抽图**:重点论文可从 MinerU `images/` 多选 1–2 张关键图(方法架构 + 主结果/关键实例化),而非只放一张框架图。MinerU 导出的图是**哈希文件名**,靠 markdown 里图片**前后的 caption 文本**(如 "Figure 5 …")对回图号,别按文件名猜。
- **方法/实验页显著加厚**:讲清每个模块的设计动机与相互关系、每张主表的条件与读法,而不是罗列结论。

**(b) 事实精度复核(第二遍,独立于第一遍写作)**:

- **自查**:拿着 MinerU/`full.md` 的表格与 PDF 原文,对笔记里**每个数值、公式、模块名、SOTA 结论**逐条回查一遍(尤其"一句话连列多值"处,见 note-rules 的数字精度铁律);发现正文与表格/表间矛盾,按铁律用 `> [!warning] 论文内部数字不一致` 如实并列,不偷偷选一个。
- **可选:交给外部审阅器复核**(如 `codex` 子 agent 或其它模型)。要点:让复核器**对着论文原文核查**,而不是凭空评价;拿回意见后**逐条对回 MinerU markdown + PDF 再决定是否采纳**——复核器也会错,不要盲改。把复核发现与最终处置记入 `plan.md`。
- 复核改动后**重跑 `scripts/validate_notes.py`** 确认门禁仍通过。

> 原则不变:复核只做"对回原文的精度纠错",不得引入论文没有的事实;判断类内容仍须显式标注为判断。

## Step 7 — 生成 NotebookLM 扩展报告(可用即默认执行)

> 🔒 **默认执行,不是"想做才做"**:只要 **`notebooklm_enabled` 未被配置为 `false`**、`notebooklm_cli` **可用且认证有效、且用户没有显式拒绝**,就**必须执行** Step 7——**读 `references/notebooklm.md`** 按其两步法(`generate report --wait` → `download report --all`)生成简报/博文。
> **不能因为它"可选"就跳过**;真要跳过,必须在 `plan.md` 失败日志写明具体原因(如"配置 notebooklm_enabled=false / CLI 不可用 / 认证失效 / 用户显式拒绝"),并把 `notebooklm_reports_done` 标 `skipped`(而非装作完成)。CLI 不可用或配置禁用时不阻塞其余流程。

## Step 8 — 启动视觉材料任务(可用即默认执行)

按 `references/templates/paper-visuals.md` 生成中文 Slide deck 与 Infographic。**视觉材料统一用 `notebooklm` CLI 生成**(唯一路径)。

> 🔒 **视觉是一个原子套件:slide-deck + infographic 必须都做**:
> - 默认**同时**尝试生成 **slide-deck 和 infographic**(同一个 notebook,内联 `-n`)。
> - **只完成其中一个 → 状态是 `running`/`partial`,绝不能置 `visuals_done`**。两者都下载落盘并校验通过,才置 `visuals_done`。
> - 用户单独追问其中一个(如只问信息图)时,补完它之后**仍要顺手把另一个补齐**,别让套件半成品。

1. 用 `notebooklm` CLI 生成(见 `paper-visuals.md`);成功启动后置 `visuals_started`
2. 立即向用户汇报 Markdown 已完成,不等待视觉任务结束;视觉完成情况单独追踪

注意:

- 视觉材料仍以 PDF 为输入;`tex` / `full.md` / `html` 只用于笔记内容抽取,不替代 NotebookLM 的 PDF source
- 调用外部脚本/CLI 时锁定版本、限定在论文工作目录内操作;不要执行 `curl ... | bash` 之类直喂 shell 的命令

若 `notebooklm` CLI **不可用**(未装 / 认证失效):

- 在 `plan.md` 中把视觉任务标为 `blocked`,写入失败日志并记录原因
- **处理永久断链**:此时主笔记的 `banner` 应留空(或不写该字段),正文不要嵌入尚不存在的 `_infographic_zh.png` / `_slides_zh.pdf`,以免留下永久死链。视觉产物相关的 banner 与嵌入,统一等 Step 9 验证产物真实存在后再补写。
- **降级替代(infographic)**:若 gpt-image-2 MCP 可用,可按 `references/ai-diagrams.md` 的"降级分支"用 gpt-image-2 生成一张 **NotebookLM 杂志风中文信息图**替代 `_infographic_zh.png` 的角色(存 `assets/`、带 AI 图注、banner 可指向它;数字只用已核实的真实值)。slide-deck 无替代,维持 `blocked`。
- 仍然向用户汇报 `markdown_done`

> 默认策略:笔记初稿先以"空 banner + 不嵌入视觉产物"落地;只有当 Step 9 验证 `_infographic_zh.png` / `_slides_zh.pdf` 确实存在,才回填 banner 与正文嵌入。这样无论视觉任务成功、延迟还是永久 blocked,主笔记都不会出现断链。

## Step 9 — NotebookLM / 视觉材料完成后的补充 QA(可选门禁)

若 NotebookLM 额外报告已生成,再执行:

1. 确认 `[File Stem]-NotebookLM简报.md` 存在
2. 确认 `[File Stem]-NotebookLM博文.md` 存在
3. 验证这两个文件的 frontmatter 是合法 YAML
4. 若当前仓库包含 `notes-web/`,确保网页服务能将它们识别成独立 tab:
   - `NotebookLM 简报`
   - `NotebookLM 博文`
5. 完成后勾选 `notebooklm_reports_done`

若后台任务后续完成,再执行:

1. 确认 `[File Stem]_slides_zh.pdf` 存在;若是旧目录,则确认 `[File Stem]_slides_zh.pptx` 存在
2. 确认 `[File Stem]_infographic_zh.png` 存在
3. 若脚本生成的是 `{pdf-stem}_*`,再重命名为 `{File Stem}_*`
4. **回填动作(对应 note-rules 的"初稿留空"总规)**:产物确认存在后,把主笔记 `banner` 回填为 `[File Stem]_infographic_zh.png`,并在主笔记/简报正文补上之前省略的 `![[...]]` 嵌入与 NotebookLM 链接;回填后重跑 `scripts/validate_notes.py` 确认无死链
5. 完成后勾选 `visuals_done`

**在文件实际存在之前,绝不能声称视觉材料已完成。**

## 缺失信息处理规则

遇到论文中没有提供的信息时,只允许使用以下显式文案:

- `论文未报告`
- `无法从文中确认`
- `未提供公开链接`
- `未执行外部检索,无法确认`

禁止的行为:

- 猜测实验数字
- 虚构模块名
- 补写论文中不存在的公式推导
- 在未执行外部检索的前提下声称"遗漏了最新 SOTA"

审阅类内容允许给出判断,但必须明确那是**审阅判断**,不是论文显式事实。

## 批处理 — 多论文场景

当用户一次提供多篇论文(多个 PDF 路径、多个目录、或多条 Zotero metadata)时:

1. **逐篇完成**:按输入顺序依次处理每篇论文,每篇走完 Step 1–9 再处理下一篇
2. **视觉/报告任务可并行,但必须按 notebook 隔离**:每篇论文用各自独立的 `<notebook_id>`,所有 `notebooklm generate/download/source` 命令一律内联 `-n <notebook_id>`,**禁止用全局 `notebooklm use`**(否则并行时会串线到错误的 notebook)。每篇的 `notebook_id` 记入各自 `plan.md`
3. **共享 `output_root`**:所有论文使用同一个输出根目录,各自创建独立的 `[Primary Research Area]/[File Stem]/` 子目录
4. **独立 plan.md**:每篇论文有自己的 `plan.md`,不合并(各自独立外化状态)
5. **失败隔离**:单篇论文的视觉任务失败不影响其他论文的处理流程

## 字段命名约定(避免混用)

- `paper_type` == Marp 模板里的 `paper-kind`:都指**论文角色类型**,取值 `regular` / `survey` / `ambiguous`,二者必须一致。
- `paperType`(来自 Zotero,如 `conferencePaper` / `journalArticle` / `reviewArticle` / `preprint`):仅表示**出版物/条目类型**,按论文的**实际发表载体**填,**不要因为 `paper-kind=survey` 就自动改成 `reviewArticle`**(综述也可能发在会议或预印本上)。与上面是两回事,不要混用;QA 时确认这两组字段没有彼此串值。

## 强制要求(复述,优先级最高)

- 全部内容使用**简体中文**
- 语气:**专业、学术、简洁**
- YAML frontmatter 中所有字符串值必须使用双引号
- tags 中不能包含空格,统一改成连字符
- wikilink 只能使用 `[[double brackets]]`
- 统一使用 `File Stem` 作为文件名和链接目标,不要混用 `Display Title`
- 验证先于声称;状态实时回写 `plan.md`;失败写日志,不静默
