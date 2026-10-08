# API 开发

入口为 zb_system/api.php，按 mod 与 act 调度到函数 api_{mod}_{act}()。

## 实现流程

1. 先确认任务是调用现有接口还是新增端点，并按需读取 api-modules.md、api-structure.md 或 custom-api.md。
2. 系统接口使用 api.php?mod={mod}&act={act}，mod 和 act 使用小写；自定义端点通过 API 扩展钩子注册，核心不会自动扫描插件目录。
3. 新增端点依次处理 ZC_API_ENABLE、基础 ApiCheckAuth、POST CSRF、限流和动作级 ApiCheckAuth；返回标准数组交给统一 JSON 响应。
4. API 细节涉及权限、输入、输出或写操作时组合读取 ../zblogphp-security/ 和 ../zblogphp-database/。

## 按症状排错

- 在插件目录直接建 api/ 目录导致 404：通过 Filter_Plugin_API_Extend_Mods 或 ApiLoadCustomMods 注册。
- act 未返回数组或函数不存在：分别造成空 data 或 404 error 96。
- 误写成类方法：Z-BlogPHP API 使用纯函数 api_{mod}_{act}()。
- 未开启 ZC_API_ENABLE：请求返回 503 error 95。
