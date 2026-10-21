# 本地开发与实测

本专题仅在用户明确要求测试、验证或排错时使用；日常交付只做静态检查（见 [主题与插件共同约定「读取与交付边界」](application-conventions.md#读取与交付边界)）。操作以只读访问为主，不只读的操作（如临时改启用列表）必须先记录原值，测试结束立即恢复，并把改动内容告知用户。

## ZBP_PRESET_THEME 无损切换主题

设置环境变量 `ZBP_PRESET_THEME` 为目标主题 ID，站点即以该主题渲染，不改动数据库中已启用的主题设置；进程结束后原主题设置不受影响（`zb_system/function/c_system_base.php` L253-260）。

- 用法：在启动服务器或执行请求的同一命令中设置环境变量。
- 页面渲染异常时，删除 `zb_users/theme/<主题ID>/compile/` 下的编译缓存后重试。
- 切换主题后需要重启 PHP 内置服务器再测。

## 插件测试：临时修改启用列表

插件没有像主题那样的免改配置切换方式，测试时临时修改启用列表，测完恢复：

1. 记录 `ZC_USING_PLUGIN_LIST` 原值（`$zbp->option['ZC_USING_PLUGIN_LIST']`，存在配置表）。
2. 改成测试所需的插件 ID 串（`|` 分隔），保留站点原有插件以免影响其他功能。
3. 访问页面验证，结束后写回原值。

注意：这样启用不会经过后台的 `PluginMng&install=` 请求，`InstallPlugin_{ID}` 不会执行，插件必须能靠激活函数自愈初始化（见 [插件生命周期「自愈式初始化」](zblogphp-plugin-development-lifecycle.md#自愈式初始化)）。测试前也可先确认插件在缺少初始化时是否会报错。

## 用 CLI 构造登录态

测试需要登录的页面时，不必真的走一遍表单。用与站点相同的 guid、用户和算法在 CLI 里算出 Cookie 值：

```php
<?php
require '<站点根目录>/zb_system/function/c_system_base.php';
$zbp->Load();
$user = $zbp->GetMemberByID(1);

$crc = hash('crc32b', $zbp->guid);
$token = CreateWebToken($user->ID, time() + 86400, $user->Guid, $user->PassWord_MD5Path);
echo 'username_' . $crc . '=' . rawurlencode($user->Name) . PHP_EOL;
echo 'token_' . $crc . '=' . $token . PHP_EOL;
```

- Cookie 名里的哈希是 `hash('crc32b', $zbp->guid)`，token 由 `CreateWebToken($id, $time, $user->Guid, $user->PassWord_MD5Path)` 生成（`c_system_event.php` L81-97、zblogphp.php L1609-1616、`c_system_common.php` L2690-2702）。漏掉任何一个参数都会得到「已登录但无权限」或直接掉登录。
- 前台登录态只需要 `username_*` 和 `token_*`；`addinfo*` 只用于后台界面显示用户信息。
- 后台页还要求用户是管理员。取创始人用 `$zbp->GetMemberByID(1)`，或直接给 `$zbp->user` 赋值后再判断权限。

## CSRF Token 无状态直算

`GetCSRFToken($id, $timecompare)` 是纯哈希，不落库、不依赖 session。输入是：

```text
md5(guid + path + [增强安全时的 GetGuestAgent()] + user->ID + user->Password + user->Status + id + 时间串)
```

`hour` 的时间串是 `YmdH`，`minute` 的是 `YmdHi`（zblogphp.php L3768-3787、L3798-3827）。CLI 里先设置 `$zbp->user`，再调用 `$zbp->GetCSRFToken('login', 'minute')`，就能得到与页面一致的 token。

- 开启 `ZC_ADDITIONAL_SECURITY` 时，哈希混入 `GetGuestAgent()`（即 `HTTP_USER_AGENT`）。CLI 与 HTTP 请求必须使用同一个 User-Agent，否则校验必失败。
- 函数内部会临时切换时区到 `ZC_TIME_ZONE_NAME`，测试脚本不需要自己改时区。

## 停用态与子进程隔离实测

插件前台页和 AJAX 处理函数通常以 `exit` / `die` 结束请求。在同一个 CLI 脚本里 `include` 这些文件，第一处 `die` 就终止整个测试脚本，后面的断言全部不执行，看起来像「测了一半就通过」。

- 每个请求用独立进程：`php -S` 起服务后用 `curl` 请求，或每个用例单独 `php -r` / 临时脚本执行。
- 同一进程内只调用不 `die` 的纯函数（生成 URL、计算 token、格式化数据），不要包含页面文件。
- `exit` 会执行已注册的 shutdown 函数和析构函数，不会返回调用方；`ob_start()` 能捕获输出，但挡不住 `die`。

停用态必须单独覆盖：

1. 从 `ZC_USING_PLUGIN_LIST` 去掉插件 ID（记录原值）。
2. 直接请求插件前台页和后台管理页。
3. 预期是 404、提示页或「插件未启用」，不能是 500，也不能出现 `Undefined array key` / `Call to undefined function`。
4. 恢复原值。

停用后 `include.php` 不加载，语言包、函数、类都不存在，页面必须自己 `LoadLanguage` 并 `CheckPlugin`，写法见[插件前台页面「停用态」](zblogphp-plugin-development-frontend-pages.md#停用态先加载语言包再判断)。

## 探测后台页面

后台页依赖管理员登录态、页头页脚的全局变量和完整的 `#divMain` 结构，直接包含容易死在半路。两种可用姿势：

- **HTTP 探针**：按上文生成管理员 Cookie，用 `curl --noproxy "*" -b "<cookie>" http://127.0.0.1:8088/zb_users/plugin/MyPlugin/main.php`，检查状态码和页面关键标题。
- **CLI 探针**：脚本顶层 `require c_system_base.php`、`require c_system_admin.php`，`$zbp->Load()`，设置 `$zbp->user = $zbp->GetMemberByID(1); $zbp->islogin = true;`，再用 `ob_start()` 包住管理页的 include，最后检查输出。后台页头用的是全局变量，探针也要在顶层 include，规则见[插件后台管理页「页头页脚只能在文件顶层 require」](zblogphp-plugin-development-admin-page.md#页头页脚只能在文件顶层-require)。

## PHP 内置服务器

```bash
php -S 127.0.0.1:8088 -t <站点根目录>
```

- PHP CLI 的路径以本机安装为准，不确定时先向用户确认。
- 进程随命令结束被终止：启动、访问、停止必须在同一条命令内完成（例如后台启动后接 curl，再停止进程），不要把服务器留在后台常驻。
- 改动 theme.xml、切换主题后重启服务器，避免旧状态干扰判断。

## 命令行请求绕过系统代理

本机 curl 默认可能走系统代理，访问 `127.0.0.1` 会失败或被转发到外网：

```bash
curl --noproxy "*" http://127.0.0.1:8088/
```

## 无头浏览器截图

- 使用 playwright-core 连接本机已安装的 Chromium，不重新下载浏览器。
- 用 `clip` 指定截图区域时需要同时设置 `fullPage: true`，否则截取不到目标区域。
- 截图仅用于向用户展示渲染结果，属于用户明确要求的实测范围。
