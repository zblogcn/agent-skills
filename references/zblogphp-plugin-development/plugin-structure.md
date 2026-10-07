# 插件目录结构与 plugin.xml 全字段说明

## 新建方式

用脚本生成骨架。在技能根目录执行：

```bash
python scripts/create_app.py -t plugin -i <应用ID> -n "<应用名称>" -a "<作者>"
```

脚本会在 `-o` 指定目录（默认当前目录）下生成 `<应用ID>/` 骨架，包含 `plugin.xml`、`include.php`（已注入 `$zbp->LoadLanguage('plugin', 'ID')`）、`logo.png`、`main.php` 和三份语言包。需要无管理页的插件加 `--no-admin`。若已在 `config.local.md` 配置 ID、名称、作者等，可省略 `-i`/`-n`/`-a`/`--url`。

不使用脚本时，按[共同约定](../application-conventions.md)准备应用副本后，补充插件内容：

1. 按下文字段表写入 `plugin.xml`。
2. 按 [lifecycle.md](lifecycle.md) 在复制的 `include.php` 中添加插件注册、钩子和生命周期逻辑。
3. 需要管理页时，按 [admin-page.md](admin-page.md) 在复制的 `main.html` 副本中添加表单与功能，并让 `<path>` 指向该文件。

## 目录结构

插件位于 `zb_users/plugin/{ID}/` 下，目录名即插件 ID（大小写敏感）。最小骨架与完整骨架：

```
zb_users/plugin/{ID}/              # 最小骨架
├── plugin.xml                     # 必需：插件声明
├── include.php                    # 必需：注册插件、挂钩子
├── logo.png                       # 必需：后台插件列表图标
├── language/                      # 默认提供三种语言
│   ├── en.php                     # 英文
│   ├── zh-cn.php                  # 简体中文
│   └── zh-tw.php                  # 繁体中文
└── main.php                       # 可选：后台管理页（对应 plugin.xml 的 path）

zb_users/plugin/{ID}/              # 按需扩展后的结构
├── plugin.xml
├── include.php
├── logo.png
├── main.php / setting.php / app_pack.php / ...   # 多个后台页面
├── function.php                   # 插件自有函数库
├── language/                      # 语言包目录：zh-cn.php / zh-tw.php / en.php
├── tpl/                           # 模板片段
└── images/
```

## 语言包

文件格式、加载和文案引用见[共同语言包约定](../application-conventions.md#语言包)。

## 关键约束

- 目录名必须与 `plugin.xml` 的 `<id>` 完全一致。启用时把 ID 写入 `ZC_USING_PLUGIN_LIST`，引导阶段按 ID 拼路径找 `plugin/{ID}/plugin.xml` 与 `include.php`（`zb_system/function/c_system_base.php` L288-295）；不一致则插件既不出现也无法启用。
- 插件列表扫描的是目录（`ZBlogPHP::LoadPlugins()`，`zb_system/function/lib/zblogphp.php` L2082-2096），再把每个目录交给 `App::LoadInfoByXml('plugin', $id)` 解析。

## plugin.xml 示例

`MyPlugin`、名称、作者和版本等均为示例值，生成时使用当前任务已确定的信息。

```xml
<?xml version="1.0" encoding="utf-8"?>
<plugin version="php">
<id>MyPlugin</id>
<name>示例插件</name>
<url></url>
<note>插件功能简介</note>
<description></description>
<path>main.php</path>
<include>include.php</include>
<level>1</level>
<author>
  <name>作者名称</name>
  <email></email>
  <url></url>
</author>
<source>
  <name></name>
  <email></email>
  <url></url>
</source>
<adapted>140614</adapted>
<version>1.4</version>
<pubdate>2013-07-07</pubdate>
<modified>2020-06-14</modified>
<price>0</price>
<advanced>
  <dependency></dependency>
  <rewritefunctions></rewritefunctions>
  <conflict></conflict>
</advanced>
<sidebars>
  <sidebar1></sidebar1>
  <sidebar2></sidebar2>
  <sidebar3></sidebar3>
  <sidebar4></sidebar4>
  <sidebar5></sidebar5>
  <sidebar6></sidebar6>
  <sidebar7></sidebar7>
  <sidebar8></sidebar8>
  <sidebar9></sidebar9>
</sidebars>
</plugin>
```

还可按需设置 `<phpver>` 和 `<advanced>` 下的 `<existsfunctions>`；`sidebars` 有 9 项，通常留空。

## 字段说明（与解析代码一一对应）

解析代码：`App::LoadInfoByXml()`，`zb_system/function/lib/app.php` L376-456。

| 字段 | 说明 |
|---|---|
| 根元素 `<plugin version="php">` | `version` 属性必须为 `php`，否则解包/加载被拒 |
| `id` | 插件 ID，必须等于目录名 |
| `name` | 显示名称 |
| `url` | 插件主页链接 |
| `note` | 一句话简介（后台列表显示） |
| `description` | 详细描述 |
| `path` | 后台管理入口文件名（相对插件目录），如 `main.php`/`setting.php`；留空则插件无「管理」按钮（`App::CanManage()` L249-256）。详见 admin-page.md |
| `include` | include 文件名，通常为 `include.php` |
| `level` | 访问管理页所需的用户等级（1=管理员） |
| `author` (name/email/url) | 作者信息 |
| `source` (name/email/url) | 原作/来源信息（可留空） |
| `adapted` | 适配的 Z-BlogPHP 版本 build 号（如 `140614`=1.3、`172900`=1.7.0、`173400`=1.7.4）。启用时若 `adapted > 当前版本` 报不兼容 |
| `version` | 插件自身版本号（字符串，如 `2.85`） |
| `pubdate` / `modified` | 发布/更新日期 |
| `price` | 价格，`0` 为免费；>0 时启用前需应用中心购买验证 |
| `phpver` | 要求的最低 PHP 版本，缺省视为 `5.2`；高于当前 PHP 版本则拒绝启用（L798-804） |
| `advanced/dependency` | 依赖的其他应用 ID，`\|` 分隔；依赖未启用则本插件不能启用（L819-830） |
| `advanced/rewritefunctions` | 声明要重写的系统函数 |
| `advanced/existsfunctions` | 要求已存在的函数名，`\|` 分隔；任一不存在则不能启用（L806-817） |
| `advanced/conflict` | 冲突应用 ID，`\|` 分隔；冲突应用已启用则本插件不能启用，反之其他应用声明与本插件冲突也会阻止本插件启用（`CheckCompatibility_Global()` L852-889） |
| `sidebars/sidebar1..9` | 侧栏相关内容（历史遗留，通常留空） |

启用/禁用时的兼容性检查入口：`EnablePlugin()` / `DisablePlugin()`，`zb_system/function/c_system_event.php` L2085-2146，会先调用 `CheckCompatibility_Global()` 与 `CheckCompatibility()`，失败则 `ShowError`。

