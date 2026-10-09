# 主题目录结构与 theme.xml

## 新建方式

用脚本生成骨架。在技能根目录执行：

```bash
python scripts/create_app.py -t theme -i <主题ID> -n "<主题名称>" -a "<作者>"
```

脚本会在 `-o` 指定目录（默认当前目录）下生成 `<主题ID>/` 骨架，包含 `theme.xml`、`include.php`（已注入 `$zbp->LoadLanguage('theme', 'ID')`）、`screenshot.png`、`template.json`、`style/style.css`、`template/`、`compile/`、`script/`、`include/` 和三份语言包。不需要配置页加 `--no-admin`。若已在 `config.local.md` 配置 ID、名称、作者等，可省略 `-i`/`-n`/`-a`/`--url`。

不使用脚本时，按[共同约定](application-conventions.md)准备主题副本后，创建 `style/`、`compile/`、`template/`、`include/`、`script/` 和 `style/style.css`，填写下文的 `theme.xml`。将管理入口的路径、启用状态判断、菜单高亮和图片引用调整为主题类型；功能扩展见 [theme-functions.md](zblogphp-theme-development-theme-functions.md)。

## 目录结构

```
zb_users/theme/{主题ID}/
├── theme.xml          # 必须。主题描述文件，<id> 必须与目录名一致
├── include.php        # 必须（由 theme.xml 的 <include> 指定）。主题激活时随每次请求加载
├── template.json      # 推荐。模板名称/类型声明，驱动后台模板下拉框筛选（见 template-hierarchy.md）
├── screenshot.png     # 后台主题列表缩略图
├── main.php           # 可选。后台主题配置页入口（由 theme.xml 的 <path> 指定，文件名可自定）
├── template/          # 模板目录。缺省文件自动回落到 zb_system/defend/default/
├── style/             # CSS/图片等静态资源
├── script/            # JS
├── language/          # 默认提供三种语言
│   ├── en.php         # 英文
│   ├── zh-cn.php      # 简体中文
│   └── zh-tw.php      # 繁体中文
└── include/           # 被 include.php 引用的类/函数文件（系统按 theme/{ID}/include/ 处理）
```

- 主题 ID = 目录名，`RegisterPlugin()` 第一个参数也用此 ID（主题本质上按插件机制加载）。
- `template/` 下可直接放 `.php` 模板文件；也可建子目录放模板（引擎 `GetAllFileDir` 递归收集）。
- 编译产物输出到 `zb_users/cache/compiled/{主题ID}/`，不要手动改那里。

## 模板文件结构（header/footer 与入口模板的分工）

文档骨架（`<!DOCTYPE html>`、`<html>`、`<head>` 开闭、`<body>` 开闭）写在每个入口模板（`index.php`、`single.php`、`search.php`、`404.php` 等）里，且骨架标签必须在入口模板内自闭合，不能拆到子模板：

```html
<!DOCTYPE html>
<html lang="{$language}">
<head>
{template:header}
</head>
<body class="{$type}">
{template:c_top}
<main class="col-main">
<!-- 页面内容 -->
</main>
{template:footer}
</body>
</html>
```

`header.php` 被 `{template:header}` 嵌入 `<head>` 内部，只写 head 内部标签，不允许出现文档骨架开标签，也不在里面留下未闭合的标签：

```html
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta http-equiv="X-UA-Compatible" content="ie=edge" />
<meta name="generator" content="{$zblogphp}" />
<meta name="renderer" content="webkit">
<title>{$name}-{$title}</title>
<link rel="stylesheet" rev="stylesheet" href="{$host}zb_users/theme/{$theme}/style/{$style}.css?{$themeinfo['modified']}" type="text/css" media="all" />
<script src="{$host}zb_system/script/jquery-latest.min.js?v={$version}"></script>
<script src="{$host}zb_system/script/zblogphp.js?v={$version}"></script>
<script src="{$host}zb_system/script/c_html_js_add.php?{if isset($html_js_hash)}hash={$html_js_hash}&{/if}v={$version}"></script>
<script src="{$host}zb_users/theme/{$theme}/script/custom.js"></script>
{$header}
{if $type=='index'&&$page=='1'&&$option['ZC_XMLRPC_ENABLE']}
<link rel="alternate" type="application/rss+xml" href="{$feedurl}" title="{$name}" />
<link rel="EditURI" type="application/rsd+xml" title="RSD" href="{$host}zb_system/xml-rpc/?rsd" />
<link rel="wlwmanifest" type="application/wlwmanifest+xml" href="{$host}zb_system/xml-rpc/wlwmanifest.xml" />
{/if}
```

页面顶部公共部分（站标、导航、侧边栏容器等）写进 `c_top.php`，页面底部公共部分（版权信息、底部导航、返回顶部等）写进 `footer.php`，各入口模板用 `{template:c_top}`、`{template:footer}` 引用，不在入口模板里重复书写。

**所有子模板（`header.php`、`footer.php`、`c_*.php`）内的 HTML 标签必须在本文件内闭合，不允许出现开标签在一个文件、闭合标签在另一个文件的跨文件配对。** 例如 `c_top.php` 里开了 `<div class="columns">`，就必须在 `c_top.php` 内把它关掉，不能等 `footer.php` 再写 `</div>`；入口模板的 `<main>` 也必须在入口模板内闭合。

`{$header}`、`{$footer}` 两个标签必须保留（见 template-syntax.md 内建变量表），分别放在 `header.php` 末尾和 `footer.php` 末尾，用于系统和插件注入头部/底部代码。

## 语言包

文件格式、加载及 PHP、模板和 JS 的文案引用见[共同语言包约定](application-conventions.md#语言包)。

## theme.xml 全字段

根元素：`<theme version="php">`。下表即完整字段说明；`mytheme`、名称、作者和版本等为示例值，生成时按当前任务填写。

| 字段 | 说明 | 示例 |
|---|---|---|
| `<id>` | 主题 ID，必须与目录名一致 | `<id>mytheme</id>` |
| `<name>` | 显示名称 | `<name>示例主题</name>` |
| `<url>` | 主题介绍/主页 URL | `<url>https://example.com/</url>` |
| `<note>` | 一句话简介 | `<note>主题功能简介</note>` |
| `<description>` | 详细描述/更新日志，可含换行 | `<description>主题说明</description>` |
| `<path>` | 后台配置入口文件（相对主题目录），留空表示无配置页 | `<path>main.php</path>` 或 `<path></path>` |
| `<include>` | 主题函数文件，每次请求随主题加载 | `<include>include.php</include>` |
| `<level>` | 使用后台配置页所需的管理员等级 | `<level>1</level>` |
| `<author>` | 作者：`<name>`/`<email>`/`<url>` | `<author><name>作者名称</name><email></email><url></url></author>` |
| `<source>` | 原作者/出处（同上三子字段） | `<source><name></name><email></email><url></url></source>` |
| `<adapted>` | 适配的系统版本号 | `<adapted>173050</adapted>` |
| `<version>` | 主题自身版本号 | `<version>1.7</version>` |
| `<pubdate>` / `<modified>` | 发布/更新日期 | `<pubdate>2019-11-27</pubdate>` |
| `<price>` | 售价（应用中心用，免费为 0） | `<price>0</price>` |
| `<phpver>` | 最低 PHP 版本 | `<phpver>5.2</phpver>` |
| `<advanced>` | 高级约束，四个子字段均可留空：`<dependency>`（依赖的应用）、`<rewritefunctions>`（要求不存在的函数名，防冲突重写）、`<existsfunctions>`（要求已存在的函数）、`<conflict>`（冲突应用） | `<advanced><dependency></dependency><rewritefunctions></rewritefunctions><existsfunctions></existsfunctions><conflict></conflict></advanced>` |
| `<sidebars>` | 启用主题时写入侧栏默认模块顺序 | 见下方完整示例 |

## `<sidebars>` 侧栏预设

9 组侧栏，子元素为 `<sidebar1>`~`<sidebar9>`，值是模块文件名以 `|` 分隔的列表。启用主题时写入系统选项 `ZC_SIDEBAR_ORDER`~`ZC_SIDEBAR9_ORDER`。

侧栏预设示例：

```xml
<sidebars>
  <sidebar1>calendar|controlpanel|catalog|previous|comments|archives|tags|link|misc</sidebar1>
  <sidebar2>calendar|controlpanel|catalog|previous|comments|archives|tags|link|misc</sidebar2>
  <sidebar3></sidebar3>
  <sidebar4></sidebar4>
  <sidebar5></sidebar5>
  <sidebar6></sidebar6>
  <sidebar7></sidebar7>
  <sidebar8></sidebar8>
  <sidebar9></sidebar9>
</sidebars>
```

- 值可为空字符串，9 组均可留空。
- 列表中的模块文件名必须存在于 `$zbp->modulesbyfilename`（系统内置或插件/主题注册的模块），否则该位置被静默跳过（template.php `MakeTemplateTags` L1010-1023）。
- 模块文件名清单与 `module.php` 模板见 modules-sidebars.md。

## 与 plugin.xml 的关系

主题与插件共用注册机制（`RegisterPlugin`），theme.xml 字段与 plugin.xml 高度相似；差异在于主题有 `<sidebars>`、`<path>` 指向主题配置页，且模板/样式目录为前端服务。插件机制详见 zblogphp-plugin-development。
