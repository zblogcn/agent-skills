# Config 与 Metas 扩展字段

两者都是「键值 + 序列化」存储，但作用域不同：

- **Config**：按「项目名（通常是插件 appid）」隔离的全局键值，存 `%pre%config` 表。适合插件设置。
- **Metas**：挂在单个实体对象（Post/Category/Tag/Member/...）上的扩展字段，序列化后存该对象主表的 `Meta` 列。适合「给文章加自定义字段」。

## 1. Config（插件配置）

源码：`zb_system/function/lib/config.php`（类 `Config`）。

标准用法：

```php
// 读
$val = $zbp->Config('myappid')->mykey;

// 写（只改内存）
$zbp->Config('myappid')->mykey = 'newvalue';
// 持久化（必须调用，否则丢失）
$zbp->SaveConfig('myappid');

// 删除整个配置
$zbp->DelConfig('myappid');
// 判断是否存在
$zbp->HasConfig('myappid');
```

要点：

- `$zbp->Config($name)`（zblogphp.php L1349）：name 不存在时自动 `new Config($name)`；name 经 `FilterCorrectName` 过滤。
- `Config::Save()`（config.php L377）对比 `kvdata` 与 `origkvdata` 算出 add/del/mod，无变化直接返回。
- 表有 `conf_Key` 字段时按「每 key 一行」原子化存储，多条 SQL 包在事务里执行（config.php L486-503）：

```php
$this->db->Transaction('begin');
// insert / update / delete ...
$this->db->Transaction('commit');
// catch 时 rollback
```

- 老表结构（无 `conf_Key`）退化为整包 serialize 后存一行（L405-424）。
- 单 key 读写可用 `AddKey($name, $value)`（L548）/ `DelKey($name)`（L566）；读取不存在的 key 返回 null。
- key 名只允许字母数字（`FilterCorrectName`），不要在 key 里放特殊字符。
- 字符串值中的 `$bloghost` 会自动替换为 `{#ZC_BLOG_HOST#}` 再序列化，读取时还原（Serialize L221 / Unserialize L245），因此存绝对 URL 是安全的。

系统级选项不要用 Config，用 `$zbp->option['ZC_XXX']` + `$zbp->SaveOption()`（zblogphp.php L1422）。

## 2. Metas（实体自定义字段）

源码：`zb_system/function/lib/metas.php`（类 `Metas`）。

每个 Base 子类对象构造时自动带 `$this->Metas = new Metas()`（base.php L82-84，构造参数 `$hasmetas = true` 时）。

用法：

```php
$post = new Post();
$post->LoadInfoByID($id);

// 读
$area = $post->Metas->area;

// 写（只是内存）
$post->Metas->area = '北京';
// 必须调用外层对象的 Save() 才会序列化进 log_Meta 列
$post->Save();

// 删除某个 key
$post->Metas->Del('area');
$post->Save();
```

要点：

- Metas 同样实现了 `__set/__get/__isset/__unset`（metas.php L31-63），`HasKey`、`CountItem`、`GetData` 可用。
- 序列化时机在 `Base::Save()` 开头：`$this->data['Meta'] = $this->Metas->Serialize()`（base.php L461-463）。**只改 Metas 不调 Save 不会入库**。
- **不要给 `$post->Meta`（单数，原始列）直接赋值。** Save 时该列会被 `$this->Metas->Serialize()` 整体覆盖，你赋的原始串静默丢失；如果赋的是非法序列化串，后续读取时 Unserialize 还会产生警告或异常。读写扩展字段一律走 `$post->Metas->key`。
- 读取时机在 `LoadInfoByAssoc` / `LoadInfoByArray` / `LoadInfoByDataArray`：遇到 `Meta` 列自动 Unserialize（base.php L296-299）。
- Meta 列类型是 text，值是 PHP serialize 串；不要手改数据库里的这个字段。

## 3. 按 Metas 字段查询

where 条件支持两个专用运算符（sql/global.php L701-710）：

```php
// 查存在某个 meta key
$where = array(array('META_NAME', 'log_Meta', 'area'));
// 查 meta key = 指定值
$where = array(array('META_NAMEVALUE', 'log_Meta', 'area', '北京'));
$list = $zbp->GetPostList(null, $where, null, array(10), null);
```

对象级等效写法（base.php L344-351 自动转成上述条件）：

```php
$post = new Post();
$post->LoadInfoByFields(array('Meta' => array('area' => '北京')));
```

注意：META_NAME/META_NAMEVALUE 是对序列化串做 LIKE 匹配，大数据量下性能差；高频查询字段应考虑建自定义表（见 dbsql.md 的 CreateTable）。

## 4. 选择建议

| 场景 | 方案 |
|---|---|
| 插件开关、密钥、少量设置 | Config |
| 给文章/分类加展示用附加字段 | Metas |
| 需要按该字段频繁检索/排序 | 自定义表 + DbSql |
| 全站选项（ZC_*） | `$zbp->option` + `SaveOption()` |
