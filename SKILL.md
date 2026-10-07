---
name: zblogphp-agent-skills
version: 1.0.0
display_name: Z-Blog PHP 主题与插件开发
display_name_en: Z-Blog PHP Theme & Plugin Development
description: 当用户请求涉及 Z-Blog PHP、zblogphp、zblog、zbp、zb_system 或 zb_users 的插件、主题、模板、Hook、数据库、API、后台或安全开发时使用。统一识别项目并按需读取对应专题参考，创建和修改 Z-Blog PHP 应用。
description_zh: zblogphp主题、插件与扩展开发的统一入口。覆盖插件/主题骨架生成、Hook 钩子、数据库与配置、API、后台页面、安全与权限等领域，按任务路由到对应专题参考实现。当用户提到 Z-Blog PHP、zblogphp、zblog、zbp、zb_system、zb_users，或要求制作/修改插件、主题、模板、钩子、接口、后台功能时使用。
description_en: Unified entry for zblogphp theme and plugin development. Covers skeleton generation, hooks, database & config, API, admin pages, security and permissions — routing each task to the right topic reference. Use when users mention Z-BlogPHP, zblogphp, zblog, zbp, zb_system, zb_users, or ask to build/modify plugins, themes, templates, hooks, APIs or admin features.
examples_zh:
  - "帮我创建一个 Z-BlogPHP 插件"
  - "开发一个新主题，要响应式的"
  - "给插件加个 Filter 钩子"
examples_en:
  - "Create a Z-BlogPHP plugin for me"
  - "Build a responsive theme"
  - "Add a Filter hook to my plugin"
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
```

3. 写入后继续执行本次任务

### 新建应用前更新配置

每创建一个新的插件或主题，都必须先更新 `config.local.md` 中的应用 ID 和应用名称（作者、作者网站通常不变，可沿用）。若沿用旧 ID 会导致生成的目录与已有应用冲突。更新后再执行 `scripts/create_app.py` 生成骨架。


## 总原则

- 技能正文与按需读取的专题 references 是实现依据，已整理的知识直接使用，不回查核心源码、默认主题或其他插件/主题来核实。源码路径、行号和真实应用名称只是溯源或示例，不是读取清单。
- 只读取任务目标文件、必要环境信息和功能所需参考，不扫描无关应用。
- 涉及主题、插件的制作或修改时，先读一次 [主题与插件共同约定](references/application-conventions.md)，再按下表选择专题。共同约定适用于所有专题，跨领域时继续沿用。
- 专题资料中的排错、验证和审计章节只在用户明确要求时使用；实现要点用于编写时参考。

## 一次识别与按需路由

目录类型未知时才识别一次；复用已有的路径和应用信息，不重复扫描、询问或播报。

| 当前任务 | 先读的参考 |
|---|---|
| 项目结构不明、需要识别站点根/插件/主题 | `references/zblogphp-project-triage/SKILL.md`；需要脚本时使用同目录 `scripts/detect_zblog_project.mjs` |
| 新建、修改或排查插件 | `references/zblogphp-plugin-development/SKILL.md`；再按需读插件 references |
| 新建、修改或排查主题、模板、侧栏 | `references/zblogphp-theme-development/SKILL.md`；再按需读主题 references |
| 查询或使用 Filter 钩子 | `references/zblogphp-hooks-reference/SKILL.md`；再按需读其 `references/` |
| 数据库、SQL、模型、Config、Meta | `references/zblogphp-database/SKILL.md`；再按需读其 `references/` |
| API、`mod`、`act`、`ApiDispatch` | `references/zblogphp-api/SKILL.md`；再按需读其 `references/` |
| 后台页面、菜单、命令、CSRF token | `references/zblogphp-admin/SKILL.md`；再按需读其 `references/` |
| XSS、SQL 注入、CSRF、权限和转义 | `references/zblogphp-security/SKILL.md`；再按需读其 `references/` |

以主任务选择专题，跨领域只补读实际需要的资料。专题 `SKILL.md` 是领域流程说明，专题 `references/` 是按需细节，无需一次读完。
