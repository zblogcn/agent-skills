# 主题 include.php：注册与钩子

主题与插件共用应用机制。include.php 在主题激活期间随**每次请求**加载（前台与后台）。在[共同约定](application-conventions.md)的应用副本中补充以下扩展逻辑；示例也供模板缺失时回退，`mytheme` 为占位 ID。

## 基本骨架

```php
<?php
if (!defined('ZBP_PATH')) {exit('Access denied');}   // 防直接访问（必须）
// 注册主题（第一个参数必须等于主题目录名 / theme.xml 的 <id>）
RegisterPlugin("mytheme", "ActivePlugin_mytheme");

// 每次请求执行：挂钩子、加载语言包
function ActivePlugin_mytheme()
{
    global $zbp;
    // 加载主题语言包 zb_users/theme/mytheme/language/
    $zbp->LoadLanguage('theme', 'mytheme');
    Add_Filter_Plugin('Filter_Plugin_Zbp_MakeTemplatetags', 'mytheme_MakeTemplatetags');
}

// 主题启用时执行一次（初始化配置）
function InstallPlugin_mytheme()
{
    global $zbp;
    $cfg = $zbp->Config('mytheme');
    if (!isset($cfg->Logo)) {
        $cfg->Logo = '示例主题';
        $cfg->Save();
    }
}

// 主题停用/卸载时执行
function UninstallPlugin_mytheme()
{
}
```

要点：

- 按需挂接 `Filter_Plugin_ViewSearch_Begin` 设置搜索行为。
- 安装函数用 `$zbp->Config('mytheme')` 初始化配置；激活函数只挂当前功能需要的钩子。切换主题可能不经过后台安装请求（如 `ZBP_PRESET_THEME`、直接改启用主题），安装函数不一定执行，配置初始化要写成可重复执行且不覆盖已有值。
- 主题停用同样会执行 `UninstallPlugin_{ID}`，其中不要删除用户配置；清理运行期缓存即可（见 [插件生命周期「停用、卸载与数据保留」](zblogphp-plugin-development-lifecycle.md#停用卸载与数据保留)）。
- 主题配置页入口由 `theme.xml` 的 `<path>` 指定，可通过 `Filter_Plugin_Admin_TopMenu` 添加后台顶部菜单链接，写法见 [菜单参考](zblogphp-admin-menus.md)。

## 注入自定义模板变量：Filter_Plugin_Zbp_MakeTemplatetags

触发点：`$zbp->PrepareTemplate()`（zblogphp.php L2291-2293），回调按引用接收 `$template->templateTags` 数组，加键即在模板中多一个变量。

注入配置、语言包和自定义侧栏列表的示例（配置项按需求提供）：

```php
function mytheme_MakeTemplatetags(&$templateTags)
{
    global $zbp;
    $cfg = $zbp->Config('mytheme');
    $templateTags['msg'] = (object) $zbp->lang['mytheme'];   // 模板中 {$msg.xxx}
    $templateTags['cfg'] = $cfg;                          // 模板中 {$cfg.Logo}
    $templateTags['sideMods'] = $cfg->MobileSide ? array() : explode(' ', trim($cfg->SideMods));
}
```

模板中即可用 `{$cfg.Logo}`、`{foreach $sideMods as $m}` 等。注意该钩子在每次构建模板标签时执行，保持轻量。

## 主题常用钩子速查

| 钩子 | 用途 |
|---|---|
| `Filter_Plugin_Zbp_MakeTemplatetags` | 注入全局模板变量 |
| `Filter_Plugin_Zbp_BuildModule` | 动态生成/更新自定义模块 |
| `Filter_Plugin_ViewList_Template` | 列表页渲染前改模板变量/换模板（回调收 `$template`），可改摘要、配合多图列表 |
| `Filter_Plugin_ViewPost_Template` | 单篇页同上 |
| `Filter_Plugin_ViewSearch_Template` | 搜索页同上 |
| `Filter_Plugin_ViewSearch_Begin` | 搜索流程开始（可改搜索行为） |
| `Filter_Plugin_Template_GetTemplate` | 重写 `{template:xxx}` 解析到的文件路径（返回自定义路径） |
| `Filter_Plugin_Zbp_PrepareTemplate` | 模板加载前可改 `$theme`/`$template_dirname`（如移动端换模板目录） |
| `Filter_Plugin_Template_Compiling_Begin` / `_End` | 模板编译前/后改模板源码 |
| `Filter_Plugin_Post_Get` | 给 Post 对象附加动态属性（模板中直接用 `{$article.Cover}`） |

钩子签名、注册细节与完整清单见 zblogphp-hooks-reference；RegisterPlugin / Config 存取 / 安装卸载生命周期见 zblogphp-plugin-development。

## 给文章附加自定义字段的两种做法

1. **动态属性**：挂 `Filter_Plugin_Post_Get`，按属性名计算赋值：

```php
Add_Filter_Plugin('Filter_Plugin_Post_Get', 'mytheme_PostGet');

function mytheme_PostGet(&$post, $name)
{
    switch ($name) {
        case 'Cover':
            $post->$name = $post->ImageCount > 0 ? $post->Thumbs(400, 300)[0] : '';
            break;
    }
}
```

之后模板直接 `{$article.Cover}`。

2. **Metas 扩展字段**：`$article->Metas->Key` / `$category->Metas->Key`；例如用 `$category->Metas->Motto` 保存分类标语，通过 `Filter_Plugin_Category_Edit_Response` 在分类编辑界面注入字段。

## 注意事项

- include.php 每次请求都加载：只做注册和挂钩子，重逻辑放钩子回调里按需执行。
- 函数名加主题前缀（`mytheme_...`）避免与插件/其他主题冲突。
- 主题的 `RegisterPlugin` ID 必须是主题目录名，否则启用/停用回调不会按预期触发。
