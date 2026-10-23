# 模板对象属性速查

按对象整理模板中可用的属性/方法，全部经过 Z-BlogPHP 1.7.5 源码核实。直接使用本文的字段与用法；各节来源文件和行号仅用于溯源，不需要再读取数据定义、魔术方法实现或主题范例。

**变量注入时机**：全局变量（`{$zbp}`/`{$user}`/`{$option}`/`{$lang}`/`{$modules}`/`{$sidebar}`~`{$sidebar9}` 等）由 `template.php` `MakeTemplateTags`（L937-1047）注入，所有模板可用。页面级变量由 `c_system_route.php` 各路由函数的 `SetTags` 调用注入：

- `ViewList`（L913，列表页：首页/分类/标签/作者/日期）：注入 `articles`、`category`、`author`、`tag`、`date`、`pagebar`、`type`、`page`、`title`、`url`（L1340-1362）
- `ViewPost`（L1404，文章/页面页）：注入 `article`、`comments`、`pagebar`、`type`、`page`、`title`、`url`（L1612-1628）——**不注入 `category`/`author`/`tag`/`date`**
- `ViewSearch`（搜索页）：注入 `article`、`articles`、`pagebar`、`type`、`page`、`title`（L848-866）——**不注入 `category`/`author`/`tag`/`date`**

因此 `$category`、`$author`、`$tag`、`$date` 仅在列表页可用；文章页/页面页请用 `$article.Category.XXX`、`$article.Author.XXX`。

---

## `{$article}`（Post 对象）

来源：`zb_system/function/lib/base/post.php`；字段定义：`datainfo.php` L10-30。

| 属性/方法 | 说明 | 来源 |
|---|---|---|
| `{$article.ID}` | 文章 ID | datainfo.php L11 |
| `{$article.Title}` | 标题 | datainfo.php L20 |
| `{$article.Alias}` | 别名 | datainfo.php L17 |
| `{$article.Url}` | 文章 URL | post.php `__get` L219-260 |
| `{$article.Intro}` | 摘要 | datainfo.php L21 |
| `{$article.Content}` | 正文 | datainfo.php L22 |
| `{$article.Status}` | 状态码（0=公开） | datainfo.php L15 |
| `{$article.StatusName}` | 状态文字 | post.php `__get` L217-218 |
| `{$article.Type}` | 类型码（0=文章 1=页面） | datainfo.php L16 |
| `{$article.TypeName}` | 类型名（article/page） | post.php `__get` L377-378 |
| `{$article.IsTop}` | 置顶状态码 | datainfo.php L18 |
| `{$article.TopType}` | 置顶类型（global/index/categorys/category） | post.php `__get` L362-376 |
| `{$article.IsLock}` | 是否锁定（禁止评论） | datainfo.php L19 |
| `{$article.CommNums}` | 评论数 | datainfo.php L26 |
| `{$article.ViewNums}` | 浏览数 | datainfo.php L27 |
| `{$article.CateID}` | 分类 ID | datainfo.php L12 |
| `{$article.Category}` | 分类对象（Category） | post.php `__get` L213-214 |
| `{$article.AuthorID}` | 作者 ID | datainfo.php L13 |
| `{$article.Author}` | 作者对象（Member） | post.php `__get` L215-216 |
| `{$article.Tag}` | 标签 ID 字符串（`{1}{2}` 格式） | datainfo.php L14 |
| `{$article.Tags}` | 标签对象数组（Tag[]） | post.php `__get` L261-262 |
| `{$article.TagsCount}` | 标签数量 | post.php `__get` L263-264 |
| `{$article.TagsName}` | 标签名逗号分隔字符串 | post.php `__get` L265-266 |
| `{$article.FirstTag}` | 首个标签对象（Tag） | post.php `__get` L267-273 |
| `{$article.Prev}` | 上一篇文章对象（Post） | post.php `__get` L299-324 |
| `{$article.Next}` | 下一篇文章对象（Post） | post.php `__get` L325-350 |
| `{$article.Template}` | 自定义模板文件名（空则走默认规则） | datainfo.php L28；`__get` L274-282 |
| `{$article.PostTime}` | 发布时间戳 | datainfo.php L24 |
| `{$article.CreateTime}` | 创建时间戳 | datainfo.php L23 |
| `{$article.UpdateTime}` | 更新时间戳 | datainfo.php L25 |
| `{$article.Time('Y-m-d')}` | 格式化发布时间 | post.php L80-109 |
| `{$article.Time('Y-m-d', 'Create')}` | 格式化创建时间 | post.php L80-109 |
| `{$article.Time('Y-m-d', 'Update')}` | 格式化更新时间 | post.php L80-109 |
| `{$article.PostDate.XXX}` / `CreateDate.XXX` / `UpdateDate.XXX` | ZbpDate 对象，`.` 后接 `date()` 格式串 | post.php `__get` L381-386 |
| `{$article.CommentPostUrl}` | 评论提交 URL | post.php `__get` L285-296 |
| `{$article.CommentPostKey}` | 评论提交 key | post.php `__get` L283-284 |
| `{$article.ValidCodeUrl}` | 验证码 URL | post.php `__get` L297-298 |
| `{$article.RelatedList}` | 相关文章数组 | post.php `__get` L351-361 |
| `{$article.AliasFirst}` | 别名优先（无别名则返回标题） | post.php `__get` L387-392 |
| `{$article.ImageCount}` | 正文图片数 | post.php `__get` L395-396 |
| `{$article.AllImages}` | 正文图片 URL 数组 | post.php `__get` L393-394 |
| `{$article.AllImages[0]}` | 第一张正文图 URL | post.php `__get` L393-394 |
| `{$article.Thumbs(640, 360, 1, false)}` | 缩略图数组（宽高、数量、是否裁剪） | post.php L420-433 |
| `{$article.Thumbs(640, 360, 1, false)[0]}` | 第一张缩略图 URL | post.php L420-433 |
| `{$article.Metas.XXX}` | 扩展字段（插件/主题写入） | `base.php` L38 `Metas`；`metas.php` `__get` |

标签的写入侧与读侧不对称：`$post->Tag` 只能赋 `{1}{2}` 格式字符串（赋数组会 fatal），`$post->Tags`（复数）赋值被静默丢弃；见 [models.md「保存与删除」](zblogphp-database-models.md#3-保存与删除)。


---

## `{$category}`（Category 对象）

来源：`zb_system/function/lib/base/category.php`；字段定义：`datainfo.php` L31-48。

| 属性 | 说明 | 来源 |
|---|---|---|
| `{$category.ID}` | 分类 ID | datainfo.php L32 |
| `{$category.Name}` | 分类名 | datainfo.php L33 |
| `{$category.Alias}` | 别名 | datainfo.php L37 |
| `{$category.Url}` | 分类 URL | category.php `__get` L119-142 |
| `{$category.Intro}` | 分类描述 | datainfo.php L39 |
| `{$category.Count}` | 本分类文章数 | datainfo.php L36 |
| `{$category.AllCount}` | 含子孙分类文章总数 | category.php `__get` L188-194 |
| `{$category.Order}` | 排序号 | datainfo.php L34 |
| `{$category.Level}` | 层级（0=顶级） | category.php `__get` L152-154 |
| `{$category.RootID}` | 祖先分类 ID | datainfo.php L40 |
| `{$category.Root}` | 祖先分类对象（Category） | category.php `__get` L165-171 |
| `{$category.ParentID}` | 父分类 ID | datainfo.php L41 |
| `{$category.Parent}` | 父分类对象（Category） | category.php `__get` L158-164 |
| `{$category.SubCategorys}` | 子分类数组（已废弃拼写，兼容保留） | category.php L38 |
| `{$category.SubCategories}` | 子分类数组 | category.php L31 |
| `{$category.ChildrenCategories}` | 子孙分类数组 | category.php L40 |
| `{$category.Template}` | 分类模板文件名 | datainfo.php L45；`__get` L172-179 |
| `{$category.LogTemplate}` | 分类下文章模板文件名 | datainfo.php L46；`__get` L180-187 |
| `{$category.Symbol}` | 后台管理用层次标识符 | category.php `__get` L143-151 |
| `{$category.SymbolName}` | 层次标识符+名称 | category.php `__get` L155-157 |
| `{$category.AliasFirst}` | 别名优先（无别名则返回名称） | category.php `__get` L195-201 |
| `{$category.Type}` | 类型码（通常 0） | datainfo.php L35 |
| `{$category.CreateTime}` / `PostTime` / `UpdateTime` | 时间戳 | datainfo.php L42-44 |
| `{$category.Time('Y-m-d')}` | 格式化时间 | category.php L381-409 |
| `{$category.Metas.XXX}` | 扩展字段 | `base.php` L38 `Metas`；`metas.php` `__get` |

---

## `{$author}` / `{$user}`（Member 对象）

`$author` 仅在列表页（作者页）由 `ViewList` 注入（c_system_route.php L1353）；`$user` 是全局变量（当前登录用户），所有模板可用。两者均为 Member 对象，属性一致。

来源：`zb_system/function/lib/base/member.php`；字段定义：`datainfo.php` L77-98。

| 属性 | 说明 | 来源 |
|---|---|---|
| `{$author.ID}` | 用户 ID | datainfo.php L78 |
| `{$author.Name}` | 登录名 | datainfo.php L82 |
| `{$author.Alias}` | 别名 | datainfo.php L90 |
| `{$author.StaticName}` | 对外展示名（别名优先，无则登录名） | member.php `__get` L163-169 |
| `{$author.Level}` | 等级码 | datainfo.php L80 |
| `{$author.LevelName}` | 等级名称 | member.php `__get` L157-159 |
| `{$author.Email}` | 邮箱 | datainfo.php L84 |
| `{$author.HomePage}` | 主页 | datainfo.php L85 |
| `{$author.Intro}` | 简介 | datainfo.php L91 |
| `{$author.Avatar}` | 头像 URL | member.php `__get` L133-156 |
| `{$author.Url}` | 作者页 URL | member.php `__get` L112-132 |
| `{$author.Articles}` | 文章数 | datainfo.php L92 |
| `{$author.Pages}` | 页面数 | datainfo.php L93 |
| `{$author.Comments}` | 评论数 | datainfo.php L94 |
| `{$author.Uploads}` | 上传数 | datainfo.php L95 |
| `{$author.Status}` | 状态码 | datainfo.php L81 |
| `{$author.IsGod}` | 是否最高管理员 | member.php `__get` L181-204 |
| `{$author.AliasFirst}` | 别名优先（无别名则返回登录名） | member.php `__get` L205-211 |
| `{$author.Template}` | 作者页模板文件名 | datainfo.php L96；`__get` L170-177 |
| `{$author.CreateTime}` / `PostTime` / `UpdateTime` | 时间戳 | datainfo.php L87-89 |
| `{$author.Time('Y-m-d')}` | 格式化时间 | member.php L310-338 |
| `{$author.Metas.XXX}` | 扩展字段 | `base.php` L38 `Metas`；`metas.php` `__get` |

---

## `{$comment}`（Comment 对象）

来源：`zb_system/function/lib/base/comment.php`；字段定义：`datainfo.php` L49-64。

| 属性 | 说明 | 来源 |
|---|---|---|
| `{$comment.ID}` | 评论 ID | datainfo.php L50 |
| `{$comment.LogID}` | 所属文章 ID | datainfo.php L51 |
| `{$comment.Post}` | 所属文章对象（Post） | comment.php `__get` L144-145 |
| `{$comment.FloorID}` | 楼层号（由评论列表模板赋值） | comment.php L34 |
| `{$comment.Level}` | 层级（嵌套深度） | comment.php `__get` L142-143 |
| `{$comment.RootID}` | 根评论 ID | datainfo.php L53 |
| `{$comment.ParentID}` | 父评论 ID | datainfo.php L54 |
| `{$comment.Parent}` | 父评论对象（Comment） | comment.php `__get` L146-151 |
| `{$comment.AuthorID}` | 作者 ID | datainfo.php L55 |
| `{$comment.Author}` | 作者对象（Member，游客时属性回填为评论中填写的信息） | comment.php `__get` L122-131 |
| `{$comment.Name}` | 评论者填写的名字 | datainfo.php L56 |
| `{$comment.Email}` | 评论者填写的邮箱 | datainfo.php L58 |
| `{$comment.HomePage}` | 评论者填写的网站 | datainfo.php L59 |
| `{$comment.Content}` | 评论内容 | datainfo.php L57 |
| `{$comment.IP}` | IP 地址 | datainfo.php L61 |
| `{$comment.Agent}` | User-Agent | datainfo.php L62 |
| `{$comment.IsChecking}` | 是否待审核 | datainfo.php L52 |
| `{$comment.IsThrow}` | 是否已丢弃（插件标记） | comment.php L29 |
| `{$comment.PostTime}` | 时间戳 | datainfo.php L60 |
| `{$comment.Time('Y-m-d H:i:s')}` | 格式化时间 | comment.php L94-97 |
| `{$comment.Comments}` | 子评论数组（Comment[]） | comment.php `__get` L132-141 |
| `{$comment.Metas.XXX}` | 扩展字段 | `base.php` L38 `Metas`；`metas.php` `__get` |


---

## `{$tag}`（Tag 对象）

来源：`zb_system/function/lib/base/tag.php`；字段定义：`datainfo.php` L99-113。

| 属性 | 说明 | 来源 |
|---|---|---|
| `{$tag.ID}` | 标签 ID | datainfo.php L100 |
| `{$tag.Name}` | 标签名 | datainfo.php L101 |
| `{$tag.Alias}` | 别名 | datainfo.php L105 |
| `{$tag.Url}` | 标签 URL | tag.php `__get` L79-101 |
| `{$tag.Intro}` | 描述 | datainfo.php L107 |
| `{$tag.Count}` | 文章数 | datainfo.php L104 |
| `{$tag.Order}` | 排序号 | datainfo.php L102 |
| `{$tag.Template}` | 标签页模板文件名 | datainfo.php L111；`__get` L102-109 |
| `{$tag.AliasFirst}` | 别名优先（无别名则返回名称） | tag.php `__get` L110-116 |
| `{$tag.CreateTime}` / `PostTime` / `UpdateTime` | 时间戳 | datainfo.php L108-110 |
| `{$tag.Time('Y-m-d')}` | 格式化时间 | tag.php L174-202 |
| `{$tag.Metas.XXX}` | 扩展字段 | `base.php` L38 `Metas`；`metas.php` `__get` |

---

## `{$pagebar}`（PageBar 对象）

来源：`zb_system/function/lib/pagebar.php`。

| 属性 | 说明 | 来源 |
|---|---|---|
| `{$pagebar.PageBarCount}` | 分页条长度（数字按钮个数） | pagebar.php L30 |
| `{$pagebar.PageCount}` / `PerPageCount` | 每页数量 | pagebar.php L35、L40 |
| `{$pagebar.PageAll}` | 总页数 | pagebar.php L45 |
| `{$pagebar.PageNow}` / `PageCurrent` | 当前页码 | pagebar.php L50、L55 |
| `{$pagebar.PageFirst}` | 起始页码 | pagebar.php L60 |
| `{$pagebar.PageLast}` | 尾页页码 | pagebar.php L65 |
| `{$pagebar.PagePrevious}` | 上一页页码 | pagebar.php L70 |
| `{$pagebar.PageNext}` | 下一页页码 | pagebar.php L75 |
| `{$pagebar.Count}` / `AllCount` | 内容总数 | pagebar.php L15、L20 |
| `{$pagebar.prevbutton}` / `PrevButton` | 上一页 URL | pagebar.php L90、L105 |
| `{$pagebar.nextbutton}` / `NextButton` | 下一页 URL | pagebar.php L95、L110 |
| `{$pagebar.buttons}` | 页码→URL 关联数组 | pagebar.php L85 |
| `{$pagebar.isFullLink}` | 是否全部输出为带链接按钮 | pagebar.php L115 |

`buttons` 特殊键名（来自语言包 `zb_users/language/zh-cn.php` L259-263）：

| 键名 | 含义 |
|---|---|
| `‹‹` | 第一页 |
| `‹` | 上一页 |
| `›` | 下一页 |
| `››` | 最后一页 |

数字页键名格式由 `numeral_button` 语言项控制，默认为 `%num%`（即键名就是 `1`、`2`、`3`...）。

---

## `{$modules['文件名']}`（Module 对象）

来源：`zb_system/function/lib/base/module.php`；字段定义：`datainfo.php` L65-76。

| 属性 | 说明 | 来源 |
|---|---|---|
| `{$modules['navbar'].ID}` | 模块 ID | datainfo.php L66 |
| `{$modules['navbar'].Name}` | 模块显示名 | datainfo.php L67 |
| `{$modules['navbar'].FileName}` | 模块文件名 | datainfo.php L68 |
| `{$modules['navbar'].Content}` | 模块 HTML 内容 | datainfo.php L69 |
| `{$modules['navbar'].HtmlID}` | HTML 元素 id | datainfo.php L70 |
| `{$modules['navbar'].Type}` | 显示类型（`div` / `ul`） | datainfo.php L71 |
| `{$modules['navbar'].MaxLi}` | ul 类型时最大条数 | datainfo.php L72 |
| `{$modules['navbar'].Source}` | 来源标识（system/user/theme/plugin_xxx 等） | datainfo.php L73 |
| `{$modules['navbar'].SourceType}` | 来源类型（system/user/theme/themeinclude/plugin） | module.php `__get` L66-90 |
| `{$modules['navbar'].IsHideTitle}` | 是否隐藏标题 | datainfo.php L74 |
| `{$modules['navbar'].NoRefresh}` | 是否禁止系统刷新 | module.php `__get` L91-93 |
| `{$modules['navbar'].ContentWithoutId}` | 去除 id 属性的 Content | module.php `__get` L94-97 |
| `{$modules['navbar'].Metas.XXX}` | 扩展字段 | `base.php` L38 `Metas`；`metas.php` `__get` |

系统内置模块文件名（由 `zblogphp.php` `RegBuildModules` L2430-2445 注册）：`catalog`、`calendar`、`comments`、`previous`、`archives`、`navbar`、`tags`、`statistics`、`authors`。

静态内容型模块（数据库直接存内容，无 ModuleBuilder 函数）：`controlpanel`、`searchpanel`、`favorite`、`link`、`misc`。它们在后台模块管理中编辑内容，模板中通过 `{module:文件名}` 或 `{$modules['文件名'].Content}` 输出。

---

## 系统变量

`{$host}`、`{$name}`、`{$type}`、`{$page}`、`{$header}`、`{$footer}` 等全局变量已在 `template-syntax.md`「内建模板变量」一节列出，此处不再重复。

---

## 与社区速查表差异

整理时已核实：以下社区速查表条目在 1.7.5 中已不存在或已废弃，不应使用，无需重新核实：

| 社区速查表条目 | 源码实际情况 |
|---|---|
| `{$pagebar.Name}` | `pagebar.php` 中无此属性（PageBar 类无 `Name` 字段） |
| `{$category.Articles}` | Category 对象无 `Articles` 属性，文章数用 `Count` / `AllCount` |
| `{$category.SubCategorys}` | 源码中存在但标注 `@deprecated`（拼写错误，兼容保留），建议用 `SubCategories` |
| `{$article.BlogTime}` | Post 对象无此属性，时间字段为 `PostTime` / `CreateTime` / `UpdateTime` |
| `{$author.BlogName}` | Member 对象无此属性 |
| `{$comment.BlogName}` | Comment 对象无此属性 |

另注意：社区速查表未区分变量注入时机，容易让人误以为 `$category`、`$author`、`$tag`、`$date` 在所有页面都可用；实际上它们仅在列表页（`ViewList`）注入，文章页/页面页/搜索页需通过 `$article.Category.XXX`、`$article.Author.XXX` 访问。
