# 代码质量要求

主题和插件编写时必须遵循以下质量要求，涵盖危险调用、全局命名、版本兼容、页面输出、资源引用和前端表现。规则本身是编码规范，不是为了通过某个检测而设；它们与官方自检工具 [zbp-app-validator](https://github.com/zblogcn/zbp-app-validator) 的检测项一致，完成后可用该工具本地自检。

## 禁止动态执行与命令执行

PHP 文件中禁止以下调用，也不要用字符串拼接、变量函数（`$fn()`）等任何方式变相调用：

- 动态执行：`eval`、`assert`、`create_function`
- 命令执行：`exec`、`system`、`popen`、`proc_open`、`pcntl_exec`、`passthru`、`shell_exec`，以及反引号运算符（`` `命令` ``）

需要外部程序能力时改写为纯 PHP 方案；需要执行用户不可控的固定系统命令时，先与用户确认实现方式。

## 优先使用系统封装的服务

| 需求 | 写法 | 不要直接用 |
|---|---|---|
| 发起 HTTP 请求 | `Network::Create()`（`zb_system/function/lib/network.php`，自动按环境选择 curl / fsockopen / file_get_contents） | `curl_init` |
| 开启/关闭 session | `$zbp->StartSession()` / `$zbp->EndSession()` | `session_start()` / `session_write_close()` |

## 不使用 ORDER BY RAND()

不要写 `ORDER BY rand()`（裸 SQL）或 `'rand()' => ''`（DbSql 排序参数），它会强制全表扫描。需要随机结果时在应用层实现，例如先取主键列表，`shuffle` 后再按随机主键取数据。普通 `rand()`/`mt_rand()` 不在此列。

## 后台写操作带 CSRF 防护

后台页面的每个 `<form>` 必须配合 `GetCSRFToken`、`BuildSafeURL` 或 `BuildSafeCmdURL`（提交端校验见 [CSRF 参考](zblogphp-security-csrf.md)）。主题前台模板和 `.js`、`.css`、`.txt` 不适用。

## 全局符号必须带应用 ID

include.php 加载后进入全局空间的一切符号都要带应用 ID（XML 中的 `id`，大小写不敏感），避免污染全局命名空间、与核心及其他应用冲突：

- 全局函数只允许：
  - 四个系统约定精确名：`ActivePlugin_{ID}`、`AddApiMods_{ID}`、`InstallPlugin_{ID}`、`UninstallPlugin_{ID}`
  - `{ID}_` 开头（如 `MyPlugin_DoSomething()`）
  - 恰好等于 `{ID}`、或以 `_{ID}` 结尾
  - 放在 `{ID}\` 或 `zblogphp\{ID}\` 开头的命名空间中
- 全局变量、常量、类：以 `{ID}` 或 `{ID}_` 开头，例如 `class MyPlugin_Helper`、`define('MYPLUGIN_VERSION', ...)`；命名空间类 `MyPlugin\Foo` 同样合规
- `AddApiMods_{ID}()` 返回数组的键（API mod 名）必须以 `{ID}` 开头
- 工具函数统一用 `{ID}_` 前缀或收进 `{ID}\` 命名空间，不在全局空间定义裸函数、裸常量

注意命名空间需要 PHP 5.3+；XML 声明的 `<phpver>` 低于 5.3 时不要使用。

## PHP 版本兼容范围与 phpver 一致

可运行的 PHP 版本范围由 XML 的 `<phpver>`（骨架默认 `5.2`）决定：

- 代码只能使用该版本及以上支持的语法和函数。`<phpver>5.2</phpver>` 时不能用命名空间、闭包、短数组 `[]`、`??`、`::class` 等 5.3+ 特性。
- 需要新语法或新版本函数时，先提高 `<phpver>` 再写代码，并保证声明范围内所有版本可运行。
- 修改已有应用时沿用原有的 `<phpver>`，不要擅自升降。

## 页面输出必须规范

- HTML 标签正确闭合、嵌套合法，不用已废弃标签和浏览器私有属性；遵循[共同约定的 HTML 语义化](application-conventions.md#html-语义化)要求。
- 子模板（`header.php`、`footer.php`、`c_*.php`）的标签在本文件内闭合，文档骨架只写在入口模板，分工见[模板文件结构](zblogphp-theme-development-theme-structure.md#模板文件结构（headerfooter-与入口模板的分工）)。
- `img` 写非空 `alt`，表单控件关联 `label`，按钮用 `button`。
- `<html>` 标签写 `lang` 属性（模板用 `{$lang['lang_bcp47']}` 或 `{$language}`）。

## 资源本地化

CSS、JS、字体、图片等资源放在应用自己的目录内，用 `{$host}`（主题模板）或 `$zbp->host`（PHP）拼路径引用：

- 不引用公网 CDN、在线字体库、外部统计脚本等任何站外资源，既保证离线环境可用，也避免第三方失效和隐私问题。
- 不引用站点其他应用或系统私有路径下的资源；系统自带资源（`zb_system/` 下的 CSS/JS/icon 字体）可以引用。
- 发布前确认每个资源路径真实存在，不产生 404。

## 前端无报错并适配多端

- 页面在浏览器控制台不能有 `error` 或未捕获脚本异常；自己的 JS 在不同页面都要能正常执行。
- 主题必须响应式，至少适配常见断点：桌面 1920 / 1366 / 1280、平板 768、手机 414 宽度；窄屏不破版、不横向溢出、图片不超出容器。
- 截图/图片资源不携带测试环境的账号、域名等不应公开的信息。

## 检测工具覆盖不到、但仍须遵守

工具只做静态分析和有限的页面实测，以下安全项没有自动检测，必须按安全专题执行：SQL 一律 DbSql 参数化（[SQL 注入防护](zblogphp-security-sql-injection.md)），输出按 [XSS 转义](zblogphp-security-xss-escaping.md)处理，后台操作做[权限校验](zblogphp-security-permissions.md)。

## 本地自检

需要时按仓库说明运行 [zbp-app-validator](https://github.com/zblogcn/zbp-app-validator)：Docker 方式 `docker build` 后 `docker run --rm --privileged -it`；本机直跑需要 Java 8 / PHP 8.1+ / Node 20+，执行 `php checker`。日常编写以本页要求为准，无需每次都跑。
