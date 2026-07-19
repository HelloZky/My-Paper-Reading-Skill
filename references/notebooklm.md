# 可选分支:NotebookLM 扩展报告(简报 / 博文)

> 何时读本文件:**仅当 `notebooklm` CLI 可用且要生成 NotebookLM 简报/博文时**(process.md Step 7 的展开层)。CLI 不可用则跳过,在 `plan.md` 失败日志记原因,不阻塞主笔记/Marp/视觉。
> 视觉材料(slides/infographic)的命令见 `references/templates/paper-visuals.md`;二者共用下面的 notebook 建立步骤。

默认为每篇论文额外生成两份 Markdown:`[File Stem]-NotebookLM简报.md`、`[File Stem]-NotebookLM博文.md`。

## 前置:建立(或复用)notebook 并加 PDF 源

报告需要一个已加入该论文 PDF 的 notebook。优先**复用视觉任务创建的同一个 `<notebook_id>`**;若尚未创建:

```bash
notebooklm create "<Display Title>" --json          # 返回 JSON,notebook_id 在 .notebook.id
notebooklm source add "<pdf绝对路径>" -n <notebook_id> --json   # 返回 JSON,source_id 在 .source.id
notebooklm source wait <source_id> -n <notebook_id> --timeout 300   # 等索引;若该子命令不存在则跳过
```

> 实测提示:`source wait` 在部分版本可能不存在/报错;**容错处理**——失败就改为固定等待约 60–90s 让索引完成,再继续;`generate ... --wait` 本身也会等到生成结束。`create`/`source add` 的 ID 字段是**嵌套**的(`notebook.id` / `source.id`),不要当成顶层 `id`。`auth check` 可先确认已登录。始终用内联 `-n <notebook_id>`,**不要**用全局 `notebooklm use`,以免批处理/并发串线。

> ⚠️ **本地 PDF 卡在 `SourceStatus.PREPARING`(实测高频坑)**:本地 PDF 偶尔会在索引阶段长时间(数分钟以上)停在 `PREPARING` 不前进,导致后续 `generate` 一直空转。**排障顺序**:① 先 `source list -n <notebook_id> --json` 看该 source 的 status;② 若超过约 3 分钟仍是 `PREPARING`,**删掉它改用 URL 源**——对 arXiv 论文用 PDF 直链最稳:`notebooklm source add "https://arxiv.org/pdf/<arxiv_id>" --type url -n <notebook_id> --json`(URL 源通常秒级 `READY`);③ 无 arXiv/开放 URL 时,删掉重新 `source add` 本地 PDF 再等一轮。把"本地 PDF 卡 PREPARING → 改用 URL 源"记入 `plan.md` 失败日志。
>
> ⚠️ **语言码必须是 `zh_Hans`**(下划线,Hans 大写),**不是** `zh-CN`/`zh`;传错会报错或产出英文。可先 `notebooklm language set zh_Hans` 设一次默认。

## 真实命令契约(命令是 `generate report`,不是 `report`)

> ⚠️ **关键坑(实测确认)**:`generate report --json` **只返回 `{task_id, status, url}`,不含报告正文**。直接把它的输出写进 `.md` 会得到一段无用的状态 JSON。**正文必须用 `download report` 单独取**(它把报告下成 markdown)。

```bash
# 1) 先生成两份报告(--wait 阻塞到完成;此步不产出正文)
notebooklm generate report --format briefing-doc -n <notebook_id> --language zh_Hans --wait --timeout 600
notebooklm generate report --format blog-post    -n <notebook_id> --language zh_Hans --wait --timeout 600

# 2) 再把报告下成 markdown 正文(--all 一次下全部到目录;返回 JSON 含每份的 title/filename/path)
notebooklm download report --all <临时目录>/ -n <notebook_id> --force --json
```

`download report` 其它形式:`download report <path>.md`(下最新一份)、`--name "<标题模糊匹配>"`、`-a <artifact_id>`、`--latest/--earliest`、`--dry-run` 预览。

## 生成要求

1. `NotebookLM简报` 对应 `--format briefing-doc`;`NotebookLM博文` 对应 `--format blog-post`(format 候选:`briefing-doc | study-guide | blog-post | custom`;可用 `--append "<额外中文指令>"` 微调)
2. **两步法取正文**:先 `generate report --wait` 生成,再 `download report --all <临时目录> --json` 下成 markdown;从返回 JSON 的 `artifacts[].title/filename` 把两份分别映射到 简报/博文(briefing-doc 的标题通常含"简报",blog-post 通常是叙述体/含"引言");**不要**直接用 `generate report` 的 stdout 当正文
3. 把下载得到的 markdown 正文写入 `[File Stem]-NotebookLM简报.md` / `[File Stem]-NotebookLM博文.md`,并补齐合法 frontmatter、`parentNote` 指向主笔记;两份均简体中文
4. 成功启动 `generate` 后置 `notebooklm_reports_started`
5. 两个 `.md` 实际存在、正文非空(不是状态 JSON)且通过基本检查后,置 `notebooklm_reports_done`

若 `notebooklm` CLI 不可用:在 `plan.md` 失败日志写明阻塞原因;不要阻塞主笔记、Marp 或视觉材料流程。
