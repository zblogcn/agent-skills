# 模板标签语法

模板先被编译为 PHP（产物在 `zb_users/cache/compiled/{theme}/`），再 include 执行。以下语法与示例可直接使用，编译函数名和行号仅为溯源信息，无需读取引擎或自带主题。

## 编译顺序速览（CompileFile，L326-374）

依次执行：移除原生 `<?php?>` 块 → 保留不编译代码 → `{template:}` → `{module:}` → 注释 `{* *}` → `{#配置#}` → `{$变量}` → `{函数()}` → `{if}` → `{foreach}` → `{for}` → `{switch}`。

注意：**模板文件里写 `<?php ... ?>` 会被直接删除**（`remove_php_blocks`），需要内嵌 PHP 时用 `{php}...{/php}`。

## 注释 `{* ... *}`

不会输出到 HTML，仅作为模板内注释使用。

> 模板的名称/类型声明（供后台模板选择器读取）统一通过主题根目录的 `template.json` 配置，见 template-hierarchy.md「后台模板选择器」一节。

## 变量 `{$...}`（parse_vars，L464-467）

`.` 会被编译为 `->`（replace_dot，L660-679），字符串引号内的 `.` 不受影响。

```
{$article.Title}                  → echo $article->Title;
{$article.Category.Name}          → echo $article->Category->Name;
{$article.Time('Y-m-d')}          → echo $article->Time('Y-m-d');   （方法调用）
{$zbp->name}                      → echo $zbp->name;                （对象属性写法）
{$option['ZC_BLOG_NAME']}         → echo $option['ZC_BLOG_NAME'];
{$lang['msg']['author']}          → echo $lang['msg']['author'];       （系统语言包）
{$lang['主题ID']['reply']}         → echo $lang['主题ID']['reply'];      （主题自定义语言包）
{$modules['navbar'].Content}      → echo $modules['navbar']->Content;
{$comment.Author.StaticName}
```

赋值写法（表达式含 `=` 时编译为语句而非 echo）：

```
{$a = 1}                          → $a = 1;
```


## 配置标签 `{#...#}`（parse_option，L456-459）

```
{#ZC_BLOG_NAME#}   → 若定义了同名常量则输出常量，否则输出 $option['ZC_BLOG_NAME']
```

用于输出站点配置项；`MakeTemplateTags` 会把 `$option` 里所有标量注册成静态标签，可在模块 HTML 内容中直接替换（`ReplaceStaticTags`）。

## 子模板 `{template:名字}`（parse_template，L440-443）

```
{template:header}   → include $this->GetTemplate('header');
```

- `名字` 不含 `.php` 后缀；实际 include 的是编译产物路径。
- `GetTemplate()`（L148-160）触发钩子 `Filter_Plugin_Template_GetTemplate`，插件/主题可借此重写任意子模板路径（返回自定义文件路径）。
- 子模板的标签闭合规则和与入口模板的分工见 [theme-structure.md「模板文件结构」](zblogphp-theme-development-theme-structure.md#模板文件结构（headerfooter-与入口模板的分工）)。
- 除系统惯用的 `post-*`、`comment*`、`module-*` 外，也可以把各页面重复的部分（导航、面包屑、文章卡片等）提取为自定义片段模板，如 `c_nav.php`，再用 `{template:c_nav}` 引用。`c_` 这类「字母+下划线」开头的文件名不会进入后台模板下拉框（规则见 template-hierarchy.md）。
- 首页模板可组合 `{template:header}`、`{template:post-multi}`、`{template:pagebar}`、`{template:sidebar}`、`{template:footer}`。

## 模块 `{module:文件名}`（parse_module，L448-451）

```
{module:navbar}  → if(isset($modules['navbar'])){echo $modules['navbar']->Content;}
```

输出指定模块的 HTML 内容；等价写法 `{$modules['navbar'].Content}`。详见 modules-sidebars.md。

## 内嵌 PHP `{php}...{/php}`

```
{php} echo date('Y'); {/php}
```

需要"不编译"的原样内容可用 `{literal}` 相关机制（`parse_uncompile_code` 保护块），日常主题开发一般用不到。

## 函数 `{name(args)}`（parse_function，L472-475）

```
{count($article.Tags)}  → echo count($article->Tags);
```

直接调用 PHP 函数并 echo 返回值。注意与 `{if count($article.Tags)>0}` 这类在流程标签内写表达式的方式区分（流程标签内无需花括号包函数）。

## 条件 `{if}`（parse_if，L480-521）

支持 `{if}`、`{elseif}`、`{else}`、`{/if}`，可嵌套。条件表达式是 PHP 表达式（变量仍用 `.` 分隔属性）：

```
{if $article.TopType}
  {template:post-istop}
{else}
  {template:post-multi}
{/if}
```

```
{if $article.Type==ZC_POST_TYPE_ARTICLE}
  {template:post-single}
{else}
  {template:post-page}
{/if}
```

```
{if (!$module.IsHideTitle)&&($module.Name)}...{else}...{/if}
```

**漏写 `{/if}` 不会报错，必须配平。** 编译器用非贪婪正则配对，漏写闭合标签的开标签会一直吞到下一个出现的同类闭合标签，表现为某块内容静默消失、条件分支错乱，且无任何报错信息；`{foreach}`、`{for}`、`{while}`、`{php}` 同理。交付前用 `python scripts/check_template_tags.py <主题目录>` 检查配平（见流程「交付前静态检查」）。

## 循环 `{foreach}`（parse_foreach，L526-548）

```
{foreach $articles as $article}
  ...
{/foreach}

{foreach $article.Tags as $i => $tag}
  <a href='{$tag.Url}'>{$tag.Name}</a>
  {if count($article.Tags) > $i}<small>,</small>{/if}
{/foreach}
```

评论树递归：`comment.php` 内 `{foreach $comment.Comments as $comment}{template:comment}{/foreach}`。

## 循环 `{for}`（parse_for，L553-575）

```
{for $i=0; $i<10; $i++} ... {/for}
```

## 分支 `{switch}`（parse_switch，L580-628）

```
{switch $article.Type}
  {case 0:}
    ...
    {break;}
  {default:}
    ...
{/switch}
```

`{case ...}`、`{break;}`、`{default:}` 为固定写法。

## 内建模板变量（MakeTemplateTags，L937-1047）

以下变量在所有模板中可用：

| 变量 | 内容 |
|---|---|
| `{$zbp}` | ZBlogPHP 全局对象（`{$zbp->name}`、`{$zbp->host}` 等） |
| `{$user}` | 当前登录用户（Member 对象） |
| `{$option}` | 站点配置数组（数据库密码等敏感键已被剔除） |
| `{$lang}` / `{$langs}` | 语言数组。系统语言包用 `{$lang['msg']['xxx']}`；主题语言包用 `{$lang['主题ID']['xxx']}`（由激活函数 `$zbp->LoadLanguage('theme', '主题ID')` 加载，键名见主题 `language/` 下的文件） |
| `{$version}` | 系统版本 |
| `{$categories}` / `{$categoriesbyorder}` / `{$categories_all}` / `{$categorys}`（别名） | 分类数组 |
| `{$modules}` | 模块数组（按文件名索引，`$modulesbyfilename`） |
| `{$title}` | 当前页面标题（已 htmlspecialchars） |
| `{$host}` `{$path}` `{$cookiespath}` | 站点 URL / 路径 |
| `{$name}` `{$subname}` | 站点名 / 副标题（已 htmlspecialchars） |
| `{$theme}` `{$themeinfo}` `{$style}` | 当前主题 ID / theme.xml 信息 / 样式目录名 |
| `{$type}` `{$page}` | 页面类型（index/category/tag/author/date/search/文章类型名）、页码，由各路由函数 SetTags |
| `{$header}` `{$footer}` | 系统注入的头部/底部代码（header.php、footer.php 必须保留这两个标签，缺失时引擎会自动补插，见 `addNonexistentTags` L303-319） |
| `{$validcodeurl}` `{$feedurl}` `{$searchurl}` `{$ajaxurl}` | 各功能 URL |
| `{$socialcomment}` | 社会化评论 HTML（非空时 comments.php 直接输出它） |
| `{$sidebar}` ~ `{$sidebar9}` | 9 组侧栏的模块对象数组（按 ZC_SIDEBAR_ORDER 排好序） |
| `{$zblogphp}` `{$zblogphphtml}` `{$copyright}` `{$language}` | 版本署名等 |

页面级变量（由 c_system_route.php 的 ViewList/ViewPost/ViewSearch 注入）见 template-hierarchy.md。

## SEO 标签需自行实现

系统不提供 keywords、description、canonical 等 SEO 标签，模板里也没有对应内建标签；`{$header}` 只汇总系统和插件注入的头部代码（系统自身仅在搜索、404 等页面追加 `noindex` 的 robots meta）。

主题需要 SEO 时在 `header.php` 自行编写，按页面类型从现有变量取值，例如：

```html
<title>{$title}_{$name}</title>
<meta name="keywords" content="{if $type=='article'}{foreach $article.Tags as $tag}{$tag.Name},{/foreach}{else}{$name}{/if}" />
<meta name="description" content="{if $type=='article'||$type=='page'}{$article.Intro}{else}{$subname}{/if}" />
```

文章摘要 `{$article.Intro}`、标签 `$article.Tags`、分类名 `{$article.Category.Name}` 等都可直接使用；更复杂的规则（自定义 SEO 字段、按页面类型区分）在主题 `include.php` 中挂接页面 Hook 生成变量后再在模板输出，见 theme-functions.md。

## 常见坑

1. 属性访问 `.` 与 `->` 两种写法都支持（`.` 会被编译为 `->`，`->` 原样保留），例如 `{$zbp.name}` 与 `{$zbp->Config('X')->Key}`。
2. `{if}` 条件内不能跨行换行（正则 `[^\n\}]+` 限制）。
3. 字符串里的 `.` 引擎会自动保护（`{%_dot_%}`），如 `{$article.Time('Y.m.d')}` 不会被误编译。
4. 原生 `<?php ?>` 会被删除；要跑 PHP 用 `{php}`。
5. 模板保存后需重建编译缓存才生效。开发期最简单：后台开启调试模式（`ZC_DEBUG_MODE`），每次访问自动检测模板变化并重建（zblogphp.php L1022-1025）。
