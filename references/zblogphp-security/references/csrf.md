# CSRF Token 机制与 Referer 校验

来源：`zb_system/function/lib/zblogphp.php`（GetCSRFToken / VerifyCSRFToken）、`zb_system/function/c_system_common.php`（CheckIsRefererValid / CheckCSRFTokenValid / BuildSafeURL）、`zb_system/cmd.php`（1.7.5.3540）。

## Token 生成与验证

### `$zbp->GetCSRFToken($id = '', $timecompare = 'hour')`

zblogphp.php L3768-3787：

```php
public function GetCSRFToken($id = '', $timecompare = 'hour')
{
    // 用时区名格式化时间
    if (strtolower($timecompare) == 'minute' || strtolower($timecompare) == 'm') {
        $time = date('YmdHi');
    } else {
        $time = date('YmdH');
    }

    $hash_pre = $this->guid . $this->path;
    if ($this->option['ZC_ADDITIONAL_SECURITY']) {
        $hash_pre .= GetGuestAgent();
    }
    $hash_pre .= $this->user->ID . $this->user->Password . $this->user->Status . $id;

    return md5($hash_pre . $time);
}
```

Token 成分：GUID + 路径 + 可选 UA + 用户 ID + 用户密码密文 + 用户状态 + `$id`。时效维度按 `hour`（整点）或 `minute`（整分）切割。

### `$zbp->VerifyCSRFToken($token, $id = '', $timecompare = 'hour')`

zblogphp.php L3798-3824：

```php
public function VerifyCSRFToken($token, $id = '', $timecompare = 'hour')
{
    // 构造同一套 $hash_pre（同 GetCSRFToken）
    if (strtolower($timecompare) == 'minute' || strtolower($timecompare) == 'm') {
        for ($i = 0; $i <= $this->csrfExpirationMinute; $i++) {    // 默认 15
            if ($token === md5($hash_pre . date('YmdHi', (time() - (60 * $i))))) {
                return true;
            }
        }
    } else {
        for ($i = 0; $i <= $this->csrfExpiration; $i++) {           // 默认 1
            if ($token === md5($hash_pre . date('YmdH', (time() - (3600 * $i))))) {
                return true;
            }
        }
    }
    return false;
}
```

属性默认值（zblogphp.php L458-463）：

```php
public $csrfExpiration = 1;       // hour 模式下回溯 1 小时
public $csrfExpirationMinute = 15; // minute 模式下回溯 15 分钟
```

## Referer 校验

`CheckIsRefererValid()`（c_system_common.php L2709-2720）：

```php
function CheckIsRefererValid()
{
    global $zbp;
    $flag = CheckCSRFTokenValid();                     // 第一步：先验 CSRF Token
    if ($flag && $zbp->option['ZC_ADDITIONAL_SECURITY']) {
        $flag = CheckHTTPRefererValid();                // 第二步：增强模式下再验 Referer
    }
    if (!$flag) {
        $zbp->ShowError(5, __FILE__, __LINE__);         // 失败统一返回错误 5
    }
}
```

注意：cmd.php 所有 POST action 调用的是 `CheckIsRefererValid()`（不是 `CheckCSRFTokenValid` 单独），所以失败都会看到「来源可能不正确」提示。

## `CheckCSRFTokenValid($fieldName = 'csrfToken', $methods = array('get', 'post'))`

c_system_common.php L2730-2745：

```php
function CheckCSRFTokenValid($fieldName = 'csrfToken', $methods = array('get', 'post'))
{
    global $zbp;
    $flag = false;
    if (is_string($methods)) {
        $methods = array($methods);
    }
    foreach ($methods as $method) {
        if ($zbp->VerifyCSRFToken(GetVars($fieldName, $method))) {
            $flag = true;
            break;
        }
    }
    return $flag;
}
```

默认同时检查 GET 和 POST 的 `csrfToken` 字段。因为 `edit.php` 用 `BuildSafeCmdURL` 把 token 放在 action URL 的 GET 参数中，所以 POST 表单本身不带 hidden input 也能过校验；但管理页表单（如 `Admin_PluginMng`）的 action 是普通 URL，因此输出 `<input type="hidden" name="csrfToken" value="...">`（c_system_admin.php L596、L1187）。

## 安全 URL 生成

`BuildSafeCmdURL($paramters)`（c_system_common.php L2139-2142）：

```php
function BuildSafeCmdURL($paramters)
{
    return BuildSafeURL('/zb_system/cmd.php?' . $paramters);
}
```

`BuildSafeURL($url, $appId = '')`（L2114-2131）：

```php
function BuildSafeURL($url, $appId = '')
{
    global $zbp;
    if (strpos($url, '?') !== false) {
        $url .= '&csrfToken=';
    } else {
        $url .= '?csrfToken=';
    }
    if (substr($url, 0, 1) === '/') {
        $url = $zbp->host . substr($url, 1);
    }
    $url = $url . $zbp->GetCSRFToken($appId);
    return $url;
}
```

使用场景：所有直接触发写操作的 `<a href>` 或 AJAX URL 都应使用 `BuildSafeCmdURL('act=FooDel&id=123')`。

## 登录页独立 CSRF

`c_system_event.php` L22-31：

```php
function VerifyLogin($throwException = true, $ignoreValidCode = true, $ignoreCsrfCheck = true)
{
    if ($zbp->option['ZC_LOGIN_CSRFCHECK_ENABLE'] && $ignoreCsrfCheck == false) {
        $zbp->csrfExpirationMinute = 5;
        if ($zbp->VerifyCSRFToken(GetVars('csrfToken', 'POST'), 'login', 'minute') == false) {
            $zbp->ShowError(5, __FILE__, __LINE__);
        }
    }
    // ...
}
```

登录表单输出：

```html
<input type="hidden" name="csrfToken" value="<?php echo $zbp->GetCSRFToken('login', 'minute'); ?>">
```

来源：`zb_system/login.php` L40。

## 后台 JS 的 Token 过期提示

`admin_header.php` 输出 meta：

```html
<meta name="csrfToken" content="<?php echo $zbp->GetCSRFToken(); ?>" />
<meta name="csrfExpiration" content="<?php echo $zbp->csrfExpiration; ?>" />
```

`zb_system/script/c_admin_js_add.php` L236-307 用定时器检查剩余时效，过期前弹出提示。

## 编写要点

- 自定义表单提交到 cmd.php 的 action 时，action URL 用 `BuildSafeCmdURL()`
- 若不用 BuildSafeCmdURL，则手动输出 `<input type="hidden" name="csrfToken" value="<?php echo $zbp->GetCSRFToken(); ?>">`
- 自定义 POST 处理函数在开头调 `CheckIsRefererValid()`
- 不手写 `$_GET['csrfToken']` 比较，始终用 `VerifyCSRFToken()` 或 `CheckCSRFTokenValid()`
