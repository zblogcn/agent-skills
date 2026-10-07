# cmd.php 的 act 分发机制与常用 action

来源：`zb_system/cmd.php`（共 382 行，1.7.5.3540）。

## 入口流程

```php
// cmd.php L10-27（节录）
define('ZBP_IN_CMD', true);
// act=ajax 或 X-Requested-With: XMLHttpRequest 时额外定义 ZBP_IN_AJAX（L12-14）
require 'function/c_system_base.php';
$action = GetVars('act', 'GET');          // L18：只从 GET 取 act
$zbp->Load();
if (!$zbp->CheckRights($zbp->action)) {   // L22：权限不足直接错误 6
    $zbp->ShowError(6, __FILE__, __LINE__);
    die();
}
HookFilterPlugin('Filter_Plugin_Cmd_Begin');  // L27：插件可在此介入/接管
switch ($zbp->action) { ... }             // L29-380：硬编码分发
HookFilterPlugin('Filter_Plugin_Cmd_End');    // L382
```

要点：

- **act 只认 GET**（`GetVars('act', 'GET')`），POST 里的 act 无效。
- 权限在进入 switch 之前统一校验；action → 所需用户级别的映射在 `zb_system/defend/actions.php`（见 zblogphp-security / references/permissions.md）。
- `Filter_Plugin_Cmd_Begin` 在所有内置 action 之前触发，是插件接管/新增 cmd 行为的标准位置。

## 内置 action 一览（按 cmd.php switch 顺序）

| act | 类型 | 处理 | 说明 |
|---|---|---|---|
| `login` | 重定向 | L30-39 | 已登录跳后台，否则跳 login.php；支持 redirect 参数写 cookie |
| `logout` | 动作 | L40-44 | `CheckIsRefererValid()` + `Logout()` |
| `admin` | 重定向 | L45-47 | 跳 `admin/index.php?act=admin` |
| `verify` | 动作 | L48-55 | `VerifyLogin(true, false, false)` 处理登录提交 |
| `search` | 重定向 | L56-58 | `Redirect_cmd_to_search()` |
| `cmt` / `getcmt` | 动作 | L59-82 | 提交评论 / 分页加载评论 |
| `ArticleEdt`/`PageEdt` | 重定向 | L83-85, L107-109 | 透传 QUERY_STRING 跳 `admin/edit.php` |
| `ArticlePst`/`PagePst` | **POST** | L97-106, L121-130 | 见下方典型模式 |
| `ArticleDel`/`PageDel` | GET 动作 | L86-93, L110-117 | `CheckIsRefererValid()` 后删除，跳管理页 |
| `ArticleMng`/`PageMng` 等 9 个 `*Mng` | 重定向 | — | 透传 QUERY_STRING 跳 `admin/index.php` |
| `CategoryEdt/TagEdt/MemberEdt/MemberNew/ModuleEdt` | 重定向 | — | 跳对应的 `admin/*_edit.php` |
| `CategoryPst/TagPst/MemberPst/ModulePst` | POST | — | 同 ArticlePst 模式 |
| `CommentDel/Chk/Bat` | GET 动作 | L153-176 | 删/审/批量评论，跳回 HTTP_REFERER |
| `UploadPst/UploadDel` | 动作 | L219-233 | 附件上传/删除 |
| `PluginMng` | 混合 | L256-263 | GET `install` 参数时执行 `InstallPlugin()` |
| `PluginEnb/PluginDis` | GET 动作 | L264-284 | 启用/禁用插件，回跳带 `&install=` |
| `ThemeMng/ThemeSet` | 混合 | L285-302 | 主题安装/切换 |
| `SidebarSet` | POST | L303-308 | 侧栏排序保存，**无跳转**（AJAX 调用） |
| `SettingSav` | POST | L334-348 | 保存站点设置；域名变更时跳新域名重新登录 |
| `PostBat` | GET 动作 | L349-355 | 文章/页面批量操作 |
| `misc` | 动态 | L356-370 | 见下 |
| `ajax` | 钩子 | L371-376 | 见下 |

## 典型 POST action 模式

以 `ArticlePst`（cmd.php L97-106）为模板，所有写操作遵循同一套仪式：

```php
case 'ArticlePst':
    $zbp->csrfExpiration = 48;                 // 可选：放宽 CSRF token 有效期（小时）
    CheckIsRefererValid();                     // 1. CSRF/Referer 校验，失败 ShowError(5)
    PostArticle();                             // 2. 业务函数（定义在 c_system_event.php）
    $zbp->BuildModule();                       // 3. 重建侧栏模块缓存
    $zbp->SaveCache();                         // 4. 落盘缓存
    $zbp->SetHint('good');                     // 5. 成功提示（写入 cookie，下一页显示）
    Redirect_cmd_end_by_script('cmd.php?act=ArticleMng');  // 6. 跳转
    break;
```

自建插件 action 处理函数时应复刻这个顺序。`SetHint('good'|'bad'|'tips', $内容, $时长)` 的提示由后台 `admin_top.php` 里的 `$zbp->GetHint()` 输出。

## misc：动态分发

cmd.php L356-370：

```php
case 'misc':
    include './function/c_system_misc.php';
    ob_clean();
    $miscType = GetVars('type', 'GET');
    $miscType = str_replace(array('<', '>', '&', ' ', '/', '"', "'"), '', $miscType);  // 消毒
    $miscType = ($miscType === 'php' . 'info') ? 'php_zbp_info' : $miscType;           // 屏蔽 phpinfo
    foreach ($GLOBALS['hooks']['Filter_Plugin_Misc_Begin'] as $fpname => &$fpsignal) {
        $fpname($miscType);                    // 插件可在此输出并 exit，接管任意 type
    }
    $function = 'misc_' . $miscType;
    $function();                               // 调用 c_system_misc.php 里的 misc_xxx()
    break;
```

内置 misc type 包括 `statistic`、`updateinfo`、`vrs`（查看权限）、`clearthumbcache`、`updatedapp` 等。插件新增 misc 类型：挂 `Filter_Plugin_Misc_Begin`，判断 `$type` 后输出内容并 `die()`。

## ajax：纯钩子

cmd.php L371-376：

```php
case 'ajax':
    foreach ($GLOBALS['hooks']['Filter_Plugin_Cmd_Ajax'] as $fpname => &$fpsignal) {
        $fpname(GetVars('src', 'GET'));        // src 参数用于区分调用方
    }
    break;
```

系统自身没有任何内置 ajax 分支——**cmd.php 的 AJAX 完全靠插件挂 `Filter_Plugin_Cmd_Ajax` 实现**。回调里按 `$src` 区分业务，自行输出 JSON 并结束。注意此时已定义 `ZBP_IN_AJAX`，`Redirect_cmd_end` 等会用 script 跳转，错误处理也应走 JSON（参考 L63-67 给评论挂的 `JsonError4ShowErrorHook` 做法）。

## 跳转辅助函数

定义于 `zb_system/function/c_system_common.php`：

- `Redirect_cmd_end($url)`：301/302 跳转并 exit（AJAX 模式下改用 JS 跳转）
- `Redirect_cmd_end_by_script($url)`：总是输出 `<script>location.href=...</script>`
- `Redirect_cmd_from_args($url)` / `Redirect_cmd_from_args_with_loggedin($url)`：按 redirect 参数条件跳转
- `BuildSafeCmdURL('act=XXX&...')`：生成带 csrfToken 的 cmd.php URL（c_system_common.php L2139），**所有 GET 写操作链接必须用它**

## 新增自定义 action 的两种方式

1. **挂 `Filter_Plugin_Cmd_Begin`**：在回调里判断 `GetVars('act','GET') == 'MyAct'`，处理完 `die()`。记得自己调 `CheckCSRFTokenValid()`。
2. **注册权限级别**：调用 `$zbp->RegAction('MyAct', 2, '我的操作')`（zblogphp.php L4127-4131，写入 `$this->actions[$name] = $level` 及语言表），否则 L22 的 CheckRights 对未定义 action 一律拒绝。
