#!/usr/bin/env python3
"""
分层解析 paper-reading 配置(全局兜底 + vault 覆盖 + 环境变量)。纯标准库。

优先级(字段级合并,高者覆盖低者;未给字段由低层兜底):
  1. 环境变量(最高):
       PAPER_READING_OUTPUT_ROOT / PAPER_READING_PYTHON /
       PAPER_READING_PAPER_PY / PAPER_READING_NOTEBOOKLM_CLI
  2. 显式配置文件:$PAPER_READING_CONFIG 指向的 json(文件层最高优先级,按字段覆盖低层;
       未提供的字段继续从 cwd/global 继承,不取代低层)
  3. 当前工作目录:./paper_setting.json   ← vault 覆盖(从 vault 目录运行时)
  4. 全局配置:~/.config/paper-reading/paper_setting.json   ← 全局兜底
  5. 内置兜底:output_root→当前目录(显式告警,不静默);python→"python3";
       paper_py→无(视觉方法B blocked);notebooklm_cli→"notebooklm"(PATH 查找);
       pdf2md→无(改用自动探测 mineru-open-api CLI;见 Step 1d)

字段:output_root / python / paper_py / notebooklm_cli / pdf2md(均可选)。

用法:
  python3 resolve_config.py [--cwd <dir>] [--json]
输出:合并后的有效配置 + _provenance(每个字段来自哪一层)+ _warnings。
退出码 0;解析本身不失败(缺配置走兜底)。
"""
import os, sys, json

FIELDS = ["output_root", "python", "paper_py", "notebooklm_cli", "pdf2md"]
ENV = {
    "output_root": "PAPER_READING_OUTPUT_ROOT",
    "python": "PAPER_READING_PYTHON",
    "paper_py": "PAPER_READING_PAPER_PY",
    "notebooklm_cli": "PAPER_READING_NOTEBOOKLM_CLI",
    "pdf2md": "PAPER_READING_PDF2MD",
}


def load_json(path, warns):
    """读取配置 json。损坏/非对象/权限错误均记入 warns(不静默吞),返回 {}。"""
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        if not isinstance(d, dict):
            warns.append(f"配置文件顶层不是对象,已忽略: {path}")
            return {}
        return d
    except FileNotFoundError:
        return {}
    except Exception as e:
        warns.append(f"配置文件解析失败,已忽略: {path}({type(e).__name__}: {e})")
        return {}


def main():
    args = sys.argv[1:]
    cwd = os.getcwd()
    as_json = "--json" in args
    if "--cwd" in args:
        i = args.index("--cwd")
        if i + 1 < len(args):
            cwd = args[i + 1]

    global_path = os.path.expanduser("~/.config/paper-reading/paper_setting.json")
    cwd_path = os.path.join(cwd, "paper_setting.json")
    explicit = os.environ.get("PAPER_READING_CONFIG")

    cfg, prov, warns = {}, {}, []

    # 文件层:字段级合并,低→高 = global < cwd < explicit(PAPER_READING_CONFIG)
    # 高层只覆盖它实际提供的字段,未提供的字段继续由低层兜底(真正的五层字段级合并)
    layers = [
        (f"global({global_path})", load_json(global_path, warns)),
        (f"cwd({cwd_path})", load_json(cwd_path, warns)),
    ]
    if explicit:
        if os.path.isfile(explicit):
            layers.append((f"explicit:PAPER_READING_CONFIG({explicit})", load_json(explicit, warns)))
        else:
            warns.append(f"PAPER_READING_CONFIG 指向的文件不存在: {explicit}")
    for label, d in layers:
        for k, v in d.items():
            if k in FIELDS and v:
                cfg[k] = v; prov[k] = label

    # 环境变量层(最高)
    for k, envname in ENV.items():
        v = os.environ.get(envname)
        if v:
            cfg[k] = v; prov[k] = f"env:{envname}"

    # 内置兜底
    if not cfg.get("output_root"):
        cfg["output_root"] = cwd
        prov["output_root"] = "fallback(当前工作目录)"
        warns.append(f"output_root 未配置,已回退到当前目录: {cwd}(不静默,请在 plan.md 与汇报中写明)")
    if not cfg.get("python"):
        cfg["python"] = "python3"; prov["python"] = "fallback"
    if not cfg.get("notebooklm_cli"):
        cfg["notebooklm_cli"] = "notebooklm"; prov["notebooklm_cli"] = "fallback(PATH)"
    if not cfg.get("paper_py"):
        cfg["paper_py"] = None; prov["paper_py"] = "fallback(无,视觉方法B blocked)"
    if not cfg.get("pdf2md"):
        cfg["pdf2md"] = None; prov["pdf2md"] = "fallback(无,改用自动探测 mineru-open-api CLI)"

    out = dict(cfg)
    out["_provenance"] = prov
    out["_warnings"] = warns
    out["_searched"] = {
        "explicit(PAPER_READING_CONFIG)": explicit or "(未设置)",
        "cwd": cwd_path,
        "global": global_path,
    }

    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("=== 有效配置 ===")
        for k in FIELDS:
            print(f"  {k} = {cfg.get(k)}   [{prov.get(k)}]")
        if warns:
            print("\n=== 告警 ===")
            for w in warns:
                print("  - " + w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
