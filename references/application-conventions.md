# 主题与插件共同约定

主题、插件开发的共同规则集中维护于此，专题资料补充各领域的实现细节。

## 系列应用独立性（禁止套壳）

- 为同一站点或同一作者开发多个主题时，每个主题必须从脚本生成的空白 `template/` 开始独立设计。禁止复制既有主题目录后替换变量名或前缀，包括但不限于 `cp -r` 旧主题改 ID、照搬模板结构只改 class 前缀和配色、把同一套模板母版换皮成多个主题。
- 新主题先按目标站点的行业和内容做信息架构设计：受众与内容类型、页面清单、导航组织、栅格节奏、列表页与文章页排版，再落到模板。不同主题在这些层面应当有可辨认的差异，而不是同一布局换皮。
- 可以复用的是知识与约定（本技能的规则、Z-BlogPHP 模板机制、与具体主题无关的通用代码片段），不是成品主题的模板和视觉结构。
- 插件同理：功能相同或相近的多个插件（如多个支付、统计类插件）必须独立实现，禁止复制既有插件换 ID、换名称。
- 完成定义：向用户汇报前，确认新应用与既有应用之间不存在模板或代码复制关系。若用户明确要求基于其旧应用改造，必须说明复用了哪些部分、重新设计了哪些部分，不能整体套壳。

## PHP 文件守卫

未由 `zb_system/function/c_system_base.php` 引导核心的 PHP 文件（例如 `include.php`、语言包、函数库和模板片段）加 `if (!defined('ZBP_PATH')) {exit('Access denied');}`；已经引导核心的管理入口沿用其引导方式。

## 语言包

主题和插件默认创建：

```text
language/en.php
language/zh-cn.php
language/zh-tw.php
```

三份文件以 PHP 文件守卫开头，返回相同键名的数组，分别提供英文、简体中文和繁体中文文案。不能只建空文件，也不能把同一种语言复制三份。例如 `zh-cn.php`：

```php
<?php
if (!defined('ZBP_PATH')) {exit('Access denied');}
return array(
    'settings' => '设置',
    'save' => '保存',
);
```

相同键在 `en.php` 中为 `Settings`、`Save`，在 `zh-tw.php` 中为 `設定`、`儲存`。按实际功能添加文案，系统已有通用文案直接复用系统语言包。

激活函数声明 `global $zbp;` 后调用 `$zbp->LoadLanguage('plugin', 'ID')` 或 `$zbp->LoadLanguage('theme', 'ID')`。系统从对应应用的 `language/` 读取语言 PHP 文件（文件名匹配 `/^([0-9A-Z\-_]*)\.php$/ui`），按 `ZC_BLOG_LANGUAGEPACK → zh-cn → zh-tw → en` 回退，内容进入 `$zbp->lang['ID']`。

PHP 页面用 `$zbp->lang['ID']['key']`，主题模板用 `{$lang['ID']['key']}`，或按 [主题变量注入示例](zblogphp-theme-development-theme-functions.md) 使用 `{$msg.key}`；JS 文案通过 JSON 传入。复制的骨架中应用自有固定文案也改为语言包引用。

## HTML 语义化

主题模板和插件页面输出的 HTML 一律使用语义化标签：页面结构用 `header`、`nav`、`main`、`aside`、`article`、`section`、`footer`；文本内容用 `h1`~`h6`、`p`、`ul`/`ol`/`li`、`blockquote`、`time`、`figure`；表单用 `fieldset`、`label` 关联输入项，按钮用 `button`。不用无语义的 `div`/`span` 堆砌可由语义标签承担的结构，仅在没有对应语义时才用 `div`/`span` 配合 `class`。

模板拆分时，每个文件内的 HTML 标签必须在本文件内闭合，不允许开标签写在一个文件、闭合标签写在另一个文件。文档骨架（`<!DOCTYPE html>`、`<html>`、`<head>`、`<body>` 及其闭合）只写在主题入口模板内。具体分工和示例见 [theme-structure.md「模板文件结构」](zblogphp-theme-development-theme-structure.md#模板文件结构（headerfooter-与入口模板的分工）)。

## 图片、图标与 SVG

- 页面和功能代码不使用 SVG，包括 `.svg` 文件、内联 `<svg>`、SVG data URI 和输出 SVG 的图标组件。
- 界面图标使用 icon 字体，优先使用 `zb_system/image/icon/icon.css?v=173540`，也可以使用其他 icon 字体库的字体/CSS 版本；加载方式和类名见 [图标参考](zblogphp-admin-icons.md)。功能所需普通图片由用户上传非 SVG 素材。

## 读取与交付边界

- 创建插件不扫描默认主题，也不读取默认主题的引用关系；只有任务明确涉及主题联动时才读取主题专题资料。
- 制作主题、插件时不读取或确认站点和 PHP 版本号；`adapted`、`phpver` 使用资料中的版本约定，修改已有应用时沿用原值。
- 交付前默认执行零成本静态检查（不访问站点、不启停应用）：全部 PHP 文件通过 `php -l`；模板中 `{if}`、`{foreach}` 等成对标签逐个配平（可用 `python scripts/check_template_tags.py <主题目录>` 检查），`{template:}` 引用的文件存在；三份语言包键名一致，模板和页面引用的语言键都有定义；引用的本地资源路径存在，无站外资源引用。发现问题先修复再交付。
- 运行时实测（访问前后台页面、启停应用、调用接口、重建编译缓存、插入调试代码）不要自动执行；只有用户明确要求测试、验证或排错时才执行对应范围，各专题的排错、验证和审计章节仅用于此类明确请求；实现要点用于编写时参考。
- 完成代码后说明文件位置、已实现内容、静态检查结果和必要使用方式。

## 代码质量

禁止危险调用、全局符号带应用 ID、代码与 XML 的 `phpver` 兼容、资源本地化、前端无报错并适配多端等硬性要求，统一见[代码质量要求](zblogphp-code-quality.md)，编写时即遵守，不是发布前才检查的清单。
