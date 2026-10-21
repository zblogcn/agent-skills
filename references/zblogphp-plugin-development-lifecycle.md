# 插件生命周期与 include.php 写法

## 生命周期总览

Z-BlogPHP 插件生命周期（机制代码均在 `zb_system/function/c_system_plugin.php`，机制自成一派）：

1. **出现**：`zb_users/plugin/{ID}/plugin.xml` 存在且可解析 → 出现在后台「插件管理」列表。
2. **启用**：后台点启用 → `cmd.php?act=PluginEnb` → `EnablePlugin($name)`（`zb_system/function/c_system_event.php` L2085-2112）：
   - 先做兼容性检查（`CheckCompatibility_Global` + `CheckCompatibility`）；
   - 把插件 ID 写入 `$zbp->option['ZC_USING_PLUGIN_LIST']` 并 `SaveOption()`；
   - 重定向回 `cmd.php?act=PluginMng&install={ID}`，此请求里执行全局函数 `InstallPlugin($ID)`（`zb_system/cmd.php` L256-263、L276-284）。
   - `InstallPlugin($name)` 的实现：若存在函数 `InstallPlugin_{ID}` 则调用一次（c_system_plugin.php L59-65）。
   - **安装回调不在 `EnablePlugin()` 内执行。** 直接调用 `EnablePlugin()`、用 CLI/SQL 改 `ZC_USING_PLUGIN_LIST`、从备份恢复站点等途径启用插件时，都不会触发 `InstallPlugin_{ID}`。因此不能把「建表、补配置、建模块」只放在安装函数里，见下文「自愈式初始化」。
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
4. **停用**：`DisablePlugin($name)`（c_system_event.php L2121-2146）的执行顺序是**先** `UninstallPlugin($name)`（L2130，存在 `UninstallPlugin_{ID}` 则执行一次），**再**从 `ZC_USING_PLUGIN_LIST` 移除并 `SaveOption()`（L2131-2143）。
   - 卸载回调里出现 fatal/未捕获异常时，列表还没更新：插件仍在启用列表中，之后每个请求都会再次 include 它并触发同一错误，站点直接不可用，只能手工改配置或删目录恢复。
   - Z-BlogPHP 没有独立的「删除应用/清除数据」钩子，`UninstallPlugin_{ID}` 就是停用时唯一的回调。

## 停用、卸载与数据保留

停用不是删除文件，也不等于清理数据，但**一定会执行 `UninstallPlugin_{ID}`**。按以下规则实现，否则用户点一次「停用」就可能丢数据：

- **默认保留数据**：卸载回调只做幂等、非破坏性的清理。需要清运行期状态时，用 `$zbp->Config('ID')->DelKey('key')` 再 `SaveConfig('ID')` 删除单个键，配置与数据表保留。
- **不删表**：卸载回调里不调用 `$zbp->db->DelTable(...)`。表一旦删除，重新启用后用户数据无法恢复，而「停用」在语义上只是暂时关闭。
- **不无条件删配置**：`$zbp->DelConfig('ID')` 会让「停用→再启用」丢失全部设置。确需清空时，做成配置页上的显式操作（如「重置设置」按钮），不要挂在停用上。
- **任何数据销毁都要用户二次确认**，并且只放在用户主动触发的功能里，不能隐含在启用/停用流程中。
- **卸载回调必须防御性且幂等**：只调用确实存在的函数和方法；缺配置、缺表、重复执行都不能报错。停用、启用可以反复来回。
- **不要卸载钩子**：`$GLOBALS['hooks']` 每个请求重建，插件停用后不再 include，钩子自然消失。不存在 `Del_Filter_Plugin()`；`Remove_Filter_Plugin($hook, $func)`（c_system_plugin.php L222-233）只在同一请求内运行时移除某项挂载，不属于停用流程。

同一系列应用必须使用同一套停用语义：不能一个插件停用即清空业务数据、另一个只清缓存。

## 自愈式初始化

由于安装回调可能不执行（CLI 启用、改配置恢复、安装请求中断），把初始化写成可重复执行的检查，在激活函数里每次请求调用：

```php
function ActivePlugin_MyPlugin()
{
    global $zbp;
    $zbp->LoadLanguage('plugin', 'MyPlugin');
    MyPlugin_EnsureInstalled();      // 缺表、缺配置时补齐，已初始化时几乎无开销
    Add_Filter_Plugin('Filter_Plugin_Member_Avatar', 'MyPlugin_Url');
}

// 后台首次启用时的一次性入口，内部复用同一套初始化
function InstallPlugin_MyPlugin()
{
    MyPlugin_EnsureInstalled();
}

function MyPlugin_EnsureInstalled()
{
    global $zbp;
    if ((int) $zbp->Config('MyPlugin')->installed_version === 1) {
        return;
    }
    // 建表、补默认配置、注册模块等初始化动作
    $zbp->Config('MyPlugin')->installed_version = 1;
    $zbp->SaveConfig('MyPlugin');
}

function UninstallPlugin_MyPlugin()
{
    global $zbp;
    // 只清运行期状态，保留配置与数据表
    $zbp->Config('MyPlugin')->DelKey('runtime_cache');
    $zbp->SaveConfig('MyPlugin');
}
```

用配置里的标记位（如 `installed_version`）判断是否已初始化，不要用 `file_exists` 之类的代理条件。

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
    MyPlugin_EnsureInstalled();     // 自愈：CLI 启用等情况安装回调不会执行
    Add_Filter_Plugin('Filter_Plugin_Member_Avatar', 'MyPlugin_Url');
}

// 安装函数：后台启用后的一次性入口；可能不执行，因此内部与自愈共用同一套检查
function InstallPlugin_MyPlugin()
{
    MyPlugin_EnsureInstalled();
}

function MyPlugin_EnsureInstalled()
{
    global $zbp;
    if ((int) $zbp->Config('MyPlugin')->installed_version === 1) {
        return;
    }
    $zbp->Config('MyPlugin')->default_url = '//example.com/avatar/{%emailmd5%}.png';
    $zbp->Config('MyPlugin')->source = '{%host%}zb_users/avatar/0.png';
    $zbp->Config('MyPlugin')->local_priority = 0;
    $zbp->Config('MyPlugin')->installed_version = 1;
    $zbp->SaveConfig('MyPlugin');
}

// 卸载函数：停用时执行一次，必须幂等且不销毁用户数据
function UninstallPlugin_MyPlugin()
{
    global $zbp;
    $zbp->Config('MyPlugin')->DelKey('runtime_cache');
    $zbp->SaveConfig('MyPlugin');
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
- `InstallPlugin_{ID}` 不能作为初始化的唯一入口（CLI 启用、改配置恢复都不会触发），初始化必须做成激活函数里可重复执行的自愈检查。
- `UninstallPlugin_{ID}` 是停用时唯一回调，默认保留配置和数据表，详见上文「停用、卸载与数据保留」。
- 卸载钩子用 `Remove_Filter_Plugin($hook, $func)`，不存在 `Del_Filter_Plugin()`；插件停用无需卸载钩子（钩子随请求重建）。
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
