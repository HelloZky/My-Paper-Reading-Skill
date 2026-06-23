#!/usr/bin/env python3
"""
安全解压 TeX 源码 tar/tar.gz(harness 缰绳)。纯标准库。

用法:
    python3 safe_extract.py <archive.tar|.tar.gz> [dest_dir]

行为:
    - 解压前逐个成员审查:拒绝绝对路径、`..` 路径穿越、符号链接、硬链接、设备/FIFO 等特殊文件。
    - 只解普通文件与目录,且全部落在 dest 内。
    - 任一成员越界/为链接 → 整体拒绝,退出码 1,不解压。
    - dest 未给时用 mktemp -d 生成随机目录,并打印其路径。

退出码:
    0  解压成功,最后一行打印 DEST=<目录>
    1  发现不安全成员或解压失败(已拒绝)
    2  用法错误
"""
import sys, os, tarfile, tempfile


def is_within(base, target):
    base = os.path.realpath(base)
    full = os.path.realpath(os.path.join(base, target))
    return full == base or full.startswith(base + os.sep)


def main():
    if len(sys.argv) not in (2, 3):
        print("用法: python3 safe_extract.py <archive.tar|.tar.gz> [dest_dir]")
        return 2
    arc = sys.argv[1]
    if not os.path.isfile(arc):
        print(f"错误: 压缩包不存在: {arc}")
        return 2
    try:
        dest = sys.argv[2] if len(sys.argv) == 3 else tempfile.mkdtemp(prefix="paper_tex.")
        os.makedirs(dest, exist_ok=True)
    except OSError as e:
        print(f"拒绝: 无法创建解压目录: {e}")
        return 1

    try:
        with tarfile.open(arc) as tf:
            members = tf.getmembers()
            for m in members:
                # 1) 拒绝链接 / 特殊文件
                if m.issym() or m.islnk():
                    print(f"拒绝: 含链接成员: {m.name}({'symlink' if m.issym() else 'hardlink'})")
                    return 1
                if not (m.isfile() or m.isdir()):
                    print(f"拒绝: 含非普通文件/目录成员: {m.name}(type={m.type!r})")
                    return 1
                # 2) 拒绝绝对路径 / 路径穿越
                if m.name.startswith("/") or os.path.isabs(m.name):
                    print(f"拒绝: 含绝对路径成员: {m.name}")
                    return 1
                if not is_within(dest, m.name):
                    print(f"拒绝: 成员越界(路径穿越): {m.name}")
                    return 1
            # 审查通过,逐个解压(再次防御;Python 3.12+ 用 data 过滤器,3.14 默认行为兼容)
            for m in members:
                try:
                    tf.extract(m, dest, filter="data")
                except TypeError:
                    tf.extract(m, dest)
    except tarfile.TarError as e:
        print(f"拒绝: 解压失败: {e}")
        return 1

    print(f"DEST={dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
