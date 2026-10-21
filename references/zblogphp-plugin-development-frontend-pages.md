# 插件前台页面：路由、登录注册与入口

插件需要独立前台页面（用户中心、投稿、订单、列表页等）时，Z-BlogPHP 没有现成的前台控制器：页面路由、登录态和注册流程都要自己接。本篇给出可复用的实现方式，页面本身按主题模板或独立 HTML 输出，质量要求与主题一致。

## 页面路由：Filter_Plugin_ViewAuto_Begin

不能把 `index.php/xxx` 这类地址当成固定入口。站点有动态（`ACTIVE`）和伪静态（`REWRITE`）两种 URL 模式（`$zbp->option['ZC_STATIC_MODE']`）；伪静态模式下 `.htaccess` 会把不存在的路径统一重写到 `index.php`（`UrlRule::Make_htaccess()`，`urlrule.php` L742-755），系统再逐条匹配 `$zbp->routes`。

把插件页面挂在 `Filter_Plugin_ViewAuto_Begin` 上，在系统路由匹配前接管请求：

```php
// include.php 激活函数里
Add_Filter_Plugin('Filter_Plugin_ViewAuto_Begin', 'MyPlugin_Route');

function MyPlugin_Route($original_url, $url)
{
    global $zbp;

    if ($zbp->option['ZC_STATIC_MODE'] === 'REWRITE') {
        $path = trim($url, '/');                        // 已去掉 cookiespath 与查询串
        if ($path !== 'myplugin' && strpos($path, 'myplugin/') !== 0) {
            return;
        }
    } elseif (!isset($_GET['myplugin'])) {               // 动态模式用查询参数
        return;
    }

    // 终止后续系统路由匹配，页面自行输出
    SetPluginSignal('Filter_Plugin_ViewAuto_Begin', 'MyPlugin_Route', PLUGIN_EXITSIGNAL_RETURN);
    require dirname(__FILE__) . '/front.php';
    exit;
}
```

要点：

- 回调参数是 `($original_url, $url)`（`c_system_route.php` L36-37）。`$url` 已去掉 `cookiespath` 和查询串，`$original_url` 保留完整地址；需要查询参数时从 `$_GET` 取。
- `SetPluginSignal(...)` 把本挂载设为 `PLUGIN_EXITSIGNAL_RETURN`，`ViewAuto()` 收到后立即返回，不再匹配系统路由，也不会把插件页面当成普通列表或 404。
- `ViewAuto()` 的返回值没有调用方接收（`ViewIndex()` 直接调用后继续执行），页面必须在回调里输出完并 `exit`，否则后续 `Index_End` 和收尾逻辑会继续跑。
- `front.php` 顶部写 `if (!defined('ZBP_PATH')) { exit('Access denied'); }`。它只允许被路由回调包含，不能被直接访问。
- 一个插件只注册一个路由回调，在回调里按路径分发到不同页面，避免多个插件争抢同一个钩子。

## URL 生成必须跟随站点模式

所有前台地址都走同一个生成函数，不要在各处硬编码：

```php
function MyPlugin_FrontUrl($args = array())
{
    global $zbp;
    if ($zbp->option['ZC_STATIC_MODE'] === 'REWRITE') {
        $url = $zbp->host . 'myplugin/';
        if ($args) {
            $url .= '?' . http_build_query($args);
        }
        return $url;
    }

    $args = array('myplugin' => '1') + $args;
    return $zbp->host . 'index.php?' . http_build_query($args);
}
```

- 模板导航、后台配置页展示的「前台访问地址」、侧栏模块内容都调用它。
- 站内链接用绝对地址，避免页面层级变化后相对路径失效；伪静态和子目录部署都能用。
- 不要写 `index.php/myplugin` 这种路径式地址，动态模式应使用查询参数。

旧地址需要保留时做 301：

```php
if (isset($_GET['old_myplugin'])) {
    Redirect301(MyPlugin_FrontUrl());
    exit;   // Redirect301 只发 Location 头，不结束请求
}
```

`Redirect301()`（`c_system_common.php` L358-364）内部只有 `SetHttpStatusCode(301)` 和 `header()`，不会 `die`；不 `exit` 的话页面会继续输出，跳转等于没生效。

## 停用态：先加载语言包，再判断

插件停用时 `include.php` 不加载，激活函数和语言包都不会执行。插件自己的前台页如果直接取 `$zbp->lang['MyPlugin'][...]`，拿到的是不存在的键：调试模式下变成错误页，关闭调试则输出 `Undefined array key` 和空白。

```php
$zbp->LoadLanguage('plugin', 'MyPlugin');    // 任何用到插件语言包的入口先加载
if (!$zbp->CheckPlugin('MyPlugin')) {
    Http404();
    return;
}
```

- `CheckPlugin($name)` 只检查 ID 是否在 `$zbp->activedapps`（zblogphp.php L2123-2126），不会加载任何文件。
- 语言包加载是幂等的，可以反复调用，不要假设激活函数执行过。
- 主题的独立入口同理：先 `$zbp->LoadLanguage('theme', 'mytheme')`。
- 停用态应该得到 404 或提示页，不能是 500；本地实测时专门覆盖这个场景，见[本地开发与实测](zblogphp-local-testing.md#停用态与子进程隔离实测)。

## 前台登录

Z-BlogPHP 只有后台登录入口。自建前台登录页要按系统 `VerifyLogin()` 的顺序完整走一遍（`c_system_event.php` L20-55）：

```php
$zbp->LoadLanguage('plugin', 'MyPlugin');

// 1. CSRF：系统登录用 login 命名空间、分钟级有效期
if ($zbp->option['ZC_LOGIN_CSRFCHECK_ENABLE']) {
    $zbp->csrfExpirationMinute = 5;
    if (!$zbp->VerifyCSRFToken(GetVars('csrfToken', 'POST'), 'login', 'minute')) {
        $zbp->ShowError(5);
    }
}

// 2. 验证码：与系统同样的命名空间和有效期
if ($zbp->option['ZC_LOGIN_VERIFY_ENABLE'] && !$zbp->CheckValidCode(GetVars('verify', 'POST'), 'login', 'minute')) {
    $zbp->ShowError(38);
}

// 3. 校验用户名与明文密码
$member = null;
if (!$zbp->Verify_Original(trim(GetVars('username', 'POST')), trim(GetVars('password', 'POST')), $member)) {
    $zbp->ShowError(8);
}

// 4. 写入登录态与 Cookie
$zbp->user = $member;
$zbp->islogin = true;
SetLoginCookie($member, time() + 3600 * 24 * 30);

// 5. 手动触发系统登录成功钩子
foreach ($GLOBALS['hooks']['Filter_Plugin_VerifyLogin_Succeed'] as $fpname => &$fpsignal) {
    $fpname();
}
```

- `Verify_Original($name, $plain, &$member)` 内部先 `md5($plain)` 再 `Verify_MD5()`，最后与 `$member->Password` 比对（zblogphp.php L1682-1693、L1660-1671）。
- `SetLoginCookie($member, $expire)` 调用 `GenerateUserToken()` → `CreateWebToken()` 生成 token，并写 `username_<crc32b(guid)>`、`token_<crc32b(guid)>`、`addinfo<cookiespath>` 三个 Cookie（`c_system_event.php` L81-97）。自己 `setcookie` 很容易漏掉 guid 哈希和 token 算法，直接调用它。
- `$zbp->CheckRights()` 依赖 `$zbp->user`，先赋值 `$zbp->user` 再做权限判断。
- `Filter_Plugin_VerifyLogin_Succeed` 由系统 `VerifyLogin()` 触发（L50-52）。自建登录不经过它，必须自己循环触发，否则积分、签到、登录日志等依赖该钩子的功能全部静默失效。
- 失败分支同样要触发 `Filter_Plugin_VerifyLogin_Failed`（L56-63），并处理信号量。

## 前台注册

Z-BlogPHP 没有前台注册，用户只能后台创建。插件要开放注册，得自己收集字段并调用模型保存：

```php
$name = trim(GetVars('username', 'POST'));

// 1. 用户名格式与查重
if (!CheckRegExp($name, '[username]') || $zbp->GetMemberByName($name)->ID > 0) {
    $zbp->ShowError(62);
}

// 2. 密码格式：长度上下限来自系统选项
$password = trim(GetVars('password', 'POST'));
if (strlen($password) < $zbp->option['ZC_PASSWORD_MIN'] || strlen($password) > $zbp->option['ZC_PASSWORD_MAX']) {
    $zbp->ShowError(54);
}

// 3. 建用户：Guid 先有，密码按 Guid 二次散列
$member = new Member();
$member->Guid = GetGuid();
$member->Name = $name;
$member->Password = Member::GetPassWordByGuid($password, $member->Guid);
$member->Alias = $name;
$member->Email = trim(GetVars('email', 'POST'));
$member->Level = ZC_MEMBER_LEVER_LOWEST;
$member->Status = 0;
$member->IP = GetGuestIP();
$member->Save();
```

- `Member::GetPassWordByGuid($plain, $guid)` = `md5(md5($plain) . $guid)`（`base/member.php` L232-235）；直接存 `md5($password)` 会导致后续登录永远失败。
- `Guid` 不会在 `new Member()` 时自动生成，注册流程要显式 `$member->Guid = GetGuid();`，系统建用户也是这样（`c_system_event.php` L1673-1675）。
- 用户名、密码的格式校验用系统函数和选项（`CheckRegExp`、`ZC_PASSWORD_MIN` / `ZC_PASSWORD_MAX`），不要自造规则。
- 注册后是否自动登录由插件决定；自动登录就复用上一节的第 4、5 步。

## 让用户找得到入口

前台页面做完后，三个入口必须同时接上：

1. **模板导航**：不要改数据库里的 `navbar` 模块内容，也不依赖后台手工加菜单。在 `Filter_Plugin_Zbp_MakeTemplatetags` 里对当前渲染的 `navbar` 对象追加 `<li>`，只影响本次渲染、不写库，写法见[主题 include.php「运行时追加导航条目」](zblogphp-theme-development-theme-functions.md#运行时追加导航条目)。
2. **后台配置页**：显示「前台访问地址」区块，输出 `MyPlugin_FrontUrl()` 生成的绝对 URL 和可点击预览链接。用户换主题、换 URL 模式后仍能从这里找到页面。
3. **侧栏模块**：模块 `Content` 存数据库，写相对路径会随页面层级和 URL 模式失效；一律保存 `MyPlugin_FrontUrl()` 生成的绝对地址，并用模块版本键在 URL 模式变化时重建，见[模块与侧栏系统「常见坑」](zblogphp-theme-development-modules-sidebars.md#常见坑)。

三个入口指向同一个 URL 生成函数，站点切换 URL 模式后不需要逐处修改。配置页里的地址区块可以直接输出：

```php
$frontUrl = MyPlugin_FrontUrl();
printf(
    '<p>%s：<a href="%s" target="_blank" rel="noopener">%s</a></p>',
    htmlspecialchars($zbp->lang['MyPlugin']['front_url'], ENT_QUOTES),
    htmlspecialchars($frontUrl, ENT_QUOTES),
    htmlspecialchars($frontUrl, ENT_QUOTES)
);
```

界面文案取自插件语言包，不硬编码中文。
