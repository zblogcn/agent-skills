# 后台管理类钩子

涵盖登录页 / 后台首尾的 Header/Footer、左右侧导航、各管理页（文章、页面、分类、评论、会员、附件、标签、插件、主题、模块、设置）的 SubMenu、Core、Table 系列钩子，以及各编辑页（Edit_*）和 OutputOptionItemsOf* 系列。所有钩子集中注册于 `zb_system/function/c_system_plugin.php`（行号即该文件行号）。

## 登录 / 后台框架

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Login_Header` | 922 | — | Login.php 首页 header 接口 |
| `Filter_Plugin_Other_Header` | 933 | — | 其它页的 header 接口（zb_system/defend/error.php:38 等处触发） |
| `Filter_Plugin_Admin_Begin` | 944 | — | 后台管理页启动接口，可拦截后台管理请求实现自己的管理 |
| `Filter_Plugin_Admin_Other_Action` | 955 | — | 后台管理页拦截 Action，实现自己的 Action（zb_system/admin/index.php 内触发） |
| `Filter_Plugin_Admin_End` | 966 | — | 后台管理页终结接口 |
| `Filter_Plugin_Admin_Header` | 977 | — | 后台首页 header 接口 |
| `Filter_Plugin_Admin_Hint` | 988 | — | 后台首页 hint 接口（常用于输出提示条） |
| `Filter_Plugin_Admin_Footer` | 999 | — | 后台首页 footer 接口 |

## 后台导航

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Admin_LeftMenu` | 1010 | `&$leftmenus` | 后台左侧栏接口，插件用 `MakeLeftMenu()` 生成菜单项并 `$leftmenus['nav_xxx'] = ...` 注入 |
| `Filter_Plugin_Admin_TopMenu` | 1021 | `&$topmenus` | 后台顶部导航栏接口 |

## 各管理页 SubMenu（页头小工具条）

| 钩子 | 行号 | 说明 |
| --- | --- | --- |
| `Filter_Plugin_Admin_SiteInfo_SubMenu` | 1032 | 后台首页 SubMenu |
| `Filter_Plugin_Admin_ArticleMng_SubMenu` | 1043 | 文章管理 |
| `Filter_Plugin_Admin_PageMng_SubMenu` | 1054 | 页面管理 |
| `Filter_Plugin_Admin_CategoryMng_SubMenu` | 1065 | 分类管理 |
| `Filter_Plugin_Admin_CommentMng_SubMenu` | 1076 | 评论管理 |
| `Filter_Plugin_Admin_MemberMng_SubMenu` | 1087 | 用户管理 |
| `Filter_Plugin_Admin_UploadMng_SubMenu` | 1098 | 附件管理 |
| `Filter_Plugin_Admin_TagMng_SubMenu` | 1109 | 标签管理 |
| `Filter_Plugin_Admin_PluginMng_SubMenu` | 1120 | 插件管理 |
| `Filter_Plugin_Admin_ThemeMng_SubMenu` | 1131 | 主题管理 |
| `Filter_Plugin_Admin_ModuleMng_SubMenu` | 1142 | 模块管理 |
| `Filter_Plugin_Admin_SettingMng_SubMenu` | 1153 | 设置管理 |

参数：均无参数。常用于 `echo` 输出额外链接按钮，或追加 JS。

## 各管理页 Core（1.7 新加入，可干预 SQL 查询）

参数统一为 `$s, $w, $or, $l, $op`（select / where / order / limit / option）。

| 钩子 | 行号 | 说明 |
| --- | --- | --- |
| `Filter_Plugin_Admin_ArticleMng_Core` | 1164 | 文章管理页核心接口 |
| `Filter_Plugin_Admin_PageMng_Core` | 1175 | 页面管理页核心接口（源码注释写为"文章管理页"，实为页面） |
| `Filter_Plugin_Admin_CommentMng_Core` | 1186 | 评论管理页核心接口 |
| `Filter_Plugin_Admin_CategoryMng_Core` | 1197 | 分类管理页核心接口 |
| `Filter_Plugin_Admin_MemberMng_Core` | 1208 | 会员管理页核心接口 |
| `Filter_Plugin_Admin_UploadMng_Core` | 1219 | 附件管理页核心接口（源码注释误写为"会员管理页"） |
| `Filter_Plugin_Admin_TagMng_Core` | 1230 | 标签管理页核心接口（源码注释误写为"会员管理页"） |

## 各管理页 Table（1.5.1 加入，可干预列表行/列）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Admin_ArticleMng_Table` | 1296 | `&$article, &$tabletds, &$tableths` | 文章管理页表处理 |
| `Filter_Plugin_Admin_PageMng_Table` | 1307 | `&$article, &$tabletds, &$tableths` | 页面管理页表处理 |
| `Filter_Plugin_Admin_CategoryMng_Table` | 1318 | `&$category, &$tabletds, &$tableths` | 分类管理页表处理 |
| `Filter_Plugin_Admin_CommentMng_Table` | 1329 | `&$cmt, &$tabletds, &$tableths, $article` | 评论管理页表处理 |
| `Filter_Plugin_Admin_MemberMng_Table` | 1340 | `&$member, &$tabletds, &$tableths` | 会员管理页表处理 |
| `Filter_Plugin_Admin_UploadMng_Table` | 1351 | `&$upload, &$tabletds, &$tableths` | 附件管理页表处理 |
| `Filter_Plugin_Admin_TagMng_Table` | 1362 | `&$tag, &$tabletds, &$tableths` | 标签管理页表处理 |

## 编辑页 SubMenu 与 Response

### SubMenu（1.5.1 加入，无参数）

| 钩子 | 行号 | 说明 |
| --- | --- | --- |
| `Filter_Plugin_Edit_SubMenu` | 1241 | 文章/页面编辑页菜单 |
| `Filter_Plugin_Tag_Edit_SubMenu` | 1252 | 标签编辑页菜单 |
| `Filter_Plugin_Module_Edit_SubMenu` | 1263 | 模块编辑页菜单 |
| `Filter_Plugin_Member_Edit_SubMenu` | 1274 | 用户编辑页菜单 |
| `Filter_Plugin_Category_Edit_SubMenu` | 1285 | 分类编辑页菜单 |

### 文章/页面编辑页（5 个 Response 槽位）

| 钩子 | 行号 | 说明 |
| --- | --- | --- |
| `Filter_Plugin_Edit_Begin` | 1373 | 文章页面编辑页开始 |
| `Filter_Plugin_Edit_End` | 1384 | 文章页面编辑页结束 |
| `Filter_Plugin_Edit_Response` | 1395 | 1 号输出接口 |
| `Filter_Plugin_Edit_Response2` | 1406 | 2 号输出接口 |
| `Filter_Plugin_Edit_Response3` | 1439 | 3 号输出接口 |
| `Filter_Plugin_Edit_Response4` | 1417 | 4 号输出接口 |
| `Filter_Plugin_Edit_Response5` | 1428 | 5 号输出接口 |

### 其它编辑页 Response

| 钩子 | 行号 | 说明 |
| --- | --- | --- |
| `Filter_Plugin_Category_Edit_Response` | 1450 | 分类编辑页输出接口 |
| `Filter_Plugin_Tag_Edit_Response` | 1461 | 标签编辑页输出接口 |
| `Filter_Plugin_Member_Edit_Response` | 1472 | 会员编辑页输出接口 |
| `Filter_Plugin_Module_Edit_Response` | 1483 | 模块编辑页输出接口 |

## 后台 JS 注入

| 钩子 | 行号 | 说明 |
| --- | --- | --- |
| `Filter_Plugin_Admin_Js_Add` | 1494 | `c_admin_js_add.php` 脚本页接口，可输出 JS（zb_system/script/c_admin_js_add.php 触发） |

## OutputOptionItemsOf* 下拉选项

这些钩子在后台函数中渲染 `<option>` 时触发。

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_OutputOptionItemsOfMemberLevel` | 1505 | `$default, $tz` | `OutputOptionItemsOfMemberLevel()` 内 |
| `Filter_Plugin_OutputOptionItemsOfMember_Begin` | 1516 | `$default, $posttype, $action, $tz` | `OutputOptionItemsOfMember()` 起始处 |
| `Filter_Plugin_OutputOptionItemsOfMember` | 1560 | `$default, $tz` | `OutputOptionItemsOfMember()` 内 |
| `Filter_Plugin_OutputOptionItemsOfCategories` | 1527 | `$default, $tz` | `OutputOptionItemsOfCategories()` 内 |
| `Filter_Plugin_OutputOptionItemsOfPostStatus` | 1538 | `$default, $tz` | `OutputOptionItemsOfPostStatus()` 内 |
| `Filter_Plugin_OutputOptionItemsOfIsTop` | 1549 | `$default, $tz` | `OutputOptionItemsOfIsTop()` 内 |
| `Filter_Plugin_OutputOptionItemsOfTemplate` | 1571 | `$default, $tz` | `OutputOptionItemsOfTemplate()` 内 |
| `Filter_Plugin_OutputOptionItemsOfCommon` | 1582 | `$default, $array, $name` | 通用型下拉，含 `$name` 区分调用方 |
