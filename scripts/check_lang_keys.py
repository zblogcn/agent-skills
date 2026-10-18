#!/usr/bin/env python3
"""Z-BlogPHP 语言包三包一致性检查工具。

功能：
1. 对比应用 language/ 下 en.php、zh-cn.php、zh-tw.php 的键名集合，
   报告缺失和多余的键。
2. 扫描模板和 PHP 文件中的语言键引用（{$lang['ID']['key']}、
   $zbp->lang['ID']['key']、{$msg.key}），报告语言包中未定义的键。

用法：
    python check_lang_keys.py <应用目录>

发现问题时退出码为 1；全部一致退出码为 0。
"""

import re
import sys
from pathlib import Path

LANG_FILES = ("en.php", "zh-cn.php", "zh-tw.php")
# 语言包中的键定义：'key' => '文案'
KEY_DEF_RE = re.compile(r"""['"]([\w\-]+)['"]\s*=>""")
# 引用形式：{$lang['ID']['key']} / $lang['ID']['key'] / $zbp->lang['ID']['key']
LANG_REF_RE = re.compile(r"""\$lang\[[^\]]+\]\[['"]([\w\-]+)['"]\]""")
# 引用形式：{$msg.key}（主题经 include.php 注入的 $msg 变量）
MSG_REF_RE = re.compile(r"""\$msg\.([\w\-]+)""")
SCAN_GLOBS = ("template/**/*.php", "*.php")


def extract_keys(path):
    """提取语言包文件中定义的键名集合，解析失败返回 None。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"错误：无法读取 {path}：{e}", file=sys.stderr)
        sys.exit(2)
    if not text.lstrip().startswith("<?php"):
        # 容忍 UTF-8 BOM
        if not text.encode("utf-8").startswith(b"\xef\xbb\xbf<?php"):
            return None
    return set(KEY_DEF_RE.findall(text))


def scan_refs(app_dir):
    """扫描模板和 PHP 文件中的语言键引用，返回 {键名: [文件:行号, ...]}。"""
    refs = {}
    seen = set()
    for pattern in SCAN_GLOBS:
        for f in sorted(app_dir.glob(pattern)):
            if f.parent.name == "compile" or f in seen:
                continue
            seen.add(f)
            text = f.read_text(encoding="utf-8", errors="replace")
            keys = set(LANG_REF_RE.findall(text)) | set(MSG_REF_RE.findall(text))
            for key in keys:
                rel = f.relative_to(app_dir)
                line_nums = [
                    i + 1
                    for i, line in enumerate(text.splitlines())
                    if re.search(rf"\$lang\[[^\]]+\]\[['\"]{key}['\"]\]|\$msg\.{key}\b", line)
                ]
                refs.setdefault(key, []).extend(f"{rel}:{n}" for n in line_nums)
    return refs


def main():
    if len(sys.argv) != 2:
        print("用法：python check_lang_keys.py <应用目录>", file=sys.stderr)
        sys.exit(2)
    app_dir = Path(sys.argv[1])
    if not app_dir.is_dir():
        print(f"目录不存在：{app_dir}", file=sys.stderr)
        sys.exit(2)

    lang_dir = app_dir / "language"
    keysets = {}
    for name in LANG_FILES:
        path = lang_dir / name
        if not path.is_file():
            print(f"错误：缺少 {path}", file=sys.stderr)
            sys.exit(2)
        keysets[name] = extract_keys(path)

    problems = 0
    base_name = "zh-cn.php"
    base = keysets[base_name]
    for name in LANG_FILES:
        diff = base ^ keysets[name]
        if diff:
            problems += len(diff)
            print(f"{name} 与 {base_name} 键不一致：")
            for key in sorted(diff):
                mark = "缺少" if key in base else "多余"
                print(f"  {mark} {key}")

    refs = scan_refs(app_dir)
    undefined = {k: v for k, v in refs.items() if k not in base}
    if undefined:
        problems += len(undefined)
        print("以下语言键被引用但未在任何语言包中定义：")
        for key, locations in sorted(undefined.items()):
            print(f"  {key}  <-  {'、'.join(locations)}")

    if problems:
        print(f"共发现 {problems} 处语言键问题。")
        sys.exit(1)
    print(f"三份语言包键一致（{len(base)} 键），引用检查通过。")


if __name__ == "__main__":
    main()
