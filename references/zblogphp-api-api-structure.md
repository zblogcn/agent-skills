# API 入口与调度流程

## 1. 入口文件

`zb_system/api.php`（全文件 42 行）执行顺序：

```php
define('ZBP_IN_API', true);
require 'function/c_system_base.php';
$zbp->Load();

ApiCheckEnable();                                   // 检查 ZC_API_ENABLE，关闭则 503
HookFilterPlugin('Filter_Plugin_API_Begin');        // 插件最早介入点
ApiCheckAuth(false, 'api');                         // 基础权限：CheckRights('api')
ApiCheckLimit();                                    // ZC_API_THROTTLE_ENABLE 时限流

$mods = &$GLOBALS['api_public_mods'];
$mod = strtolower(GetVars('mod', 'GET', ''));
$act = strtolower(GetVars('act', 'GET', ''));

ApiLoadMods();        // 注册所有 mod
ApiCheckMods();       // 黑/白名单检查
ApiLoadPostData();    // 把 JSON body 合并进 $_POST
ApiVerifyCSRF();      // POST 且非 token 认证时校验 csrf_token
ApiDispatch($mods, $mod, $act);
```

URL 形式：`{host}zb_system/api.php?mod=post&act=get&id=1`。`$zbp->apiurl`（zblogphp.php L905）即该地址；生成 URL 可用 `ApiUrlGenerate($mod, $act, $query)`（c_system_api.php L872）。

## 2. mod 注册与派发（核心不是反射，是函数命名约定）

`ApiLoadMods()`（c_system_api.php L77）做两件事：

1. 触发 `Filter_Plugin_API_Extend_Mods` 钩子，插件可返回 `array(mod名 => 文件路径)` 追加 mod（L81-91）
2. `ApiLoadSystemMods()`（L100）扫描 `$zbp->apimodsdir`（即 `zb_system/api/`）下全部 php 文件注册进 `$api_public_mods`

`ApiDispatch($mods, $mod, $act)`（L751）的真实逻辑（L757-787）：

```php
if (empty($act)) { $act = 'get'; }                    // act 缺省为 get
if (isset($mods[$mod]) && file_exists($mod_file = $mods[$mod])) {
    include_once $mod_file;
    $func = 'api_' . $mod . '_' . $act;               // 关键：拼接函数名
    if (function_exists($func)) {
        $result = call_user_func($func);
        // 按 $result 的 raw/json/data 键输出
    }
}
$zbp->ShowError($GLOBALS['lang']['error']['96'], ..., 404); // 找不到则 404
```

**即：每个 act 是一个全局函数 `api_{mod}_{act}()`，定义在以 mod 名命名的 php 文件里。** 不存在类或反射。

另有内部调用通道 `ApiExecute($mod, $act, $get, $post)`（L798）：在 PHP 进程内直接执行某个 act 并取回 `data`，支持 `$api_private_mods`（由 `ApiLoadPrivateMods($dir)` L126 注册）；HTTP 请求只会走 public mods。

## 3. 返回格式

act 函数返回 array，ApiDispatch 按三种键处理（L767-780）：

| 返回键 | 处理方式 |
|---|---|
| `raw`（可配 `raw-type`） | `ApiResponseRaw` 原样输出（如下载文件） |
| `json` | 直接 JsonEncode 输出，不包标准结构 |
| 其他（`data`/`error`/`code`/`message`） | 走 `ApiResponse` 标准结构 |

标准响应（ApiResponse，L337-376）：

```json
{
  "code": 200,
  "message": "OK",
  "data": { ... },
  "error": null
}
```

- 有 error 时 code 默认改 500，error 含 `type/code/message`；debug 模式追加 `message_full/file/line/moreinfo`。
- `ZC_RUNINFO_DISPLAY` 开启时响应附带 `runtime` 字段。
- 全局错误由 `ApiDebugHandler`（L54）兜底，同样输出 ApiResponse 结构。

## 4. 认证

两种并存（互斥优先 Cookie）：

1. **Cookie 会话**：与网页后台同一套登录态。
2. **API Token**：`ApiTokenVerify`（L26）在 `$zbp->PreLoad()` 时挂到 `Filter_Plugin_Zbp_PreLoad`（zblogphp.php L950）。未登录时从 `Authorization: Bearer {token}` 头或 `?token=` 参数取 token，`$zbp->VerifyAPIToken($api_token)` 验证，成功则定义常量 `ZBP_IN_API_VERIFYBYTOKEN` 并写入 `$zbp->user`。

token 由 `mod=member&act=login` 颁发（zb_system/api/member.php L58）：

```php
'token' => $zbp->GenerateApiToken($member, $sdt),  // GenerateApiToken 在 zblogphp.php L1626
'expire_time' => $sdt,
```

## 5. CSRF

`ApiVerifyCSRF`（L683）：仅对 **POST** 请求校验 `csrf_token` 参数（`$zbp->VerifyCSRFToken($csrf_token, 'api')`），失败 419。以下情况跳过：

- token 认证请求（`ZBP_IN_API_VERIFYBYTOKEN` 已定义）
- 内置白名单：`member/login`、`comment/post`
- 插件可用 `Filter_Plugin_API_VerifyCSRF_Skip` 钩子追加白名单

token 用 `$zbp->GetCSRFToken('api')` 生成。

## 6. 权限

```php
ApiCheckAuth($loginRequire = false, $action = 'view', $throwException = true); // L458
```

- `$loginRequire=true` 且未登录 → 401（error 6）
- `$zbp->CheckRights($action)` 不过 → 403
- 权限动作名定义在 `zb_system/defend/actions.php`

## 7. 黑白名单与限流

- 全局规则：`$GLOBALS['api_allow_mods_rule']` / `$GLOBALS['api_disallow_mods_rule']`，格式 `array(array('mod名' => 'act名'))`，act 为空串匹配整个 mod。
- `ApiCheckMods`（L257）先触发 `Filter_Plugin_API_CheckMods` 让插件合并规则，再检查；白名单非空时不在名单内一律拒绝（503 error 95）。
- 程序化增删：`ApiAddAllowMod/ApiAddDisallowMod/ApiRemoveAllowMod/ApiRemoveDisallowMod`（L195-250）。
- 限流：`ZC_API_THROTTLE_ENABLE` 开启时按 IP 每分钟限 `ZC_API_THROTTLE_MAX_REQS_PER_MIN`（默认 60）次，超限 429（ApiThrottle L905）。
- 每页最大条数：`$zbp->apiMaxCountPerPage = 50`（zblogphp.php L453）；列表默认条数取 `ZC_API_DISPLAY_COUNT`。

## 8. 常用辅助函数

- `ApiGetRequestFilter($limitDefault, $sortableColumns, $max_count_perpage)`（L566）：把 `sortby/order/page/perpage` 请求参数转成 `limit/order/option`（含 pagebar）。
- `ApiGetPagebarInfo($option)`（L621）：输出分页信息（AllCount/PageNow/PageAll 等）。
- `ApiGetObjectArray($object, $other_props, $remove_props, $with_relations)`（L489）：对象转数组；Member 自动剔除 Guid/Password/IP。
- `ApiGetObjectArrayList($list, ...)`（L542）：列表版。
- `ApiGetAndFilterRelationQuery($info)`（L657）：解析 `?with_relations=Author,Category`。
- `ApiCheckHttpMethod('GET|POST')`（L930）：限制 HTTP 方法，不符 405。
