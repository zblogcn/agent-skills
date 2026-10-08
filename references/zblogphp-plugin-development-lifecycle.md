# 插件生命周期与 include.php 写法

## 生命周期总览

Z-BlogPHP 插件生命周期（机制代码均在 `zb_system/function/c_system_plugin.php`，机制自成一派）：

1. **出现**：`zb_users/plugin/{ID}/plugin.xml` 存在且可解析 → 出现在后台「插件管理」列表。
2. **启用**：后台点启用 → `cmd.php?act=PluginEnb` → `EnablePlugin($name)`（`zb_system/function/c_system_event.php` L2085-2112）：
   - 先做兼容性检查（`CheckCompatibility_Global` + `CheckCompatibility`）；
   - 把插件 ID 写入 `$zbp->option['ZC_USING_PLUGIN_LIST']` 并 `SaveOption()`；
   - 重定向回 `cmd.php?act=PluginMng&install={ID}`，此请求里执行全局函数 `InstallPlugin($ID)`（`zb_system/cmd.php` L256-263、L276-284）。
   - `InstallPlugin($name)` 的实现：若存在函数 `InstallPlugin_{ID}` 则调用一次（c_system_plugin.php L59-65）。
3. **运行**：之后每次请求，`c_system_base.php` 引导阶段（L277-301）遍历 `ZC_USING_PLUGIN_LIST`：
   ```php
   foreach ($aps as $ap) {
       if (is_readable($file_base = $GLOBALS['usersdir'] . 'plugin/' . $ap . '/plugin.xml')) {
           $GLOBALS['activedapps'][] = $ap;
       }
       if (is_readable($file_base = $GLOBALS['usersdir'] . 'plugin/' . $ap . '/include.php')) {
           include $file_base;          // 执行 include.php → RegisterPlugin 注册激活函数
       }
   }
   foreach ($GLOBALS['plugins'] as &$fn) {
       if (function_exists($fn)) {
           $fn();                       // 依次调用所有 ActivePlugin_{ID}
       }
   }
   ```
   即：先 include 所有已启用插件的 include.php（此时只应注册），全部加载完后再统一调用各插件的激活函数。
4. **禁用**：`DisablePlugin($name)`（c_system_event.php L2121-2146）→ 内部先调用 `UninstallPlugin($name)`（若存在 `UninstallPlugin_{ID}` 则执行一次，c_system_plugin.php L74-80），再从 `ZC_USING_PLUGIN_LIST` 移除。

> 注意：「禁用」就会执行 `UninstallPlugin_{ID}`——它是「停用」而非「删除文件」。配置清理（`DelConfig`）放在这里意味着禁用即清配置，按目标插件需求决定是否清理。

## include.php 标准写法

在[共同约定](application-conventions.md)的应用副本中补充以下生命周期逻辑；示例也供模板缺失时回退。`MyPlugin` 为占位 ID，头像钩子和配置项按目标功能替换：

```php
<?php
if (!defined('ZBP_PATH')) {exit('Access denied');}   // 防直接访问（必须，见下）

// 注册插件：参数1=插件ID，参数2=激活时执行的函数名
RegisterPlugin("MyPlugin", "ActivePlugin_MyPlugin");

// 激活函数：插件启用后每个请求都会执行，在这里挂 Filter 钩子
function ActivePlugin_MyPlugin()
{
    global $zbp;
    $zbp->LoadLanguage('plugin', 'MyPlugin');
    Add_Filter_Plugin('Filter_Plugin_Member_Avatar', 'MyPlugin_Url');
}

// 安装函数：只在启用后的那一次请求中执行
function InstallPlugin_MyPlugin()
{
    global $zbp;
    $zbp->Config('MyPlugin')->default_url = '//example.com/avatar/{%emailmd5%}.png';
    $zbp->Config('MyPlugin')->source = '{%host%}zb_users/avatar/0.png';
    $zbp->Config('MyPlugin')->local_priority = 0;
    $zbp->SaveConfig('MyPlugin');
}

// 卸载函数：禁用时执行一次
function UninstallPlugin_MyPlugin()
{
    global $zbp;
    $zbp->DelConfig('MyPlugin');
}

// 钩子回调
function MyPlugin_Url(&$member)
{
    global $zbp;
    // ... 处理后 return 结果
}
```

规则要点：

- `include.php` 在引导阶段被 include，**只做注册和函数定义，不要输出任何内容**，否则导致 headers already sent。
- `RegisterPlugin($strPluginName, $strPluginActiveFunction)` 只是把激活函数名存入 `$GLOBALS['plugins']`（c_system_plugin.php L47-50）。
- 函数命名约定：`ActivePlugin_{ID}`、`InstallPlugin_{ID}`、`UninstallPlugin_{ID}`，其中后两个必须严格匹配才会被 `InstallPlugin()`/`UninstallPlugin()` 找到。
- 多个回调共存时，建议函数名带插件 ID 前缀（如 `MyPlugin_Url`），避免与其他插件重名冲突。

## Filter 钩子机制

钩子 API（c_system_plugin.php）：

| 函数 | 行号 | 作用 |
|---|---|---|
| `DefinePluginFilter($name)` | L89-99 | 定义一个新钩子（核心已预定义大量 `Filter_Plugin_*`，插件也可定义自己的钩子供别的插件挂） |
| `Add_Filter_Plugin($hook, $func, $signal)` | L201-212 | 把函数挂到钩子；`$signal` 默认 `PLUGIN_EXITSIGNAL_NONE` |
| `Remove_Filter_Plugin($hook, $func)` | L222-233 | 卸载某项挂载 |
| `List_Filter_Plugin($hook)` | L242-249 | 列出该钩子全部挂载 |
| `SetPluginSignal($hook, $func, $signal)` | L158-169 | 运行时改变某挂载的信号量 |
| `UsingPluginFilter($hook)` | L120-128 | 取得钩子挂载数组引用（钩子触发处使用） |

信号量常量（c_system_plugin.php L17-29）：`PLUGIN_EXITSIGNAL_NONE`（继续执行后续挂载）、`PLUGIN_EXITSIGNAL_RETURN`（本回调返回后终止该钩子后续挂载，返回值作为钩子结果）、`PLUGIN_EXITSIGNAL_BREAK`（终止且不覆盖结果）。

回调内动态设置信号：

```php
$GLOBALS['Filter_Plugin_Member_Avatar']['MyPlugin_Url'] = PLUGIN_EXITSIGNAL_RETURN;
return $s;   // 终止后续挂载并以本返回值为准
```

钩子触发处的典型写法（核心代码中随处可见）：

```php
foreach ($GLOBALS['hooks']['Filter_Plugin_XXX'] as $fpname => &$fpsignal) {
    $fpreturn = $fpname($args);
    if ($fpsignal == PLUGIN_EXITSIGNAL_RETURN) { return $fpreturn; }
    if ($fpsignal == PLUGIN_EXITSIGNAL_BREAK) { break; }
}
```

钩子名清单与触发点见技能 zblogphp-hooks-reference。
