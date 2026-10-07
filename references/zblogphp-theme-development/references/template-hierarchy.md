# 模板选择规则（页面 → 模板文件）

模板选择逻辑在 `zb_system/function/c_system_route.php`（ViewList / ViewPost / ViewSearch 等）。入口模板通过 `$template->SetTemplate('名字')` 设定，Display 时 include 编译产物 `{名字}.php`。

## 总体规则

每个内容类型（posttype）定义 7 个模板名（`zb_system/defend/posttype_article.php`，article 与 page 默认一致）：

| 键 | 默认值 | 用途 |
|---|---|---|
| `template` | `single` | 单篇内容页 |
| `list_template` | `index` | 首页列表 |
| `category_template` | `index` | 分类列表 |
| `tag_template` | `index` | 标签列表 |
| `author_template` | `index` | 作者列表 |
| `date_template` | `index` | 日期归档列表 |
| `search_template` | `search` | 搜索结果 |

全局默认由选项决定：`ZC_POST_DEFAULT_TEMPLATE`=`single`、`ZC_INDEX_DEFAULT_TEMPLATE`=`index`、`ZC_SEARCH_DEFAULT_TEMPLATE`=`search`（`zb_system/defend/option.php` L191-193）。

## 列表页（ViewList，c_system_route.php L993-1368）

按页面类型决定候选模板名 `$list_template`：

| 页面类型 `{$type}` | 候选模板 | 注入的额外模板变量 |
|---|---|---|
| `index`（首页） | posttype 的 `list_template`（默认 `index`） | `$articles`、`$pagebar`、`$page` |
| `category`（分类） | `$category->Template`（分类对象自带模板字段，后台分类编辑可选；空时回落见下） | `$category`、`$articles`、`$pagebar` |
| `tag`（标签） | `$tag->Template` | `$tag`、`$articles`、`$pagebar` |
| `author`（作者） | `$author->Template` | `$author`、`$articles`、`$pagebar` |
| `date`（日期归档） | posttype 的 `date_template`（默认 `index`） | `$date`、`$articles`、`$pagebar` |

最终判定（L1364-1368）：

```
if ($template->hasTemplate($list_template)) SetTemplate($list_template);
else SetTemplate('index');   // 主题没有该文件时一律回落到 index
```

- 分类/标签/作者的 `Template` 字段存在数据库中（`cate_Template` 等，`zb_system/defend/datainfo.php`），后台编辑时可从主题里 template.json 声明 `type` 含 `list` 的模板中选择。
- 列表页可用变量：`$articles`（Post 数组）、`$pagebar`（Pagebar 对象，无分页时为 null）、`$page`、`$type`、`$posttype`、`$category`/`$tag`/`$author`/`$date`（按类型）、`$url`。

### 列表项片段模板

列表模板中区分置顶文章与普通文章：

```
{foreach $articles as $article}
  {if $article.TopType}{template:post-istop}{else}{template:post-multi}{/if}
{/foreach}
<div class="pagebar">{template:pagebar}</div>
```

- `post-istop.php`：置顶文章条目
- `post-multi.php`：普通文章条目（`{$article.Url}`、`{$article.Title}`、`{$article.Intro}`、`{$article.Author.StaticName}`、`{$article.Category.Name}`、`{$article.ViewNums}`、`{$article.CommNums}`）
- `pagebar.php`：分页条（`$pagebar.buttons` 为 页码=>URL 数组，`$pagebar.PageNow`、`$pagebar.isFullLink`）

## 单篇内容页（ViewPost，c_system_route.php L1610-1650）

```
if ($template->hasTemplate($article->Template)) SetTemplate($article->Template);
else SetTemplate($option['ZC_POST_DEFAULT_TEMPLATE']);   // 默认 single
```

- 每篇文章/页面有独立 `Template` 字段（`log_Template`），后台编辑器侧栏可为单篇选择 template.json 声明 `type` 含 `single` 的模板。
- 文章与页面共用 `single.php`，模板内用类型常量区分：

```
{if $article.Type==ZC_POST_TYPE_ARTICLE}
  {template:post-single}
{else}
  {template:post-page}
{/if}
```

- 可用变量：`$article`（Post 对象）、`$comments`（Comment 数组）、`$pagebar`（评论分页）、`$commentspagebar`、`$type`（=文章类型名）、`$posttype`、`$url`、`$title`（含状态前缀）。

### 正文与评论片段

- `post-single.php`：文章正文 + 标签循环 + 末尾 `{if !$article.IsLock}{template:comments}{/if}`
- `post-page.php`：页面正文
- `comments.php`：评论总模板。`{if $socialcomment}{$socialcomment}{else}...{/if}`；遍历 `{foreach $comments as $key => $comment}{template:comment}{/foreach}`；含 `{template:pagebar}` 与 `{template:commentpost}`
- `comment.php`：单条评论，含楼中楼递归 `{foreach $comment.Comments as $comment}{template:comment}{/foreach}`
- `commentpost.php` / `commentpost-verify.php`：评论表单与验证码

## 搜索页（ViewSearch，c_system_route.php L866-872）

```
if (HasTemplate(posttype 的 search_template)) SetTemplate('search');
else SetTemplate(posttype 的 list_template);   // 回落 index
```

- `{$type}` 固定为 `search`；额外变量：`$search`（关键词）、`$articles`（结果，已做关键词高亮）、`$article`、`$issearch=true`。
- 若需要列表式搜索结果，可在 `Filter_Plugin_ViewSearch_Begin` 回调中把 `ZC_SEARCH_TYPE` 设为 `list`。

## 其他入口模板

| 模板 | 触发 | 出处 |
|---|---|---|
| `404.php` | 路由未命中，`SetTemplate('404')` | c_system_function.php L460 |
| `external-link.php` | 外链跳转页 | c_system_route.php L1827 |

## 系统默认模板回落（LoadTemplates，template.php L761-799）

以下是模板引擎的运行时行为，不是开发时读取文件的步骤：

1. 引擎先加载 `zb_system/defend/default/*.php` 作为基础模板集（含 header/footer/index/single/post-*/comment*/module*/sidebar/pagebar/external-link 等全套）；
2. 引擎再加载主题 `template/` 目录（递归子目录）同名覆盖；
3. 自动生成 `sidebar2`~`sidebar9`：若主题未提供，从 `sidebar` 模板把 `$sidebar` 替换为 `$sidebarN` 派生。

**结论：主题只需提供与默认不同的模板文件**；缺哪个就回落到系统默认，不会报错。入口模板文件缺失时 Display 报 86 号错误（L706-708）。

## 后台模板选择器与 Template Type（template.json）

后台「文章编辑 / 分类编辑 / 标签编辑 / 作者编辑」页的模板下拉框由 `OutputOptionItemsOfTemplate()` 生成（`zb_system/function/c_system_admin_function.php` L418-498）。每个模板文件的**显示名称**与**类型**通过主题根目录的 `template.json` 声明（解析见 template.php `GetTemplateNameAndType` L821-873）。

### template.json

在主题根目录 `zb_users/theme/{主题ID}/template.json` 声明：

```json
{
    "id": "主题ID",
    "templates": [
        { "filename": "index",  "type": "list",   "name": "列表自动模板" },
        { "filename": "single", "type": "single", "name": "文章/单页自动模板" }
    ]
}
```

- `filename` 与模板文件名（不含 .php）做**大小写不敏感**匹配（L846）。

### type 类型约定

| type | 含义 | 出现的下拉框 |
|---|---|---|
| `index` | 首页 | （一般作为回落，不直接参与筛选） |
| `list` | 列表页通用 | 分类/标签/作者编辑页 |
| `category` / `tag` / `author` / `date` | 对应列表页细分类型 | 分类/标签/作者编辑页 |
| `single` | 单篇通用（文章+页面） | 文章编辑页、分类的「单篇模板」 |
| `article` / `page` | 文章页 / 单页页面细分 | 文章编辑页（按 posttype 名匹配） |
| `search` | 搜索页 | — |
| `404` | 404 页 | — |
| `none` | **不出现在任何下拉框** | — |

- 一个模板可标多个 type，分隔符 `,` `，` `;` `；` `、` 都会被规范化为 `|`（L856），如 `type: "list|category"`。
- 未标注时按文件名给默认 type（L860-871）：`index`→`list|index`、`single`→`single`、`404`→`404`、`search`→`search`。
- 文件名匹配 `/^(\.|post-|module|header|footer|comment|sidebar|pagebar|external-link|[a-zA-Z]\_)/si` 的模板（L421）**始终不进下拉框**——这些是片段模板，无需标注。

### 筛选行为（isuse_nameandtype）

- 只要**有任意一个模板**声明了 type，主题即进入 `isuse_nameandtype=true` 模式（L857-859）：下拉框按各编辑页传入的 `$accept_type` 白名单筛选模板——
  - 文章/页面编辑页（edit.php L275）：接受 `single` + posttype 名（`article`/`page`），排除 `index,404,module,search,lm-`
  - 分类编辑页（category_edit.php L115/122）：列表模板接受 `list,category`；单篇模板接受 `single,article`
  - 标签编辑页（tag_edit.php L80）：`list,tag`；作者编辑页（member_edit.php L134）：`list,author`
- 若全主题都未声明 type，退化为传统行为：所有非片段模板出现在所有下拉框。
- 实践建议：新主题**应当**提供 template.json 并给 index/single 等入口模板标注 type，否则用户会在文章编辑器里看到 comment、pagebar 之外的全部模板裸文件名。
