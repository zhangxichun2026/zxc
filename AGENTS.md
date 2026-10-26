# AGENTS.md — 项目规则（D:\高级网页vscode）

> 所有 AI Agent / 开发者在本项目下**新建或修改文件**时必须遵守本规则。
> 最后更新：2026-10-26

---

## 1. HTML 页头注释（新建 .html 文件必填）

每个新建的 `.html` 文件，必须在 `<html>` 标签之后、`<head>` 之前加入一条注释，包含四项信息：**姓名、建立时间、使用的大模型、功能名称**。

格式：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<!-- 姓名：张熙淳，建立时间：YYYY-MM-DD，使用模型：模型名称，功能名称：xxx -->
<head>
```

实际示例：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<!-- 姓名：张熙淳，建立时间：2026-10-26，使用模型：GLM-5.3-Flash，功能名称：数7游戏 一百个盒子演示 -->
<head>
```

说明：
- **建立时间**：创建文件当天的日期，格式 `YYYY-MM-DD`。
- **使用模型**：生成本文件时所使用的大模型名称（如 `GLM-5.3-Flash`、`Claude`、`GPT` 等）。
- **功能名称**：本页面实现的功能，简明中文描述。

## 2. 命名前缀

所有 **JS 变量**、**CSS 类名**、**HTML id** 一律以 `zxc_` 开头。

```js
// ❌ 错误
var name = "张三";

// ✅ 正确
var zxc_name = "张三";
```

```css
/* ❌ 错误 */
.container { }
#header { }

/* ✅ 正确 */
.zxc_container { }
#zxc_header { }
```

## 3. 技术栈限制

仅使用 **原生 HTML**、**原生 CSS**、**原生 JavaScript**。

**严格禁止**：
- 任何第三方 JS 库（jQuery、axios、lodash、Vue、React 等）
- 任何第三方 CSS 框架（Bootstrap、Tailwind 等）
- 任何 CDN 链接（如 `https://cdn.jsdelivr.net/...`）

## 4. 图标规范

图标一律使用本地 `font/` 目录下的 iconfont 字体文件，禁止使用在线图标 CDN。

HTML 引入：

```html
<link rel="stylesheet" href="font/iconfont.css">
```

HTML 使用：

```html
<i class="iconfont zxc_icon_search"></i>
```

> ⚠️ 当前项目中 `font/` 目录尚未创建，需先将 iconfont.css + 字体文件（.woff2 / .woff / .ttf / .eot）放入 `D:\高级网页vscode\font\`。

## 5. 网络请求

所有与服务器端的数据交互，**只允许使用原生 `fetch` API**。

```js
// ✅ 正确
fetch('/api/data')
    .then(function (zxc_res) { return zxc_res.json(); })
    .then(function (zxc_data) { console.log(zxc_data); });

// ❌ 禁止
// - XMLHttpRequest
// - axios / $.ajax
// - 任何第三方封装库
```

---

## 历史变更

| 时间 | 变更 |
|------|------|
| 2026-10-12 | 初始规则：`zhang_` 前缀（见 zhang_prompt.md 记录 #1-3） |
| 2026-10-22 | 升级为 `zxc_` 前缀；新增：原生技术栈 / iconfont / fetch（记录 #4） |
| 2026-10-26 | 页头注释格式升级：增加「建立时间」「使用的大模型」字段；新建本 AGENTS.md（记录 #5） |
