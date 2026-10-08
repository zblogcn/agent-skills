# 页面图标与图片

适用于主题前台、插件页面和后台功能代码；素材选用见[共同约定](application-conventions.md#图片图标与-svg)。本文记录 Z-Blog icon 字体的加载和使用。

## Z-Blog 自带图标字体

样式地址：`zb_system/image/icon/icon.css?v=173540`。

- 字体名为 `zblog`，样式通过相对路径加载同目录的 `zblog.ttf`。
- 类名为 `icon-*`，由 `:before` 输出字体图标；不需要额外的 `icon` 或 `bi` 基类。
- 页面已加载此样式时直接使用；未加载时从站点 URL 引入一次，避免从当前插件或主题目录解析相对地址。
- 图标类放在独立的 `i` / `span` 元素上，通过 `font-size`、`color` 调整大小与颜色；不要把图标字体应用到整段文字。

主题模板引入方式：

```html
<link rel="stylesheet" href="{$host}zb_system/image/icon/icon.css?v=173540">
```

PHP 页面引入方式：

```php
<link rel="stylesheet" href="<?php echo $zbp->host; ?>zb_system/image/icon/icon.css?v=173540">
```

按钮示例：

```html
<button type="button"><i class="icon-gear" aria-hidden="true"></i> 设置</button>
<button type="button" aria-label="搜索"><i class="icon-search" aria-hidden="true"></i></button>
```

## 常用类名

| 用途 | 类名 |
|---|---|
| 首页、菜单 | `icon-house`、`icon-list` |
| 搜索、设置 | `icon-search`、`icon-gear`、`icon-gear-fill`、`icon-sliders` |
| 新增、编辑、删除 | `icon-plus`、`icon-plus-circle`、`icon-pencil-square`、`icon-trash` |
| 确认、关闭 | `icon-check`、`icon-check-circle`、`icon-x`、`icon-x-circle` |
| 上传、下载、图片 | `icon-upload`、`icon-download`、`icon-image`、`icon-images` |
| 链接、刷新 | `icon-link`、`icon-link-45deg`、`icon-arrow-clockwise` |
| 用户、时间、通知 | `icon-person`、`icon-people`、`icon-calendar`、`icon-clock`、`icon-bell` |
| 收藏、喜欢、查看 | `icon-star`、`icon-star-fill`、`icon-heart`、`icon-eye` |
| 安全、锁定 | `icon-shield-check`、`icon-lock` |
| 帮助、提示、警告 | `icon-question-circle-fill`、`icon-info-circle`、`icon-exclamation-triangle` |
| 方向 | `icon-chevron-left`、`icon-chevron-right`、`icon-chevron-up`、`icon-chevron-down` |
| Z-Blog 标识 | `icon-zblog`、`icon-zblogphp`、`icon-zblog-appcenter` |

`MakeLeftMenu()` / `MakeTopMenu()` 的图标参数可直接传上述类名，调用方式见 [menus.md](zblogphp-admin-menus.md)。
