# Paper Reading Skill（论文阅读 · harness 版）

一个 [Claude Code](https://claude.com/claude-code) Skill：把一篇学术论文（PDF / 论文源文件目录 / Zotero 条目 JSON）转成一套结构化中文 Obsidian 笔记 + Marp 演示稿，并可选生成 NotebookLM 简报/博文、视觉材料（slides / infographic）与 AI 示意图。自动判断论文是常规 / 综述 / 模糊类型并路由模板，内置**确定性 QA 门禁**。

## 特性

- **6 份笔记 + Marp**：主笔记、简报、方法介绍、实验结果、审阅建议、后续灵感 + 演示稿。
- **确定性质量门禁**：`scripts/validate_notes.py` 机械校验 frontmatter、占位符、断链、AI 图红线，不通过不放行。
- **状态外化**：每篇论文一个 `plan.md`（唯一真相来源 + provenance + 失败日志），中断可无损接手。
- **配置与 skill 解耦**：分层解析（全局兜底 + vault 覆盖 + 环境变量），skill 内零机器路径。
- **可选能力优雅降级**：NotebookLM CLI、gpt-image-2 MCP、`paper.py` 缺失都不阻塞核心笔记。
- **递归渐进式披露**：精简 `SKILL.md` 入口 → `references/process.md` 主干 → 按需分支文件。

## 安装

```bash
git clone https://github.com/HelloZky/My-Paper-Reading-Skill ~/.claude/skills/paper-reading
```

然后按 [`INSTALL.md`](INSTALL.md) 配置 `output_root`（你的 Obsidian 论文库）即可。最简：

```bash
mkdir -p ~/.config/paper-reading
cp ~/.claude/skills/paper-reading/paper_setting.example.json ~/.config/paper-reading/paper_setting.json
# 编辑该文件，把 output_root 改成自己的论文库目录
```

可选依赖（缺了也能用，只是少对应能力）：`python3`（+ `pip install pyyaml` 启用严格 QA）、[notebooklm-py](https://github.com/teng-lin/notebooklm-py)、[gpt-image-2 MCP](https://github.com/Borys520/gpt-image-2-mcp)。详见 `INSTALL.md`。

## 使用

在 Claude Code 里说（任一形式）：

```
处理这篇论文：/abs/path/to/paper.pdf
处理这篇论文：/abs/path/to/论文源文件目录/
帮我整理这篇论文
```

或直接粘贴 Zotero 导出的条目 JSON。命令名 `/paper-reading`。

## 目录结构

```
SKILL.md                      # 入口（精简目录 + 硬约束 + 文件地图）
INSTALL.md                    # 安装与配置说明
paper_setting.example.json    # 配置模板
references/
  process.md                  # 主流程 Step 1–9 主干
  note-rules.md               # 6 份笔记共享规则
  plan-template.md            # plan.md 状态模板
  input-zotero.md             # 【分支】Zotero JSON 解析
  notebooklm.md               # 【分支】NotebookLM 报告命令契约
  ai-diagrams.md              # 【分支】gpt-image-2 AI 示意图（含红线）
  templates/                  # 各类型笔记 / Marp / 视觉模板
scripts/
  validate_notes.py           # 确定性 QA 门禁
  resolve_config.py           # 分层配置解析
  safe_extract.py             # tar 源码包安全解压
```

## 许可

MIT
