# 插件后台管理页（path 字段与 main.php/setting.php）

## path 字段的作用

`plugin.xml` 的 `<path>` 指定插件的后台管理入口文件（相对插件目录），如 `<path>main.php</path>` 或 `<path>setting.php</path>`。

- `path` 非空则后台插件列表显示「管理」入口；
- 管理链接为 `{host}zb_users/plugin/{ID}/{path}`。

## 管理页标准骨架

在应用副本中补充以下管理页逻辑；示例也供模板缺失时回退。`MyPlugin`、配置项和重定向文件名按目标应用调整：

```php
<?php
require '../../../zb_system/function/c_system_base.php';    // 引导核心
require '../../../zb_system/function/c_system_admin.php';   // 后台函数

$zbp->Load();

// 1. 权限检查：root 仅管理员；权限不足报错误 6
$action = 'root';
if (!$zbp->CheckRights($action)) {
    $zbp->ShowError(6);
    die();
}

// 2. 确认本插件处于启用状态；否则报错误 48
if (!$zbp->CheckPlugin('MyPlugin')) {
    $zbp->ShowError(48);
    die();
}

$blogtitle = $zbp->lang['MyPlugin']['settings'];

// 3. 处理表单提交（含 CSRF 校验）
if (count($_POST) > 0) {
    CheckIsRefererValid();
    $zbp->Config('MyPlugin')->default_url = $_POST['default_url'];
    $zbp->SaveConfig('MyPlugin');
    $zbp->SetHint('good');
    Redirect('./main.php');
}

// 4. 输出后台页头/页脚
require $blogpath . 'zb_system/admin/admin_header.php';
require $blogpath . 'zb_system/admin/admin_top.php';
?>
<div id="divMain">
  <div class="divHeader"><?php echo $blogtitle; ?></div>
  <div class="SubMenu"></div>
  <div id="divMain2">
    <form id="edit" name="edit" method="post" action="#">
      <input type="hidden" name="csrfToken" value="<?php echo $zbp->GetCSRFToken() ?>">
      <!-- 表单字段 -->
      <input type="submit" class="button" value="<?php echo $lang['msg']['submit']; ?>" />
    </form>
    <script type="text/javascript">ActiveLeftMenu("aPluginMng");</script>
    <script type="text/javascript">AddHeaderIcon("<?php echo $bloghost . 'zb_users/plugin/MyPlugin/logo.png'; ?>");</script>
  </div>
</div>
<?php
require $blogpath . 'zb_system/admin/admin_footer.php';
RunTime();
?>
```

## 要点说明

- **权限**：`$action = 'root'` 对应 `plugin.xml` 中 `<level>1</level>` 的管理页要求；`CheckRights` 失败即 `ShowError(6)`。
- **插件状态**：必须 `$zbp->CheckPlugin('ID')`（`zb_system/function/lib/zblogphp.php` L2123-2126，检查 ID 是否在已启用列表中），防止未启用时直接访问管理页。
- **CSRF 两种模式**：
  - `CheckIsRefererValid()` + 表单隐藏域 `csrfToken`（`$zbp->GetCSRFToken()`）；
  - `$zbp->ValidToken(GetVars('token', 'POST'), 'ID')` + `$zbp->GetToken('ID')`。
- **后台布局**：`admin_header.php` + `admin_top.php` + `#divMain`（`.divHeader` / `.SubMenu` / `#divMain2`）+ `admin_footer.php`，最后调用 `RunTime()`。
- **导航高亮与图标**：`ActiveLeftMenu("aPluginMng")` 让左侧「插件管理」菜单高亮；`AddHeaderIcon()` 使用插件默认 `logo.png`。功能图标写法见[图标参考](../zblogphp-admin/icons.md)。
- **子菜单**：挂接 `Filter_Plugin_Admin_LeftMenu`，在回调中用 `MakeLeftMenu()` 向左侧导航添加入口；完整写法见 [菜单参考](../zblogphp-admin/menus.md)。
- **多页面插件**：path 只指定主入口；其余页面各自都是独立 PHP 文件，同样要做权限与 `CheckPlugin` 检查，页面间用相对链接互跳。
