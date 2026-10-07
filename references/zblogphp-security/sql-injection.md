# SQL 注入防护

来源：`zb_system/function/lib/dbsql.php`、`zb_system/function/lib/sql/global.php`（1.7.5.3540）。

## 原则：永远使用 DbSql 构造器，禁止字符串拼接

Z-BlogPHP 所有 SQL 必须通过 `$zbp->db->sql`（DbSql 实例）的方法构造。构造器内部会把值交给 `$this->db->EscapeString()` 转义。

```php
// 正确
$sql = $zbp->db->sql->Select(
    $zbp->table['Post'],
    '*',
    array(array('=', 'log_ID', $id)),   // 值会被自动转义
    'log_PostTime DESC',
    10,
    null
);
$array = $zbp->GetListType('Post', $sql);
```

```php
// 错误 —— 永远不要这样写
$sql = "SELECT * FROM {$zbp->table['Post']} WHERE log_ID = $id";
```

## where 数组的转义行为

`sql/global.php` 中 `where()` 对数组条件的值统一调用 `$this->db->EscapeString()`：

- L591：`$y = $this->db->EscapeString((string) $value[2]);`（IN/BETWEEN 等）
- L631：`$y = $this->db->EscapeString((string) $value[($searchCount - 1)]);`
- L671：`$y[1] = $this->db->EscapeString($y[1]);`（BETWEEN）
- L697：`$y = $this->db->EscapeString($y);`（普通比较）
- L1234/1237/1241/1281：insert/update data 同样转义

支持的运算符（数组第一个元素）：`=`、`!=`、`<>`、`>`、`<`、`>=`、`<=`、`LIKE`、`NOT LIKE`、`IN`、`NOT IN`、`BETWEEN`、`NOT BETWEEN`、`SEARCH`（多列 OR LIKE）、`META`（Meta 表查询）、`EXISTS`、`NOT EXISTS`、`CUSTOM`（自定义表达式）。

**例外**：如果 `where` 传的是字符串而不是数组，DbSql 会原样拼接进 SQL，不做任何转义。这是历史遗留，插件开发中**只允许在 where 字符串里写字段名、AND/OR、括号，绝不写变量**。

## Insert / Update

```php
$sql = $zbp->db->sql->Insert($zbp->table['Post'], array(
    'log_Title'   => $title,   // 值自动转义
    'log_AuthorID'=> $zbp->user->ID,
));

$sql = $zbp->db->sql->Update(
    $zbp->table['Post'],
    array('log_Title' => $newTitle),
    array(array('=', 'log_ID', $id))
);
```

## 表前缀替换

SQL 中写 `%pre%` 占位符，由 `ReplacePre()` 自动替换为真实表前缀（dbsql.php L45-50）。不要硬编码 `zbp_`。

## 排序与 LIMIT

`orderBy($order)` 和 `limit($limit)` 接受字符串/数字，但仍建议：

- 排序字段白名单校验：`$order = in_array($order, array('log_PostTime', 'log_CommNums')) ? $order : 'log_PostTime';`
- 分页用 `(int)` 强转

## 常见错误模式

```php
// 危险：where 用字符串拼接变量
$w = "log_ID = " . GetVars('id');            // 注入
$w = array(array('=', 'log_ID', GetVars('id'))); // 安全

// 危险：把 $_GET 直接放进 orderBy
$sql->orderBy(GetVars('sort'));              // 可能注入
$allow = array('log_PostTime', 'log_ViewNums');
$sql->orderBy(in_array(GetVars('sort'), $allow) ? GetVars('sort') : 'log_PostTime');

// 危险：不用 DbSql 直接 $zbp->db->Query($sql)
// 除非在存储过程/特殊 DDL 场景，否则禁止
```

## 安全审计

- [ ] 全项目搜索 `->Query(`、`->query(`，确认没有拼接外部输入
- [ ] 搜索 `where` 参数是否为字符串拼接
- [ ] 确认所有 ID 类参数 `(int)` 强转或走数组 where
- [ ] 确认表名使用 `%pre%` 或 `$zbp->table[]`/`$zbp->datainfo[]`，不硬编码
