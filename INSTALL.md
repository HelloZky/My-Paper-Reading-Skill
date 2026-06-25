# paper-reading skill — 安装与使用

把一篇学术论文(PDF / 论文源文件目录 / Zotero 条目 JSON)转成一套结构化中文 Obsidian 笔记 + Marp 演示稿,并可选生成 NotebookLM 简报/博文与视觉材料(slides / infographic)。自动判断论文是常规/综述/模糊类型并路由模板,内置确定性 QA 门禁。

## 1. 这个 skill 包含什么

整个 `paper-reading/` 文件夹是**自包含**的,不含任何机器绝对路径,可直接拷到别人机器使用:

```
paper-reading/
├── SKILL.md                  # 入口(给 Claude Code 读)
├── INSTALL.md                # 本文件
├── paper_setting.example.json# 配置模板
├── references/               # 主流程、笔记规则、plan 模板、13 个笔记/Marp/视觉模板
└── scripts/                  # validate_notes.py / safe_extract.py / resolve_config.py(纯标准库)
```

## 2. 环境要求

| 组件 | 必需? | 作用 | 缺失后果 |
|---|---|---|---|
| **Claude Code** | 必需 | 运行 skill 的载体 | 无法使用 |
| **python3** | 强烈建议 | 跑确定性 QA 门禁 / 配置解析 / 安全解压 | 缺则回退人工检查,功能仍可用但少了自动门禁 |
| **PyYAML**(`pip install pyyaml`) | 可选 | QA 门禁严格校验 frontmatter YAML | 缺则降级为保守检查 |
| **notebooklm-py**(`uv tool install "notebooklm-py[browser]"` 后 `notebooklm login`) | 可选 | 生成 NotebookLM 简报/博文 + slides/infographic | 缺则跳过这些,只出 Markdown 笔记 |
| **gpt-image-2 MCP**(见下) | 可选 | 给笔记生成 AI 示意图/流程图(方法流程图等) | 未注册则跳过,笔记不插 AI 图 |
| **MinerU CLI `mineru-open-api`**(见 §5B) | 可选 | 仅有 PDF(无 tex/html)时转出结构化文本,提升公式/表格/版面质量 | 缺则降级为内置直接读 PDF |
| **Marp CLI / Obsidian Marp 插件** | 可选 | 把生成的 `-marp.md` 导出 pptx/pdf | 缺则 `-marp.md` 仍生成,只是不自动导出 |
| **Obsidian** | 可选 | 浏览生成的笔记(笔记就是普通 Markdown) | 用任意编辑器也能看 |

> 注:`notes-web/`(本地网页浏览)、Marp `blue` 主题**不随本 skill 分发**。视觉材料统一由 `notebooklm` CLI 生成;Marp 主题缺失时自动回退 `theme: default`。

## 3. 安装位置(二选一)

- **全局(推荐)**:拷到 `~/.claude/skills/paper-reading/` → 任何项目/目录都能用,命令 `/paper-reading`。
- **项目级**:拷到 `<某项目>/.claude/skills/paper-reading/` → 只在该项目内可用。

## 4. 配置(与 skill 解耦,分层解析)

skill 本身不含路径;配置按优先级解析(高覆盖低,字段级合并):

1. 环境变量(最高):`PAPER_READING_OUTPUT_ROOT` / `PAPER_READING_PYTHON` / `PAPER_READING_PDF2MD` / `PAPER_READING_NOTEBOOKLM_CLI`
2. 显式文件:`PAPER_READING_CONFIG=/abs/path.json`
3. **vault 覆盖**:从某目录运行时,该目录下的 `./paper_setting.json`
4. **全局兜底**:`~/.config/paper-reading/paper_setting.json`
5. 内置兜底:`output_root`→当前目录(会告警,不静默);`python`→`python3`;`notebooklm_cli`→`notebooklm`;`pdf2md`→无(自动探测 mineru-open-api)

**最简单的做法**:把 `paper_setting.example.json` 改名为 `paper_setting.json`,填上自己的论文库路径,放到 `~/.config/paper-reading/`:

```bash
mkdir -p ~/.config/paper-reading
cp ~/.claude/skills/paper-reading/paper_setting.example.json ~/.config/paper-reading/paper_setting.json
# 然后编辑该文件,至少把 output_root 改成自己的 Obsidian 论文库目录
```

字段(全部可选,缺省走兜底):
```json
{
  "output_root": "/abs/path/to/你的Obsidian库/论文笔记",
  "python": "python3",
  "notebooklm_cli": "notebooklm",
  "pdf2md": ""
}
```

验证配置是否被正确读到:
```bash
python3 ~/.claude/skills/paper-reading/scripts/resolve_config.py --cwd .
```

## 5. 使用

在 Claude Code 里说(任一形式):

- `处理这篇论文:/abs/path/to/paper.pdf`
- `处理这篇论文:/abs/path/to/论文源文件目录/`(含 tex/full.md/html 更佳)
- `帮我整理这篇论文`
- 直接粘贴 Zotero 导出的条目 JSON(含 `attachments`)

skill 会:抽元数据并判类型 → 在 `output_root` 下建 `[研究方向]/[分类]/[论文名]/` → 写 `plan.md` → 生成 6 份笔记 + Marp → 跑 `validate_notes.py` 门禁 → (可选)NotebookLM 报告/视觉 → 完成后回填并复核。

## 5A. 可选:安装 gpt-image-2 MCP(给笔记画示意图/流程图)

仓库:https://github.com/Borys520/gpt-image-2-mcp ;要求 Node.js ≥20 + 有 `gpt-image-2` 权限的 OpenAI API key。

```bash
git clone https://github.com/Borys520/gpt-image-2-mcp
cd gpt-image-2-mcp && pnpm install && pnpm run build   # 产出 build/index.js
```

在 Claude Code 注册(`~/.claude.json` 或项目根 `.mcp.json`):

```json
{
  "mcpServers": {
    "gpt-image-2": {
      "command": "node",
      "args": ["/abs/path/to/gpt-image-2-mcp/build/index.js"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "OPENAI_BASE_URL": "https://你的代理/v1"
      }
    }
  }
}
```

> `OPENAI_BASE_URL` 仅在用代理/自建网关时需要;官方 API 可省略。注册后重启 Claude Code,skill 检测到 `mcp__gpt-image-2__generate_image` 即会在合适位置(方法流程图等)生成 AI 示意图。
> ⚠️ 注意:① 该模型按量计费(非免费,除非你用自建网关);② AI 图仅为**示意/流程图**且会标注"🤖 AI 生成",**不会**生成冒充论文实验结果的数据图。

## 5B. 可选:安装 MinerU CLI(仅有 PDF 时提质)

当论文只有 PDF(典型:Zotero 条目仅含 Full Text PDF)时,用 [MinerU CLI `mineru-open-api`](https://github.com/opendatalab/MinerU-Ecosystem) 把 PDF 转成结构化 `full.md`(+ 图片),比直接读 PDF 更准(尤其公式、表格、多栏版面、中文)。skill 会**自动探测 `mineru-open-api`** 并使用,默认就用它。

```bash
npm install -g mineru-open-api          # 或 go install ...mineru-open-api@latest
mineru-open-api auth                     # 配 token(解锁 extract 完整模式;flash-extract 免 token)
mineru-open-api version                  # 验证
```

- **`extract`**(需 token):保留图表/公式、可多格式、批量 —— skill 默认用它。
- **`flash-extract`**(免 token):仅 markdown、≤10MB/20页 —— 无 token 时的兜底。
- ⚠️ **走云端 API**(文档上传 MinerU 服务器解析)。
- ⚠️ **国内代理(Clash 等)务必把 `openxlab.org.cn` 设为直连**,否则结果文件从 openxlab CDN 下载会被 TLS 重置(表现为 `download ... EOF` / `SSL_ERROR_SYSCALL`)。

想换别的转换工具(marker / markitdown / 纯本地 `pymupdf4llm` 等,或介意云端上传),在 `paper_setting.json` 设 `pdf2md`(`{pdf}`/`{outdir}` 占位)即可覆盖默认:

```json
{ "pdf2md": "mineru-open-api extract {pdf} -o {outdir}" }
```

> 不装也没关系:skill 会降级为内置直接读取 PDF。

## 6. 常见问题

- **没装 notebooklm**:正常,只少了 NotebookLM 简报/博文与 slides/infographic,Markdown 笔记照常产出(会在 `plan.md` 失败日志标 blocked)。
- **没装 pyyaml**:QA 门禁自动降级为保守检查,仍能用;装上更严格。
- **output_root 没配**:会回退到当前目录并显式告警——建议先按第 4 节配置好。
- **想给不同 Obsidian 库用不同输出位置**:全局配公共项,在各库根目录放一个只写 `output_root` 的 `paper_setting.json` 即可覆盖。
