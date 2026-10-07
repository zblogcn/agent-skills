# 后台开发

Z-BlogPHP 后台由两层入口构成：zb_system/cmd.php 负责动作请求，zb_system/admin/ 负责页面渲染。扩展后台通过插件钩子完成，不改 zb_system 核心文件。

## 实现流程

### 1. 动作请求

所有后台写操作走 cmd.php?act=XXX。读取 act 后先做 CheckRights，再由 switch 分发；插件可通过 Filter_Plugin_Cmd_Begin、Filter_Plugin_Cmd_End 和 Filter_Plugin_Cmd_Ajax 介入。动作样式和安全 URL 见 references/cmd-actions.md。

### 2. 页面渲染

admin/index.php 按 act 分发到 Admin_* 函数，未匹配动作交给 Filter_Plugin_Admin_Other_Action。编辑类页面使用独立入口；页面框架为 admin_header、admin_top、正文和 admin_footer。详见 references/admin-pages.md。

### 3. 菜单与子菜单

左侧菜单使用 Filter_Plugin_Admin_LeftMenu，顶部菜单使用 Filter_Plugin_Admin_TopMenu，各管理页和编辑页有对应 SubMenu 钩子。MakeLeftMenu、MakeTopMenu、MakeSubMenu 会按权限过滤。详见 references/menus.md 和 references/icons.md。

### 4. 安全

GET 写操作链接用 BuildSafeCmdURL()；自定义 POST 调用 CheckCSRFTokenValid() 或 CheckIsRefererValid()；新动作注册所需 action 并调用 CheckRights。安全细节见 ../zblogphp-security/。

## 按症状排错

- 直接输出页面而不走后台入口钩子：丢失 CSRF meta 和 CSP 头。
- 自定义 act 未注册 action：CheckRights 失败并报错误 6。
- AJAX 忘记 ZBP_IN_AJAX：Redirect 行为异常，应使用 JsonError/exit 结束。
