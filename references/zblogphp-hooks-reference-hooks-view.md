# 前台展示类钩子

涵盖 index.php / search.php / feed.php 入口、ViewIndex / ViewList / ViewPost / ViewSearch / ViewFeed / ViewAuto / ViewComment(s) 等视图输出，以及 GetPost / GetList 结果与模块/模板编译。所有钩子集中注册于 `zb_system/function/c_system_plugin.php`（行号即该文件行号）。

## 入口页 Begin / End

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Index_Begin` | 777 | — | `index.php` 起动接口 |
| `Filter_Plugin_Index_End` | 788 | — | `index.php` 结束接口 |
| `Filter_Plugin_Search_Begin` | 820 | — | 搜索页接口，可接管搜索页 |
| `Filter_Plugin_Search_End` | 830 | — | 搜索接口结束 |
| `Filter_Plugin_Feed_Begin` | 840 | — | Feed 页接口，可接管 Feed 页 |
| `Filter_Plugin_Feed_End` | 850 | — | Feed 页接口结束 |

## 前台 JS 注入

| 钩子 | 行号 | 说明 |
| --- | --- | --- |
| `Filter_Plugin_Html_Js_Add` | 799 | `c_html_js_add.php` 脚本接口，允许插件输出内容 |
| `Filter_Plugin_Html_Js_ZbpConfig` | 809 | `c_html_js_add.php` 脚本接口，允许插件设置 `zbpConfig` |

## 视图入口 Begin

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_ViewIndex_Begin` | 1650 | — | `ViewIndex` 输出接口 Begin |
| `Filter_Plugin_ViewFeed_Begin` | 1661 | — | `ViewFeed` 输出接口 Begin |
| `Filter_Plugin_ViewSearch_Begin` | 1672 | — | `ViewSearch` 输出接口 Begin |
| `Filter_Plugin_ViewAuto_Begin` | 1683 | `&$url` | `ViewAuto` 输出接口 Begin |
| `Filter_Plugin_ViewAuto_End` | 1694 | `&$url` | `ViewAuto` 输出接口 End |
| `Filter_Plugin_ViewPost_Begin` | 1771 | `&$id, $alias, $isrewrite, $object` | `ViewPost` 显示输出 Begin |
| `Filter_Plugin_ViewPost_Begin_V2` | 1782 | `&$array` | 同上，第 2 版（只传一个数组） |
| `Filter_Plugin_ViewList_Begin` | 1705 | `&$page, &$cate, &$auth, &$date, &$tags, &$isrewrite, &$object` | 列表输出接口 |
| `Filter_Plugin_ViewList_Begin_V2` | 1716 | `&$array` | 同上，第 2 版（只传一个数组） |

`Filter_Plugin_ViewAuto_Begin` 也是插件接管前台 URL 的入口：在回调里判断路径后 `SetPluginSignal(..., PLUGIN_EXITSIGNAL_RETURN)` 并输出页面。完整路由、登录注册和停用态写法见 [插件前台页面](zblogphp-plugin-development-frontend-pages.md)。

## 视图核心查询 Core

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_ViewList_Core` | 1727 | `&$type, &$page, &$category, &$author, &$datetime, &$tag, &$w, &$pagebar, $list_template` | 列表核心接口，可改写 SQL 条件 |
| `Filter_Plugin_ViewSearch_Core` | 1738 | `$q, $page, $w, $pagebar` | 搜索核心接口 |
| `Filter_Plugin_ViewFeed_Core` | 1749 | `$w` | Feed 核心接口 |
| `Filter_Plugin_ViewFeed_End` | 1760 | `$rss2` | Feed 结束接口 |
| `Filter_Plugin_ViewPost_Core` | 1793 | `&$select, &$w, &$order, &$limit, &$option` | 文章/页面显示核心接口 |
| `Filter_Plugin_ViewPost_ViewNums` | 1826 | `&$article` | 浏览数计数接口（zb_system/api/post.php:55 也会触发） |

## 视图模板 Template（替换模板）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_ViewList_Template` | 1804 | `&$template` | 列表模板接口 |
| `Filter_Plugin_ViewPost_Template` | 1815 | `&$template` | 文章/页面模板接口 |
| `Filter_Plugin_ViewSearch_Template` | 1837 | `&$template` | 搜索结果模板接口 |
| `Filter_Plugin_ViewComments_Template` | 1848 | `&$template` | 评论列表模板接口 |
| `Filter_Plugin_ViewComment_Template` | 1859 | `&$template` | 单条评论模板接口 |
| `Filter_Plugin_ViewExternalLink_Template` | 1870 | `&$template` | 外链模板接口 |

## GetPost / GetList 结果

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_GetPost_Result` | 1628 | `&$post` | `GetPost()` 输出结果接口 |
| `Filter_Plugin_GetList_Result` | 1639 | `&$list` | `GetList()` 输出结果接口 |

## cmd.php / misc 入口（与前台相关的拦截点）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Cmd_Begin` | 864 | — | `cmd.php` 启动接口，可在这里拦截各种 action |
| `Filter_Plugin_Cmd_End` | 875 | — | `cmd.php` 结束接口 |
| `Filter_Plugin_Cmd_Ajax` | 886 | — | `cmd.php` 的 Ajax 命令专用接口，**插件需自行判断权限** |
| `Filter_Plugin_Cmd_Redirect` | 897 | `$url, $action` | `cmd.php` 最后跳转接口，用于修改 url 跳转值 |
| `Filter_Plugin_Misc_Begin` | 908 | `$type` | `c_system_misc.php` 启动接口，可拦截各种 type |

## 大数据（后台列表 / GetList 性能优化）

由 `c_system_admin.php` 在管理列表和 `GetList` 中触发，参数结构相同。

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_LargeData_Article` | 2801 | `&$select, &$where, &$order, &$limit, &$option` | 大数据文章接口 |
| `Filter_Plugin_LargeData_Page` | 2812 | 同上 | 大数据页面接口 |
| `Filter_Plugin_LargeData_Comment` | 2823 | 同上 | 大数据评论接口 |
| `Filter_Plugin_LargeData_CountTagArray` | 2834 | `$string, $plus, $articleid` | 大数据增减文章标签关联表 |
| `Filter_Plugin_LargeData_GetList` | 2845 | `&$select, &$where, &$order, &$limit, &$option` | 大数据 `GetList` 函数 |
