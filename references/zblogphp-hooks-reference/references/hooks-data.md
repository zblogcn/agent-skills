# 数据操作 / 对象方法 / 上传 / XML-RPC / API 类钩子

涵盖数据写入/删除的 `_Core` 与 `_Succeed` 系列、对象方法拦截（`Post_*` / `Category_*` / `Tag_*` / `Member_*` / `Comment_*` / `Module_*` / `Upload_*`）、`Upload` 文件操作、登录/登出、插件启用禁用、XML-RPC 与 API。所有钩子集中注册于 `zb_system/function/c_system_plugin.php`（行号即该文件行号）。

## 登录 / 登出（c_system_event.php、api/member.php 触发）

| 钩子 | 行号 | 说明 |
| --- | --- | --- |
| `Filter_Plugin_VerifyLogin_Succeed` | 1595 | 登录成功 |
| `Filter_Plugin_VerifyLogin_Failed` | 1606 | 登录失败 |
| `Filter_Plugin_Logout_Succeed` | 1617 | 登出成功 |

## 数据写入 _Core（操作**前**，可改写对象属性）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_PostArticle_Core` | 1947 | `&$article` | 文章编辑的核心接口 |
| `Filter_Plugin_PostPage_Core` | 1958 | `&$article` | 页面编辑的核心接口 |
| `Filter_Plugin_PostPost_Core` | 2145 | `&$post` | Post 类对象的通用编辑核心接口（1.7.0 加入） |
| `Filter_Plugin_PostCategory_Core` | 1914 | `&$cate` | 分类编辑的核心接口 |
| `Filter_Plugin_PostTag_Core` | 1903 | `&$tag` | 标签编辑的核心接口 |
| `Filter_Plugin_PostMember_Core` | 1892 | `&$mem` | 会员编辑的核心接口 |
| `Filter_Plugin_PostModule_Core` | 1881 | `&$mod` | 模块编辑的核心接口 |
| `Filter_Plugin_PostComment_Core` | 1925 | `&$cmt` | 评论发表的核心接口 |
| `Filter_Plugin_CheckComment_Core` | 1936 | `&$cmt` | 评论审核的核心接口 |

## 数据写入 _Succeed（操作**成功**后触发）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_PostArticle_Succeed` | 2035 | `&$article` | 文章编辑成功 |
| `Filter_Plugin_PostPage_Succeed` | 2024 | `&$article` | 页面编辑成功 |
| `Filter_Plugin_PostPost_Succeed` | 2167 | `&$post` | Post 通用编辑成功（1.7.0 加入） |
| `Filter_Plugin_PostCategory_Succeed` | 1991 | `&$cate` | 分类编辑成功 |
| `Filter_Plugin_PostTag_Succeed` | 1980 | `&$tag` | 标签编辑成功 |
| `Filter_Plugin_PostMember_Succeed` | 1969 | `&$mem` | 会员编辑成功 |
| `Filter_Plugin_PostModule_Succeed` | 2046 | `&$mod` | 模块编辑成功 |
| `Filter_Plugin_PostComment_Succeed` | 2002 | `&$cmt` | 评论发表成功 |
| `Filter_Plugin_CheckComment_Succeed` | 2013 | `&$cmt` | 评论审核成功 |
| `Filter_Plugin_PostUpload_Succeed` | 2057 | `&$upload` | 附件上传成功 |

## 数据删除（Core / Succeed）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_DelPost_Core` | 2156 | `&$post` | Post 通用删除核心接口（1.7.0 加入） |
| `Filter_Plugin_DelPost_Succeed` | 2178 | `&$post` | Post 通用删除成功接口（1.7.0 加入） |
| `Filter_Plugin_DelArticle_Succeed` | 2123 | `&$article` | 文章删除成功 |
| `Filter_Plugin_DelPage_Succeed` | 2112 | `&$article` | 页面删除成功 |
| `Filter_Plugin_DelCategory_Succeed` | 2090 | `&$cate` | 分类删除成功 |
| `Filter_Plugin_DelTag_Succeed` | 2079 | `&$tag` | 标签删除成功 |
| `Filter_Plugin_DelMember_Succeed` | 2068 | `&$mem` | 会员删除成功 |
| `Filter_Plugin_DelComment_Succeed` | 2101 | `&$cmt` | 评论删除成功 |
| `Filter_Plugin_DelModule_Succeed` | 2134 | `&$mod` | 模块删除成功 |

## 插件启用 / 禁用 / 批量提交

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_EnablePlugin` | 2189 | `&name`（源码注释如此，应为 `&$name`） | 1.6.0 加入 |
| `Filter_Plugin_DisablePlugin` | 2200 | `&name` | 1.6.0 加入 |
| `Filter_Plugin_BatchPost` | 2210 | `&type` | 1.6.1 加入 |

## 对象方法拦截：Post 类

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Post_Url` | 2225 | `&$this` | 干预 `Url` 方法 |
| `Filter_Plugin_Post_Get` | 2236 | `&$this, $method` | 干预 `Get` |
| `Filter_Plugin_Post_Set` | 2246 | `&$this, $method, $arg` | 干预 `Set` |
| `Filter_Plugin_Post_Thumbs` | 2257 | `&$this, &$all_images, &$width, &$height, &$count, &$clip` | 干预 `Thumbs` |
| `Filter_Plugin_Post_CommentPostUrl` | 2361 | `$post` | 返回 CommentPostUrl 值 |
| `Filter_Plugin_Post_Prev` | 2372 | `$post` | 返回 Prev 值 |
| `Filter_Plugin_Post_Next` | 2383 | `$post` | 返回 Next 值 |
| `Filter_Plugin_Post_RelatedList` | 2394 | `$post` | 返回 RelatedList Array |
| `Filter_Plugin_Post_Call` | 2405 | `&$post, $method, $args` | Post 类 `__call` 魔术方法 |
| `Filter_Plugin_Post_Del` | 2481 | `&$post` | Post 类 `Del` |
| `Filter_Plugin_Post_Save` | 2567 | `&$post` | Post 类 `Save` |

## 对象方法拦截：Category / Tag / Member / Comment / Module

每类对象的拦截钩子结构一致：`_Url`、`_Get`、`_Set`、`_Call`、`_Del`、`_Save`（Comment 无 `_Url`）。

| 对象 | 行号（Url/Get/Set/Call/Del/Save） |
| --- | --- |
| Category | 2268 / 2278 / 2288 / 2459 / 2514 / 2600 |
| Tag | 2299 / 2309 / 2319 / 2448 / 2492 / 2589 |
| Member | 2330 / 2340 / 2350 / 2470 / 2525 / 2611 |
| Comment | — / 2427 / 2437 / 2416 / 2503 / 2578 |
| Module | — / 2547 / 2557 / — / 2536 / 2622 |

参数模式：

- `_Url`: `&$this`
- `_Get`: `&$this, $method`
- `_Set`: `&$this, $method, $arg`
- `_Call`: `&$obj, $method, $args`
- `_Del` / `_Save`: `&$obj`

> 注：源码 2299 行注释写为 "Filter_Plugin_Category_Get"，但实际注册的是 `Filter_Plugin_Tag_Get`；以 `DefinePluginFilter('Filter_Plugin_Tag_Get')` 为准。

### Member 特例

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Member_Avatar` | 2633 | `$member` | 返回 Avatar 值，可返回 `null`；建议挂接时设 `PLUGIN_EXITSIGNAL_RETURN` 并在插件函数中 `return $url`。

## Upload 类

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Upload_SaveFile` | 2646 | `$tmp, $this` | `SaveFile` 方法接口，对 `$tmp` 临时文件进行拦截 |
| `Filter_Plugin_Upload_SaveBase64File` | 2657 | `$str64, $this` | `SaveBase64File` 方法接口 |
| `Filter_Plugin_Upload_Del` | 2668 | `$this` | `Del` 方法接口 |
| `Filter_Plugin_Upload_DelFile` | 2679 | `$this` | `DelFile` 方法接口 |
| `Filter_Plugin_Upload_Url` | 2690 | `$upload` | `Url` 方法接口，返回值可覆盖默认 URL（可返回 null） |
| `Filter_Plugin_Upload_Dir` | 2722 | `$upload` | `Dir` 方法接口，返回值可覆盖默认目录（可返回 null） |
| `Filter_Plugin_Upload_Get` | 2701 | `&$this, $method` | 干预 `Get` |
| `Filter_Plugin_Upload_Set` | 2711 | `&$this, $method, $arg` | 干预 `Set` |

## XML-RPC

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_Xmlrpc_Begin` | 2859 | `&xml`（源码注释如此，应为 `&$xml`） | xml-rpc 页 begin 接口（1.5.1 加入，zb_system/xml-rpc/index.php:852 触发） |

## API（zb_system/api/，1.7 引入）

| 钩子 | 行号 | 参数 | 说明 |
| --- | --- | --- | --- |
| `Filter_Plugin_API_Begin` | 2906 | — | API 启动 |
| `Filter_Plugin_API_Extend_Mods` | 2928 | — | API 的应用追加模块机制 |
| `Filter_Plugin_API_CheckMods` | 2939 | `&$mods_allow, &$mods_disallow` | API 黑白名单机制 |
| `Filter_Plugin_API_Dispatch` | 2917 | `$mods, $mod, $act` | API 分发前 |
| `Filter_Plugin_API_Get_Request_Filter` | 2950 | `&$condition` | API 获取约束过滤条件 |
| `Filter_Plugin_API_Get_Pagination_Info` | 2961 | `&$info, &$pagebar` | API 获取分页信息 |
| `Filter_Plugin_API_Get_Object_Array` | 2972 | `&$object, &$array, &$other_props, &$remove_props, &$with_relations` | 转换 Object 到 Array |
| `Filter_Plugin_API_VerifyCSRF_Skip` | 2983 | `&$skip_acts` | 校验 CSRF Token 跳过验证 |
| `Filter_Plugin_API_Pre_Response` | 2884 | `&$data, &$error, &$code, &$message` | API 响应处理前 |
| `Filter_Plugin_API_Pre_Response_Raw` | 3016 | `&$raw, &$$raw_type`（源码注释如此，应为 `&$raw, &$raw_type`） | 处理返回数据（Raw 模式） |
| `Filter_Plugin_API_Response` | 2895 | `&$response` | API 响应内容处理 |
| `Filter_Plugin_API_Result_Data` | 2994 | `&$result, $mod, $act` | 处理返回数据 |
| `Filter_Plugin_API_Post_List_Core` | 3005 | `&$select, $where, $order, $limit, $option` | 处理 `api_post_list` 的查询 |
