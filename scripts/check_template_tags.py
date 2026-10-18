#!/usr/bin/env python3
"""Z-BlogPHP 模板成对标签配平检查工具。

模板编译器用非贪婪正则配对流程标签，漏写 {/if}、{/foreach} 等闭合标签
不会报错，而是静默吞掉后续内容，导致页面某块内容消失或条件错乱。
交付前运行本脚本扫描模板文件，可以提前发现配平问题。

用法：
    python check_template_tags.py <目录或文件> [更多目录或文件...]

目录会递归扫描全部 .php 文件（跳过 compile/ 编译产物目录）。
发现问题时列出文件、行号和原因，退出码为 1；全部配平退出码为 0。
"""

import re
import sys
from pathlib import Path

# 成对流程标签：{if}、{foreach}、{for}、{while}、{php}
OPEN_RE = re.compile(r"\{(if|foreach|for|while|php)(?=[\s(}])")
CLOSE_RE = re.compile(r"\{/(if|foreach|for|while|php)\}")
# literal 块内的花括号是原样输出的内容，不参与配平
LITERAL_RE = re.compile(r"\{literal\}.*?\{/literal\}", re.S)


def check_file(path):
    """检查单个文件，返回问题列表（字符串）。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    # literal 块替换为等长空格，保持行号不变
    text = LITERAL_RE.sub(lambda m: " " * len(m.group(0)), text)

    tokens = []
    for m in OPEN_RE.finditer(text):
        tokens.append((m.start(), m.group(1), True))
    for m in CLOSE_RE.finditer(text):
        tokens.append((m.start(), m.group(1), False))
    tokens.sort()

    problems = []
    stack = []
    for pos, name, is_open in tokens:
        line = text.count("\n", 0, pos) + 1
        if is_open:
            stack.append((name, line))
        elif not stack:
            problems.append(f"  第 {line} 行：多余的 {{/{name}}}，前面没有对应的 {{{name}}}")
        elif stack[-1][0] == name:
            stack.pop()
        else:
            problems.append(
                f"  第 {line} 行：{{/{name}}} 与第 {stack[-1][1]} 行的 {{{stack[-1][0]}}} 交叉"
                "（可能漏写了中间层的闭合标签）"
            )
            stack.pop()
    for name, line in stack:
        problems.append(f"  第 {line} 行：{{{name}}} 缺少闭合标签 {{/{name}}}")
    return problems


def main():
    if len(sys.argv) < 2:
        print("用法：python check_template_tags.py <目录或文件> [更多目录或文件...]", file=sys.stderr)
        sys.exit(2)

    files = []
    for target in sys.argv[1:]:
        path = Path(target)
        if path.is_dir():
            found = sorted(path.rglob("*.php"))
            files.extend(f for f in found if "compile" not in f.parts)
        elif path.is_file():
            files.append(path)
        else:
            print(f"路径不存在：{target}", file=sys.stderr)
            sys.exit(2)

    if not files:
        print("未找到 .php 模板文件。")
        return

    total = 0
    for f in files:
        problems = check_file(f)
        if problems:
            total += len(problems)
            print(f"{f}:")
            print("\n".join(problems))

    if total:
        print(f"共发现 {total} 处配平问题，漏写闭合标签会导致内容静默错乱，请先修复。")
        sys.exit(1)
    print(f"全部 {len(files)} 个模板文件配平正常。")


if __name__ == "__main__":
    main()
