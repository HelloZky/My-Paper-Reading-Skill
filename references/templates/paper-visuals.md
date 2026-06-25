# Paper Visuals Skill — NotebookLM 视觉材料生成

生成中文 **Slide deck** 与 **Infographic**。这是可选步骤，不能阻塞 Markdown 笔记完成。

## 执行顺序

1. 先完成全部 7 个 Markdown 文件
2. 再用 `notebooklm` CLI 启动视觉材料生成(slide-deck + infographic,二者都做)
3. 任务启动成功后即可向用户汇报 `markdown_done`
4. 后续只有在 slide-deck 与 infographic **都真正落盘**后，才能置 `visuals_done`

## 用 notebooklm CLI 生成

直接调用 `notebooklm` CLI 完成全部流程。

前置条件：`notebooklm status` 或 `notebooklm list` 能正常返回（已认证）。

#### 步骤

```text
1. 设置语言（仅首次）
   notebooklm language set zh_Hans

2. 查找或创建 notebook
   notebooklm list --json
   → 按标题查找已有 notebook，找到则复用其 notebook_id，跳到步骤 4
   → 未找到则创建新的：
   notebooklm create "<Display Title>" --json
   → 记录 notebook_id

3. 上传 PDF 并等待索引(统一用 -n,不用全局 use)
   notebooklm source add "<absolute/path/to/paper.pdf>" -n <notebook_id> --json   # source_id 在 .source.id
   notebooklm source wait <source_id> -n <notebook_id> --timeout 300
   # ⚠️ source wait 在部分版本不存在/会报错;失败就固定等待约 60–90s 再继续

4. 生成 slide-deck 并等待完成(--wait 阻塞到生成结束,无需单独的 artifact wait)
   notebooklm generate slide-deck -n <notebook_id> --wait --timeout 900

5. 生成 infographic 并等待完成
   notebooklm generate infographic --orientation portrait -n <notebook_id> --wait --timeout 900

6. 下载产物（同样内联 -n）
   notebooklm download slide-deck "<outdir>/<File Stem>_slides_zh.pdf" --format pdf -n <notebook_id>
   notebooklm download infographic "<outdir>/<File Stem>_infographic_zh.png" -n <notebook_id>
```

> 实测说明(2026-06,真跑一篇 TIFS 论文确认):`generate slide-deck/infographic -n <id> --wait` 可直接阻塞到完成,随后 `download` 即得 13MB 级 PDF 与数 MB 级 PNG;`--format detailed`、`--detail`、`--style`、`artifact wait` 等参数非必需,能跑通的最小组合就是 `generate --wait` + `download`。

#### 并行处理多篇论文

为每篇论文创建独立 notebook;所有 `generate`/`download`/`source` 命令一律内联 `-n <notebook_id>`,**禁止全局 `notebooklm use`**,以免并发串线。不同论文的 `generate --wait` 可在各自后台进程中并行等待。

#### 超时与重试

- `generate slide-deck/infographic --wait` 建议 timeout 900s(生成耗时 5–15 分钟)
- 若 `source wait` 子命令不存在或报错,改为固定等待约 60–90s 再继续
- 若生成失败(rate limit),等 5–10 分钟后重试一次
- 下载后必须校验文件真实存在且非空(PDF 以 `%PDF` 开头、PNG 以 PNG magic 开头)再置 `visuals_done`

## 配置来源

路径(`python` / `notebooklm_cli` / `output_root`)都用 process.md Step 2 的分层解析(`scripts/resolve_config.py`)取得;本文件只**消费**解析结果,不自行读配置文件。

降级规则:

- `notebooklm_cli` 缺失 → 由 resolve_config 回退 `notebooklm`(PATH 查找)
- `notebooklm` CLI **不可用或认证失效** → 视觉任务标 `blocked`,在 `plan.md` 失败日志写明原因;**不阻塞** Markdown 笔记产出

## 产物命名

| 产物 | 文件名 |
|------|--------|
| Slide deck | `<File Stem>_slides_zh.pdf` |
| Infographic | `<File Stem>_infographic_zh.png` |

## 运行时要求

- 生成任务耗时较长（slide-deck 5–15 分钟，infographic 5–15 分钟），可后台等待
- 启动成功后，把 `visuals_started` 勾上
- 若启动失败，把失败原因写入 `plan.md`

## 完成后的校验

产物下载后，做以下检查：

1. `<File Stem>_slides_zh.pdf` 存在
2. `<File Stem>_infographic_zh.png` 存在
3. 校验通过后勾选 `visuals_done`

## 严格禁止

- 在文件尚未生成时声称视觉材料已经完成
- 因为视觉任务失败而回滚已经完成的 Markdown 结果
- 依赖硬编码的某一台机器上的绝对路径
