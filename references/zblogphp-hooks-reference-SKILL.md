# Hook 参考

## 实现流程

1. 按扩展点类别读取 hooks-core.md、hooks-admin.md、hooks-view.md 或 hooks-data.md。
2. 用 using-hooks.md 的规范注册：先 RegisterPlugin，再在 ActivePlugin_xxx 中 Add_Filter_Plugin。
3. 回写参数声明引用符号；需要宿主提前返回时设置对应的 PLUGIN_EXITSIGNAL_RETURN 或 BREAK 信号。
4. Hook 任务需要后台、数据库、API 或安全知识时，再读取对应专题目录。

## 按症状排错

- 钩子不触发：插件未启用、激活函数未挂接或名称不一致。
- 参数修改无效：回调参数缺少引用。
- return 后仍继续执行：未设置退出信号。
- Add_Filter_Plugin 返回 false：目标钩子未被定义。
- 同名函数无法重复挂接：按函数名去重，替换实现前先 Remove_Filter_Plugin。
