#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Z-BlogPHP 应用骨架生成器

使用同目录下的 AppCentre 素材（include.html、main.html、
plugin.png、theme.png）创建插件或主题的最小可运行骨架。

用法示例：
    python create_app.py -t plugin -i MyPlugin -n "示例插件" -a "张三"
    python create_app.py -t theme  -i mytheme  -n "示例主题" -a "张三" --no-admin

若已在技能根目录的 config.local.md 配置 id / name / author-name / author-url，
可省略 -i / -n / -a / --url，命令行参数优先于配置值：
    python create_app.py -t plugin
"""

import argparse
import os
import re
import shutil
import sys
from datetime import date

# 素材目录：与本脚本同级
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKELETON_DIR = SCRIPT_DIR

# 技能根目录下的本地配置（私有，不随技能分发）
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_FILE = os.path.join(SKILL_ROOT, "config.local.md")

TODAY = date.today().isoformat()

# 适配的系统版本 build 号（参考 plugin-structure.md）
DEFAULT_ADAPTED = "173540"  # 1.7.5


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def read_skeleton(filename):
    """读取 skeleton 目录下的素材文件，失败则退出。"""
    path = os.path.join(SKELETON_DIR, filename)
    if not os.path.isfile(path):
        print(f"错误：找不到素材文件 {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def copy_skeleton_image(src_name, dst_path):
    """复制 skeleton 中的图片素材到目标位置。"""
    src = os.path.join(SKELETON_DIR, src_name)
    if not os.path.isfile(src):
        print(f"错误：找不到图片素材 {src}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copyfile(src, dst_path)


def write_text(path, content):
    """写入文本文件，自动创建父目录。"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def render(template, **kwargs):
    """简单的占位符替换：<%key%> -> value。"""
    out = template
    for k, v in kwargs.items():
        out = out.replace(f"<%{k}%>", str(v))
    return out


def load_config():
    """读取技能根目录下的 config.local.md，返回变量名到值的字典。

    config.local.md 是 markdown 表格，列依次为：配置项 | 变量名 | 值。
    变量名对应：id / name / author-name / author-url。
    文件不存在或解析失败时返回空字典。
    """
    cfg = {}
    if not os.path.isfile(CONFIG_FILE):
        return cfg
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|"):
                    continue
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) < 3:
                    continue
                # 跳过表头和分隔行
                if cells[1] in ("变量名", "") or set(cells[1]) <= {"-", ":"}:
                    continue
                varname, value = cells[1], cells[2]
                if value:
                    cfg[varname] = value
    except OSError:
        pass
    return cfg


# ---------------------------------------------------------------------------
# 语言包
# ---------------------------------------------------------------------------

LANG_GUARD = "<?php\nif (!defined('ZBP_PATH')) {exit('Access denied');}\nreturn array(\n"

LANG_KEYS = {
    "en": {
        "settings": "Settings",
        "save": "Save",
        "saved": "Saved successfully.",
    },
    "zh-cn": {
        "settings": "设置",
        "save": "保存",
        "saved": "保存成功。",
    },
    "zh-tw": {
        "settings": "設定",
        "save": "儲存",
        "saved": "儲存成功。",
    },
}


def write_language_packs(app_dir):
    """在 {app_dir}/language/ 下生成 en.php / zh-cn.php / zh-tw.php。"""
    lang_dir = os.path.join(app_dir, "language")
    for code, items in LANG_KEYS.items():
        lines = [LANG_GUARD]
        for k, v in items.items():
            lines.append(f"    '{k}' => '{v}',\n")
        lines.append(");\n")
        write_text(os.path.join(lang_dir, f"{code}.php"), "".join(lines))


# ---------------------------------------------------------------------------
# include.php 生成
# ---------------------------------------------------------------------------

def build_include_php(app_id, app_type):
    """基于 skeleton/include.html 生成 include.php，补充语言加载。"""
    tpl = read_skeleton("include.html")
    # 在 ActivePlugin 函数体中加入语言包加载
    inject = (
        "function ActivePlugin_<%appid%>() {\n"
        "    global $zbp;\n"
        "    $zbp->LoadLanguage('<%apptype%>', '<%appid%>');\n"
        "\n"
        "}"
    )
    tpl = tpl.replace(
        "function ActivePlugin_<%appid%>() {\n\n}",
        inject,
    )
    return render(tpl, appid=app_id, apptype=app_type)


# ---------------------------------------------------------------------------
# 管理入口 main.php 生成
# ---------------------------------------------------------------------------

def build_main_php(app_id, app_name):
    """基于 skeleton/main.html 生成后台管理/配置入口。"""
    tpl = read_skeleton("main.html")
    return render(tpl, appid=app_id, appname=app_name)


# ---------------------------------------------------------------------------
# plugin.xml 生成
# ---------------------------------------------------------------------------

def build_plugin_xml(args):
    path_value = "main.php" if not args.no_admin else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<plugin version="php">
<id>{args.id}</id>
<name>{args.name}</name>
<url>{args.url}</url>
<note>{args.note}</note>
<description>{args.description}</description>
<path>{path_value}</path>
<include>include.php</include>
<level>1</level>
<author>
  <name>{args.author}</name>
  <email></email>
  <url></url>
</author>
<source>
  <name></name>
  <email></email>
  <url></url>
</source>
<adapted>{args.adapted}</adapted>
<version>{args.version}</version>
<pubdate>{TODAY}</pubdate>
<modified>{TODAY}</modified>
<price>0</price>
<phpver>7.0</phpver>
<advanced>
  <dependency></dependency>
  <rewritefunctions></rewritefunctions>
  <existsfunctions></existsfunctions>
  <conflict></conflict>
</advanced>
<sidebars>
  <sidebar1></sidebar1>
  <sidebar2></sidebar2>
  <sidebar3></sidebar3>
  <sidebar4></sidebar4>
  <sidebar5></sidebar5>
  <sidebar6></sidebar6>
  <sidebar7></sidebar7>
  <sidebar8></sidebar8>
  <sidebar9></sidebar9>
</sidebars>
</plugin>
"""


# ---------------------------------------------------------------------------
# theme.xml 生成
# ---------------------------------------------------------------------------

def build_theme_xml(args):
    path_value = "main.php" if not args.no_admin else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<theme version="php">
<id>{args.id}</id>
<name>{args.name}</name>
<url>{args.url}</url>
<note>{args.note}</note>
<description>{args.description}</description>
<path>{path_value}</path>
<include>include.php</include>
<level>1</level>
<author>
  <name>{args.author}</name>
  <email></email>
  <url></url>
</author>
<source>
  <name></name>
  <email></email>
  <url></url>
</source>
<adapted>{args.adapted}</adapted>
<version>{args.version}</version>
<pubdate>{TODAY}</pubdate>
<modified>{TODAY}</modified>
<price>0</price>
<phpver>7.0</phpver>
<advanced>
  <dependency></dependency>
  <rewritefunctions></rewritefunctions>
  <existsfunctions></existsfunctions>
  <conflict></conflict>
</advanced>
<sidebars>
  <sidebar1></sidebar1>
  <sidebar2></sidebar2>
  <sidebar3></sidebar3>
  <sidebar4></sidebar4>
  <sidebar5></sidebar5>
  <sidebar6></sidebar6>
  <sidebar7></sidebar7>
  <sidebar8></sidebar8>
  <sidebar9></sidebar9>
</sidebars>
</theme>
"""


# ---------------------------------------------------------------------------
# theme template.json 与 style.css
# ---------------------------------------------------------------------------

def build_template_json(app_id):
    return f"""{{
    "id": "{app_id}",
    "templates": [
        {{ "filename": "index",  "type": "list|index",   "name": "首页" }},
        {{ "filename": "single", "type": "single",       "name": "文章/单页" }}
    ]
}}
"""


def build_style_css(app_id):
    return f"""/* {app_id} theme styles */
body {{
    margin: 0;
    padding: 0;
}}
"""


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def create_plugin(args):
    app_dir = os.path.join(args.output, args.id)
    if os.path.exists(app_dir):
        print(f"错误：目标目录已存在 {app_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"正在创建插件 {args.id} -> {app_dir}")

    # plugin.xml
    write_text(os.path.join(app_dir, "plugin.xml"), build_plugin_xml(args))

    # include.php（含语言包加载）
    write_text(os.path.join(app_dir, "include.php"), build_include_php(args.id, "plugin"))

    # logo.png
    copy_skeleton_image("plugin.png", os.path.join(app_dir, "logo.png"))

    # 管理入口
    if not args.no_admin:
        write_text(os.path.join(app_dir, "main.php"), build_main_php(args.id, args.name))

    # 语言包
    write_language_packs(app_dir)

    print(f"插件 {args.id} 创建完成。")


def create_theme(args):
    app_dir = os.path.join(args.output, args.id)
    if os.path.exists(app_dir):
        print(f"错误：目标目录已存在 {app_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"正在创建主题 {args.id} -> {app_dir}")

    # theme.xml
    write_text(os.path.join(app_dir, "theme.xml"), build_theme_xml(args))

    # include.php
    write_text(os.path.join(app_dir, "include.php"), build_include_php(args.id, "theme"))

    # screenshot.png
    copy_skeleton_image("theme.png", os.path.join(app_dir, "screenshot.png"))

    # 配置入口
    if not args.no_admin:
        write_text(os.path.join(app_dir, "main.php"), build_main_php(args.id, args.name))

    # template.json
    write_text(os.path.join(app_dir, "template.json"), build_template_json(args.id))

    # style/style.css
    write_text(os.path.join(app_dir, "style", "style.css"), build_style_css(args.id))

    # 空目录（对齐官方 theme_edit.php：style/compile/template/include/script）
    for d in ("template", "compile", "script", "include"):
        os.makedirs(os.path.join(app_dir, d), exist_ok=True)

    # 语言包
    write_language_packs(app_dir)

    print(f"主题 {args.id} 创建完成。")


def main():
    parser = argparse.ArgumentParser(
        description="Z-BlogPHP 应用骨架生成器",
    )
    parser.add_argument(
        "-t", "--type", required=True, choices=["plugin", "theme"],
        help="应用类型：plugin（插件）或 theme（主题）",
    )
    parser.add_argument(
        "-i", "--id", default=None,
        help="应用 ID（未提供时从 config.local.md 读取）",
    )
    parser.add_argument(
        "-n", "--name", default=None,
        help="应用显示名称（未提供时从 config.local.md 读取）",
    )
    parser.add_argument(
        "-a", "--author", default=None,
        help="作者名称（未提供时从 config.local.md 读取，再默认「作者名称」）",
    )
    parser.add_argument(
        "-v", "--version", default="1.0",
        help="应用版本号（默认：1.0）",
    )
    parser.add_argument(
        "--adapted", default=DEFAULT_ADAPTED,
        help=f"适配的系统 build 号（默认：{DEFAULT_ADAPTED}）",
    )
    parser.add_argument(
        "--url", default=None,
        help="应用主页 URL（未提供时从 config.local.md 读取）",
    )
    parser.add_argument(
        "--note", default="",
        help="一句话简介（可选）",
    )
    parser.add_argument(
        "--description", default="",
        help="详细描述（可选）",
    )
    parser.add_argument(
        "--no-admin", action="store_true",
        help="不创建后台管理/配置入口（main.php）",
    )
    parser.add_argument(
        "-o", "--output", default=os.getcwd(),
        help="输出根目录（默认：当前目录），应用会创建在其下以 ID 命名的子目录",
    )

    args = parser.parse_args()

    # 从 config.local.md 读取默认值（CLI 参数优先覆盖）
    cfg = load_config()
    if args.id is None:
        args.id = cfg.get("id")
    if args.name is None:
        args.name = cfg.get("name")
    if args.author is None:
        args.author = cfg.get("author-name", "作者名称")
    if args.url is None:
        args.url = cfg.get("author-url", "")

    # 必填项校验
    if not args.id:
        print("错误：缺少应用 ID。请通过 -i 参数提供，或在 config.local.md 中配置。", file=sys.stderr)
        sys.exit(1)
    if not args.name:
        print("错误：缺少应用名称。请通过 -n 参数提供，或在 config.local.md 中配置。", file=sys.stderr)
        sys.exit(1)

    # 校验 ID：与官方 plugin_edit.php / theme_edit.php 一致
    if not re.match(r"^[A-Za-z0-9_]{3,30}$", args.id):
        print("错误：应用 ID 只能包含字母、数字、下划线，长度 3-30 个字符。", file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(SKELETON_DIR):
        print(f"错误：找不到素材目录 {SKELETON_DIR}", file=sys.stderr)
        sys.exit(1)

    if args.type == "plugin":
        create_plugin(args)
    else:
        create_theme(args)


if __name__ == "__main__":
    main()
