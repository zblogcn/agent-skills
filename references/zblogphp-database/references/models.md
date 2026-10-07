# Base 模型与 CRUD

源码：`zb_system/function/lib/base.php`（类 `Base`）。
子类：`zb_system/function/lib/` 下的 `post.php`（Post）、`category.php`（Category）、`tag.php`（Tag）、`member.php`（Member）、`comment.php`（Comment）、`module.php`（Module）、`upload.php`（Upload）等，均继承 Base。

## 1. 属性访问与表结构

Base 用魔术方法把数据列映射为对象属性（base.php L96-109）：

```php
public function __set($name, $value) { $this->data[$name] = $value; }
public function __get($name)         { return $this->data[$name]; }
```

属性名是 `zb_system/defend/datainfo.php` 中的键名（不是真实列名）。例如 Post：

```php
// defend/datainfo.php
'Post' => array(
    'ID'         => array('log_ID', 'integer', '', 0),
    'CateID'     => array('log_CateID', 'integer', '', 0),
    'Title'      => array('log_Title', 'string', 250, ''),
    'Content'    => array('log_Content', 'string', '', ''),
    // ...
    'Meta'       => array('log_Meta', 'string', '', ''),
),
```

所以写 `$post->Title = 'x'` 而不是 `$post->log_Title`。数组元素格式：`array(真实列名, 类型, 长度, 默认值)`，datainfo 的第一个键是主键 ID 名。

完整数据字典见 [schema.md](schema.md)。

构造：`$post = new Post();`（子类内部已绑定 table/datainfo）。Base 构造函数签名：`__construct(&$table, &$datainfo, $classname = '', $hasmetas = true, &$db = null)`（L67）。

## 2. 读取

```php
$post = new Post();
$post->LoadInfoByID($id);                 // L256，成功返回 true，失败 false
$post->LoadInfoByField('Alias', 'hello'); // L323，按单字段取第一条
$post->LoadInfoByFields(array('AuthorID' => 1, 'CateID' => 2)); // L337，多字段 AND
$post->LoadInfoByAssoc($row);             // L281，从关联数组直接装载
```

注意：

- `LoadInfoByField(s)` 里 `'Meta'` 键有特殊处理：值 `array('area' => '北京')` 会转为 `META_NAMEVALUE` 条件（L344-351），可直接按 Metas 自定义字段查对象。
- `LoadInfoByAssoc` 遇到 `Meta` 列会自动 `$this->Metas->Unserialize(...)`（L298）。
- 字符串列读取时会把 `{#ZC_BLOG_HOST#}` 占位符换回 `$bloghost`（L295）。

## 3. 保存与删除

```php
$post->Title = '新标题';
$post->CateID = 1;
$post->Save();   // L458：ID 为空走 Insert 并回填自增 ID；否则走 Update（只更新有变化的字段）
$post->Del();    // L550：按主键删除，并清理对象缓存
```

Save 的行为要点（L458-543）：

- 保存前若存在 `Meta` 键，先 `$this->Metas->Serialize()` 序列化（L461-463）。
- boolean/integer/float 会强制类型转换；string 会把 `$bloghost` 替换为 `{#ZC_BLOG_HOST#}` 占位符再入库（L503）。
- Update 时会和 `original` 对比，没变化的字段不进 SQL；全部无变化则直接返回 true（L531）。
- 若用 `UnsetData($key)`（L187）删掉了某个键，Save 时该列不会被写入。

放弃修改：`$post->RevertChanges()`（L204）把 data 恢复为 original。

## 4. $zbp 的魔术列表方法

`ZBlogPHP::__call`（zblogphp.php L533）按方法名正则派发：

| 调用形式 | 匹配正则 | 实际调用 |
|---|---|---|
| `$zbp->GetXxxList(...)` | `Get([a-zA-Z]\w*)List` | `GetListWithBaseObject`（L2750） |
| `$zbp->GetXxxByArray($ids)` | `Get([a-zA-Z]\w*)ByArray` | `GetListByArrayWithBaseObject`（L2772） |
| `$zbp->GetXxxByID($id)` | `Get([a-zA-Z]\w*)ByID` | `GetSingleByIDWithBaseObject`（L2780，优先读缓存） |

`Xxx` 必须是 Base 的子类名（Post/Category/Tag/Member/Comment/Module/Upload/...）。

真实签名（zblogphp.php L2794）：

```php
public function GetPostList($select = null, $where = null, $order = null, $limit = null, $option = null)
```

- 5 个参数与 `DbSql::Select` 完全对应（见 dbsql.md），返回 `Post[]`。
- `$select` 也可以直接传一个 `SQL__Global` 子类对象（L2752-2753），此时其余参数忽略。
- `$option['pagebar']` 传入 Pagebar 引用时，返回后 `pagebar->CurrentCount` 会被填上（L2762-2764）。

已显式定义的便捷方法： `GetPostList`（L2794）、`GetArticleList`（L2811，自动加 `log_Type=0` 并预载标签）、`GetPageList`（L2842，`log_Type=1`）、`GetCommentList`（L2865）、`GetMemberList`、`GetCategoryList` 等。

示例（组合 where，源自 zb_system/api/post.php L297-311 的简化）：

```php
$where = array();
$where[] = array('=', 'log_Type', 0);
$where[] = array('=', 'log_Status', 0);
$where[] = array('LIKE', 'log_Tag', '%{' . $tagId . '}%');
$order = array('log_PostTime' => 'DESC');
$limit = array(0, 10);
$list = $zbp->GetPostList(null, $where, $order, $limit, null);
```

## 5. 对象缓存与克隆

- `Get*ByID` 走 `$zbp` 的对象缓存（CheckCache/AddCache），同一请求内同 ID 返回同一实例。
- 需要一个独立副本用 `$post->Cloned($with_original = false)`（L587）。
- 子类 `Del()` 后会 `$zbp->RemoveCache($this)`（L556-558）。

## 6. 子类额外属性

子类在 Base 之外提供只读计算属性（如 Post 的 `Url`、`TagsCount`、`TagsName`、`CommentPostKey`、Category 的 `ChildrenCategories` 等），这些不在 data 里，Save 时不会入库。API 输出时常用 `ApiGetObjectArray($post, array('Url', ...))` 追加它们（详见 zblogphp-api）。
