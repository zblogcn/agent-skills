# 插件配置存取（$zbp->Config / SaveConfig / DelConfig）

Z-BlogPHP 为每个插件提供独立的键值配置空间，按插件 ID 隔离。API 实现位于 `zb_system/function/lib/zblogphp.php`：`Config()` L1349-1361、`SaveConfig()` L1312-1321、`DelConfig()` L1330-1340、`HasConfig()` L1370-1373。

以下示例中的 `MyPlugin` 是占位 ID，替换为目标插件 ID；配置项与值按需求调整。

## 核心 API

```php
global $zbp;

// 读：不存在时自动创建内存中的空 Config 对象
$value = $zbp->Config('MyPlugin')->default_url;

// 写：只改内存对象，必须 SaveConfig 才落盘
$zbp->Config('MyPlugin')->default_url = '//example.com/avatar/{%emailmd5%}';
$zbp->SaveConfig('MyPlugin');

// 删除整个配置（仅用于用户显式触发的「重置设置」，不要挂在停用回调里）
$zbp->DelConfig('MyPlugin');
```

注意：`Config($name)` 只返回内存对象（`$this->configs[$name]`），**不调用 `SaveConfig($name)` 就什么都不会保存**——这是配置「保存后丢失」最常见的原因。

## 辅助方法（Config 对象）

按键判断或删除配置项：

```php
// 判断某个键是否存在
if (!$zbp->Config('MyPlugin')->HasKey('enabledcheck')) {
    $zbp->Config('MyPlugin')->enabledcheck = 1;   // 补默认值
    $zbp->SaveConfig('MyPlugin');
}

// 删除单个键（保存后生效）
$zbp->Config('MyPlugin')->DelKey('username');
$zbp->SaveConfig('MyPlugin');
```

## 生命周期中的典型用法

- **安装时写默认值**（同一段逻辑也放进激活函数的自愈检查，不能只依赖安装回调）：

```php
function InstallPlugin_MyPlugin()
{
    global $zbp;
    $zbp->Config('MyPlugin')->default_url = '//example.com/avatar/{%emailmd5%}.png';
    $zbp->Config('MyPlugin')->source = '{%host%}zb_users/avatar/0.png';
    $zbp->Config('MyPlugin')->local_priority = 0;
    $zbp->SaveConfig('MyPlugin');
}
```

- **卸载时清理（默认保留数据）**：

```php
function UninstallPlugin_MyPlugin()
{
    global $zbp;
    // 停用会执行本函数，只清运行期状态，保留配置和数据表
    $zbp->Config('MyPlugin')->DelKey('runtime_cache');
    $zbp->SaveConfig('MyPlugin');
}
```

`UninstallPlugin_{ID}` 在后台点「停用」时就会执行（`DisablePlugin()` 先调用它再改启用列表）。不要在这里 `DelConfig` 或 `DelTable`，否则停用即丢数据；确需清空配置就做成配置页上的显式按钮，见 lifecycle.md「停用、卸载与数据保留」。

安装默认值同样不能只放在 `InstallPlugin_{ID}`：CLI 启用、改配置恢复不会触发该回调，激活函数里要调用可重复执行的初始化检查（lifecycle.md「自愈式初始化」）。

- **管理页表单保存**：

```php
if (count($_POST) > 0) {
    CheckIsRefererValid();
    $zbp->Config('MyPlugin')->default_url = $_POST['default_url'];
    $zbp->Config('MyPlugin')->source = $_POST['source'];
    $zbp->Config('MyPlugin')->local_priority = $_POST['local_priority'];
    $zbp->SaveConfig('MyPlugin');
    $zbp->SetHint('good');
    Redirect('./main.php');
}
```

## 注意事项

- 配置名建议就用插件 ID，保证与插件目录一一对应。
- 停用时会执行 `UninstallPlugin_{ID}`，不要把 `DelConfig` 放在其中（停用即丢设置）；清空配置只能作为配置页上的显式操作。
- 值按标量存取；要存数组请自行序列化（如 `implode('|', ...)`）。
- 敏感配置（token、密钥）也会被原样保存，不要在日志中输出。
- 全局站点配置是 `$zbp->option`（`SaveOption()`），与插件 Config 是两套机制；插件只应写自己的 Config 空间。
