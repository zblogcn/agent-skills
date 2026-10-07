# 数据库开发

Z-BlogPHP 数据访问分为 DbSql 查询构造器、Base 模型和 Config/Metas 键值扩展三层。

## 实现流程

1. 读取 models.md、dbsql.md、config-metas.md 或 schema.md，按数据对象和操作类型选资料。
2. 单个实体优先使用 Base 模型；条件列表使用 GetPostList 等封装；复杂查询或自定义表使用 DbSql 与 db 操作。
3. SQL 表名使用 %pre% 或 $zbp->table，值走 DbSql 的转义路径；不要拼接外部输入。Config 写入后调用 SaveConfig，Metas 写入后保存外层对象。
4. 写操作组合读取 ../zblogphp-security/，确认权限与 CSRF；需要 API 输出时组合读取 ../zblogphp-api/。

## 按症状排错

- 硬编码 zbp_post 或表前缀：换站点配置会失效；使用 %pre% 或表映射。
- LoadInfoByID 失败后直接 Save：ID 为空会误插入新行。
- 把数组或对象写入普通模型属性：复杂值放 Metas。
- 忘记 SaveConfig：配置只在内存中。
