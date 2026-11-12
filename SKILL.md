---
name: zblogphp-agent-skills
version: 1.0.8
display_name: Z-BlogPHP主题与插件开发
display_name_en: Z-Blog PHP Theme & Plugin Development
description: 创建和修改 Z-Blog PHP 插件与主题；当用户提到 Z-Blog PHP、zblogphp、zblog、zbp、zb_system、zb_users，或要求实现插件、主题、模板、Hook、数据库、API、后台、安全相关功能时使用。按任务路由到对应专题参考。
description_zh: zblogphp 主题、插件与扩展开发的统一入口。创建和修改插件与主题，覆盖 Hook 钩子、数据库与配置、API、后台页面、安全与权限，按任务路由到对应专题参考。当用户提到 Z-Blog PHP、zblogphp、zblog、zbp、zb_system、zb_users，或要求制作/修改插件、主题、模板、钩子、接口、后台功能时使用。
description_en: Create and modify Z-BlogPHP plugins and themes — covering hooks, database & config, API, admin pages, security and permissions, routed to the matching topic reference. Use when users mention Z-BlogPHP, zblogphp, zblog, zbp, zb_system, zb_users, or ask to build/modify plugins, themes, templates, hooks, APIs or admin features.
examples_zh:
  - "帮我创建一个 Z-BlogPHP 用户中心插件"
  - "开发一个民宿主题"
  - "主题的文章页打开是空白，帮我排查"
examples_en:
  - "Create a Z-BlogPHP user center plugin for me"
  - "Build a guesthouse theme"
  - "My theme's article page is blank, help me debug it"
---

# zblogphp-agent-skills

这是 Z-BlogPHP 开发的唯一入口技能。插件、主题、Hook、数据库、API、后台和安全资料都在本技能的 `references/` 下；不要寻找或调用其他同名顶层技能。

## 全局配置（唯一配置点）

创建主题或插件时，需要先配置应用信息。配置存放在技能目录下的 `config.local.md`（私有文件，不随技能公开分发），所有子技能和脚本从这里读取。

### 首次配置流程（config.local.md 不存在或缺少必填项时，作为任务第一步执行）

1. 一次性向用户询问以下信息，不得猜测、不得使用示例值：
   - 应用ID（例如 ytecn_myplugin），给用户推荐3-5个候选值。符合 `/^[A-Za-z0-9_]{3,30}$/`，格式为「品牌/作者标识 + `_` + 功能或主题主体名」。
   - 应用名称（例如 MyPlugin），给用户推荐3-5个候选值。
   - 作者（例如 YTECN）
   - 作者网站（选填，例如 https://www.ytecn.com）
2. 将用户提供的值写入技能目录下的 `config.local.md`，格式：

```markdown
| 配置项 | 变量名 | 值 |
|---|---|---|
| 应用ID | id | <应用ID> |
| 应用名称 | name | <应用名称> |
| 作者 | author-name | <作者> |
| 作者网站 | author-url | <作者网站> |
| 静态检查 | static-check | on |

静态检查默认开启；把 `static-check` 设为 `off` 后，跳过交付前的所有静态检查（`php -l`、模板配平、语言包键、资源引用），由用户自行检查。

## 应用清单

| 应用ID | 类型 | 名称 | 创建日期 | 备注 |
|---|---|---|---|---|
| <应用ID> | <plugin或theme> | <应用名称> | <日期> | <一句话用途/行业> |
```

3. 写入后继续执行本次任务

### 新建应用前更新配置

每创建一个新的插件或主题，按以下顺序执行：

1. 先读 `config.local.md` 的「应用清单」：确认新应用 ID 不与已有应用重复；同一站点或作者已有同类型应用时，触发「系列应用独立性」约束（见 [application-conventions.md](references/application-conventions.md)），新应用必须独立设计，禁止套壳。
2. 更新配置表中的应用 ID 和应用名称（作者、作者网站通常不变，可沿用）。若沿用旧 ID 会导致生成的目录与已有应用冲突。
3. 生成骨架完成后，把新应用登记进「应用清单」，作为后续任务的既有应用记录。


## 总原则

- 技能正文与按需读取的专题 references 是实现依据，已整理的知识直接使用，不回查核心源码、默认主题或其他插件/主题来核实。源码路径、行号和真实应用名称只是溯源或示例，不是读取清单。
- 只读取任务目标文件、必要环境信息和功能所需参考，不扫描无关应用。
- 创建或修改主题、插件时读一次 [主题与插件共同约定](references/application-conventions.md)；纯查询、纯排错任务不读。
- 每个主题、插件必须独立设计实现：禁止复制既有应用换名套壳（`cp -r` 改 ID、照搬结构改前缀和配色）；新主题先做信息架构和设计语言，再写模板，汇报前确认与既有应用无复制关系（见共同约定「系列应用独立性」）。
- 专题资料中的排错、验证和审计章节只在用户明确要求时使用；实现要点用于编写时参考。
- 产物是站点内的标准应用目录：主题对应 [theme-structure.md](references/zblogphp-theme-development-theme-structure.md#主题目录结构与-themexml)，插件对应 [plugin-structure.md](references/zblogphp-plugin-development-plugin-structure.md#目录结构)；完成后的说明内容按共同约定「读取与交付边界」执行。

## 前置条件

- 生成骨架和检查脚本需要 Python 3；静态检查中的 `php -l` 需要本机 PHP CLI，没有时说明并跳过该项。
- 站点根目录不是必须的。用户给出站点根时，建议直接把工作区设为该目录：既能定位插件、主题目录和已有应用，生成的应用也会放到正确位置。未给出时，由用户指定生成目录。
- 技能目录必须可写，`config.local.md` 写在这里；不可写时说明原因，由用户指定配置位置。
- 不要求提前了解 Z-BlogPHP：所需知识在 references 中按需提供；模板语法、Hook 等概念以文档为准，不按其他 CMS 的经验推断。

## 适用边界与异常输入

- 只处理 Z-BlogPHP 站点内的插件、主题、模板与扩展开发。目标是 WordPress、Typecho 等其他程序时，说明本技能不适用，不套用这些规则。
- 站点根无法确定时，按路由表读取 `zblogphp-project-triage-SKILL.md` 识别一次；仍缺少 `zb_system/function/c_system_base.php` 等特征就问用户要站点根，不猜测路径、不搜索无关目录。
- 应用 ID 不符合 `/^[A-Za-z0-9_]{3,30}$/`、与 `config.local.md` 应用清单或目标目录中已有应用重复时，说明原因并重新给 3-5 个候选让用户确认，不擅自改名，不覆盖已有目录。
- 用户拒绝提供必填配置或多次给出的值都不可用时，停下说明缺哪一项、为什么无法继续，不用示例值或猜测值代替。
- 路由表中没有与当前任务匹配的专题时，选最接近的一个流程文件继续，仍无法判断就直接问用户；不改为通读 `references/` 或全库搜索。
- 目标文件不存在、路径只读或写入失败时，说明具体路径和原因后停下，不建平行副本绕过。

## 按需加载（渐进式披露）

资料分三层，用到哪一层才读哪一层，不要预先读完：

| 层级 | 读什么 | 时机 |
|---|---|---|
| 第一层 | 本文件的路由表 | 任务开始时 |
| 第二层 | 对应的那**一个** `references/zblogphp-*-SKILL.md` | 判定任务类型后 |
| 第三层 | 第二层文档在具体步骤里链接的文件 | 执行到该步骤时 |

- 禁止预先读取整个 `references/` 目录，禁止为了“了解全貌”批量打开同目录的 `.md`。
- 动手写代码前，第三层最多先读 1~2 个文件；后续步骤需要哪个再读哪个。
- 跨领域只补读实际用到的那一份，不整套转读。
- 排错、验证、审计章节只在用户明确要求时使用。

## 一次识别与按需路由

目录类型未知时才识别一次；复用已有的路径和应用信息，不重复扫描、询问或播报。每行只读“先读的参考”列出的那一个文件。

| 当前任务 | 先读的参考 |
|---|---|
| 项目结构不明、需要识别站点根/插件/主题 | `references/zblogphp-project-triage-SKILL.md`；需要脚本时使用 `scripts/detect_zblog_project.mjs` |
| 新建、修改或排查插件 | `references/zblogphp-plugin-development-SKILL.md` |
| 插件前台页面、URL 路由、前台登录与注册、入口可发现性 | `references/zblogphp-plugin-development-frontend-pages.md` |
| 新建、修改或排查主题、模板、侧栏 | `references/zblogphp-theme-development-SKILL.md` |
| 查询或使用 Filter 钩子 | `references/zblogphp-hooks-reference-SKILL.md` |
| 数据库、SQL、模型、Config、Meta | `references/zblogphp-database-SKILL.md` |
| API、`mod`、`act`、`ApiDispatch` | `references/zblogphp-api-SKILL.md` |
| 后台页面、菜单、命令、CSRF token | `references/zblogphp-admin-SKILL.md` |
| XSS、SQL 注入、CSRF、权限和转义 | `references/zblogphp-security-SKILL.md` |
| 危险函数、全局符号命名、phpver 兼容、资源本地化、前端多端适配等代码质量要求 | `references/zblogphp-code-quality.md` |
| 本地实测、切换主题渲染、内置服务器、无头截图（仅用户明确要求测试/排错时） | `references/zblogphp-local-testing.md` |

以主任务选择专题，跨领域只补读实际需要的资料。

## 开发主干

新建应用时按以下顺序执行，具体步骤见对应专题文件：

1. 按「全局配置」确认应用 ID、名称、作者，并登记到应用清单。
2. 读流程文件：[插件开发](references/zblogphp-plugin-development-SKILL.md#实现流程)或[主题开发](references/zblogphp-theme-development-SKILL.md#实现流程)。
3. 用 `scripts/create_app.py` 生成骨架，不手工拼装目录和 XML。
4. 按功能逐步补代码，需要哪一步的细节才读该步骤链接的文件。
5. 对本次新建或修改的文件执行静态检查（`config.local.md` 的 `static-check` 为 `off` 时跳过），然后按「读取与交付边界」汇报。
