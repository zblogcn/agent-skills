# 插件开发

## 实现流程

### 1. 创建插件骨架

确保已按主技能 `SKILL.md` 的「全局配置」完成 `config.local.md`（含应用 ID、名称、作者等）。用 `scripts/create_app.py` 生成骨架（命令见 [plugin-structure.md](zblogphp-plugin-development-plugin-structure.md#新建方式)），脚本会自动从 `config.local.md` 读取 ID、名称、作者、作者网站，无需重复传参；命令行参数可覆盖配置值。脚本会创建目录、plugin.xml、include.php、logo.png、main.php 和三份语言包；plugin.xml 各字段含义查 [plugin-structure.md](zblogphp-plugin-development-plugin-structure.md)。

### 2. 注册与生命周期

在 include.php 中用 RegisterPlugin() 注册激活函数，在激活函数中用 Add_Filter_Plugin() 挂钩；按需实现 InstallPlugin_{ID} 和 UninstallPlugin_{ID}。详细加载时机、信号量和骨架见 lifecycle.md。

### 3. 配置

用 Config('ID')->key = value 写入内存，随后 $zbp->SaveConfig('ID') 持久化；禁用时按需求调用 $zbp->DelConfig('ID')。完整方法见 config.md。

### 4. 后台管理页

按 [admin-page.md](zblogphp-plugin-development-admin-page.md) 处理管理页权限、插件启用状态、CSRF、后台页头尾和重定向。注意脚本生成的 `main.php` 只有权限校验空壳（`<!--代码-->` 空注释），不要照抄空壳；实现配置页时按 admin-page.md「管理页标准骨架」补全表单、csrfToken 隐藏域和 `$zbp->Config` 读写。

### 5. 交付前静态检查

按 [共同约定「读取与交付边界」](application-conventions.md#读取与交付边界) 默认执行零成本静态检查并修复问题：全部 PHP 文件 `php -l`；语言包三包键一致且代码引用的语言键都有定义（用 `python scripts/check_lang_keys.py <插件目录>` 检查）；引用的本地资源路径存在、无站外资源。静态检查结果随交付说明一并汇报；运行时实测只在用户明确要求时进行（手段见 [本地开发与实测](zblogphp-local-testing.md)）。

## 按症状排错

| 现象 | 原因 / 排查方向 |
|---|---|
| 插件不出现在管理列表 | 目录名与 plugin.xml 的 id 不一致，或 XML 无法解析；对照 plugin-structure.md。 |
| 启用时报不兼容 | adapted、phpver、依赖或冲突声明不符合目标环境；修改已有插件时沿用原值，只有用户要求排错才处理兼容性。 |
| 钩子不触发 | 插件未启用、激活函数未挂接、回调名或钩子名不一致；对照 Hook reference。 |
| 启用后安装函数没跑 | 函数名必须严格为 InstallPlugin_{ID}，且定义在 include.php。 |
| 管理页 403 / 报错 6 | 权限等级、CheckRights 或 CheckPlugin 缺失或不匹配。 |
| 配置保存后丢失 | 修改 Config 后忘记调用 $zbp->SaveConfig('ID')。 |
| include.php 导致白屏 | 引导阶段只应注册和定义，不应直接输出；检查 PHP 文件守卫与代码。 |
