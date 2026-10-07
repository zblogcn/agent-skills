# 如何挂接钩子

Z-BlogPHP 1.7.x 的插件钩子系统集中在 `zb_system/function/c_system_plugin.php`。本文说明插件挂接钩子的标准用法、引用传参与执行信号控制。

## 1. 标准骨架

以下以头像回调演示挂接；`MyPlugin` 是占位 ID，按目标插件替换。直接使用本文示例，不读取其他插件寻找对应实现。

```php
<?php
// zb_users/plugin/<PluginID>/include.php

// 1) 注册插件：插件 ID + 激活函数名
RegisterPlugin("MyPlugin", "ActivePlugin_MyPlugin");

// 2) 激活函数里挂接钩子（不要在文件顶层挂，否则未启用也会执行）
function ActivePlugin_MyPlugin()
{
    Add_Filter_Plugin('Filter_Plugin_Member_Avatar', 'MyPlugin_Url');
}

// 3) 钩子回调：参数是引用传过来的，必须加 &
function MyPlugin_Url(&$member)
{
    global $zbp;
    // ...
    // 4) 通过修改信号控制后续行为
    $GLOBALS['Filter_Plugin_Member_Avatar']['MyPlugin_Url'] = PLUGIN_EXITSIGNAL_RETURN;
    return htmlspecialchars($url);
}
```


## 2. `Add_Filter_Plugin` 签名

```php
function Add_Filter_Plugin($plugname, $functionname, $exitsignal = PLUGIN_EXITSIGNAL_NONE)
```

参数（c_system_plugin.php:201–212）：

- `$plugname`：钩子名（`Filter_Plugin_*`）
- `$functionname`：要挂接的函数名，支持以下形式（由 `ParseFilterPlugin` 解析，见 c_system_plugin.php:313）：
  1. 普通函数名字符串 `'MyFunc'`
  2. 类静态方法 `'MyClass::myMethod'`
  3. 类动态方法 `'MyClass@myMethod'`（每次自动 new 一个对象）
  4. 全局对象方法 `'myObject@myMethod'`（`$GLOBALS['myObject']` 上的方法）
  5. 全局匿名函数（`$GLOBALS['xxx'] = function(...)`）
- `$exitsignal`：默认信号，见下文。

返回 `true` 表示挂接成功；钩子未定义或函数已挂接则返回 `false`。

## 3. 信号常量

定义于 c_system_plugin.php:17–29：

| 常量 | 值 | 含义 |
| --- | --- | --- |
| `PLUGIN_EXITSIGNAL_NONE` | `''` | 不退出，继续执行后续插件 |
| `PLUGIN_EXITSIGNAL_RETURN` | `'return'` | 当前插件执行完后立即从钩子循环 return，**返回当前函数的返回值**给宿主 |
| `PLUGIN_EXITSIGNAL_BREAK` | `'break'` | 同上，但返回值不强调（中断后续插件） |
| `PLUGIN_EXITSIGNAL_GOTO` | `'goto'` | 同 RETURN/BREAK，供宿主编排使用 |

宿主在 `HookFilterPluginBack`（c_system_plugin.php:373）中遇到上述三种信号时：清信号 → 返回当前函数值给宿主。

## 4. 信号控制方式（两种）

### 4.1 挂接时给默认信号

```php
Add_Filter_Plugin('Filter_Plugin_Member_Avatar', 'MyPlugin_Url', PLUGIN_EXITSIGNAL_RETURN);
```

### 4.2 函数内动态改写信号（推荐）

```php
function MyPlugin_Url(&$member)
{
    if (/* 命中本地缓存 */) {
        // 把当前函数的信号改为 RETURN，相当于让钩子立即返回
        $GLOBALS['Filter_Plugin_Member_Avatar']['MyPlugin_Url'] = PLUGIN_EXITSIGNAL_RETURN;
        return $url;
    }
    // 不改写信号则继续执行下一个插件
    return $default;
}
```

也可以用 API：

```php
SetPluginSignal('Filter_Plugin_DisablePlugin', __FUNCTION__, PLUGIN_EXITSIGNAL_RETURN);
```


## 5. 参数引用传递 `&`

- 多数"干预数据"的钩子（`Filter_Plugin_*_Core`、`*_Table`、`Post_*` 等）传入的是 **引用**，回调必须声明为 `function MyHook(&$article)`，否则不会回写。
- 若签名忘记加 `&`，PHP 不会报错但参数修改无效。
- 常见引用参数钩子：`Filter_Plugin_ViewList_Core`、`Filter_Plugin_ViewPost_Core`、`Filter_Plugin_LargeData_*`、`Filter_Plugin_Post*_Core`、`Filter_Plugin_Admin_*Mng_Table`、`Filter_Plugin_OutputOptionItemsOf*` 之外的引用型。

## 6. 多个插件挂同一钩子的执行顺序

- `$GLOBALS['hooks'][$hookname]` 是关联数组，键是函数名，值是信号；执行顺序为 **挂接顺序**（先进先出）。
- 同名函数重复挂接会被忽略（c_system_plugin.php:203–204 `isset` 检查）。
- 一旦某个函数触发了 `PLUGIN_EXITSIGNAL_RETURN / BREAK / GOTO`，后续插件函数不再执行。
- 挂接顺序本质上由插件启用顺序决定；要让本插件"最后执行"，可考虑在较晚钩子（如 `Filter_Plugin_Zbp_Load`）中再 `Add_Filter_Plugin`。

## 7. 自定义钩子

插件可以 `DefinePluginFilter('Filter_Plugin_XXX_Mine')` 注册自己的钩子供其它插件挂接。

注册与挂接示例：

```php
DefinePluginFilter('Filter_Plugin_XXX_Mine');
Add_Filter_Plugin('Filter_Plugin_XXX_Mine', 'MyPlugin_CustomHook');
```

宿主方调用：

```php
// 简单触发（无返回值）
HookFilterPlugin('Filter_Plugin_XXX_Mine', $arg1, $arg2);

// 带返回值 + 信号控制
$result = HookFilterPluginBack('Filter_Plugin_XXX_Mine', $arg1);
```

## 8. 卸载与查询

```php
Remove_Filter_Plugin($hookname, $functionname); // 卸载某函数
ClearFilterPlugin($hookname);                    // 清空某钩子
SuspendFilterPlugin($hookname);                  // 暂停（备份后可恢复）
ResumeFilterPlugin($hookname);                   // 恢复
$list = List_Filter_Plugin($hookname);           // 查询某钩子已挂接的函数数组
$exists = ExistsPluginFilter($hookname);         // 检查钩子是否存在
RemovePluginFilter($hookname);                   // 整体移除钩子定义
```

以上 API 可直接使用；参数名即调用时需提供的钩子名或函数名。

## 9. 常见踩坑

1. **钩子不触发**：插件未在后台启用；`ActivePlugin_xxx` 函数名拼写错；回调函数未在全局命名空间定义。
2. **参数修改无效**：回调参数漏写 `&`。
3. **想让系统提前 return 却没生效**：必须在挂接或函数体内显式声明 `PLUGIN_EXITSIGNAL_RETURN`，并且只 `return $value;` 不够——还要改信号。
4. **返回值丢失**：宿主要通过 `HookFilterPluginBack`（而非 `HookFilterPlugin`）触发才能拿到返回值；插件不要混用两种调用约定。
