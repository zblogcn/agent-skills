# 系统自带 API mod 一览

mod 文件位于 `zb_system/api/`，共 9 个（由 `ApiLoadSystemMods` 扫描注册）。每个 act 对应文件内一个函数 `api_{mod}_{act}()`。以下 act 列表逐一取自 1.7.5.3540 源码（grep `^function api_` 结果）。

调用形式：`{host}zb_system/api.php?mod={mod}&act={act}&...`

## post（zb_system/api/post.php）

| act | 函数 | 说明 | 关键参数 / 权限 |
|---|---|---|---|
| get | api_post_get | 获取单篇文章/页面 | `id`；公开文章需 `view` 权限，非公开需作者本人或 `all` 权限；`viewnums=true` 增加浏览数；`with_relations=Author,Category,Tags` |
| post | api_post_post | 新增/修改文章/页面 | 需登录 + `{type}_post` 权限；`Type`、`CateID`（或 `CateName`）、`PostTime`（支持秒/毫秒时间戳或时间字符串） |
| delete | api_post_delete | 删除文章/页面 | 需登录 + del 权限；强制 CSRF（`ApiVerifyCSRF(true)`） |
| list | api_post_list | 文章列表 | `cate_id/cate_alias/with_subcate/tag_id/auth_id/auth_name/date/search/type/manage`；`manage=1` 走管理模式（manage 权限），否则只返回公开文章，每页默认 `ZC_API_DISPLAY_COUNT`；排序 `sortby=ID/CreateTime/PostTime/UpdateTime/CommNums/ViewNums&order=DESC`；`without_content=1` 剔除正文 |

list 返回：

```json
{ "code": 200, "message": "OK", "data": { "list": [...], "pagebar": { "AllCount": 100, "PageNow": 1, "PageAll": 10, ... } }, "error": null }
```

## system（zb_system/api/system.php）

| act | 函数 | 说明 | 权限 |
|---|---|---|---|
| basic_info | api_system_basic_info | 站点基本信息（name/host/version/各项 count/当前登录用户） | `view`，无需登录 |
| get_info | api_system_get_info | 系统信息（环境/文章数/启用应用等；root 额外返回 php、db 版本、扩展列表） | 登录 + `admin` |
| get_setting | api_system_get_setting | 读取白名单内系统设置 | 登录 + `root` + `SettingMng` |
| save_setting | api_system_save_setting | 更新白名单内系统设置（`$setting_keys`，文件顶部 L14-49） | 登录 + `root` + `SettingSav` |
| misc_statistic | api_system_misc_statistic | 清空缓存并重新统计 | 强制 CSRF；`root` + `misc` |
| misc_showtags | api_system_misc_showtags | 常用 tag 列表（按 Count 排序前 100） | 登录 + `misc` |

## member（zb_system/api/member.php）

| act | 函数 | 说明 |
|---|---|---|
| login | api_member_login | 登录，返回 `{user, token, expire_time}`（token 供后续 Bearer 认证）；POST 免 CSRF |
| logout | api_member_logout | 登出（客户端自行删 token） |
| get | api_member_get | 获取用户；带 `id` 查他人需 `MemberMng`，否则查自己 |
| post | api_member_post | 新增/修改用户（`MemberPst`） |
| delete | api_member_delete | 删除用户 |
| list | api_member_list | 用户列表 |
| get_auth | api_member_get_auth | 获取当前登录状态与权限 |

Member 输出经 `ApiGetObjectArray` 自动剔除 `Guid/Password/IP`。

## comment（zb_system/api/comment.php）

| act | 函数 | 说明 |
|---|---|---|
| get | api_comment_get | 获取单条评论 |
| post | api_comment_post | 发表评论（POST 免 CSRF，内置白名单） |
| delete | api_comment_delete | 删除评论 |
| list | api_comment_list | 评论列表（`post_id` 等过滤） |
| check | api_comment_check | 评论前校验（验证码等） |
| batch | api_comment_batch | 批量操作（审核/删除） |

## category / tag（zb_system/api/category.php、tag.php）

两者结构一致，均为标准四 act：

| act | 说明 |
|---|---|
| get | 获取单个（`id`） |
| post | 新增/修改 |
| delete | 删除 |
| list | 列表（tag 支持 `sortby=Count` 等） |

## module（zb_system/api/module.php）

| act | 说明 |
|---|---|
| get / post / delete / list | 模块的标准 CRUD |
| set_sidebar | 设置侧栏模块布局 |
| list_sidebar | 获取侧栏布局 |

## upload（zb_system/api/upload.php）

| act | 说明 |
|---|---|
| get / post / delete / list | 附件的标准 CRUD；post 为上传（ multipart ） |

## app（zb_system/api/app.php）

应用管理，全部需要高权限：

| act | 说明 |
|---|---|
| get | 获取单个应用信息 |
| get_apps / get_plugins / get_themes | 应用/插件/主题列表 |
| enable_plugin / disable_plugin | 启用/停用插件 |
| set_theme | 切换主题 |

## 通用请求参数（列表类 act）

由 `ApiGetRequestFilter`（c_system_api.php L566）解析：

- `sortby` + `order=ASC|DESC`（sortby 必须在 act 声明的 `$sortableColumns` 白名单内）
- `page`（页码）、`perpage`（每页条数，上限 `$zbp->apiMaxCountPerPage = 50`）
- `with_relations=Author,Category,Tags`：按 act 声明的关联白名单附带关联对象
