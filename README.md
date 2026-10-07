# Z-BlogPHP Agent Skills

面向 AI 编码助手（Claude Code / Cursor / Codex / Trae 等）的 Z-BlogPHP 开发技能。统一入口技能为 `zblogphp-agent-skills`，覆盖项目识别、主题、插件、模板、Hook、数据库、API、后台和安全开发。

技能正文与按需读取的 references 是开发依据，已整理的知识直接使用。

## 功能

| 领域 | 用途 |
|---|---|
| 项目识别 | 识别站点根、插件目录和主题目录；含检测脚本 |
| 插件开发 | 插件结构、生命周期、配置和管理页 |
| 主题开发 | 主题结构、模板、变量、层级、侧栏和主题函数 |
| Hook 参考 | Filter 钩子分类、参数与用法 |
| 数据库 | 模型、SQL、Schema、Config/Meta |
| API | API 结构、模块和自定义端点 |
| 后台 | 菜单、页面、命令、CSRF 和图标 |
| 安全 | XSS、SQL 注入、CSRF、权限和转义 |

## 创建主题或插件

技能内置 `scripts/create_app.py`，可一键生成插件或主题骨架。

### 配置应用信息

创建前先在技能根目录准备 `config.local.md`（私有文件，不随技能分发），格式：

```markdown
| 配置项 | 变量名 | 值 |
|---|---|---|
| 应用ID | id | <应用ID> |
| 应用名称 | name | <应用名称> |
| 作者 | author-name | <作者> |
| 作者网站 | author-url | <作者网站> |
```

每做一个新应用，需更新其中的应用 ID 和应用名称（作者、作者网站可沿用）。

### 生成骨架

```bash
# 插件（自动读取 config.local.md）
python scripts/create_app.py -t plugin

# 主题
python scripts/create_app.py -t theme

# 也可用命令行参数覆盖配置
python scripts/create_app.py -t plugin -i MyPlugin -n "示例插件" -a "作者"
```

脚本会生成目录、XML、include.php、语言包（英/简中/繁中）、logo/screenshot 等完整骨架，与官方 AppCentre「新建插件/主题」结果一致。

## 主题与插件共同约定

共同规则维护在 [`references/application-conventions.md`](references/application-conventions.md)，包括 PHP 文件守卫、三种语言包、icon 字体、禁止 SVG、交付边界等。

## 目录结构

```text
zblogphp-agent-skills/
├── SKILL.md
├── README.md
├── scripts/
│   ├── create_app.py              # 主题/插件骨架生成器
│   ├── detect_zblog_project.mjs   # 站点/插件/主题目录识别脚本
│   ├── include.html               # AppCentre 骨架模板
│   ├── main.html                  # AppCentre 后台页骨架模板
│   ├── plugin.png                 # 插件默认 logo
│   └── theme.png                  # 主题默认截图
└── references/
    ├── application-conventions.md
    ├── zblogphp-project-triage/
    ├── zblogphp-plugin-development/
    ├── zblogphp-theme-development/
    ├── zblogphp-hooks-reference/
    ├── zblogphp-database/
    ├── zblogphp-api/
    ├── zblogphp-admin/
    └── zblogphp-security/
```

## 适用版本

- Z-Blog PHP 1.7.x（基于已整理的 1.7.5 资料）
- PHP 5.6+（Z-Blog PHP 1.7 要求）

## 官方资源

- 官网与应用中心：https://www.zblogcn.com/
- 官方文档：https://docs.zblogcn.com/
- 源码仓库：https://github.com/zblogcn/zblogphp
