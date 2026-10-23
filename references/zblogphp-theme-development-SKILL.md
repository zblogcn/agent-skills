# 主题开发

## 硬约束：每个主题独立设计，禁止套壳

这条规则优先于后续所有步骤：

- 禁止 `cp -r` 既有主题后替换 ID、变量名和文案；禁止照搬既有主题的模板结构、只改 class 前缀和配色；禁止把同一套模板母版换皮成多个主题。
- 每个主题从脚本生成的空白 `template/` 目录开始，按本次目标站点的信息架构重新设计。
- 不同主题之间，导航组织、栅格节奏、列表页与文章页排版应当有可辨认的差异。
- 完成后向用户汇报前，必须确认新主题与站点内既有主题不存在模板复制关系。规则全文见 [主题与插件共同约定「系列应用独立性」](application-conventions.md#系列应用独立性禁止套壳)。

## 实现流程

### 1. 设计先行（动手写模板之前完成）

先明确设计决策，再生成骨架和写代码：

- 目标站点的行业、受众和主要内容类型（如门店展示、内容资讯、图文作品、商品导购）。
- 页面清单：首页、列表、文章、单页、搜索、404 分别承载什么内容模块。
- 信息架构：导航如何组织（顶部/侧边、单级/多级、是否带搜索入口）、栅格节奏（栏数、侧栏有无与位置、卡片密度）、列表页排版（卡片/列表/瀑布流等，只选与内容匹配的）、文章页排版（标题区、元信息、正文宽度、目录、相关内容）。
- 视觉方向：配色、字体层级、间距节奏，与同站点既有主题拉开差异。

站点内已有同类型主题时，逐项写出新主题的不同决策，不允许"先复制再慢慢改"。

### 2. 创建主题骨架

确保已按主技能 `SKILL.md` 的「全局配置」完成 `config.local.md`（含应用 ID、名称、作者等）。用 `scripts/create_app.py` 生成骨架（命令见 [theme-structure.md](zblogphp-theme-development-theme-structure.md#新建方式)），脚本会自动从 `config.local.md` 读取 ID、名称、作者、作者网站，无需重复传参；命令行参数可覆盖配置值。脚本会创建目录、theme.xml、include.php、screenshot.png、template.json、style.css 和三份语言包；theme.xml 各字段含义查 [theme-structure.md](zblogphp-theme-development-theme-structure.md)。脚本结束时的独立性提醒即第 1 步的硬约束。

### 3. 模板与页面对应

按 template-hierarchy.md 从页面类型选择模板，再按 template-syntax.md 编写标签。对象属性和页面变量查 template-vars.md。主题只提供与默认行为不同的模板文件，缺失文件由运行时回落机制处理。

### 4. 侧栏和模块

按 modules-sidebars.md 设置 theme.xml 的 9 组侧栏、模板中的 sidebar 系列变量和模块模板。

### 5. include.php 与主题功能

主题按插件机制注册，按需挂接模板变量和页面 Hook；注册、配置、文章动态字段和常用扩展见 [theme-functions.md](zblogphp-theme-development-theme-functions.md)。

### 6. 交付前静态检查

按 [共同约定「读取与交付边界」](application-conventions.md#读取与交付边界) 默认执行零成本静态检查并修复问题：全部 PHP 文件 `php -l`；模板 `{if}`、`{foreach}` 等成对标签逐个配平（用 `python scripts/check_template_tags.py <主题目录>` 检查，漏写闭合不会报错、只会静默吞内容）；`{template:}` 引用的文件存在；语言包三包键一致且模板引用的语言键都有定义（用 `python scripts/check_lang_keys.py <主题目录>` 检查）；本地资源路径存在、无站外资源。静态检查结果随交付说明一并汇报；运行时实测只在用户明确要求时进行（手段见 [本地开发与实测](zblogphp-local-testing.md)）。

## 按症状排错

- 页面某块内容静默消失或条件分支错乱，且无任何报错：大概率是模板漏写了 `{/if}`、`{/foreach}` 等闭合标签，编译器非贪婪配对把后续内容吞进上一个标签块；用 `python scripts/check_template_tags.py <主题目录>` 定位（机制见 template-syntax.md 条件一节）。
- 模板编译后页面直接 500，编译产物里有 `$article.Title` 这类点号写法：点号转 `->` 只在模板表达式里生效，`{php}` 块内不转换，块内必须写 `$article->Title`（见 template-syntax.md 变量一节）。
- 日期归档页 `{$date}` 输出报错：`$date` 是 Metas 对象不是字符串，归档标题用 `{$title}`（见 template-hierarchy.md 列表页类型表）。
- 模板修改不生效：按模板层级定位文件；必要时由用户重建编译缓存。
- 模板标签原样输出：对照 template-syntax.md 修正标签空格、属性分隔和方法调用。
- 变量为空：确认当前页面是否提供该变量，并对照 template-hierarchy.md。
- 后台选不到新模板：在 template.json 声明正确的 filename 和 type。
- include.php 报错导致白屏：检查注册、语言加载、Hook 回调和防直接访问守卫。
- theme.xml 识别异常：保持 id、目录名和 RegisterPlugin() ID 完全一致。
- 侧栏不显示：检查模块文件名是否存在于 $zbp->modulesbyfilename。
