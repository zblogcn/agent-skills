# 权限控制：actions 表与 CheckRights

来源：`zb_system/defend/actions.php`、`zb_system/function/c_system_base.php`、`zb_system/function/lib/zblogphp.php`（CheckRights / RegAction）（1.7.5.3540）。

## 权限表：`$GLOBALS['actions']`

加载位置：`zb_system/function/c_system_base.php` L72：

```php
$GLOBALS['actions'] = include ZBP_PATH . 'zb_system/defend/actions.php';
```

`zblogphp.php` L684 将其引用进对象：`$this->actions = &$actions;`，因此 `$zbp->actions` 与 `$GLOBALS['actions']` 同一份数据。

表内容（zb_system/defend/actions.php 全文，数字为所需最低级别）：

```php
'login' => 6, 'logout' => 6, 'verify' => 6, 'admin' => 5,
'search' => 6, 'misc' => 6, 'feed' => 6, 'cmt' => 6, 'getcmt' => 6,
'ajax' => 6, 'view' => 6, 'api' => 6,

'ArticleNew' => 4, 'ArticleEdt' => 4, 'ArticlePst' => 4, 'ArticleDel' => 4, 'ArticlePub' => 3,
'PageNew' => 2, 'PageEdt' => 2, 'PagePst' => 2, 'PageDel' => 2, 'PagePub' => 2,
'CategoryNew' => 2, 'CategoryEdt' => 2, 'CategoryPst' => 2, 'CategoryDel' => 2,
'CommentEdt' => 5, 'CommentSav' => 5, 'CommentDel' => 5, 'CommentChk' => 5, 'CommentBat' => 5,
'MemberNew' => 1, 'MemberEdt' => 5, 'MemberPst' => 5, 'MemberDel' => 1,
'TagNew' => 2, 'TagEdt' => 2, 'TagPst' => 2, 'TagDel' => 2,
'PluginEnb' => 1, 'PluginDis' => 1,
'UploadPst' => 3, 'UploadDel' => 3,
'ModuleEdt' => 1, 'ModulePst' => 1, 'ModuleDel' => 1,
'ThemeSet' => 1, 'SidebarSet' => 1,
'SettingSav' => 1,

'ArticleMng' => 4, 'PageMng' => 2, 'CategoryMng' => 2, 'SettingMng' => 1,
'TagMng' => 2, 'CommentMng' => 5, 'UploadMng' => 3, 'MemberMng' => 5,
'ThemeMng' => 1, 'PluginMng' => 1, 'ModuleMng' => 1,

'PostBat' => 2,
'ArticleAll' => 2, 'PageAll' => 2, 'CategoryAll' => 2, 'CommentAll' => 2,
'MemberAll' => 1, 'TagAll' => 2, 'UploadAll' => 2,
'NoValidCode' => 5,
'root' => 1,
```

## 用户级别语义

`zb_users/language/zh-cn.php` L375-382：

```php
'user_level_name' => array(
    '1' => '管理员',
    '2' => '网站编辑',
    '3' => '作者',
    '4' => '协作者',
    '5' => '评论者',
    '6' => '游客',
),
```

**数字越小权限越高**。`$zbp->user->Level` 存的就是这个级别。

`$zbp->user->IsGod`：级别为 1 且是系统中第一个 1 级用户（base/member.php L181-203）。可通过环境变量 `ZBP_PRESET_DISABLE_ROOT` 禁用。

## 校验函数

### `$zbp->CheckRights($action, $level = null)`

zblogphp.php L1527-1550：

```php
public function CheckRights($action, $level = null)
{
    if ($level === null) {
        $level = $this->user->Level;
    }
    foreach ($GLOBALS['hooks']['Filter_Plugin_Zbp_CheckRights'] as $fpname => &$fpsignal) {
        $fpreturn = $fpname($action, $level);
        if ($fpsignal == PLUGIN_EXITSIGNAL_RETURN) {
            $fpsignal = PLUGIN_EXITSIGNAL_NONE;
            return $fpreturn;
        }
    }
    if (!isset($this->actions[$action])) {
        if (is_numeric($action)) {
            return $level <= $action;
        } else {
            return false;   // 未注册的 action 一律拒绝
        }
    }
    return $level <= $this->actions[$action];
}
```

要点：

- 比较方式是 `$level <= $required`（数字小者胜出）
- 未注册的 action 返回 false——这是「安全默认拒绝」
- 允许传数字级别：`CheckRights('admin')` 等价于查表；`CheckRights('5')` 直接和 5 比
- 钩子 `Filter_Plugin_Zbp_CheckRights` 可完全接管结果（返回 true/false 并置 `PLUGIN_EXITSIGNAL_RETURN`）

### `$zbp->CheckRightsByLevel($action, $level)`

L1560-1563，只是参数换序的别名。

### 注册新 action：`$zbp->RegAction($name, $level, $title)`

zblogphp.php L4127-4131：

```php
public function RegAction($name, $level, $title)
{
    $this->actions[$name] = $level;
    $this->lang['actions'][$name] = $title;
}
```

插件应在 `ActivePlugin()` 或全局 include 时调用，否则 cmd.php L22 的 CheckRights 会拒绝请求。

## 在代码中的使用

入口校验（cmd.php L22 / admin/index.php L20）：

```php
if (!$zbp->CheckRights($zbp->action)) {
    $zbp->ShowError(6, __FILE__, __LINE__);
    die();
}
```

页面内部分级显示（c_system_admin_function.php 菜单函数）：

```php
if ($zbp->CheckRights('MemberNew')) {
    echo MakeSubMenu(...);
}
```

插件自定义页面：

```php
if (!$zbp->CheckRights('MyAct')) {
    $zbp->ShowError(6, __FILE__, __LINE__);
}
```

## 密码与登录安全（关联权限）

- 密码存储：`Member::GetPassWordByGuid($ps, $guid) = md5(md5($ps) . $guid)`（base/member.php L232-235）
- 登录验证：`$zbp->Verify_MD5($name, $md5pw, &$member)`（zblogphp.php L1660），比较 `md5($md5pw . $member->Guid)`
- Token 登录：`CreateWebToken()` 用 hash_hmac('sha256', ...)（c_system_common.php L2701 附近）
- 登录钩子：`Filter_Plugin_VerifyLogin_Succeed` / `Filter_Plugin_VerifyLogin_Failed`（c_system_event.php L50/L56）

## 文件与目录防护

- 应用 PHP 文件守卫见[共同约定](application-conventions.md#php-文件守卫)。
- 上传实现规则见[安全专题](zblogphp-security-SKILL.md)。
