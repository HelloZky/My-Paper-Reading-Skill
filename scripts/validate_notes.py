#!/usr/bin/env python3
"""
确定性 Markdown QA 门禁(Step 6)。优先用 PyYAML 做严格 frontmatter 校验,
无 PyYAML 时降级为保守的行级检查。无其他第三方依赖。

用法:
    python3 validate_notes.py <paper_output_dir> "<File Stem>"

退出码:
    0  全部检查通过 → 允许把 markdown_done 置为 done
    1  存在硬性失败 → QA 不通过,禁止声称完成
    2  用法/环境错误

只读;不修改任何文件。若本机没有 python3,流程应回退到 process.md Step 6 的人工逐项检查。
"""
import sys, os, re

try:
    import yaml  # PyYAML
    HAVE_YAML = True
except Exception:
    HAVE_YAML = False

SUITE_SUFFIXES = ["", "-简报", "-方法介绍", "-实验结果", "-审阅建议", "-后续灵感"]
# 允许暂不存在的"未来产物"(Step 7/8/9 才生成)
OPTIONAL_TARGETS = re.compile(r"(_slides_zh|_infographic_zh|NotebookLM简报|NotebookLM博文)")
VISUAL_PRODUCTS = re.compile(r"(_slides_zh|_infographic_zh)")
NB_PRODUCTS = re.compile(r"(NotebookLM简报|NotebookLM博文)")
PLACEHOLDER_SQUARE = re.compile(r"\[(?:Placeholder|placeholder|TODO|待填|占位)\]")

# 角度括号判定:区分"模板占位符"(要拦) vs "合法 HTML(marp)/NLP 特殊 token"(放行)
_ANGLE = re.compile(r"<([^<>\n]{1,60})>")
_HTML_TAGS = {
    "div", "span", "br", "hr", "p", "img", "a", "b", "i", "u", "em", "strong",
    "ul", "ol", "li", "table", "tr", "td", "th", "code", "pre", "sub", "sup",
    "small", "center", "figure", "section", "h1", "h2", "h3", "h4", "blockquote",
}
_KNOWN_PLACEHOLDER_WORDS = {"year", "venue", "date", "placeholder", "todo", "占位"}


def is_placeholder(inner):
    """inner 为 <...> 内文。返回 True 表示这是未替换的模板占位符(应拦)。
    放行:HTML 标签/注释(<div..>, </span>, <!-- -->、带 = 的属性标签)、NLP 特殊 token(<eos>,<MASK>)。"""
    inner = inner.strip()
    if not inner or inner[0] in "/!":          # 闭合标签 / 注释
        return False
    if "=" in inner:                            # 带属性的 HTML 标签
        return False
    if "://" in inner or "@" in inner:          # URL / email 的 autolink,非占位符
        return False
    first = re.split(r"[ /]", inner, maxsplit=1)[0].lower()
    if first in _HTML_TAGS:                     # 裸 HTML 标签 <div> <span>
        return False
    low = inner.lower()
    if low in _KNOWN_PLACEHOLDER_WORDS:         # <Year> <Venue> 等单词占位符
        return True
    # 占位符形态:含空格/竖线、含中文、连字符接大写(Primary-Research)、camelCase(FirstAuthor)
    if (" " in inner or "|" in inner
            or re.search(r"[一-鿿]", inner)
            or re.search(r"-[A-Z]", inner)
            or re.search(r"[a-z][A-Z]", inner)):
        return True
    return False


def find_placeholders(text):
    out = []
    for m in _ANGLE.finditer(text):
        prev = text[m.start() - 1] if m.start() > 0 else ""
        if prev.isalnum() or prev == "_":      # 形如 List<MyType> 的泛型,非占位符
            continue
        if is_placeholder(m.group(1)):
            out.append(m.group(0))
    return out


def fail(errs, msg):
    errs.append(msg)


def split_frontmatter(text):
    """行级精确切分:首行必须是 '---',闭合行必须精确为 '---'(不接受 '---oops')。
    返回 (frontmatter_str | None, ok: bool)。"""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, False
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), True
    return None, False  # 未闭合


def check_frontmatter(text, fname, errs):
    fm, ok = split_frontmatter(text)
    if not ok:
        fail(errs, f"{fname}: 缺少合法 frontmatter(首行需为 '---' 且有精确的 '---' 闭合行)")
        return
    if HAVE_YAML:
        try:
            data = yaml.safe_load(fm)
        except yaml.YAMLError as e:
            first = str(e).splitlines()[0] if str(e) else "解析失败"
            fail(errs, f"{fname}: frontmatter 不是合法 YAML（{first}）")
            return
        if not isinstance(data, dict):
            fail(errs, f"{fname}: frontmatter 顶层应为键值映射")
    else:
        if re.search(r"^\.\.\.\s*$", fm, re.M):
            fail(errs, f"{fname}: frontmatter 含非法 '...' 文档结束符")
    ph = find_placeholders(fm)
    if ph:
        fail(errs, f"{fname}: frontmatter 残留模板占位符: {', '.join(sorted(set(ph))[:5])}")
    if PLACEHOLDER_SQUARE.search(fm):
        fail(errs, f"{fname}: frontmatter 残留占位符 [Placeholder]/[TODO] 等")


def strip_link_decoration(s):
    """去掉 wikilink/嵌入里的 |别名或尺寸 和 #fragment,返回纯目标。"""
    s = s.strip()
    s = s.split("|", 1)[0]
    s = s.split("#", 1)[0]
    return s.strip()


def main():
    if len(sys.argv) != 3:
        print("用法: python3 validate_notes.py <paper_output_dir> \"<File Stem>\"")
        return 2
    d, stem = sys.argv[1], sys.argv[2]
    if not os.path.isdir(d):
        print(f"错误: 目录不存在: {d}")
        return 2

    errs, warns = [], []

    # 读 plan.md 的「任务状态表」判断视觉 / NotebookLM 报告是否 blocked/skipped。
    # 只解析状态表的 markdown 行(精确任务名 + 状态格),不再用整行关键词粗判,
    # 避免失败日志等自由文本里的"视觉/NotebookLM"字样造成误判。
    visuals_blocked = False
    reports_blocked = False
    plan = os.path.join(d, "plan.md")
    if os.path.isfile(plan):
        for ln in open(plan, encoding="utf-8").read().splitlines():
            if "|" not in ln:
                continue
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            task, status = cells[0].lower(), cells[1].lower()
            if status not in ("blocked", "skipped"):
                continue
            if task.startswith("visuals"):                 # visuals_started / visuals_done
                visuals_blocked = True
            if "notebooklm_reports" in task:               # notebooklm_reports_started / _done
                reports_blocked = True

    # 1) 必需套件文件存在(6 笔记 + marp)
    suite_files = [os.path.join(d, f"{stem}{suf}.md") for suf in SUITE_SUFFIXES]
    marp = os.path.join(d, f"{stem}-marp.md")
    for f in suite_files + [marp]:
        if not os.path.isfile(f):
            fail(errs, f"缺少必需文件: {os.path.basename(f)}")

    existing = [f for f in suite_files + [marp] if os.path.isfile(f)]

    # 2) 逐文件检查:frontmatter / 占位符 / [[[ / 嵌入图存在性 / blocked 视觉死链
    for f in existing:
        name = os.path.basename(f)
        text = open(f, encoding="utf-8").read()
        check_frontmatter(text, name, errs)
        body_ph = find_placeholders(text)
        if PLACEHOLDER_SQUARE.search(text) or body_ph:
            extra = (": " + ", ".join(sorted(set(body_ph))[:5])) if body_ph else ""
            fail(errs, f"{name}: 正文残留占位符{extra}")
        if "[[[" in text:
            fail(errs, f"{name}: 存在错误的三重方括号 '[[['")
        # 嵌入图 ![[...]] :去掉 |尺寸/#frag 后检查本目录 images/ 是否存在
        for emb in re.findall(r"!\[\[([^\]]+)\]\]", text):
            tgt = strip_link_decoration(emb)
            if OPTIONAL_TARGETS.search(tgt):
                if visuals_blocked and VISUAL_PRODUCTS.search(tgt):
                    fail(errs, f"{name}: 视觉任务已 blocked,仍嵌入未生成的产物: {tgt}")
                if reports_blocked and NB_PRODUCTS.search(tgt):
                    fail(errs, f"{name}: NotebookLM 报告已 blocked,仍嵌入未生成的产物: {tgt}")
                continue
            if (tgt.startswith("images/") or tgt.startswith("assets/")) and not os.path.isfile(os.path.join(d, tgt)):
                fail(errs, f"{name}: 嵌入图片不存在: {tgt}")

        # AI 示意图(assets/)硬约束:① 实验结果页禁止 AI 图;② 每张必须紧跟"AI 生成"图注
        is_experiments = name.endswith("-实验结果.md")
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            m = re.search(r"!\[\[(assets/[^\]]+)\]\]", ln)
            if not m:
                continue
            if is_experiments:
                fail(errs, f"{name}: 实验结果页不得嵌入 AI 示意图(assets/),以免被误读为真实结果图")
            # 找后续最多 3 个非空行,要求出现"AI 生成"标注
            nxt = [x for x in lines[i + 1:i + 6] if x.strip()][:3]
            if not any("AI 生成" in x for x in nxt):
                fail(errs, f"{name}: AI 示意图缺少必带图注(应紧跟含'🤖 AI 生成示意图…'的一行): {m.group(1)}")

    # 3) 主笔记 wikilink(排除嵌入 ![[...]]):必需套件强制存在;视觉 blocked 时死链报错
    main_note = os.path.join(d, f"{stem}.md")
    if os.path.isfile(main_note):
        text = open(main_note, encoding="utf-8").read()
        suite_stems = {f"{stem}{suf}" for suf in SUITE_SUFFIXES} | {f"{stem}-marp"}
        # (?<!!) 排除 ![[...]] 嵌入语法
        for raw in re.findall(r"(?<!!)\[\[([^\]]+)\]\]", text):
            tgt = strip_link_decoration(raw)
            base = tgt.split("/")[-1]
            cand = base[:-3] if base.endswith(".md") else base
            if OPTIONAL_TARGETS.search(base):
                if visuals_blocked and VISUAL_PRODUCTS.search(base):
                    fail(errs, f"主笔记:视觉任务已 blocked,仍保留指向未生成产物的链接 [[{raw}]]")
                if reports_blocked and NB_PRODUCTS.search(base):
                    fail(errs, f"主笔记:NotebookLM 报告已 blocked,仍保留指向未生成产物的链接 [[{raw}]]")
                continue
            if cand in suite_stems:
                if not os.path.isfile(os.path.join(d, f"{cand}.md")):
                    fail(errs, f"主笔记 wikilink 指向缺失的套件文件: [[{raw}]]")
            else:
                if not os.path.isfile(os.path.join(d, f"{cand}.md")):
                    warns.append(f"主笔记 wikilink 指向当前目录外实体(Vault 级,未阻断): [[{raw}]]")

    # 4) marp 头
    if os.path.isfile(marp):
        head = open(marp, encoding="utf-8").read()[:300]
        if not head.startswith("---"):
            fail(errs, f"{os.path.basename(marp)}: 未以 '---' 开头")
        if not re.search(r"^marp:\s*true\s*$", head, re.M):
            fail(errs, f"{os.path.basename(marp)}: 缺少 'marp: true'")

    # 报告
    print("=== Markdown QA (validate_notes.py) ===")
    print(f"目录: {d}")
    print(f"File Stem: {stem}")
    print(f"YAML 严格校验: {'开启 (PyYAML)' if HAVE_YAML else '降级 (无 PyYAML,仅保守检查)'}")
    if visuals_blocked:
        print("注意: 检测到视觉任务 blocked/skipped → 不得保留指向视觉产物的链接/嵌入")
    if reports_blocked:
        print("注意: 检测到 NotebookLM 报告 blocked/skipped → 不得保留指向报告产物的链接/嵌入")
    if warns:
        print(f"\n警告 ({len(warns)}):")
        for w in warns:
            print(f"  - {w}")
    if errs:
        print(f"\n失败 ({len(errs)}):")
        for e in errs:
            print(f"  - {e}")
        print("\n结果: QA 不通过 → 禁止勾选 markdown_done")
        return 1
    print("\n结果: QA 通过 → 可勾选 markdown_done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
