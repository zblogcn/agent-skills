# 模块与侧栏系统

模块（Module）是可复用的 HTML 块；侧栏（sidebar）是按顺序排列的一组模块。数据源：`zb_system/function/lib/module.php`、`modulebuilder.php`、`template.php` 的 `MakeTemplateTags`（L999-1028）。

## Module 对象

模板中可用的属性如下，下方已附模块模板骨架：

| 属性 | 说明 |
|---|---|
| `{$module.FileName}` | 文件名（唯一标识，`$modulesbyfilename` 的键） |
| `{$module.Name}` | 显示名称（模块标题） |
| `{$module.Content}` | 模块 HTML 内容 |
| `{$module.Type}` | 渲染类型：`div` 或 `ul`（决定内容包裹标签） |
| `{$module.IsHideTitle}` | 是否隐藏标题 |
| `{$module.HtmlID}` | HTML 元素 id |

系统默认单个模块模板（module.php）：

```
<dl class="function" id="{$module.HtmlID}">
{if (!$module.IsHideTitle)&&($module.Name)}<dt class="function_t">{$module.Name}</dt>{else}<dt style="display:none;"></dt>{/if}
<dd class="function_c">
{if $module.Type=='div'}<div>{$module.Content}</div>{/if}
{if $module.Type=='ul'}<ul>{$module.Content}</ul>{/if}
</dd>
</dl>
```

## 侧栏变量 `$sidebar` ~ `$sidebar9`

- 共 9 组侧栏。每组对应选项 `ZC_SIDEBAR_ORDER`~`ZC_SIDEBAR9_ORDER`，值为模块文件名以 `|` 分隔（安装默认值见 `zb_system/defend/option.php` L194-202，如 `calendar|controlpanel|catalog|searchpanel|comments|archives|favorite|link|misc`）。
- `MakeTemplateTags` 把每组解析为模块对象数组注入模板：`$sidebar`（第 1 组）、`$sidebar2`~`$sidebar9`。列表中不存在的模块文件名会被跳过。
- 主题启用时用 `theme.xml` 的 `<sidebars>` 覆盖这些选项（见 theme-structure.md）。

默认 `sidebar.php`（系统默认模板）：

```
{foreach $sidebar as $module}
{template:module}
{/foreach}
```

引擎会为第 2~9 组自动派生 `sidebar2.php`~`sidebar9.php`（把 `$sidebar` 替换为 `$sidebarN`），所以模板里直接 `{template:sidebar2}` 即可输出第 2 组侧栏；需要不同样式就在主题 `template/` 下提供对应的 `sidebarN.php`。

## 输出模块的两种方式

```
{module:navbar}                 （等效于 isset 判断后 echo $modules['navbar']->Content）
{$modules['navbar'].Content}    （直接输出）
```

## 系统内置模块文件名

由 `$zbp->RegBuildModule()` 注册（zblogphp.php L2432-2440），内容每次动态生成：

| FileName | 生成函数 | 内容 |
|---|---|---|
| `navbar` | ModuleBuilder::Navbar | 导航条 `<li>` 列表 |
| `catalog` | ModuleBuilder::Catalog | 分类列表 |
| `calendar` | ModuleBuilder::Calendar | 日历 |
| `comments` | ModuleBuilder::Comments | 最新评论 |
| `previous` | ModuleBuilder::LatestArticles | 最新文章 |
| `archives` | ModuleBuilder::Archives | 文章归档 |
| `tags` | ModuleBuilder::TagList | 标签列表 |
| `statistics` | ModuleBuilder::Statistics | 站点统计 |
| `authors` | ModuleBuilder::Authors | 作者列表 |

另有 `controlpanel`（控制面板）、`searchpanel`（搜索）、`favorite`（收藏）、`link`（链接）、`misc`（杂项）等以模块记录形式存在（可在后台"模块管理"查看/编辑）。模块的 HTML 骨架模板为 `zb_system/defend/default/module-{文件名}.php`，主题可在 `template/` 下用同名文件覆盖其外观。

注意：模块 `Content` 在输出前会做静态标签替换（`Display()` 中对每个模块 `ReplaceStaticTags`），所以模块内容里可直接写 `{$name}`、`{#ZC_BLOG_NAME#}` 等静态标签。

## 主题/插件创建自定义模块

- 后台"模块管理"手工新建，或代码里 `new Module()` 后设置 `FileName`/`Name`/`Source`/`Content` 再 `Save()`。
- 可挂 `Filter_Plugin_Zbp_BuildModule` 钩子动态生成/更新自定义模块，模块名带目标主题前缀，`Source` 设为 `themeinclude_{主题ID}`。
- 也可挂 `Filter_Plugin_Template_GetTemplate` 返回自定义路径，替换任意子模板（含 `module-*`）。

## 常见坑

- 在 theme.xml `<sidebars>` 里写了不存在（未注册/未创建）的模块文件名 → 该位置静默消失，检查后台模块管理中是否存在该 FileName。
- 改了 `<sidebars>` 但前台没变 → 侧栏顺序只在**启用主题时**写入选项；已在用的站点需在后台"模块管理/侧栏"重新拖拽，或重新启用主题。
- 想在某页显示不同侧栏：用 `{if $type=='index'}{template:sidebar}{else}{template:sidebar2}{/if}` 这类判断，或建独立的列表/单篇模板。
