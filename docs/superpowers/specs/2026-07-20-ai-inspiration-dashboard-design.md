# AI 灵感看板 —— 设计规格文档

> **目标用户：** AI 工具测评博主秋芝2046 及其团队
> **核心价值：** 把每天花 1-2 小时刷多个平台找选题的时间压缩到 5 分钟

---

## 1. 产品概述

一个每日自动更新的静态网页看板，聚合 ProductHunt 每日 Top 6 新品，经 DeepSeek V4 AI 自动评分（视频化程度、小白友好度、热度）并生成视频创作灵感建议，按推荐度排序展示。

- **站点名称：** "秋芝选题站"
- **部署地址：** CloudBase 静态托管（`xxx.tcloudbase.com`）
- **访问方式：** 无需登录，有链接就能看
- **更新频率：** 每天北京时间 15:01 自动更新

---

## 2. 技术架构

```
GitHub Actions 每日定时
  → ProductHunt GraphQL API（拉 Top 6）
  → DeepSeek V4 Pro（三维度打分+视频灵感）
  → 生成 JSON 存入仓库 public/data/
  → git commit & push
  → CloudBase 检测更新 → 构建 Vue → 部署静态文件
  → 用户浏览器加载（收藏/笔记存 localStorage）
```

**技术栈：**

| 层 | 选型 |
|---|---|
| 构建脚本 | Python 3.x |
| 前端框架 | Vue 3 + Vite |
| AI 服务 | DeepSeek V4 Pro（`deepseek-v4-pro`） |
| 数据源 | ProductHunt GraphQL API v2 |
| 定时触发 | GitHub Actions（cron: `01 7 * * *`） |
| 静态托管 | 腾讯云 CloudBase 静态网站托管 |
| 用户数据 | 浏览器 LocalStorage |

---

## 3. 数据管线

### 3.1 触发方式

- GitHub Actions 每天 UTC 7:01（北京时间 15:01）自动运行
- 支持 `workflow_dispatch` 手动触发

### 3.2 数据抓取

ProductHunt GraphQL API v2，按票数排序，取前一天 Top 6：

```graphql
posts(order: VOTES, postedAfter: "${date}T00:00:00Z",
      postedBefore: "${date}T23:59:59Z", first: 6)
```

每个产品提取字段：`id, name, tagline, description, votesCount, createdAt, website, url, media`

### 3.3 LLM 处理

每个产品调用一次 DeepSeek V4 Pro，System Prompt 要求输出结构化 JSON，包含：

- **中文翻译：** 产品名称、标语、简介（科普风格，通俗口语化）
- **三维度评分（各 1-5 分 + 理由）：**
  - 🎬 视频化程度：画面观感、演示效果、视觉冲击力
  - 🌱 小白友好度：概念复杂度、技术门槛、使用门槛
  - 🔥 热度：PH 排名、票数、话题性
- **视频灵感建议：** 标题灵感、拍摄角度、拍摄建议、目标观众
- **综合建议：** 强力推荐 / 可以做 / 谨慎考虑 + 理由

评分与建议映射规则：
- 🎬≥4 且 🌱≥4 → 强力推荐
- 🎬≥2 → 可以做
- 其余 → 谨慎考虑

### 3.4 输出格式

数据文件保存在 `public/data/YYYY-MM-DD.json`：

```json
{
  "date": "2026-07-19",
  "generated_at": "2026-07-20T15:01:00+08:00",
  "generation_error": false,
  "products": [
    {
      "id": "product-hunt-id",
      "name": "原始英文名",
      "name_zh": "中文译名",
      "tagline_zh": "中文标语",
      "description_zh": "中文简介",
      "url": "PH链接",
      "website": "产品官网",
      "image_url": "封面图URL",
      "votes_count": 834,
      "scores": {
        "video_suitability": { "score": 4, "reason": "..." },
        "beginner_friendly": { "score": 5, "reason": "..." },
        "popularity": { "score": 4, "reason": "..." }
      },
      "video_inspiration": {
        "title_idea": "...",
        "angle": "...",
        "shooting_tips": "...",
        "target_audience": "..."
      },
      "overall_suggestion": "强力推荐",
      "overall_reason": "..."
    }
  ]
}
```

---

## 4. 前端组件

### 4.1 路由设计（URL search params，无 vue-router）

| 路由 | 说明 |
|---|---|
| `/` | 首页，默认最新日期 |
| `/?date=2026-07-19` | 首页，指定日期 |
| `/?date=2026-07-19&id=1172870` | 首页 + 自动打开指定产品详情弹窗 |
| `/workspace` | 个人工作台 |

### 4.2 组件树

```
App.vue
├── NavBar.vue              站点名 + 榜单/工作台切换
├── HomePage.vue            首页榜单
│   ├── DatePicker.vue      日期选择器
│   └── ProductCard.vue ×6  产品卡片
│       ├── ScoreBar.vue    三维度星级
│       ├── SuggestionTag.vue  彩色综合建议标签
│       └── BookmarkButton.vue 收藏星标按钮
├── ProductDetail.vue（弹窗）产品详情
│   ├── ScoreDetail.vue     评分详细分析
│   ├── VideoInspiration.vue 拍摄建议卡片
│   └── NotesEditor.vue     个人笔记（可编辑,自动保存）
└── Workspace.vue           个人工作台
    ├── BookmarkList.vue    收藏列表（筛选/排序/取消）
    ├── NotesList.vue       笔记列表（筛选/展开/编辑）
    └── DataExport.vue      导出JSON/清空数据
```

### 4.3 首页 UI 要点

- 产品卡片横向排列（桌面端 2-3 列，移动端单列）
- 排名序号醒目大数字
- 产品封面图 + 名称（中英） + 一句话简介
- 三维度星级展示
- 综合建议彩色标签：🟢强力推荐 / 🟡可以做 / 🔴谨慎考虑
- 收藏星标按钮
- 点击卡片 → 打开详情弹窗

### 4.4 产品详情弹窗

- 大图封面
- 名称 + 简介 + 原 ProductHunt 链接
- 热度数据（Upvote 数）
- 三维度详细分析（每维度：评分、一句话结论、详细理由、拍摄建议）
- 视频灵感完整卡片（标题灵感、角度、技巧、受众）
- 个人笔记区（textarea，自动保存到 localStorage）
- 底部：收藏按钮 / 上一个下一个切换 / 关闭

### 4.5 个人工作台

- **我的收藏：** 卡片列表，按日期筛选、按评分排序，支持取消收藏
- **我的笔记：** 产品名 + 笔记摘要（前 50 字），展开可看完整内容并编辑，按日期筛选
- **数据导出：** 导出 JSON（全部/仅收藏/仅笔记可选），浏览器 Blob 下载
- **数据管理：** 清空数据按钮（二次确认），显示本地数据占用大小

---

## 5. 数据存储

| 数据类型 | 来源 | 存储位置 |
|---|---|---|
| 产品榜单数据 | ProductHunt API（构建时抓取） | `public/data/YYYY-MM-DD.json` |
| 收藏状态 | 用户操作 | 浏览器 localStorage |
| 个人笔记 | 用户输入 | 浏览器 localStorage |
| 导出文件 | 本地数据聚合 | 浏览器下载 |

---

## 6. 错误处理 & 容错

| 环节 | 可能错误 | 处置 |
|---|---|---|
| ProductHunt API | 超时/限流/Token 过期 | 重试 3 次（间隔递增）；仍失败则复用前一天数据并标记 `generation_error: true` |
| DeepSeek API | 超时/余额不足/JSON 格式错误 | 单个产品失败不影响其他——该产品字段为 null，前端显示"评分暂不可用"。全部失败则复用前一天数据 |
| Git Push | 网络问题 | 失败不阻塞，下次定时触发自动补上 |
| CloudBase 部署 | 构建失败 | CloudBase 回滚到上一个可用版本 |
| 前端加载 | 某日 JSON 不存在 | 显示"该日期暂无数据"，日期选择器灰掉无数据日期 |

页面底部提示：`数据更新时间：YYYY-MM-DD HH:MM | 如未更新可能是上游 API 延迟，稍后刷新即可`

---

## 7. 部署配置

### 7.1 GitHub Secrets（用户配置）

| Secret | 说明 |
|---|---|
| `PRODUCTHUNT_DEVELOPER_TOKEN` | ProductHunt Developer Token |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `TCB_ENV_ID` | CloudBase 环境 ID |
| `TCB_SECRET_ID` | 腾讯云 API SecretId |
| `TCB_SECRET_KEY` | 腾讯云 API SecretKey |

### 7.2 环境变量（前端构建时）

| 变量 | 说明 |
|---|---|
| `VITE_DATA_BASE_URL` | JSON 数据文件的基础路径，默认 `/data/` |

---

## 8. 不做的事（YAGNI）

- ❌ HackerNews / AI 公司动态数据源（V1 聚焦 ProductHunt）
- ❌ 用户登录/注册/多用户
- ❌ 后端服务 / 数据库
- ❌ 服务端 API
- ❌ 内容推荐算法 / 个性化
- ❌ 评论区 / 社交功能
- ❌ SEO 优化（内部工具）
- ❌ 微信小程序 / 移动端 App（移动端响应式适配即可）

---

## 9. 成功标准

1. 秋芝打开网页 5 分钟内能浏览完当天所有产品的评分和建议
2. 每天自动化运行，无需人工干预
3. 收藏和笔记功能正常，数据不丢失
4. 支持切换历史日期查看过往榜单
