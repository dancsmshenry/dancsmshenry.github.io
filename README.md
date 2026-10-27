# dancsmshenry.github.io

个人技术博客，基于 **Hexo 3.9.0** + **Matery** 主题，部署在 **GitHub Pages**。

- 站点地址：https://dancsmshenry.github.io
- 源码仓库：`git@github.com:dancsmshenry/dancsmshenry.github.io.git`
- 部署分支：`main`

## 环境要求

| 项目 | 要求 |
|---|---|
| Node.js | **最低 16**；当前验证 **24.16.0**（推荐使用 24.x） |
| npm | 随 Node.js 安装 |
| Hexo | 3.9.0（项目本地依赖，无需全局安装） |
| Git | 部署到 GitHub Pages 需要 |
| SSH | 需要为 GitHub 配置可推送的 SSH key |

> 项目已在 Node.js 24.16.0 / npm 11.13.0 / macOS arm64 下验证。Node 16 已 EOL，仅作为最低兼容线。
> 由于 Hexo 3.9 较老，Node 14+ 需要 `tools/patch-hexo-generate.js` 修补 generate 命令，并用 `tools/patch-hexo-fs.js` 修补 deploy 时的文件复制；`npm install` 会自动执行这两个补丁。

## 快速开始

```bash
# 1. 安装依赖（会自动执行 postinstall 补丁）
npm install

# 2. 本地预览
npx hexo server
# 打开 http://localhost:4000
```

不需要全局安装 `hexo-cli`；`npx hexo` 会使用项目本地的 Hexo。

## 常用命令

| 命令 | 作用 |
|---|---|
| `npx hexo clean` | 删除 `public/` 和 `db.json` |
| `npx hexo generate` / `npx hexo g` | 生成静态站点到 `public/` |
| `npx hexo server` / `npx hexo s` | 本地预览（默认 4000 端口） |
| `npx hexo deploy` / `npx hexo d` | 部署到 GitHub Pages |
| `npx hexo new post "标题"` | 新建文章 |
| `npx hexo version` | 查看 Hexo / Node 版本 |
| `node tools/patch-hexo-generate.js` | 手动修补 generate 的 Node 兼容问题 |
| `node tools/patch-hexo-fs.js` | 手动修补 deploy 的 hexo-fs 复制问题 |

完整构建并部署：

```bash
npx hexo clean
npx hexo generate
npx hexo deploy
```

或者：

```bash
npx hexo clean && npx hexo generate && npx hexo deploy
```

> `hexo server` 是长驻进程；不要把它和 `deploy` 写在同一个脚本里直接顺序执行。

## 部署环境

| 项目 | 配置 |
|---|---|
| 托管平台 | GitHub Pages |
| 仓库 | `git@github.com:dancsmshenry/dancsmshenry.github.io.git` |
| 分支 | `main` |
| 站点 URL | https://dancsmshenry.github.io |
| 自定义域名 | 无（`source/CNAME` 已移除） |
| 部署插件 | `hexo-deployer-git` |

部署前确认：

1. 已配置可推送该仓库的 SSH key。
2. `npm install` 已执行（postinstall 会修补 Hexo generate 和 hexo-fs）。
3. `npx hexo clean && npx hexo generate` 成功，且：
   ```bash
   find public -type f -size 0 | wc -l   # 必须是 0
   ```
4. 再执行 `npx hexo deploy`。

如果以后要启用自定义域名，添加 `source/CNAME` 并配置 DNS；当前使用 GitHub Pages 默认域名。

## 项目结构

```text
.
├── _config.yml                  # Hexo 站点配置
├── package.json                 # 依赖与 postinstall
├── tools/
│   ├── patch-hexo-generate.js   # Node 14+ / Hexo 3.9 generate 补丁
│   └── patch-hexo-fs.js         # Node 24 / hexo-fs 复制补丁
├── themes/matery/               # Matery 主题（模板、样式、资源）
├── source/
│   ├── _posts/                  # 文章与文章资源目录
│   ├── _data/                   # 音乐、友链等数据
│   ├── about/                   # 关于页
│   ├── archives/                # 归档页
│   ├── categories/              # 分类页
│   ├── tags/                    # 标签页
│   └── ...
├── bug_fix/                     # Node 兼容性与问题修复记录
├── public/                      # 构建产物（gitignore）
└── db.json                      # Hexo 缓存（gitignore）
```

## 依赖组件

### 核心

| 组件 | 版本 | 用途 |
|---|---|---|
| `hexo` | `^3.9.0`（当前 3.9.0） | 静态站点生成器 |
| `hexo-server` | `^0.3.3` | 本地预览服务器 |

### 渲染器

| 组件 | 版本 | 用途 |
|---|---|---|
| `hexo-renderer-ejs` | `^0.3.1` | 渲染主题 EJS 模板 |
| `hexo-renderer-marked` | `^1.0.1` | 渲染 Markdown |
| `hexo-renderer-stylus` | `^0.3.3` | 渲染 Stylus 样式 |

### 生成器

| 组件 | 版本 | 用途 |
|---|---|---|
| `hexo-generator-index` | `^0.2.1` | 首页分页 |
| `hexo-generator-archive` | `^0.1.5` | 归档页 |
| `hexo-generator-category` | `^0.1.3` | 分类页（当前未使用） |
| `hexo-generator-tag` | `^0.2.0` | 标签页 |
| `hexo-generator-feed` | `^1.2.2` | `atom.xml` |
| `hexo-generator-sitemap` | `^1.2.0` | `sitemap.xml` |
| `hexo-generator-baidu-sitemap` | `^0.1.6` | `baidusitemap.xml` |
| `hexo-generator-search` | `^2.4.0` | `search.xml` 搜索索引 |

### 部署与内容插件

| 组件 | 版本 | 用途 |
|---|---|---|
| `hexo-deployer-git` | `^1.0.0` | 部署到 GitHub Pages |
| `hexo-prism-plugin` | `^2.3.0` | 代码高亮（Prism，tomorrow 主题） |
| `hexo-permalink-pinyin` | `^1.1.0` | 中文标题转拼音 URL |
| `hexo-wordcount` | `^6.0.1` | 字数统计与阅读时长 |
| `hexo-baidu-url-submit` | `0.0.6` | 生成 `baidu_urls.txt`（deploy 类型与 token 已移除） |
| `hexo-helper-live2d` | `^3.1.1` | Live2D 插件（当前关闭） |

### 工具

| 组件 | 版本 | 用途 |
|---|---|---|
| `lodash` | `^4.17.21` | 工具函数 |
| `eslint` | `^6.0.1` | JS 代码检查（可选） |
| `opencollective-postinstall` | `^2.0.3` | 依赖安装提示 |

### 主题与兼容性

- **主题**：Matery，位于 `themes/matery/`（随仓库提供，不是 npm 依赖）。
- **Node 24 兼容**：
  - `package.json` 的 `overrides.hexo-front-matter` 固定为 `1.0.0`。
  - `tools/patch-hexo-generate.js` 修复 Hexo 3.9 在 Node 14+ 下 generate 输出 0 字节的问题。
  - `tools/patch-hexo-fs.js` 修复 Node 24 下 `hexo d` 复制 public 时 `fs.copyFile` 的 mode 参数错误。
  - 这些补丁都由 `npm install` 自动应用。

## 写文章

```bash
npx hexo new post "文章标题"
```

文章生成在 `source/_posts/`。项目开启了 `post_asset_folder: true`，因此会同时创建同名资源目录，图片可直接放在该目录并使用相对路径引用。

常用 front matter：

```yaml
title: 文章标题
date: 2026-10-27 12:00:00
tags:
- CPP
toc: true
mathjax: false   # 只有需要公式的文章才设为 true
```

- 本项目当前不使用 `categories`；如需分类，可自行在 front matter 中添加 `categories` 字段。
- 只有真正使用公式的文章才设置 `mathjax: true`，避免无谓加载 MathJax。
- 搜索索引由 `hexo-generator-search` 生成，页面首次点击搜索图标时才会加载。

## 注意事项

- **不要把 Node 工具脚本放在 `scripts/`**：Hexo 会把该目录下的 `.js` 当插件自动加载。工具脚本放在 `tools/`。
- **部署前必须检查 0 字节文件**：
  ```bash
  npx hexo clean && npx hexo generate
  find public -type f -size 0 | wc -l   # 必须是 0
  ```
- 如果 `hexo g` 后出现大量 0 字节文件，执行：
  ```bash
  node tools/patch-hexo-generate.js
  npx hexo clean && npx hexo generate
  ```
- 如果 `hexo d` 报 `TypeError: mode must be int32 or null/undefined`，执行：
  ```bash
  node tools/patch-hexo-fs.js
  npx hexo clean && npx hexo generate && npx hexo deploy
  ```
- `build.sh` 已移除；构建和部署命令以本文档为准。
- 百度提交的 token 已从 `_config.yml` 移除；`baidu_urls.txt` 仍会生成。
- 更多兼容性说明见 `bug_fix/node24-hexo-compatibility.md`，已修复问题见 `bug_fix/hexo-fix-report-2026-10-27.md`，剩余问题见 `bug_fix/hexo-audit-2026-10-22.md`。
