# 数据字典（schema 速查）

本文是已整理的 **Z-BlogPHP 1.7.5.3540** 表结构快照，开发时直接使用下文的数据字典。来源为 `zb_system/defend/datainfo.php`（字段定义，格式 `属性名 => array(真实列名, 类型, 长度, 默认值)`）、`zb_system/defend/table.php`（表名映射）和 `zb_system/defend/createtable/{mysql,sqlite,pgsql}.sql`（主键/索引）。这些路径仅用于溯源，不是重新读取或核实的步骤；其他版本的任务必需信息确实缺失时，按主技能的知识缺口规则处理。

SQL 中表名一律写 `%pre%`（如 `%pre%post`），执行时由 `DbSql::ReplacePre()` 替换为真实前缀 `$zbp->db->dbpre`（详见 [dbsql.md](dbsql.md)）。

## 0. 表总览

| datainfo 键 | 表名 | 用途 | datainfo.php 行号 | 字段数 |
|---|---|---|---|---|
| Config | `%pre%config` | 键值配置存储（插件配置等） | L4-9 | 4 |
| Post | `%pre%post` | 文章与页面 | L10-30 | 19 |
| Category | `%pre%category` | 分类 | L31-48 | 16 |
| Comment | `%pre%comment` | 评论 | L49-64 | 14 |
| Module | `%pre%module` | 模块（侧栏/自定义模块） | L65-76 | 10 |
| Member | `%pre%member` | 用户 | L77-98 | 20 |
| Tag | `%pre%tag` | 标签 | L99-113 | 13 |
| Upload | `%pre%upload` | 附件/上传文件 | L114-126 | 11 |

类型（datainfo 第 2 个元素）取值：`integer` / `string`（或 `char`）/ `boolean` / `float`，由 `Base::Save()` 按类型强制转换（base.php L486-498）。「长度」为空表示不限长（text/longtext 类列）。

## 1. Post（%pre%post）——文章与页面

datainfo.php L10-30。

| 属性名 | 真实列名 | 类型 | 长度 | 默认值 | 说明 |
|---|---|---|---|---|---|
| ID | log_ID | integer | | 0 | 主键，自增 |
| CateID | log_CateID | integer | | 0 | 所属分类 ID |
| AuthorID | log_AuthorID | integer | | 0 | 作者用户 ID |
| Tag | log_Tag | string | 250 | '' | 标签 ID 集合（`{id}` 拼接格式） |
| Status | log_Status | integer | | 0 | 状态 |
| Type | log_Type | integer | | 0 | 类型（0=文章，1=页面） |
| Alias | log_Alias | string | 250 | '' | 别名（访问 URL 用） |
| IsTop | log_IsTop | integer | | 0 | 是否置顶 |
| IsLock | log_IsLock | boolean | | false | 是否锁定（禁止评论） |
| Title | log_Title | string | 250 | '' | 标题 |
| Intro | log_Intro | string | | '' | 摘要/简介 |
| Content | log_Content | string | | '' | 正文 |
| CreateTime | log_CreateTime | integer | | 0 | 创建时间（Unix 时间戳） |
| PostTime | log_PostTime | integer | | 0 | 发布时间（Unix 时间戳） |
| UpdateTime | log_UpdateTime | integer | | 0 | 更新时间（Unix 时间戳） |
| CommNums | log_CommNums | integer | | 0 | 评论数 |
| ViewNums | log_ViewNums | integer | | 0 | 浏览数 |
| Template | log_Template | string | 250 | '' | 模板文件名 |
| Meta | log_Meta | string | | '' | Metas 序列化存储列（见特别说明） |

主键/索引（mysql.sql L21-22）：

- PRIMARY KEY (`log_ID`)
- KEY `%pre%log_TPISC` (`log_Type`, `log_PostTime`, `log_IsTop`, `log_Status`, `log_CateID`) —— 前台列表主查询走此索引

## 2. Category（%pre%category）——分类

datainfo.php L31-48。

| 属性名 | 真实列名 | 类型 | 长度 | 默认值 | 说明 |
|---|---|---|---|---|---|
| ID | cate_ID | integer | | 0 | 主键，自增 |
| Name | cate_Name | string | 250 | '' | 分类名 |
| Order | cate_Order | integer | | 0 | 排序 |
| Type | cate_Type | integer | | 0 | 类型 |
| Count | cate_Count | integer | | 0 | 文章数 |
| Alias | cate_Alias | string | 250 | '' | 别名 |
| Group | cate_Group | string | 250 | '' | 分组 |
| Intro | cate_Intro | string | | '' | 简介 |
| RootID | cate_RootID | integer | | 0 | 根分类 ID |
| ParentID | cate_ParentID | integer | | 0 | 父分类 ID |
| CreateTime | cate_CreateTime | integer | | 0 | 创建时间（Unix 时间戳） |
| PostTime | cate_PostTime | integer | | 0 | 发布时间（Unix 时间戳） |
| UpdateTime | cate_UpdateTime | integer | | 0 | 更新时间（Unix 时间戳） |
| Template | cate_Template | string | 250 | '' | 分类页模板 |
| LogTemplate | cate_LogTemplate | string | 250 | '' | 该分类文章列表模板 |
| Meta | cate_Meta | string | | '' | Metas 序列化存储列 |

主键/索引（mysql.sql L43-44）：

- PRIMARY KEY (`cate_ID`)
- KEY `%pre%cate_Order` (`cate_Order`)

## 3. Tag（%pre%tag）——标签

datainfo.php L99-113。

| 属性名 | 真实列名 | 类型 | 长度 | 默认值 | 说明 |
|---|---|---|---|---|---|
| ID | tag_ID | integer | | 0 | 主键，自增 |
| Name | tag_Name | string | 250 | '' | 标签名 |
| Order | tag_Order | integer | | 0 | 排序 |
| Type | tag_Type | integer | | 0 | 类型 |
| Count | tag_Count | integer | | 0 | 文章数 |
| Alias | tag_Alias | string | 250 | '' | 别名 |
| Group | tag_Group | string | 250 | '' | 分组 |
| Intro | tag_Intro | string | | '' | 简介 |
| CreateTime | tag_CreateTime | integer | | 0 | 创建时间（Unix 时间戳） |
| PostTime | tag_PostTime | integer | | 0 | 发布时间（Unix 时间戳） |
| UpdateTime | tag_UpdateTime | integer | | 0 | 更新时间（Unix 时间戳） |
| Template | tag_Template | string | 250 | '' | 标签页模板 |
| Meta | tag_Meta | string | | '' | Metas 序列化存储列 |

主键（mysql.sql L136）：PRIMARY KEY (`tag_ID`)，无其他索引。

## 4. Member（%pre%member）——用户

datainfo.php L77-98。

| 属性名 | 真实列名 | 类型 | 长度 | 默认值 | 说明 |
|---|---|---|---|---|---|
| ID | mem_ID | integer | | 0 | 主键，自增 |
| Guid | mem_Guid | string | 36 | '' | 用户 GUID |
| Level | mem_Level | integer | | 6 | 等级（权限级别） |
| Status | mem_Status | integer | | 0 | 状态 |
| Name | mem_Name | string | 250 | '' | 用户名 |
| Password | mem_Password | string | 250 | '' | 密码（哈希存储） |
| Email | mem_Email | string | 250 | '' | 邮箱 |
| HomePage | mem_HomePage | string | 250 | '' | 个人主页 |
| IP | mem_IP | string | 250 | '' | 注册/最后 IP |
| CreateTime | mem_CreateTime | integer | | 0 | 创建时间（Unix 时间戳） |
| PostTime | mem_PostTime | integer | | 0 | 发布时间（Unix 时间戳） |
| UpdateTime | mem_UpdateTime | integer | | 0 | 更新时间（Unix 时间戳） |
| Alias | mem_Alias | string | 250 | '' | 别名 |
| Intro | mem_Intro | string | | '' | 简介 |
| Articles | mem_Articles | integer | | 0 | 文章数 |
| Pages | mem_Pages | integer | | 0 | 页面数 |
| Comments | mem_Comments | integer | | 0 | 评论数 |
| Uploads | mem_Uploads | integer | | 0 | 附件数 |
| Template | mem_Template | string | 250 | '' | 用户页模板 |
| Meta | mem_Meta | string | | '' | Metas 序列化存储列 |

主键/索引（mysql.sql L99-102）：

- PRIMARY KEY (`mem_ID`)
- KEY `%pre%mem_Name` (`mem_Name`)、KEY `%pre%mem_Alias` (`mem_Alias`)、KEY `%pre%mem_Level` (`mem_Level`)

## 5. Comment（%pre%comment）——评论

datainfo.php L49-64。

| 属性名 | 真实列名 | 类型 | 长度 | 默认值 | 说明 |
|---|---|---|---|---|---|
| ID | comm_ID | integer | | 0 | 主键，自增 |
| LogID | comm_LogID | integer | | 0 | 所属文章/页面 ID |
| IsChecking | comm_IsChecking | boolean | | false | 是否待审核 |
| RootID | comm_RootID | integer | | 0 | 根评论 ID |
| ParentID | comm_ParentID | integer | | 0 | 父评论 ID |
| AuthorID | comm_AuthorID | integer | | 0 | 评论者用户 ID（游客为 0） |
| Name | comm_Name | string | 250 | '' | 评论者昵称 |
| Content | comm_Content | string | | '' | 评论内容 |
| Email | comm_Email | string | 250 | '' | 评论者邮箱 |
| HomePage | comm_HomePage | string | 250 | '' | 评论者主页 |
| PostTime | comm_PostTime | integer | | 0 | 评论时间（Unix 时间戳） |
| IP | comm_IP | string | 250 | '' | 评论者 IP |
| Agent | comm_Agent | string | | '' | 浏览器 UA |
| Meta | comm_Meta | string | | '' | Metas 序列化存储列 |

主键/索引（mysql.sql L63-65）：

- PRIMARY KEY (`comm_ID`)
- KEY `%pre%comm_LRI` (`comm_LogID`, `comm_RootID`, `comm_IsChecking`)
- KEY `%pre%comm_IsChecking` (`comm_IsChecking`)

## 6. Module（%pre%module）——模块

datainfo.php L65-76。

| 属性名 | 真实列名 | 类型 | 长度 | 默认值 | 说明 |
|---|---|---|---|---|---|
| ID | mod_ID | integer | | 0 | 主键，自增 |
| Name | mod_Name | string | 250 | '' | 模块名 |
| FileName | mod_FileName | string | 250 | '' | 模块文件名 |
| Content | mod_Content | string | | '' | 模块内容 |
| HtmlID | mod_HtmlID | string | 250 | '' | HTML 元素 ID |
| Type | mod_Type | string | 5 | 'div' | 容器标签类型（默认 div） |
| MaxLi | mod_MaxLi | integer | | 0 | 列表最大条数 |
| Source | mod_Source | string | 250 | 'user' | 来源（默认 user） |
| IsHideTitle | mod_IsHideTitle | boolean | | false | 是否隐藏标题 |
| Meta | mod_Meta | string | | '' | Metas 序列化存储列 |

主键（mysql.sql L118）：PRIMARY KEY (`mod_ID`)。注意：建表 SQL 中还有一列 `mod_SidebarID`（mysql.sql L111 等），但 datainfo.php 未定义该属性，模型层读写不到它，属遗留列。

## 7. Upload（%pre%upload）——附件

datainfo.php L114-126。

| 属性名 | 真实列名 | 类型 | 长度 | 默认值 | 说明 |
|---|---|---|---|---|---|
| ID | ul_ID | integer | | 0 | 主键，自增 |
| AuthorID | ul_AuthorID | integer | | 0 | 上传者用户 ID |
| Size | ul_Size | integer | | 0 | 文件大小（字节） |
| Name | ul_Name | string | 250 | '' | 保存后的文件名 |
| SourceName | ul_SourceName | string | 250 | '' | 原始文件名 |
| MimeType | ul_MimeType | string | 250 | '' | MIME 类型 |
| PostTime | ul_PostTime | integer | | 0 | 上传时间（Unix 时间戳） |
| DownNums | ul_DownNums | integer | | 0 | 下载次数 |
| LogID | ul_LogID | integer | | 0 | 关联文章/页面 ID |
| Intro | ul_Intro | string | | '' | 简介 |
| Meta | ul_Meta | string | | '' | Metas 序列化存储列 |

主键（mysql.sql L152）：PRIMARY KEY (`ul_ID`)，无其他索引。

## 8. Config（%pre%config）——键值配置

datainfo.php L4-9。

| 属性名 | 真实列名 | 类型 | 长度 | 默认值 | 说明 |
|---|---|---|---|---|---|
| ID | conf_ID | integer | | 0 | 主键，自增 |
| Name | conf_Name | string | 250 | '' | 项目名（通常是插件 appid） |
| Key | conf_Key | string | 250 | '' | 配置键名 |
| Value | conf_Value | string | | '' | 配置值（单值序列化存储） |

主键/索引（mysql.sql L74-75）：

- PRIMARY KEY (`conf_ID`)
- KEY `%pre%conf_Name` (`conf_Name`)

## 特别说明

### Meta 列（log_Meta / cate_Meta / comm_Meta / mod_Meta / mem_Meta / tag_Meta / ul_Meta）

每张实体表都有一个 `Meta` 列，是 **Metas 自定义字段的 PHP serialize 序列化存储处**：`Base::Save()` 开头把 `$this->Metas->Serialize()` 写入该列（base.php L461-463），读取时自动 Unserialize（base.php L296-299）。不要手改库里的这个字段；用法与按 Meta 查询（`META_NAME` / `META_NAMEVALUE`）见 [config-metas.md](config-metas.md)。

### Config 表结构

按「项目名 + 键」存储：`conf_Name` = 项目名（`$zbp->Config($appid)` 的 appid），`conf_Key` = 键名（每键一行），`conf_Value` = 单值序列化。`Config::Save()` 在有 `conf_Key` 列时按 key 增/删/改原子化存储（config.php L405-503）；老库无 `conf_Key` 列则退化为整包 serialize 存一行。插件配置一律存这里，API 见 [config-metas.md](config-metas.md)。

### 日期时间列的存储格式

`CreateTime` / `PostTime` / `UpdateTime`（以及 `comm_PostTime`、`ul_PostTime`）在 datainfo 中都是 **`integer`，存 Unix 时间戳（秒）**，没有独立的 time 类型。写入时用 PHP `time()`（如 `zb_system/function/lib/base/post.php` L51-53 三个时间戳一起赋值），显示时再经 `date()`/模板函数格式化。因此 SQL 里可直接数值比较，如 `array('BETWEEN', 'log_PostTime', $t1, $t2)`。

### 各数据库差异（mysql / sqlite / postgresql）

建表 SQL 在 `zb_system/defend/createtable/{mysql,sqlite,pgsql}.sql`，字段定义三库一致，仅类型/索引有差异：

| 差异点 | MySQL | SQLite | PostgreSQL |
|---|---|---|---|
| boolean 列 | tinyint(4) | bit | char(1) |
| 大文本 | text / longtext | text | text |
| 自增 | AUTO_INCREMENT | autoincrement | sequence + nextval |
| 额外索引 | — | 每表 UNIQUE `*_ID` | 每表 `*_ix_id` + `post_ix_tpisc` |
| 其他 | — | `mem_Password` 为 varchar(32)（MySQL/PG 为 250） | 无 `mem_Level`、`conf_Name` 索引 |

（SQLite 也无 `mem_Level`、`conf_Name` 索引；Module 的遗留列 `mod_SidebarID` 三库 SQL 均有。）

## 常用查询对照（DbSql 风格）

```php
// 1. 取某分类最新 10 篇已发布文章（走 log_TPISC 索引）
$sql = $zbp->db->sql->Select('%pre%post',
    array('log_ID', 'log_Title', 'log_PostTime'),
    array(array('=', 'log_Type', 0), array('=', 'log_Status', 0), array('=', 'log_CateID', 1)),
    array('log_PostTime' => 'DESC'),
    array(10));
$rows = $zbp->db->Query($sql);

// 2. 更新文章浏览数（zb_system/api/post.php 同款）
$sql = $zbp->db->sql->Update('%pre%post',
    array('log_ViewNums' => 101),
    array(array('=', 'log_ID', 1)));
$zbp->db->Update($sql);

// 3. 按 Metas 自定义字段查文章（对 log_Meta 序列化串做匹配，见 config-metas.md）
$sql = $zbp->db->sql->Select('%pre%post', null,
    array(array('META_NAMEVALUE', 'log_Meta', 'area', '北京')),
    array('log_PostTime' => 'DESC'),
    array(0, 10));
$list = $zbp->db->Query($sql);
```

注意：模型层查询请优先用 `$zbp->GetPostList(...)` 等（见 [models.md](models.md)）；表名取 `$zbp->table['Post']` 或写 `%pre%`，不要硬编码前缀。
