# 后台页面结构与 zb_system/admin/ 文件职责

来源：`zb_system/admin/`（1.7.5.3540）。

## 文件清单

| 文件 | 职责 |
|---|---|
| `cmd.php?act=admin` / `admin/index.php` | 后台管理页统一入口，按 act 分发到 `Admin_*` 函数 |
| `admin/edit.php` | 文章/页面编辑器（含 Category/Tag/Template/Status 选择等） |
| `admin/category_edit.php` | 分类编辑 |
| `admin/member_edit.php` | 用户编辑 |
| `admin/tag_edit.php` | 标签编辑 |
| `admin/module_edit.php` | 模块编辑 |
| `admin/updatedb.php` | 数据库升级脚本 |
| `admin/admin_header.php` | 公共 HTML 头部（CSP、csrfToken meta、CSS/JS 引用） |
| `admin/admin_top.php` | 顶部导航栏 + 左侧菜单 aside 的开始标签 |
| `admin/admin_left.php` | 左侧菜单 UL，调用 `ResponseAdmin_LeftMenu()` |
| `admin/admin_footer.php` | 公共 HTML 尾部（结束标签） |

## 页面渲染流程

以 `admin/index.php`（L9-127）为例：

```php
require '../function/c_system_base.php';
require '../function/c_system_admin.php';   // 引入 Admin_* 函数、菜单构建函数

$zbp->Load();
$zbp->action = GetVars('act', 'GET');
$zbp->action = ($zbp->action == '') ? 'admin' : $zbp->action;

if (!$zbp->CheckRights($zbp->action)) {       // 权限校验
    $zbp->ShowError(6, __FILE__, __LINE__);
    die();
}

HookFilterPlugin('Filter_Plugin_Admin_Begin');

switch ($zbp->action) {                       // 按 act 分发
    case 'ArticleMng':
        $admin_function = 'Admin_ArticleMng';
        $blogtitle = $lang['msg']['article_manage'];
        break;
    // ... PageMng / CategoryMng / CommentMng / MemberMng / UploadMng / TagMng / PluginMng / ThemeMng / ModuleMng / SettingMng / admin
    default:
        foreach ($GLOBALS['hooks']['Filter_Plugin_Admin_Other_Action'] as $fpname => &$fpsignal) {
            $fpsignal = $fpname($zbp->action, $admin_function);
            if ($fpsignal == PLUGIN_EXITSIGNAL_RETURN || $fpsignal == PLUGIN_EXITSIGNAL_BREAK) {
                break;
            }
        }
        break;
}

require ZBP_PATH . 'zb_system/admin/admin_header.php';
require ZBP_PATH . 'zb_system/admin/admin_top.php';
?>
<div id="divMain">
    <?php $admin_function(); ?>               <!-- 实际内容 -->
</div>
<?php
require ZBP_PATH . 'zb_system/admin/admin_footer.php';
```

## Admin_* 页面函数

12 个 `Admin_*` 函数全部定义在 `zb_system/function/c_system_admin.php`：

| 函数 | 行号 | 对应 act |
|---|---|---|
| `Admin_SiteInfo` | L23 | `admin` |
| `Admin_ArticleMng` | L108 | `ArticleMng` |
| `Admin_PageMng` | L292 | `PageMng` |
| `Admin_CategoryMng` | L435 | `CategoryMng` |
| `Admin_CommentMng` | L580 | `CommentMng` |
| `Admin_MemberMng` | L770 | `MemberMng` |
| `Admin_UploadMng` | L918 | `UploadMng` |
| `Admin_TagMng` | L1046 | `TagMng` |
| `Admin_ThemeMng` | L1174 | `ThemeMng` |
| `Admin_ModuleMng` | L1234 | `ModuleMng` |
| `Admin_PluginMng` | L1447 | `PluginMng` |
| `Admin_SettingMng` | L1531 | `SettingMng` |

每个函数的结构极为一致：

1. `echo '<div class="divHeader">标题</div>'`
2. `echo '<div class="SubMenu">'`，循环 `Filter_Plugin_Admin_XxxMng_SubMenu` 钩子
3. `echo '<div id="divMain2">'`，表格/列表/表单
4. 每个列表页都有「批量操作下拉 + 提交」，`action` 指向 `cmd.php?act=PostBat`（或 CommentBat），请求方法 POST，由 cmd.php switch 硬编码处理

## 编辑页独立文件

编辑类页面不走 `admin/index.php` 的 switch，而是独立文件，由 cmd.php 的 `*Edt` action 重定向：

- `act=ArticleEdt` / `PageEdt` → `admin/edit.php`
- `act=CategoryEdt` → `admin/category_edit.php`
- `act=MemberEdt` / `MemberNew` → `admin/member_edit.php`
- `act=TagEdt` → `admin/tag_edit.php`
- `act=ModuleEdt` → `admin/module_edit.php`

这些编辑页同样 `require '../function/c_system_admin.php'`，所以菜单框架、头部、CSRF meta 等保持一致。

## CSP 与安全响应头

`admin_header.php`（L4-11）在 `ZC_ADDITIONAL_SECURITY` 开启时输出：

```php
header('X-Frame-Options: SAMEORIGIN');
header('X-XSS-Protection: 1; mode=block');
header('Content-Security-Policy: ' . GetBackendCSPHeader());
if ($zbp->isHttps) {
    header('Upgrade-Insecure-Requests: 1');
}
```

后台所有页面统一带 CSP，插件在编辑页内联 JS 时需用 `nonce` 或确保在 CSP 策略中。

## 插件新增自定义后台页

推荐做法：

```php
// 插件注册文件中的 Add_Filter_Plugin
Add_Filter_Plugin('Filter_Plugin_Admin_Other_Action', 'myplugin_admin_page');

function myplugin_admin_page($action, &$admin_function) {
    if ($action == 'MyPageMng') {
        $admin_function = 'myplugin_Admin_MyPageMng';  // 自定义输出函数
        return PLUGIN_EXITSIGNAL_RETURN;
    }
}

function myplugin_Admin_MyPageMng() {
    // 输出完整的 divHeader / SubMenu / divMain2 结构
    echo '<div class="divHeader">我的页面</div>';
    echo '<div class="SubMenu">';
    // ...
    echo '</div><div id="divMain2">...</div>';
}
```

然后在菜单注入 `cmd.php?act=MyPageMng` 的链接即可。如需要编辑页，可单独建 `admin/myplugin_edit.php` 文件，自定义 act 后重定向。
