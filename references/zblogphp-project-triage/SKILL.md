# 项目识别

## 实现流程

运行 detect_zblog_project.mjs 目录路径，或按下列确定性标志手工判断：

- 站点根：同时存在 zb_system、zb_users 和 zb_system/function/c_system_base.php
- 插件目录：存在 plugin.xml，且 id 与目录名一致，并位于 zb_users/plugin/ 下
- 主题目录：存在 theme.xml 且包含 theme version="php"，并位于 zb_users/theme/ 下
- 均不满足：返回 unknown，不套用 Z-BlogPHP 约定

需要站点配置或已安装应用清单时，再读取 zb_users/c_option.php 或对应的 zb_users/plugin/、zb_users/theme/ 目录。

## 按症状排错

- 解压层级不完整导致找不到 zb_system：确认用户给出的路径层级。
- c_option.php 不存在：说明站点可能尚未完成安装，继续处理不依赖该配置的任务。