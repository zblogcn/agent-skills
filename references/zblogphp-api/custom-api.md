# 插件注册自定义 API 端点

**先记住一个反直觉的事实：Z-BlogPHP 核心不会自动扫描插件目录下的 `api/` 子目录。** 系统 mod 目录（`$zbp->apimodsdir` = `zb_system/api/`）会被 `ApiLoadSystemMods` 自动扫描，但插件必须显式注册自己的 mod。注册有以下三种方式。

## 方式一（推荐）：Filter_Plugin_API_Extend_Mods 钩子

这是 `ApiLoadMods()`（c_system_api.php L81-91）为插件预留的正式入口：钩子函数返回 `array(mod名 => mod文件路径)`，核心会合并进 `$api_public_mods`。

插件 `include.php`：

```php
<?php
RegisterPlugin('myplugin', 'ActivePlugin_myplugin');

function ActivePlugin_myplugin()
{
    Add_Filter_Plugin('Filter_Plugin_API_Extend_Mods', 'myplugin_api_mods');
}

function myplugin_api_mods()
{
    global $zbp;
    return array(
        // mod 名 => mod 文件绝对路径
        'myplugin' => $zbp->usersdir . 'plugin/myplugin/api/myplugin.php',
    );
}
```

mod 文件 `zb_users/plugin/myplugin/api/myplugin.php`：

```php
<?php
if (!defined('ZBP_PATH')) {exit('Access denied');}

// URL: zb_system/api.php?mod=myplugin&act=hello
function api_myplugin_hello()
{
    global $zbp;

    // 动作级权限：必须登录且有 view 权限
    ApiCheckAuth(true, 'view');

    return array(
        'data' => array('hello' => 'world'),
        'message' => 'OK',
    );
}
```

## 方式二：ApiLoadCustomMods / ApiAddMod（目录级/单文件注册）

在 `Filter_Plugin_API_Begin` 钩子（api.php L19，调度前最后介入点）里主动注册：

```php
function ActivePlugin_myplugin()
{
    Add_Filter_Plugin('Filter_Plugin_API_Begin', 'myplugin_api_begin');
}

function myplugin_api_begin()
{
    global $zbp;
    // 整目录注册：目录下每个 xxx.php 成为 mod=xxx
    ApiLoadCustomMods($zbp->usersdir . 'plugin/myplugin/api/');
    // 或单文件注册：ApiAddMod('myplugin', $dir . 'api/myplugin.php');
}
```

- `ApiLoadCustomMods($modsdir)`（c_system_api.php L113）把目录下所有 php 注册进 `$api_public_mods`，mod 名为文件名（转小写）。
- `ApiAddMod($modname, $filename)`（L139）注册单个；已存在同名 mod 时返回 false（不覆盖）。
- 对应移除函数：`ApiRemoveMod($modname)`（L153）。
- 注意：`ApiLoadCustomMods` 会**覆盖**同名系统 mod（L118 无存在性判断），而方式一和 `ApiAddMod` 不会覆盖。不要恶意/无意覆盖系统 mod。

## 方式三：Private mods（仅供 PHP 内部调用）

`ApiLoadPrivateMods($dir)`（L126）注册的 mod 进 `$api_private_mods`，**HTTP 请求不可达**，只能被 PHP 代码通过 `ApiExecute($mod, $act, $get, $post)`（L798）调用，适合插件内部复用 act 逻辑：

```php
$data = ApiExecute('myplugin', 'hello', array('id' => 1)); // 返回 act 结果中的 data
```

## act 编写规范

1. **函数名**：`api_{mod}_{act}`，全小写；act 缺省为 `get`。
2. **返回值**：array，键支持 `data` / `message` / `code` / `error`（走标准 JSON 结构），或 `raw`（原样输出）、`json`（不包结构直接输出）。详见 api-structure.md 第 3 节。
3. **权限**：函数内第一行调 `ApiCheckAuth($loginRequire, $action)`；未登录 401、无权限 403。
4. **CSRF**：POST 请求默认自动校验 `csrf_token`；若该端点设计给纯 token 客户端或公开提交（如评论），可用 `Filter_Plugin_API_VerifyCSRF_Skip` 加白名单。token 认证（Bearer）请求自动跳过 CSRF。
5. **取参**：`GetVars('id')`、`GetVars('name', 'POST')`；JSON body 已被 `ApiLoadPostData()` 合并进 `$_POST`。
6. **列表端点**：用 `ApiGetRequestFilter($limitDefault, $sortableColumns)` 解析分页排序，配合 `$zbp->GetXxxList()` 查询，输出用 `ApiGetObjectArrayList()` + `ApiGetPagebarInfo($option)`。完整范例见 `zb_system/api/post.php` 的 `api_post_list()`。
7. **限制 HTTP 方法**：`ApiCheckHttpMethod('GET')`。

## 输出对象时的脱敏

`ApiGetObjectArray($member, ...)` 对 Member 类自动剔除 `Guid/Password/IP`（c_system_api.php L501-506）。输出其他含敏感字段的对象时，自己传 `$remove_props`。需要追加计算属性（如 Url）用 `$other_props`。

## 接口测试与排错

- [ ] 浏览器访问 `api.php?mod=myplugin&act=hello` 返回标准 JSON（404 error 96 = mod/act 没注册上；503 error 95 = API 未开启或被黑白名单拦）
- [ ] 未登录访问需登录端点返回 401
- [ ] POST 端点不带 csrf_token 返回 419（除非已加白名单或走 Bearer token）
- [ ] 响应含 `code/message/data/error` 四键

## Escalation

- 官方文档：https://docs.zblogcn.com/
- 钩子定义：`zb_system/function/c_system_plugin.php` 中 `Filter_Plugin_API_Extend_Mods`（L2928）、`Filter_Plugin_API_Begin`、`Filter_Plugin_API_Dispatch`、`Filter_Plugin_API_Response` 等
