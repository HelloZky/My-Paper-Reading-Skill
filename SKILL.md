---
name: paper-reading
description: 处理学术论文并产出结构化中文笔记。仅当用户表达了"阅读/整理学术论文"的意图、且给出论文输入时触发——典型表达:"处理这篇论文/读取这篇论文并生成笔记/帮我整理这篇(几篇)论文",并附带 PDF、论文源文件目录(含 tex/full.md/html),或粘贴 Zotero 导出的条目 JSON(含 attachments)。也覆盖一次给多篇论文的批处理。不要仅因为出现一个 PDF 路径就触发(非学术 PDF 不适用)。产出:Obsidian 笔记(主笔记+简报+方法+实验+审阅+灵感)、Marp 演示稿,及可选的 NotebookLM 简报/博文与视觉材料;自动判断常规/综述/模糊类型并路由模板。
---

# Paper Reading Skill(论文阅读 · harness 版)

把一篇论文稳定地转成一套可落地的中文 Obsidian 笔记 + Marp 演示稿(+ 可选 NotebookLM 与视觉材料)。本 skill 按 **harness 工程标准**组织:用 `plan.md` 外化状态、用验证门禁兜底质量、用失败日志积累信号、靠渐进式披露控制上下文。

## 何时触发

满足任一条即进入论文处理流程:

- `处理这篇论文:/path/to/paper.pdf`
- `处理这篇论文:/path/to/paper-folder/`
- `读取这篇论文并生成笔记` / `帮我整理这篇论文`
- 直接粘贴 Zotero 导出的条目 JSON(含 `key`、`attachments` 等字段)

一次给多篇 → 见 `references/process.md` 的「批处理」一节,逐篇走完再处理下一篇。

## 三层认知(别混)

| 层 | 在本场景里是什么 | 谁负责 |
|---|---|---|
| **模型**(马) | 读论文、写笔记的 LLM 推理能力 | 不由本 skill 控制 |
| **Harness**(挽具,本 skill) | 流程编排 + 硬约束 + `plan.md` 状态 + 验证门禁 + 失败日志 | **本 skill** |
| **产品环境**(马车) | Obsidian 库、NotebookLM CLI、MinerU CLI、gpt-image-2 MCP、Marp | 探测后按需使用,缺了就降级 |

> 本 skill 只保证「挽具」这一层稳:无论产品环境缺多少可选件,**全部 Markdown 笔记必须照常产出**。

## 怎么干(主循环概览)

按 `references/process.md` 的 Step 1–9 顺序执行,核心是一个「读取状态 → 做一件事 → 验证 → 回写状态」的循环:

1. **读源文件、抽元数据、判类型**(Step 1)— `tex + full.md + html` 优先,PDF 兜底;判 `regular/survey/ambiguous`。
2. **探测环境**(Step 2)— 读 `paper_setting.json`,缺了就降级,不阻塞。
3. **建目录 + 写 `plan.md`**(Step 3)— `plan.md` 是这篇论文的**唯一真相来源/记忆**,每完成一步就回写,让任何新会话都能接手。
4. **生成 6 份笔记**(Step 4)— 按类型选模板,一次性完成。**可选 Step 4A**:若 gpt-image-2 MCP 可用,为方法流程图等少数高价值位置生成 AI 示意图(守红线)。
5. **生成 Marp**(Step 5)。
6. **Markdown QA 门禁**(Step 6,**硬门禁**)— 不过不准勾 `markdown_done`。**可选 Step 6B**:重点/顶会论文或用户要求"更详细精准"时,做深度校准 + 事实精度复核(逐个数值对回 MinerU 表格 + PDF,可选外部审阅器复核)。
7. **NotebookLM 扩展报告**(Step 7,可选)。
8. **启动视觉材料任务**(Step 8,可选,后台)。
9. **完成后补充 QA**(Step 9,可选)。

## 不可违背的硬约束(harness 的缰绳)

把这些当作**机械强制**,不是建议:

1. **不编造 + 数字可回溯**:实验数字、模块名、公式推导、SOTA 结论一律不许猜。缺失只能用固定文案:`论文未报告` / `无法从文中确认` / `未提供公开链接` / `未执行外部检索,无法确认`。凡写进笔记的数值都必须**能逐一对回源文件**(MinerU 表格单元格 + PDF 交叉核对);一句话连列多值时逐个绑定到对应行/列,严防错位串号;正文与表格/表间自相矛盾则**两值如实并列**并用 `> [!warning] 论文内部数字不一致` 标出,不许偷偷选一个(细则见 `references/note-rules.md`)。
2. **事实与判断分离**:审阅判断、延伸想法必须显式标明是判断,不得伪装成论文事实。
3. **验证先于声称**:在文件**实际存在并通过校验**之前,绝不声称该产物已完成。`visuals_started ≠ visuals_done`。
4. **状态外化**:每完成一步立即回写 `plan.md`(含 provenance 与失败日志),不靠"记得"。
5. **全简体中文**;YAML 字符串值一律双引号;tags 不含空格(用连字符);wikilink 只用 `[[双括号]]`;文件名与链接统一用 `File Stem`,不混用原始标题。
6. **优雅降级**:任何可选依赖缺失,都不得阻塞 Markdown 笔记产出;把缺失写进 `plan.md` 失败日志。
7. **工具安全**:不现场 `curl ... | bash`;调用脚本/CLI 固定版本、限定在论文工作目录内操作。
8. **AI 示意图红线**(若启用 gpt-image-2 MCP):只画忠于原文的示意/流程/概念图,**严禁**生成像真实实验结果的数据图或冒充论文原图,**严禁**在实验页生成结果图;每张存 `assets/` 且必带"🤖 AI 生成示意图"图注。等同"不编造"。

## 依赖与可移植性(诚实清单)

**自包含、可移植**(拷到 `~/.claude/skills/` 全局使用也成立):本 skill 的全部 Markdown 产出能力——`SKILL.md` + `references/`(流程、笔记规则、plan 模板、13 个模板)。**核心笔记功能不依赖父仓库。**

**依赖父仓库 `paper_reading/`、全局安装后会失效或降级**的能力:

| 能力 | 依赖 | 不可用时 |
|---|---|---|
| 视觉材料(slides/infographic) | `notebooklm` CLI(唯一路径;slide+infographic 都做) | 不可用则标 `blocked`,仅出 Markdown |
| NotebookLM 简报/博文报告 | `notebooklm` CLI | 不可用则跳过,不影响笔记 |
| AI 示意图/流程图(可选) | **gpt-image-2 MCP**(`mcp__gpt-image-2__generate_image`) | 未注册则跳过,笔记不插 AI 图;见 Step 4A |
| 笔记网页浏览 | 父目录 `notes-web/` | 跳过,不影响笔记 |
| Marp 主题 `blue` | 父目录 `.vscode/marp_themes/blue.css` | 回退 `theme: default` |
| 输出位置 / 工具路径 | **分层配置(与 skill 解耦,见下)** | output_root 缺省回退 cwd(不静默);视觉工具缺省走 notebooklm 或 blocked |

### 配置与 skill 解耦(为全局安装 / Obsidian vault 准备)

**skill 目录内不含任何机器路径**;配置由 `scripts/resolve_config.py` 分层解析,优先级(字段级合并,高覆盖低):

1. 环境变量(最高):`PAPER_READING_OUTPUT_ROOT` / `PAPER_READING_PYTHON` / `PAPER_READING_PDF2MD` / `PAPER_READING_NOTEBOOKLM_CLI`
2. 显式文件:`PAPER_READING_CONFIG=/abs/path.json`
3. **vault 覆盖**:`./paper_setting.json`(从某个 Obsidian vault 目录运行时)
4. **全局兜底**:`~/.config/paper-reading/paper_setting.json`(装到 `~/.claude/skills/` 全局用也成立)
5. 内置兜底:`output_root`→cwd(**不静默**,写进 plan.md 与汇报);`python`→`python3`;`notebooklm_cli`→`notebooklm`;`pdf2md`→无(自动探测 mineru-open-api)

> 模板见 `paper_setting.example.json`(改名为 `paper_setting.json` 放到上面任一位置)。这样:① reinstall skill 不丢配置;② 不同 vault 可用各自的 `output_root`,公共项由全局兜底;③ skill 可整体拷到 `~/.claude/skills/` 而不带任何用户路径。

## 渐进式披露(本 skill 的文件地图)

本文件只是**目录**,不是百科。按需打开下列引用文件,不要一次性全读:

| 需要做什么 | 打开 |
|---|---|
| 主流程主干 Step 1–9、类型判定、命名、批处理、`plan.md` schema、失败日志(精简骨架,分支细节见下) | `references/process.md` |
| 6 份笔记的共享规则、段落/列表取舍、Callout 规范、frontmatter 规则 | `references/note-rules.md` |
| `plan.md` 的可直接套用模板 | `references/plan-template.md` |
| **【分支】Zotero JSON 输入**:字段映射、附件→Source Bundle、tar 安全解压 | `references/input-zotero.md` |
| **【分支】NotebookLM 报告**:建 notebook、两步法取正文命令契约 | `references/notebooklm.md` |
| **【分支】AI 示意图/流程图**(gpt-image-2 MCP,含红线) | `references/ai-diagrams.md` |
| **【分支】视觉材料**(slides/infographic)后台任务规范 | `references/templates/paper-visuals.md` |
| Step 6 确定性 QA 门禁脚本(标准库;PyYAML 时严格 YAML 校验,否则降级;缺 python 回退人工) | `scripts/validate_notes.py` |
| Step 2 分层配置解析(全局兜底 + vault 覆盖 + 环境变量) | `scripts/resolve_config.py` |
| tar 源码包安全解压(纯标准库) | `scripts/safe_extract.py` |
| 配置模板(改名 paper_setting.json 放全局或 vault) | `paper_setting.example.json` |
| 各类型笔记的具体结构 | `references/templates/paper-note-*.md` |
| Marp 演示稿结构 | `references/templates/paper-marp.md` |

> 设计原则:**SKILL.md 保持精简稳定**(入口/约束/地图),细节都在 `references/`。这样上下文窗口不被撑爆,改动也"可撕可换"。
