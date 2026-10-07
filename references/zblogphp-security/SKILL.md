# 安全开发

Z-BlogPHP 安全模型围绕 CSRF/Referer 校验、FormatString 转义、DbSql 参数化和 action 权限控制。

## 实现流程

1. CSRF：后台写操作使用 CheckIsRefererValid、CheckCSRFTokenValid 或 BuildSafeCmdURL；表单输出 csrfToken。登录按登录专用 CSRF 规则处理。详见 references/csrf.md。
2. XSS：用户输入和模板输出按 FormatString、htmlspecialchars 或 XssHtml 处理；模板标签不会自动转义。详见 references/xss-escaping.md。
3. SQL：使用 DbSql 构造器和转义参数，禁止拼接外部输入；排序、分页也使用构造器。详见 references/sql-injection.md。
4. 权限：用 CheckRights 校验 action，新增 action 先注册；菜单辅助函数自带权限过滤。详见 references/permissions.md。
5. 上传：按扩展名白名单、大小和服务端重命名规则处理。
6. 应用 PHP 文件守卫见[共同约定](../application-conventions.md#php-文件守卫)。

## 按症状排错

- 表单缺 csrfToken：提交报 ShowError(5)。
- GetVars 值直接拼 SQL：存在注入风险。
- 模板直接输出评论内容：可能形成存储型 XSS。
- 自定义 AJAX 绕开 cmd.php：丢失 ZBP_PATH 防护和统一安全流程。
