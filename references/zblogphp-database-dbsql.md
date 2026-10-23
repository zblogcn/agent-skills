# DbSql 查询构造器

源码：`zb_system/function/lib/dbsql.php`（类 `DbSql`）。
SQL 方言：`zb_system/function/lib/sql/global.php`（`SQL__Global`），子类 `SQL__MySQL` / `SQL__SQLite` / `SQL__PostgreSQL`（同目录 mysql.php / sqlite.php / postgresql.php）。
驱动接口：`zb_system/function/lib/database/interface.php`（`Database__Interface`），8 种驱动在同目录：mysql / mysqli / pdo_mysql / sqlite / sqlite3 / pdo_sqlite / postgresql / pdo_postgresql。

## 1. 表名与前缀 %pre%

表名映射定义在 `zb_system/defend/table.php`：

```php
return array(
    'Post'     => '%pre%post',
    'Category' => '%pre%category',
    'Comment'  => '%pre%comment',
    'Tag'      => '%pre%tag',
    'Upload'   => '%pre%upload',
    'Module'   => '%pre%module',
    'Member'   => '%pre%member',
    'Config'   => '%pre%config',
);
```

- SQL 中的 `%pre%` 由 `DbSql::ReplacePre(&$s)`（dbsql.php L45）在执行时替换成 `$zbp->db->dbpre`。
- 系统表用 `$zbp->table['Post']` 取值；自定义表可写 `'%pre%myplugin_table'`。
- `$zbp->PreLoad()` 阶段 `ConvertTableAndDatainfo()`（zblogphp.php L4766）会把 `$zbp->table` 里的 `%pre%` 预先替换，因此运行期 `$zbp->table['Post']` 已是真实表名。

## 2. CRUD 构造器（返回 SQL 字符串，需交给驱动执行）

全部定义在 dbsql.php：

```php
// 查询 L127
$sql = $zbp->db->sql->Select($table, $select = null, $where = null, $order = null, $limit = null, $option = null);
// 计数 L186
$sql = $zbp->db->sql->Count($table, $countofnum, $where = null, $option = null);
// 更新 L217
$sql = $zbp->db->sql->Update($table, $keyvalue, $where, $option = null);
// 插入 L230
$sql = $zbp->db->sql->Insert($table, $keyvalue);
// 删除 L244
$sql = $zbp->db->sql->Delete($table, $where, $option = null);
```

执行（接口见 database/interface.php）：

```php
$array = $zbp->db->Query($sql);     // SELECT，返回关联数组数组
$id    = $zbp->db->Insert($sql);    // INSERT，返回自增 ID
$zbp->db->Update($sql);             // UPDATE
$zbp->db->Delete($sql);             // DELETE
```

示例（更新文章浏览数，源自 `zb_system/api/post.php` L61）：

```php
$sql = $zbp->db->sql->Update($zbp->table['Post'], array('log_ViewNums' => $post->ViewNums), array(array('=', 'log_ID', $post->ID)));
$zbp->db->Update($sql);
```

## 3. WHERE 数组语法

`$where` 是「条件数组的数组」。每个条件 `array(运算符, 字段, 值...)`。运算符支持（源自 sql/global.php L580-711）：

| 运算符 | 说明 | 示例 |
|---|---|---|
| `= < > >= <= <> !=` | 比较 | `array('=', 'log_CateID', 1)` |
| `LIKE` / `NOT LIKE` / `ILIKE` | 模糊（ILIKE 为 PostgreSQL 不区分大小写） | `array('LIKE', 'log_Tag', '%{1}%')` |
| `SEARCH` | 多字段搜索，值自动两边加 `%` | `array('search', 'log_Content', 'log_Intro', 'log_Title', $search)` |
| `BETWEEN` / `NOT BETWEEN` | 区间 | `array('BETWEEN', 'log_PostTime', $t1, $t2)` |
| `EXISTS` / `NOT EXISTS` | 子查询 | `array('exists', $subsql)` |
| `IN` | 枚举 | `array('IN', 'log_ID', array(1,2,3))` 或值用逗号串 |
| `OR` / `ARRAY` | 多条件 OR，2 个以上条件写成 `array('or', $c1, $c2, ...)` | 见下 |
| `array`（值是数组） | 字段 IN 列表，`array('array', array(array('log_CateID',1), array('log_CateID',2)))` | 见 api/post.php L266-273 |
| `META_NAME` | 匹配 Metas 中某个 key | `array('META_NAME', 'log_Meta', $key)` |
| `META_NAMEVALUE` | 匹配 Metas 中 key=value | `array('META_NAMEVALUE', 'log_Meta', $key, $value)` |

顶层多个条件默认 AND 连接。

## 4. Select 的参数细节

- `$select`：字段数组，如 `array('*')`、`array('log_ID', 'log_Title')`；字符串会被 trim 后包成单元素数组。
- `$order`：关联数组，如 `array('log_PostTime' => 'DESC')`。
- `$limit`：`array(0, 10)`（偏移, 条数）或单元素 `array(10)`。
- `$option`（键名不区分大小写，dbsql.php L138-145）：`groupby`、`having`、`orderby`、`limit`、`count/min/max/sum/avg`、`innerjoin/leftjoin/...`、`on`、`distinct`、`useindex/forceindex/ignoreindex` 等。
- `$option['pagebar']`：传入 `Pagebar` 对象引用时，构造器会先自动发一条 count 查询填 `pagebar->Count` 再 `Make()` 分页（L147-162）。API 层的用法示例：

```php
// 源自 c_system_api.php ApiGetRequestFilter L599-606
$p = new Pagebar(null, false);
$p->PageNow = (int) $pageNow == 0 ? 1 : (int) $pageNow;
$p->PageCount = $perPage;
$limit = array(($p->PageNow - 1) * $p->PageCount, $p->PageCount);
$op = array('pagebar' => &$p);
```

## 5. 建表 / 删表 / 判存在

```php
$zbp->db->sql->CreateTable($table, $datainfo, $engine = null, $charset = null, $collate = null); // L98
$zbp->db->sql->DelTable($table);      // L69
$zbp->db->sql->ExistTable($table);    // L82
```

`$datainfo` 格式同 `zb_system/defend/datainfo.php`：`字段名 => array('列名', '类型', '长度', '默认值')`。类型支持 `integer/string/char/boolean/float/double/timestamp` 等（方言各自映射）。

**后三个参数要传 `''` 不要传 `null`。** 函数内部直接 `trim($engine)`（L102-110），PHP 8.1+ 下 `trim(null)` 报 Deprecated；骨架基线 8.2 下调用写成 `CreateTable($table, $datainfo, '', '', '')`（不指定引擎时传空串走数据库默认）。

## 6. 事务

```php
$zbp->db->Transaction('begin');
// ... 多条 Insert/Update/Delete ...
$zbp->db->Transaction('commit');
// 异常时 $zbp->db->Transaction('rollback');
```

真实用例见 `Config::Save()`（lib/config.php L486-503）。`DbSql::Transaction($command)`（dbsql.php L344）只负责把命令规范化为 `BEGIN/COMMIT/ROLLBACK` 字符串；真正执行的是驱动的 `Database__Interface::Transaction()`。

## 7. 调试与过滤

- `DbSql::Filter($sql)`（L256）触发 `Filter_Plugin_DbSql_Filter` 钩子并累计 `$_SERVER['_query_count']`。
- 原始导出（备份用）：`$zbp->db->sql->Export($table, $keyvalue, $type)`（L276）。
- 手写整段 SQL 时，至少保证表名经 `ReplacePre`、值经 `$zbp->db->EscapeString()` 转义（见 zblogphp-security）。
