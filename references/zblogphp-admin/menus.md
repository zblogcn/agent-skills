# 左侧/顶部菜单钩子与子菜单注入

来源：`zb_system/function/c_system_admin_function.php`（1.7.5.3540）。

菜单图标的引入方式与类名见 [icons.md](icons.md)。

## 左侧菜单：`Filter_Plugin_Admin_LeftMenu`

左侧菜单由 `ResponseAdmin_LeftMenu()` 输出（L189-219），**不是固定 HTML，而是先构造数组再让钩子修改**。注册钩子：

```php
Add_Filter_Plugin('Filter_Plugin_Admin_LeftMenu', 'myplugin_leftmenu');

function myplugin_leftmenu(&$leftmenus) {
    $leftmenus['myplugin_nav'] = MakeLeftMenu(
        'MyAct',                        // 所需 action（权限不够时自动返回空字符串，不显示）
        '我的插件',
        $GLOBALS['zbp']->cmdurl . '?act=MyPageMng',
        'nav_myplugin',
        'aMyPlugin',
        '',                             // 自定义图片 URL（一般用图标类代替）
        'icon-star-fill'                // Z-Blog 自带 icon 字体类名
    );
}
```

### `MakeLeftMenu` 签名

```php
function MakeLeftMenu(
    $requireAction,    // 字符串 action 名
    $strName,          // 显示文本
    $strUrl,           // 链接
    $strLiId,          // <li id="...">
    $strAId,           // <a id="...">
    $strImgUrl,        // 自定义背景图（旧版用，新版留空即可）
    $strIconClass = '' // icon 字体类名，优先级高于 $strImgUrl
)
```

返回值是 `<li>...</li>` 字符串。权限不足时返回空字符串（`''`），数组 push 后 foreach 输出时自动消失。

左侧默认顺序（在钩子之前已写入数组）：

1. nav_new（新建文章）
2. nav_article（文章管理）
3. nav_page（页面管理）
4. split（分割线 `<li class='split'><hr/></li>`）
5. nav_category（分类管理）
6. nav_tags（标签管理）
7. nav_comment1（评论管理）
8. nav_upload（附件管理）
9. nav_member（用户管理）
10. split
11. nav_theme（主题管理）
12. nav_module（模块管理）
13. nav_plugin（插件管理）

## 顶部菜单：`Filter_Plugin_Admin_TopMenu`

`ResponseAdmin_TopMenu()`（L224-246）同样先构造 `$topmenus` 数组，再执行钩子：

```php
Add_Filter_Plugin('Filter_Plugin_Admin_TopMenu', 'myplugin_topmenu');

function myplugin_topmenu(&$topmenus) {
    $topmenus[] = MakeTopMenu(
        'admin',                          // 所需 action
        '帮助',
        'https://docs.zblogcn.com/',
        '_blank',
        '',                               // strLiId（空则自动编号 topmenuN）
        'icon-question-circle-fill'
    );
}
```

### `MakeTopMenu` 签名

```php
function MakeTopMenu(
    $requireAction,
    $strName,
    $strUrl,
    $strTarget,
    $strLiId,
    $strIconClass = ''
)
```

默认顶部菜单只有「仪表盘(admin)」和「网站设置(SettingMng)」，之后钩子注入，最后是「官方网站」外部链接。

## 管理页子菜单：`*Mng_SubMenu`

9 个管理页在 `c_system_admin.php` 的每个 `Admin_*Mng` 函数开头都输出 `.SubMenu` div，并遍历对应的 SubMenu 钩子：

| 管理页 | 钩子名 |
|---|---|
| 文章管理 | `Filter_Plugin_Admin_ArticleMng_SubMenu` |
| 页面管理 | `Filter_Plugin_Admin_PageMng_SubMenu` |
| 分类管理 | `Filter_Plugin_Admin_CategoryMng_SubMenu` |
| 评论管理 | `Filter_Plugin_Admin_CommentMng_SubMenu` |
| 用户管理 | `Filter_Plugin_Admin_MemberMng_SubMenu` |
| 附件管理 | `Filter_Plugin_Admin_UploadMng_SubMenu` |
| 标签管理 | `Filter_Plugin_Admin_TagMng_SubMenu` |
| 插件管理 | `Filter_Plugin_Admin_PluginMng_SubMenu` |
| 主题管理 | `Filter_Plugin_Admin_ThemeMng_SubMenu` |
| 模块管理 | `Filter_Plugin_Admin_ModuleMng_SubMenu` |
| 设置管理 | `Filter_Plugin_Admin_SettingMng_SubMenu` |

回调签名：无参数，**直接 `echo` 菜单项 HTML**。用 `MakeSubMenu` 辅助：

```php
Add_Filter_Plugin('Filter_Plugin_Admin_PluginMng_SubMenu', 'myplugin_submenu');

function myplugin_submenu() {
    echo MakeSubMenu('配置', $GLOBALS['zbp']->cmdurl . '?act=MyPageMng', 'm-left', '', '', '', 'icon-gear-fill');
}
```

### `MakeSubMenu` 签名

```php
function MakeSubMenu(
    $strName,
    $strUrl,
    $strClass = 'm-left',   // 或 'm-right'
    $strTarget = '',
    $strId = '',
    $strTitle = '',
    $strIconClass = ''
)
```

内置子菜单由 `c_system_admin_function.php` 里的 `Include_Admin_Add*` 函数输出（如新建文章/新建分类/清除缩略图缓存等），这些函数本身也是通过上述 SubMenu 钩子挂载的，所以插件子菜单与内置子菜单并列。

## 编辑页子菜单

4 个编辑页在 `admin/edit.php`、`admin/category_edit.php`、`admin/tag_edit.php`、`admin/module_edit.php`、`admin/member_edit.php` 中各自触发：

- `Filter_Plugin_Edit_SubMenu`
- `Filter_Plugin_Category_Edit_SubMenu`
- `Filter_Plugin_Tag_Edit_SubMenu`
- `Filter_Plugin_Module_Edit_SubMenu`
- `Filter_Plugin_Member_Edit_SubMenu`

用法与 `*Mng_SubMenu` 完全一致：直接 echo `MakeSubMenu(...)`。

## 菜单 URL 必须带安全 Token

所有链接到 `cmd.php?act=XXX` 的 URL 应使用 `BuildSafeCmdURL('act=XXX&...')`（c_system_common.php L2139），它会自动附加 `&csrfToken=...`。否则用户打开链接时如果后台会话已过期，会被 CSRF 拦截（ShowError 5）。
