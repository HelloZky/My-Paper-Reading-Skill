# Paper Note — Main Folder Note (`[File Stem].md`)

**Filename**: 使用清洗后的 `File Stem`，不要直接使用未清洗的原始标题。  
**Folder**: `[Primary Research Area]/[File Stem]/`

主笔记不是“越短越好”的封面页，而是整套笔记的稳定入口。它不需要像方法页那么长，但应该让人一页内看懂：这篇论文做什么、值不值得读、属于哪一类、最该先点哪几份笔记。

## Frontmatter

```yaml
---
banner: ""   # 初稿留空,避免死链;Step 9 验证 <File Stem>_infographic_zh.png 真实存在后再回填
banner_icon: ""
uid: "YYYYMMDDHHMMSS"
aliases: []
type: "FolderNote"
desc: "一句话概括论文主题、核心贡献或综述价值"
tags:
  - "Area/Paper/<Primary-Research-Area>"
  - "Area/Paper/<Secondary-Research-Area>"
technique:
  - "<技术点1>"
  - "<技术点2>"
category-path: "<领域内分类1 / 领域内分类2>"
method-category: "<survey | traditional | deep-learning | theory | benchmark | system | other>"
zotero-key: ""
zotero-url: ""
title: "<Display Title>"
citekey: "<FirstAuthorSurname><FirstWordOfTitle><Year>"
paperType: "<conferencePaper | journalArticle | reviewArticle | preprint>"
paper-kind: "<regular | survey | ambiguous>"
publication-year: "<Year>"
author:
  - "[[Author 1]]"
  - "[[Author 2]]"
venue: "<Venue Name>"
venue-abbrev: "<Venue Abbreviation>"
shortTitle: ""
paperURL: "未提供公开链接"
star: "⭐⭐⭐"
file-stem: "<File Stem>"
---
```

## Content

```markdown
## Intro

[用 3 至 5 段写出一份扎实的中文导读，不要泛泛而谈]

> 根据 `paper-kind` 只选下面**一组**引导来写，不要把两组都输出。

**若 `paper-kind` = regular**：
- **核心任务**：论文具体要解决什么问题？
- **研究动机**：为什么这个问题值得做？
- **现有难点**：现有方法卡在哪里？
- **论文策略**：本文的总体解决思路是什么？
- **主要结论**：实验最终证明了什么？

**若 `paper-kind` = survey 或 ambiguous**：
- **覆盖领域**：这篇综述聚焦什么问题域？
- **分类视角**：作者如何组织和分类现有方法？
- **核心发现**：最重要的结论和趋势是什么？
- **实用价值**：读完这篇综述，能获得什么？

> [!abstract] 一句话定位
> [用一句话概括这篇论文最核心的贡献或价值]

## 一页式结论

- **一句话定位**：这篇论文最应该被如何归类？
- **最值得记住的 3 点**：
  - [点 1]
  - [点 2]
  - [点 3]
- **适合谁读**：这篇论文最适合什么类型的读者或什么研究阶段阅读？
- **不适合指望它解决什么**：这篇论文没有覆盖或没有说清的部分是什么？

## 发表信息（建议）

- **Venue**：[全称（简称）]
- **Year**：[年份]
- **Paper Type / Kind**：[conferencePaper / journalArticle / reviewArticle / preprint] + [regular / survey / ambiguous]
- **资源链接**：代码、项目页、补充材料；若无则明确写 `未提供公开链接`

## 视觉框架图

<!-- 初稿留空:视觉产物(infographic)尚未生成时不要写嵌入,以免死链。
     仅当 Step 9 验证 <File Stem>_infographic_zh.png 真实存在后,才回填下面这行:
     ![[<File Stem>_infographic_zh.png]] -->

## 关键原论文图（可选）

> 若 MinerU 提取到了很重要的原论文图，可补 1 张最关键的图；没有就省略本节。

![[images/<key-figure>.jpg]]

图注：Figure X，说明这张图为什么值得保留，以及它帮助理解论文的哪一部分。

## 阅读导航

> [!tip] 阅读建议
> [根据论文特点，给出最适合的阅读顺序建议，例如"这篇论文方法是核心亮点，建议先看方法介绍"]

- **先看哪一份**：
  - 如果你想快速判断值不值得读，先看 `简报`
  - 如果你想理解技术细节，先看 `方法介绍`
  - 如果你想看数字证据，先看 `实验结果`
  - 如果你想判断论文强弱，先看 `审阅建议`
- **本论文最核心的章节**：[可点名论文原文中的 section]

## paper

> 初稿只写**已存在的套件文件**(下面 6 条)。指向尚未生成产物的链接(slides PPT、NotebookLM 简报/博文)**初稿不要写**,等 Step 9 验证产物存在后再回填。

- [[<File Stem>-简报|简报]]
- [[<File Stem>-方法介绍|方法介绍]]
- [[<File Stem>-实验结果|实验结果]]
- [[<File Stem>-审阅建议|审阅建议]]
- [[<File Stem>-后续灵感|后续灵感]]
- [[<File Stem>-marp|Marp演示]]

<!-- Step 9 回填片段(产物确认存在后再加,否则删除本注释,勿留死链):
- [[<File Stem>_slides_zh.pdf|简报PPT]]
- [[<File Stem>-NotebookLM简报|NotebookLM简报]]
- [[<File Stem>-NotebookLM博文|NotebookLM博文]]
-->
```

## Rules

- `title` 保留论文原始标题；文件名和链接目标使用 `File Stem`
- 主笔记应保持“入口页”定位，但不能过于空泛；至少要让读者不点进其他页面也能理解论文定位、价值和边界
- 主研究方向默认取 `tags` 中第一个 `Area/Paper/...` 标签的最后一段；`category-path` 填该领域内的层级分类；`method-category` 填方法范式或论文角色
- 视觉材料 PNG 应作为主笔记的 `banner`，用于论文介绍区头图；同时在正文提供一个独立的“视觉框架图”区块，便于查看细节
- 若原论文中存在非常关键的框架图或总览图，可在主笔记额外保留 1 张原图，但不要和 NotebookLM infographic 重复堆叠多张
- `paperType` 按论文**实际出版物类型**填写(`conferencePaper / journalArticle / reviewArticle / preprint`);**不要**因为 `paper-kind=survey` 就自动改成 `reviewArticle`(综述也可能发在会议或预印本上),以 PDF / Zotero `type` 实际为准
- `paper-kind` 与主流程判断保持一致：`regular` / `survey` / `ambiguous`
- `Intro` 只能按 `paper-kind` 选一套侧重点来写：`regular` 用常规论文视角，`survey` / `ambiguous` 用综述视角，不要把两套提示混入最终成品
- `citekey` 采用 `<FirstAuthorSurname><FirstWordOfTitle><Year>` 风格；FirstWord 应跳过冠词和介词（a, an, the, on, in, of, for, to, with），取第一个实词
- 若输入为 Zotero metadata，`zotero-key` 和 `zotero-url` 应直接从 Zotero JSON 中填入（`zotero-url` 格式：`zotero://select/library/items/<key>`）
- `venue` 填全称，`venue-abbrev` 填标准缩写；网页中的 CCF/JCR/中科院分区由本地 lookup 数据库按这两个字段实时查询，不再手写进 frontmatter
- `简报PPT` 链接默认使用 `<File Stem>_slides_zh.pdf`
- tags 中不能有空格，统一改为连字符
- `paperURL`、`zotero-key`、`zotero-url` 不明确时使用显式降级值，不要留裸占位符
- 所有 wikilink 必须使用 `[[double brackets]]`
- 写完后检查所有链接目标在当前目录中真实存在或将在后台任务完成后生成
