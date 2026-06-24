# 输入分支:Zotero JSON metadata 解析

> 何时读本文件:**仅当用户直接粘贴 Zotero 导出的条目 JSON(含 `attachments` 字段)时**。给 PDF/目录路径时无需本文件。这是 process.md Step 1c 的展开层。

当用户直接粘贴 Zotero 导出的条目 JSON 时:

**元数据直接提取**(无需从 PDF 解析):

| Zotero 字段 | 映射到 |
|-------------|--------|
| `title` | Display Title |
| `authors` | author 列表 |
| `year` / `date` | publication-year |
| `proceedingsTitle` / `publicationTitle` / `journalAbbreviation` | venue / venue-abbrev |
| `type` | paperType(`conferencePaper` → `conferencePaper`,`journalArticle` → `journalArticle`,等) |
| `DOI` | DOI |
| `url` | paperURL |
| `shortTitle` | shortTitle |
| `key` | zotero-key |
| `abstractNote` | 用于 paper-type 判断和 Intro 撰写 |
| `tags` | 可辅助判断 Primary Research Area |

**Zotero URL 生成**:`zotero-url` 设为 `"zotero://select/library/items/<key>"`

**附件映射到 Source Bundle**:

按 `attachments` 数组中的 `contentType` 和 `filePath` 识别源文件:

| contentType | 识别为 | 处理方式 |
|-------------|--------|---------|
| `application/pdf` | PDF 源 | 作为 PDF 兜底源和视觉材料输入 |
| `text/html` | HTML 源 | 用于交叉核对标题、章节、图表标题等 |
| `application/x-gzip`、`application/x-tar`,或 filePath 以 `.tar.gz` / `.tar` 结尾 | TeX 源码压缩包 | 解压到临时目录,按标准 TeX 优先级读取 |

**解压 TeX 源码包(安全解压,harness 缰绳)**:

若附件中存在 tar/tar.gz 文件,**不要**用 `tar -xf` 直接解压到可预测路径(`tar -tf` 只列文件名,看不出符号/硬链接,无法挡路径穿越)。**优先用本 skill 自带的纯标准库脚本**,它用 `tarfile.getmembers()` 逐个审查、拒绝绝对路径/`..`穿越/符号链接/硬链接/特殊文件,通过后才解压到随机目录:

```bash
# 注意 1:不要写成 DEST=$(python ... | sed ...) —— 管道末端取到的是 sed 的退出码,会吞掉拒绝码。
# 注意 2:不要写成 OUT=$(...); rc=$? —— 在 set -e 下子进程非零退出会直接终止 shell,rc=$? 永不执行。
# 用 if 直接判命令成功与否,兼容 set -e:
OUT=
rc=126
if OUT="$(python3 <skill根>/scripts/safe_extract.py "<filePath>")"; then
  rc=0
else
  rc=$?
fi
if [ "$rc" -eq 0 ]; then
  DEST="$(printf '%s\n' "$OUT" | sed -n 's/^DEST=//p')"   # 仅在成功后提取解压目录
else
  : # 退出码非 0 → 已拒绝(不安全/损坏),记失败日志,改用 PDF 兜底
fi
```

- 脚本退出码 `1`(发现链接/越界成员或解压失败)→ **拒绝该压缩包**,在 `plan.md` 失败日志记一条(缺失类型: 源文件/安全),改用 PDF 兜底。
- 用完清理 `$DEST`;在 shell 中可加 `trap 'rm -rf "$DEST"' EXIT` 保证异常退出也清理。
- 若本机没有 `python3`:退回到"先 `tar -tzf` 人工审查成员名、拒绝以 `/` 开头或含 `../` 的成员,确认后再 `tar -xzf` 到 `mktemp -d` 目录",并在失败日志注明未能做链接类型检查。

解压并通过安全审查后,按 process.md 1b 的标准优先级检查 `main.tex`、`*.tex` 等。

**附件中可能存在多个同类型文件**(如多个 HTML snapshot):优先选择文件名或 title 中包含论文标题关键词的那个;若无法区分,按数组顺序取第一个。

**完成附件映射后**,合并进入标准的源文件优先级和交叉核对流程(与 process.md 1b 相同),继续 Step 1 的"抽取并记录信息 / 选研究方向 / 读取细则"。

> 常见情况:Zotero 条目**只有 Full Text PDF**(无 tex/html)。此时**先看 process.md 的 1d 节**——优先探测 MinerU / marker / markitdown / pymupdf4llm 把 PDF 转成 `full.md`(+ `images/`)再读,质量明显更好;没有任何工具才降级到内置 PDF 读取。
