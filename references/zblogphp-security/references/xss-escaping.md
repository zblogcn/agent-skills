# XSS 转义与 HTML 过滤

来源：`zb_system/function/c_system_common.php`（FormatString / htmlspecialchars_array）、`zb_system/function/lib/xsshtml.php`、`zb_system/function/lib/template.php`（1.7.5.3540）。

## 核心函数：`FormatString($source, $para)`

c_system_common.php L1956-1996：

```php
function FormatString($source, $para)
{
    if (strpos($para, '[html-format]') !== false) {
        $source = htmlspecialchars($source);         // HTML 实体编码
    }
    if (strpos($para, '[nohtml]') !== false) {
        $source = preg_replace("/<([^<>]*)>/si", "", $source);  // 去标签
        $source = str_replace("<", "˂", $source);
        $source = str_replace(">", "˃", $source);
    }
    if (strpos($para, '[noscript]') !== false) {
        $class  = new XssHtml($source);              // HTML 白名单过滤
        $source = trim($class->getHtml());
    }
    if (strpos($para, '[enter]') !== false) { ... }   // \r\n → <br/>
    if (strpos($para, '[noenter]') !== false) { ... } // 去换行
    if (strpos($para, '[filename]') !== false) { ... }// 去路径非法字符
    if (strpos($para, '[normalname]') !== false) { ...}
    return $source;
}
```

**别名**：`TransferHTML($source, $param)`（L2006-2009）已标记 Deprecated，内部就是调用 `FormatString`。新代码应直接使用 `FormatString`。

## 内置使用场景（c_system_event.php）

| 字段 | 过滤模式 | 行号 |
|---|---|---|
| `$_POST['Alias']` | `[noscript]` | L244, L391, L775, L1370, L1515 |
| `$_POST['Tag']` | `[noscript]` | L248, L391 |
| `$_POST['Intro']` | `[nohtml]` | L405, L426 |
| `$_POST['Name']` | `[nohtml]` | 登录/会员保存 |
| 评论内容 | `[nohtml][enter]` / `[noscript]` | 视设置而定 |

规律：凡来自 `$_POST` 的用户输入，在入库前统一过 `FormatString`；输出到前端模板时通常不再二次转义（由入库时的过滤保证）。

## 数组批量转义：`htmlspecialchars_array($array)`

c_system_common.php L2048-2060：

```php
function htmlspecialchars_array($array)
{
    $newArray = array();
    foreach ($array as $key => $value) {
        $newKey = htmlspecialchars($key);
        if (is_array($value)) {
            $newArray[$newKey] = htmlspecialchars_array($value);
        } elseif (is_string($value)) {
            $newArray[$newKey] = htmlspecialchars($value);
        }
    }
    return $newArray;
}
```

用于递归转义整个数组（如配置、表单回显）。

## HTML 白名单过滤：`XssHtml` 类

来源：`zb_system/function/lib/xsshtml.php`。

构造时传入原始 HTML，`getHtml()` 返回白名单过滤后的 HTML。白名单默认允许常见排版标签（p、div、span、img、a、strong、em、table、ul、ol 等），移除 script/iframe/on* 事件等危险内容。

在 `FormatString` 中对应 `[noscript]` 模式。也可直接使用：

```php
$xss = new XssHtml($html);
$safe = $xss->getHtml();
```

## 模板输出的转义真相

**重要**：Z-BlogPHP 的模板引擎（`zb_system/function/lib/template.php`）对 `{$article.Title}` 这类标签**默认不做 htmlspecialchars 转义**。

模板编译流程（template.php L328-375）最终把 `{...}` 替换成 PHP 代码：

```php
// parse_vars_replace_dot（L635-643）
return '{php} echo $' . $this->replace_dot($matches[1]) . '; {/php}';
```

即 `{$article.Title}` 编译为 `<?php echo $article->Title; ?>`，**原样输出**。

例外：`{$header}`、`{$footer}`、`{$name}`、`{$subname}`、`{$title}` 等站点级标签在 `template.php` L972-977 处被 `htmlspecialchars()` 处理过（因为这些是系统内部使用的 meta 标题）。

**含义**：

- 文章标题、内容、评论等字段在入库时已用 `FormatString` 过滤，所以模板里直接 `{$article.Title}` 通常是安全的（前提是插件没绕过入库过滤）。
- 如果插件从外部 API / 富文本 / 未过滤来源取数据，输出前必须自行 `htmlspecialchars()`。
- 主题开发者不应假设 `{$xxx}` 标签已转义，尤其是对自定义模块/插件注入的数据。

## 编写要点

- 所有 `$_POST`/`$_GET` 字段在入库前根据用途调用 `FormatString($x, '[html-format]')` 或 `FormatString($x, '[noscript]')`
- 输出到 HTML 的未知/外部数据使用 `htmlspecialchars($x)` 或 `FormatString($x, '[html-format]')`
- 富文本内容用 `FormatString($x, '[noscript]')` 或 `new XssHtml($x)` 白名单过滤
- 不要依赖模板引擎自动转义
