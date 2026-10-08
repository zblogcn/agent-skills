# 主题开发

## 实现流程

### 1. 创建主题骨架

确保已按主技能 `SKILL.md` 的「全局配置」完成 `config.local.md`（含应用 ID、名称、作者等）。用 `scripts/create_app.py` 生成骨架（命令见 [theme-structure.md](zblogphp-theme-development-theme-structure.md#新建方式)），脚本会自动从 `config.local.md` 读取 ID、名称、作者、作者网站，无需重复传参；命令行参数可覆盖配置值。脚本会创建目录、theme.xml、include.php、screenshot.png、template.json、style.css 和三份语言包；theme.xml 各字段含义查 [theme-structure.md](zblogphp-theme-development-theme-structure.md)。

### 2. 模板与页面对应

按 template-hierarchy.md 从页面类型选择模板，再按 template-syntax.md 编写标签。对象属性和页面变量查 template-vars.md。主题只提供与默认行为不同的模板文件，缺失文件由运行时回落机制处理。

### 3. 侧栏和模块

按 modules-sidebars.md 设置 theme.xml 的 9 组侧栏、模板中的 sidebar 系列变量和模块模板。

### 4. include.php 与主题功能

主题按插件机制注册，按需挂接模板变量和页面 Hook；注册、配置、文章动态字段和常用扩展见 [theme-functions.md](zblogphp-theme-development-theme-functions.md)。

## 按症状排错

- 模板修改不生效：按模板层级定位文件；必要时由用户重建编译缓存。
- 模板标签原样输出：对照 template-syntax.md 修正标签空格、属性分隔和方法调用。
- 变量为空：确认当前页面是否提供该变量，并对照 template-hierarchy.md。
- 后台选不到新模板：在 template.json 声明正确的 filename 和 type。
- include.php 报错导致白屏：检查注册、语言加载、Hook 回调和防直接访问守卫。
- theme.xml 识别异常：保持 id、目录名和 RegisterPlugin() ID 完全一致。
- 侧栏不显示：检查模块文件名是否存在于 $zbp->modulesbyfilename。
