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

## 分区配置：SubMenu 页签与 `?sec=` 白名单

配置项一多就必须分区，用后台原生的 `.SubMenu` 做页签，地址用 `?sec=` 区分。不要把十几个字段堆成一页长表单，也不要用纯 JavaScript 切换显示——那样刷新会丢当前页、地址也没法分享。

```php
$sections = array(
    'basic'    => '基础设置',
    'display'  => '显示设置',
    'advanced' => '高级设置',
);
$sec = (string) GetVars('sec', 'GET');
if (!isset($sections[$sec])) {
    $sec = 'basic';   // 缺失或非法一律回退默认分区
}
?>
<div id="divMain">
  <div class="divHeader"><?php echo $blogtitle; ?></div>
  <div class="SubMenu">
    <?php
    foreach ($sections as $key => $name) {
        $class = 'm-left' . ($key === $sec ? ' m-now' : '');
        echo MakeSubMenu($name, './main.php?sec=' . urlencode($key), $class);
    }
    ?>
  </div>
  <div id="divMain2">
    <?php require __DIR__ . '/sec/' . $sec . '.php'; ?>
  </div>
</div>
```

每个分区一个独立文件（如 `sec/basic.php`、`sec/display.php`），文件内自带完整、闭合的表单片段；表单里带隐藏的当前分区：

```html
<form method="post" action="./main.php">
  <input type="hidden" name="csrfToken" value="<?php echo $zbp->GetCSRFToken(); ?>" />
  <input type="hidden" name="sec" value="<?php echo $sec; ?>" />
  <!-- 本分区字段 -->
</form>
```

保存时只处理提交上来的那一个分区，保存后重定向回同一分区：

```php
if (count($_POST) > 0) {
    CheckIsRefererValid();
    $postSec = (string) GetVars('sec', 'POST');
    if (!isset($sections[$postSec])) {
        Redirect('./main.php');
    }

    $cfg = $zbp->Config('MyPlugin');
    switch ($postSec) {
        case 'basic':
            $cfg->logo = $_POST['logo'];
            break;
        case 'display':
            $cfg->layout = $_POST['layout'];
            break;
        case 'advanced':
            $cfg->cache_ttl = (int) $_POST['cache_ttl'];
            break;
    }
    $zbp->SaveConfig('MyPlugin');
    $zbp->SetHint('good');
    Redirect('./main.php?sec=' . urlencode($postSec));
}
```

要点：

- **`.SubMenu` 默认是隐藏的**（`admin2.css` 里 `display: none`），前台 JS 只在里面找到 `span` 时才显示（`c_admin_js_add.php` L262-263）。用 `MakeSubMenu()` 生成 `<span class="m-left">`，不要手写裸 `<a>`，否则页签不出现。
- **当前页签的类名是 `m-now`**，加在 `m-left` 后面（`admin2.css` L299 负责高亮），不是 `current`。
- `?sec=` 只做白名单分派：未知值回退默认分区，**绝不能**把 `$_GET['sec']` 直接拼进 `include`/`require` 路径。
- 分区名从语言包取，不要写死中文；三份语言包都要有对应键。
- 保存后跳回 `?sec=` 当前分区，不要跳回默认页；链接里还有其他参数（如 `?id=1`）时要一并保留。
- 主题配置页（`theme.xml` 的 `<path>` 指向的文件）同样按这套分区和页签处理，不要因为主题只有几个选项就堆成长表单。

## 图片/URL 字段：行内上传与预览

图片、Logo、横幅、附件地址这类字段必须**行内集成**：输入框旁边就是上传按钮、已配置时的缩略图预览和清除按钮。不要把上传做成页面下方的独立区块，也不要让用户先上传到别处再回来粘贴 URL——这种拆分会直接打断配置流程。

结构上分两处：

- 输入框、上传按钮、预览、清除按钮都在**主配置表单内**；
- 隐藏的 `<form>` 带 `enctype="multipart/form-data"`，放在**主表单之外**（表单不能嵌套），用按钮 `.click()` 触发文件选择，`onchange` 直接提交。

```html
<!-- 主配置表单内 -->
<div class="myplugin-field">
  <label for="logo">Logo</label>
  <input type="text" name="logo" id="logo" value="<?php echo htmlspecialchars($cfg->logo); ?>" />
  <button type="button" class="button" id="logo-upload">上传</button>
  <button type="button" class="button" id="logo-clear">清除</button>
  <span id="logo-preview">
    <?php if ($cfg->logo) { ?>
      <img src="<?php echo htmlspecialchars($cfg->logo); ?>" alt="当前 Logo" width="64" height="64" />
    <?php } ?>
  </span>
</div>

<!-- 主表单之外：隐藏的上传表单 -->
<form id="logo-form" method="post" enctype="multipart/form-data" action="./main.php" style="display:none">
  <input type="hidden" name="csrfToken" value="<?php echo $zbp->GetCSRFToken(); ?>" />
  <input type="file" name="logo_file" id="logo-file" accept="image/*" onchange="this.form.submit()" />
</form>
<script>
  document.getElementById('logo-upload').addEventListener('click', function () {
    document.getElementById('logo-file').click();
  });
  document.getElementById('logo-clear').addEventListener('click', function () {
    document.getElementById('logo').value = '';
    document.getElementById('logo-preview').innerHTML = '';
  });
</script>
```

服务端在同一个管理页里处理上传，保存后重定向回本页，刷新时预览自然出现：

```php
if (isset($_FILES['logo_file']) && $_FILES['logo_file']['error'] === 0) {
    CheckIsRefererValid();

    $upload = new Upload();
    $upload->Name = $_FILES['logo_file']['name'];
    $upload->SourceName = $_FILES['logo_file']['name'];
    $upload->MimeType = $_FILES['logo_file']['type'];
    $upload->Size = $_FILES['logo_file']['size'];
    $upload->AuthorID = $zbp->user->ID;

    if (!$upload->CheckExtName('jpg|jpeg|png|gif|webp')) {
        $zbp->ShowError(26);
    }
    if (!$upload->CheckSize()) {
        $zbp->ShowError(27);
    }
    // 重命名，避免同名覆盖
    $upload->Name = date('YmdHis') . mt_rand(1000, 9999) . '.' . GetFileExt($upload->Name);
    $upload->SaveFile($_FILES['logo_file']['tmp_name']);
    $upload->Save();

    $zbp->Config('MyPlugin')->logo = $upload->Url;
    $zbp->SaveConfig('MyPlugin');
    $zbp->SetHint('good');
    Redirect('./main.php');
}

if (count($_POST) > 0) {
    CheckIsRefererValid();
    $zbp->Config('MyPlugin')->logo = $_POST['logo'];
    $zbp->SaveConfig('MyPlugin');
    Redirect('./main.php');
}
```

要点：

- **先处理上传再处理普通保存**。上传请求同样满足 `count($_POST) > 0`，顺序颠倒会把输入框里的空值写回去，冲掉刚上传的地址。
- 不要直接把表单提交到 `cmd.php?act=UploadPst`：它处理完会 `Redirect` 到上传管理页，插件拿不回文件 URL。在插件自己的页面里用 `Upload` 类处理。
- `CheckExtName('jpg|jpeg|png|gif|webp')` 用白名单限制图片类型；`CheckSize()` 受后台「上传文件大小」限制。两项都要在 `SaveFile()` 前检查，`SaveFile()` 本身不报错。
- `$upload->Url` 是 `$zbp->host` 开头的**绝对 URL**，可直接存进配置和侧栏模块。
- 预览图片的 URL 输出必须 `htmlspecialchars()`，防止配置值里的引号破坏属性。
- 清除按钮先只清空输入框和预览，随「保存」落盘；如果希望点清除立即生效，可在清除后自动提交一次保存。清除只解除配置引用，不会删除磁盘上的文件；确需彻底删除时按 `Upload` ID 取对象后 `DelFile()` + `Del()`。
- **前台入口**：插件有前台页面时，配置页要显示「前台访问地址」区块，输出跟随站点 URL 模式的绝对地址和预览链接，见[插件前台页面「让用户找得到入口」](zblogphp-plugin-development-frontend-pages.md#让用户找得到入口)。
