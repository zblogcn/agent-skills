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
    // 未启用时 include.php 不在引导列表里，插件函数和语言包都不存在
    require dirname(__FILE__) . '/include.php';
    $zbp->LoadLanguage('plugin', 'MyPlugin');
    $zbp->ShowError(48);
    die();
}

$zbp->LoadLanguage('plugin', 'MyPlugin');
$cfg = $zbp->Config('MyPlugin');

$blogtitle = $zbp->lang['MyPlugin']['settings'];

// 3. 处理表单提交（含 CSRF 校验）
if (count($_POST) > 0) {
    CheckIsRefererValid();
    $cfg->default_url = $_POST['default_url'];
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

## 常见实操坑

### `$cfg` 两个分支都要定义

管理页在插件未启用、配置为空或配置项缺失时也要能渲染提示，不能等到取 `$cfg->xxx` 时才出错。先判断状态，再决定配置来源：

```php
if ($zbp->CheckPlugin('MyPlugin')) {
    $cfg = $zbp->Config('MyPlugin');             // 已启用：激活函数已保证默认值
} else {
    require dirname(__FILE__) . '/include.php';  // 未启用：include.php 不在引导列表里，手动加载
    $zbp->LoadLanguage('plugin', 'MyPlugin');    // 语言包同样要自己加载
    $cfg = $zbp->Config('MyPlugin');
    $zbp->ShowError(48);
    die();
}
```

- 插件停用后 `include.php` 不会被引导加载，插件函数、类、语言包都不存在；配置值虽然还留在库里，但不能依赖激活函数补过默认值（插件从未启用或配置被清理时 `Config` 是空的）。
- 管理页被直接访问时，这个分支决定是显示「插件未启用」还是直接 fatal。两个分支都定义 `$cfg`，后续代码不再判断 `isset`。

### 页头页脚只能在文件顶层 require

`admin_header.php`、`admin_top.php`、`admin_left.php`、`admin_footer.php` 直接使用 `$zbp`、`$lang`、`$blogtitle` 等全局变量，文件内没有 `global` 声明（`admin_header.php` L4/L13、`admin_top.php` L6-18）。被 require 的文件使用包含处的作用域：

- 在文件顶层 require：看到的是全局变量，正常。
- 在函数或方法里 require：函数作用域里没有 `$zbp` 和 `$lang`，直接 `Undefined variable $zbp` 或页头空白；即使在函数里补 `global`，也容易漏掉 `$action`、`$bloghost` 等页头用到的变量。

管理页的引导、权限检查、表单处理都写在文件顶层。需要复用逻辑时抽成函数，但页头页脚的 require 留在顶层。

### 不要覆盖全局 `$lang`

管理页里写 `$lang = $zbp->lang['MyPlugin'];` 会替换全局语言树，随后 require 的后台页头取 `$lang['msg']`、`$lang['lang_bcp47']` 全部缺失，表现为满屏 `Undefined array key "msg"`。插件语言包用 `$zbp->lang['MyPlugin']['key']` 访问，规则见[代码质量要求「不要覆盖全局 lang」](zblogphp-code-quality.md#不要覆盖全局-lang)。

### 非启用态不要依赖激活函数

管理页用到的常量、函数、类、语言包都来自 `include.php`。插件未启用时这些全部不存在，所以管理页要：

- 顶部先 `if (!defined('ZBP_PATH')) { exit('Access denied'); }`；
- 需要插件函数时先手动 `require include.php`（只注册，不输出）；
- 语言包用 `$zbp->LoadLanguage('plugin', 'MyPlugin')` 自行加载，不假设激活函数执行过。

## 要点说明

- **权限**：`$action = 'root'` 对应 `plugin.xml` 中 `<level>1</level>` 的管理页要求；`CheckRights` 失败即 `ShowError(6)`。
- **插件状态**：必须 `$zbp->CheckPlugin('ID')`（`zb_system/function/lib/zblogphp.php` L2123-2126，检查 ID 是否在已启用列表中），防止未启用时直接访问管理页。
- **CSRF 两种模式**：
  - `CheckIsRefererValid()` + 表单隐藏域 `csrfToken`（`$zbp->GetCSRFToken()`）；
  - `$zbp->ValidToken(GetVars('token', 'POST'), 'ID')` + `$zbp->GetToken('ID')`。
- **token 按用户和 `$id` 隔离**：哈希含 `user->ID + Password + Status + $id`（zblogphp.php L3783）。后台页（管理员身份）生成的 token 不能给前台访客表单用，`GetCSRFToken()` 与 `GetCSRFToken('login')` 也互不通用；跨场景复用 token 是「明明带着 token 却校验失败」的常见原因。
- **后台布局**：`admin_header.php` + `admin_top.php` + `#divMain`（`.divHeader` / `.SubMenu` / `#divMain2`）+ `admin_footer.php`，最后调用 `RunTime()`。
- **导航高亮与图标**：`ActiveLeftMenu("aPluginMng")` 让左侧「插件管理」菜单高亮；`AddHeaderIcon()` 使用插件默认 `logo.png`。功能图标写法见[图标参考](zblogphp-admin-icons.md)。
- **子菜单**：挂接 `Filter_Plugin_Admin_LeftMenu`，在回调中用 `MakeLeftMenu()` 向左侧导航添加入口；完整写法见 [菜单参考](zblogphp-admin-menus.md)。
- **多页面插件**：path 只指定主入口；其余页面各自都是独立 PHP 文件，同样要做权限与 `CheckPlugin` 检查，页面间用相对链接互跳。
- **前台入口**：插件有前台页面时，配置页要显示「前台访问地址」区块，输出跟随站点 URL 模式的绝对地址和预览链接，见[插件前台页面「让用户找得到入口」](zblogphp-plugin-development-frontend-pages.md#让用户找得到入口)。
