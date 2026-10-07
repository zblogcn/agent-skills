# 主题与插件共同约定

主题、插件开发的共同规则集中维护于此，专题资料补充各领域的实现细节。

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

PHP 页面用 `$zbp->lang['ID']['key']`，主题模板用 `{$lang['ID']['key']}`，或按 [主题变量注入示例](zblogphp-theme-development/references/theme-functions.md) 使用 `{$msg.key}`；JS 文案通过 JSON 传入。复制的骨架中应用自有固定文案也改为语言包引用。

## 图片、图标与 SVG

- 页面和功能代码不使用 SVG，包括 `.svg` 文件、内联 `<svg>`、SVG data URI 和输出 SVG 的图标组件。
- 界面图标使用 icon 字体，优先使用 `zb_system/image/icon/icon.css?v=173540`，也可以使用其他 icon 字体库的字体/CSS 版本；加载方式和类名见 [图标参考](zblogphp-admin/references/icons.md)。功能所需普通图片由用户上传非 SVG 素材。

## 读取与交付边界

- 创建插件不扫描默认主题，也不读取默认主题的引用关系；只有任务明确涉及主题联动时才读取主题专题资料。
- 制作主题、插件时不读取或确认站点和 PHP 版本号；`adapted`、`phpver` 使用资料中的版本约定，修改已有应用时沿用原值。
- 完成代码后直接说明文件位置、已实现内容和必要使用方式，由用户自行检查测试。不要自动复查代码对错、运行 `php -l` 或其他测试、访问前后台、启停应用、调用接口、检查编译产物或插入调试代码；只有用户明确要求测试、验证或排错时才执行对应范围。各专题的排错、验证和审计章节仅用于此类明确请求；实现要点用于编写时参考。
