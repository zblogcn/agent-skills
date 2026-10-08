# 核心 / 系统类钩子

涵盖调试（Debug）、自动加载、HTTP 请求转换、日志、DbSql 以及 Zbp 主类的魔术方法与生命周期钩子。所有钩子集中注册于 `zb_system/function/c_system_plugin.php`（下文行号即该文件行号）。

## 调试与错误处理

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Debug_Handler` | 481 | — | **1.7.3 已废弃，不应再使用** |
| `Filter_Plugin_Debug_Handler_ZEE` | 492 | `$zee`（ZbpErrorException）, `$debug_type` | 定义 `Debug_Exception_Handler` / `Debug_Error_Handler` 的接口 |
| `Filter_Plugin_Debug_Handler_Common` | 503 | `int $errno, string $errstr, string $errfile, int $errline` | 是 `Filter_Plugin_Zbp_ShowError` 的替代品，无须改动插件函数参数 |
| `Filter_Plugin_Debug_Display` | 514 | `$zec`（ZbpErrorContrl） | `ZBlogException::Display` 的接口（与 Handler 区别：传入的是错误控制类而非异常类） |

触发位置参考：`zb_system/function/c_system_debug.php` 第 139/163/172/181/209/229/237/246/273/288/296/305 行。

## 自动加载 / HTTP / 日志

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Autoload` | 525 | `$classname` | 监控 `autoload` 魔术方法 |
| `Filter_Plugin_Http_Request_Convert_To_Global` | 536 | `$request` | `http_request_convert_to_global()` 函数内触发 |
| `Filter_Plugin_Logs` | 547 | `$s, $iserror` | 监控记录函数（zb_system/function/c_system_common.php:2471 触发） |

## DbSql

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_DbSql_Filter` | 561 | `$method, $args` | DbSql 类的 SQL 过滤和统计方法接口 |

## Zbp 主类魔术方法与生命周期

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Zbp_Call` | 575 | `$method, $args` | Zbp 类 `__call` 魔术方法接口 |
| `Filter_Plugin_Zbp_Get` | 586 | `$name` | Zbp 类 `__get` 魔术方法接口 |
| `Filter_Plugin_Zbp_Set` | 597 | `$name, $value` | Zbp 类 `__set` 魔术方法接口 |
| `Filter_Plugin_Zbp_CheckRights` | 608 | `$action` | 检查当前用户权限接口 |
| `Filter_Plugin_Zbp_ShowError` | 619 | — | **1.7.3 已废弃**，请改用 `Filter_Plugin_Debug_Handler_Common`，参数不变 |
| `Filter_Plugin_Zbp_ShowValidCode` | 630 | `$id` | 显示验证码接口，具有唯一性 |
| `Filter_Plugin_Zbp_CheckValidCode` | 641 | `$vaidcode, $id` | 比对验证码接口，具有唯一性 |
| `Filter_Plugin_Zbp_BuildTemplate` | 652 | `$template` | 重新编译模板接口 |
| `Filter_Plugin_Zbp_MakeTemplatetags` | 663 | `$template` | 生成模板标签接口 |
| `Filter_Plugin_Zbp_BuildModule` | 674 | — | 生成模块内容的接口 |
| `Filter_Plugin_Zbp_RegBuildModules` | 685 | — | 注册模块时的接口 |
| `Filter_Plugin_Zbp_PreLoad` | 696 | — | 预加载接口 |
| `Filter_Plugin_Zbp_Load` | 707 | — | 加载接口 |
| `Filter_Plugin_Zbp_Load_Pre` | 718 | — | 加载（预处理）接口 |
| `Filter_Plugin_Zbp_PrepareTemplate` | 729 | `&$theme, &$template_dirname` | `PrepareTemplate` 接口，可更换主题/模板目录 |
| `Filter_Plugin_Zbp_LoadManage` | 741 | — | 后台管理初始加载接口 |
| `Filter_Plugin_Zbp_Terminate` | 752 | — | 终结接口 |
| `Filter_Plugin_Zbp_CheckSiteClosed` | 763 | — | 跳出关站检查接口 |

## 模板编译（Template 类）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Template_Compiling_Begin` | 2744 | `$this, $content` | Template 类编译一个模板**前**的接口 |
| `Filter_Plugin_Template_Compiling_End` | 2755 | `$this, $content` | Template 类编译一个模板**后**的接口 |
| `Filter_Plugin_Template_GetTemplate` | 2766 | `$this, $name` | Template 类读取一个模板前的接口 |
| `Filter_Plugin_Template_Display` | 2777 | `$this, $entryPage` | Template 类显示接口 |
| ~~`Filter_Plugin_Template_MakeTemplatetags`~~ | 2788 | — | 该行被注释掉，**未启用**，不要挂载 |

## 其它（系统级杂项）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_CSP_Backend` | 2870 | `&$xml`（源码注释如此，实际为 `&$csp` 数组） | 后台 CSP(Content-Security-Policy) 接口，1.5.2 加入 |
| `Filter_Plugin_App_Pack` | 2733 | `$this, $this->dirs, $this->files` | App 类 `Pack` 方法接口（打包应用时触发） |
