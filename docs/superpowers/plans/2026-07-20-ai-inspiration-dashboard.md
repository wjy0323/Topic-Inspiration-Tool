# AI 灵感看板 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建"秋芝选题站"——每日自动从 ProductHunt 拉取 Top 6 产品，经 DeepSeek V4 打分后生成静态 JSON，通过 Vue 3 单页应用展示，部署到腾讯云 CloudBase。

**Architecture:** GitHub Actions 每天 15:01 运行 Python 脚本 → ProductHunt GraphQL API 抓数据 → DeepSeek V4 Pro 打分 → JSON 写入 `public/data/` → git push → CloudBase 构建 Vue → 部署。前端为 Vue 3 + Vite 单页应用，收藏/笔记存储在浏览器 localStorage，无需后端。

**Tech Stack:** Python 3.x, Vue 3 (Composition API, `<script setup>`), Vite, DeepSeek V4 Pro API, ProductHunt GraphQL API v2, GitHub Actions, CloudBase 静态托管

## Global Constraints

- 站点名称："秋芝选题站"
- 每日产品数量：6 个（Top 6 by votes）
- 评分维度：3 个（video_suitability, beginner_friendly, popularity），各 1-5 整数
- 综合建议三档：强力推荐 / 可以做 / 谨慎考虑（🎬≥4 且 🌱≥4 → 强力推荐；🎬≥2 → 可以做；其余 → 谨慎考虑）
- 数据文件命名：`YYYY-MM-DD.json`，存放于 `public/data/`
- URL 路由：使用 search params（`?date=YYYY-MM-DD&id=PRODUCT_ID`），不使用 vue-router
- 用户数据：全部存储在 localStorage，无后端
- 定时时间：每天 UTC 7:01（北京时间 15:01）
- 所有命令和路径使用 Unix 风格（Git Bash）

---

## 文件结构总览

```
Topic Inspiration Tool/
├── .github/workflows/
│   └── daily.yml                   # 定时抓数据+部署
├── scripts/
│   ├── fetch_and_score.py          # 数据管线脚本
│   └── requirements.txt            # Python 依赖
├── src/
│   ├── main.js                     # Vue 入口，createApp
│   ├── App.vue                     # 根组件：路由+布局
│   ├── composables/
│   │   ├── useData.js              # 加载 JSON 数据
│   │   ├── useBookmarks.js         # 收藏管理（localStorage）
│   │   └── useNotes.js             # 笔记管理（localStorage）
│   ├── components/
│   │   ├── NavBar.vue              # 顶部导航
│   │   ├── DatePicker.vue          # 日期选择器
│   │   ├── ProductCard.vue         # 产品卡片
│   │   ├── ScoreBar.vue            # 三维度星级
│   │   ├── SuggestionTag.vue       # 综合建议标签
│   │   ├── BookmarkButton.vue      # 收藏星标按钮
│   │   ├── ProductDetail.vue       # 产品详情弹窗
│   │   ├── ScoreDetail.vue         # 评分详细展开
│   │   ├── VideoInspiration.vue    # 视频灵感卡片
│   │   ├── NotesEditor.vue         # 笔记编辑器
│   │   ├── Workspace.vue           # 个人工作台
│   │   ├── BookmarkList.vue        # 收藏列表
│   │   ├── NotesList.vue           # 笔记列表
│   │   └── DataExport.vue          # 数据导出
│   └── utils/
│       └── storage.js              # localStorage 读写工具
├── public/
│   └── data/                       # JSON 数据文件（CI 生成）
├── index.html                      # HTML 入口
├── vite.config.js                  # Vite 配置
├── package.json                    # Node 依赖
└── .gitignore
```

---

### Task 1: 项目脚手架

**Files:**
- Create: `package.json`
- Create: `vite.config.js`
- Create: `index.html`
- Create: `.gitignore` (already exists, verify)

**Interfaces:**
- Produces: `npm run dev` 启动开发服务器，`npm run build` 构建到 `dist/`

**说明:** 使用 Vue 3 + Vite + `<script setup>` + Composition API。不使用 vue-router、Pinia、TypeScript。

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "qiuzhi-inspiration-board",
  "private": true,
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.0",
    "vite": "^6.0.0"
  }
}
```

- [ ] **Step 2: 安装依赖**

Run: `npm install`
Expected: 无报错，`node_modules/` 生成

- [ ] **Step 3: 创建 vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: './',
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  },
  server: {
    port: 3000
  }
})
```

- [ ] **Step 4: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>秋芝选题站</title>
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📋</text></svg>" />
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 5: 创建 src/main.js**

```javascript
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
```

- [ ] **Step 6: 创建最简 App.vue 验证脚手架**

```vue
<template>
  <div>秋芝选题站 - 脚手架就绪</div>
</template>
```

- [ ] **Step 7: 验证开发服务器**

Run: `npm run dev`
Expected: `http://localhost:3000` 显示 "秋芝选题站 - 脚手架就绪"

- [ ] **Step 8: 验证构建**

Run: `npm run build`
Expected: `dist/` 目录生成，含 `index.html` 和 `assets/`

- [ ] **Step 9: Commit**

```bash
git add package.json package-lock.json vite.config.js index.html src/main.js src/App.vue
git commit -m "feat: scaffold Vue 3 + Vite project"
```

---

### Task 2: localStorage 工具 + composables

**Files:**
- Create: `src/utils/storage.js`
- Create: `src/composables/useBookmarks.js`
- Create: `src/composables/useNotes.js`

**Interfaces:**
- Produces:
  - `storage.js`: `loadFromStorage(key, fallback)` → value, `saveToStorage(key, value)` → void
  - `useBookmarks.js`: `useBookmarks()` → `{ bookmarks: ref(Set), isBookmarked(id): boolean, toggleBookmark(id): void, getBookmarkList(): computed }`
  - `useNotes.js`: `useNotes()` → `{ notes: ref({}), getNote(id): string, saveNote(id, text): void, getNotesList(): computed }`

- [ ] **Step 1: 创建 src/utils/storage.js**

```javascript
export function loadFromStorage(key, fallback) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

export function saveToStorage(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (e) {
    console.error(`Failed to save to localStorage key="${key}":`, e)
  }
}
```

- [ ] **Step 2: 创建 storage.test.js 并运行**

Create `src/utils/__tests__/storage.test.js`:

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { loadFromStorage, saveToStorage } from '../storage.js'

describe('loadFromStorage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns fallback when key does not exist', () => {
    expect(loadFromStorage('nonexistent', [])).toEqual([])
  })

  it('returns parsed value when key exists', () => {
    localStorage.setItem('test', JSON.stringify({ a: 1 }))
    expect(loadFromStorage('test', {})).toEqual({ a: 1 })
  })

  it('returns fallback on corrupted JSON', () => {
    localStorage.setItem('bad', '{corrupted')
    expect(loadFromStorage('bad', 'fallback')).toBe('fallback')
  })
})

describe('saveToStorage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('saves value as JSON string', () => {
    saveToStorage('test', { b: 2 })
    expect(localStorage.getItem('test')).toBe('{"b":2}')
  })
})
```

- [ ] **Step 3: 安装 Vitest 并运行测试**

Run: `npm install -D vitest`
Then add to `package.json` scripts: `"test": "vitest run"`

Run: `npm test`
Expected: 4 tests pass

- [ ] **Step 4: 创建 src/composables/useBookmarks.js**

```javascript
import { ref, computed } from 'vue'
import { loadFromStorage, saveToStorage } from '../utils/storage.js'

const STORAGE_KEY = 'qiuzhi_bookmarks'
const bookmarks = ref(new Set(loadFromStorage(STORAGE_KEY, [])))

export function useBookmarks() {
  function persist() {
    saveToStorage(STORAGE_KEY, [...bookmarks.value])
  }

  function isBookmarked(productId) {
    return bookmarks.value.has(productId)
  }

  function toggleBookmark(productId) {
    const s = new Set(bookmarks.value)
    if (s.has(productId)) {
      s.delete(productId)
    } else {
      s.add(productId)
    }
    bookmarks.value = s
    persist()
  }

  const bookmarkList = computed(() => [...bookmarks.value])

  return { bookmarks, isBookmarked, toggleBookmark, bookmarkList }
}
```

- [ ] **Step 5: 创建 src/composables/useNotes.js**

```javascript
import { ref, computed } from 'vue'
import { loadFromStorage, saveToStorage } from '../utils/storage.js'

const STORAGE_KEY = 'qiuzhi_notes'
const notes = ref(loadFromStorage(STORAGE_KEY, {}))

export function useNotes() {
  function persist() {
    saveToStorage(STORAGE_KEY, { ...notes.value })
  }

  function getNote(productId) {
    return notes.value[productId] || ''
  }

  function saveNote(productId, text) {
    notes.value = { ...notes.value, [productId]: text }
    persist()
  }

  const notesList = computed(() => {
    return Object.entries(notes.value)
      .filter(([, text]) => text.trim().length > 0)
      .map(([id, text]) => ({ id, text, summary: text.slice(0, 50) }))
  })

  return { notes, getNote, saveNote, notesList }
}
```

- [ ] **Step 6: 为 composables 写测试并运行**

Create `src/composables/__tests__/useBookmarks.test.js`:

```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { useBookmarks } from '../useBookmarks.js'

describe('useBookmarks', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('starts with empty bookmarks', () => {
    const { bookmarkList } = useBookmarks()
    expect(bookmarkList.value).toEqual([])
  })

  it('toggleBookmark adds and removes', () => {
    const { isBookmarked, toggleBookmark, bookmarkList } = useBookmarks()
    expect(isBookmarked('prod-1')).toBe(false)
    toggleBookmark('prod-1')
    expect(isBookmarked('prod-1')).toBe(true)
    expect(bookmarkList.value).toContain('prod-1')
    toggleBookmark('prod-1')
    expect(isBookmarked('prod-1')).toBe(false)
  })
})
```

Create `src/composables/__tests__/useNotes.test.js`:

```javascript
import { describe, it, expect, beforeEach } from 'vitest'
import { useNotes } from '../useNotes.js'

describe('useNotes', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('starts with empty notes', () => {
    const { getNote } = useNotes()
    expect(getNote('prod-1')).toBe('')
  })

  it('saveNote persists and retrieves', () => {
    const { saveNote, getNote, notesList } = useNotes()
    saveNote('prod-1', '这是一个好选题')
    expect(getNote('prod-1')).toBe('这是一个好选题')
    expect(notesList.value.length).toBe(1)
    expect(notesList.value[0].summary).toBe('这是一个好选题')
  })
})
```

Run: `npm test`
Expected: 8 tests pass (4 from storage + 2 from bookmarks + 2 from notes)

- [ ] **Step 7: Commit**

```bash
git add src/utils/ src/composables/ package.json package-lock.json
git commit -m "feat: add storage utils and bookmark/notes composables"
```

---

### Task 3: Python 数据管线脚本

**Files:**
- Create: `scripts/requirements.txt`
- Create: `scripts/fetch_and_score.py`

**Interfaces:**
- Produces: 运行后生成 `public/data/YYYY-MM-DD.json`
- 命令行调用: `python scripts/fetch_and_score.py`

**前置:** 需要设置环境变量 `PRODUCTHUNT_DEVELOPER_TOKEN` 和 `DEEPSEEK_API_KEY`

- [ ] **Step 1: 创建 scripts/requirements.txt**

```
requests>=2.28.0
openai>=1.0.0
python-dotenv>=0.20.0
pytz>=2022.1
```

- [ ] **Step 2: 创建 scripts/fetch_and_score.py**

```python
#!/usr/bin/env python3
"""Fetch ProductHunt Top 6, score with DeepSeek V4, output JSON."""

import os
import json
import sys
import traceback
from datetime import datetime, timedelta, timezone

import pytz
import requests
from openai import OpenAI
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"
PH_GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"
BEIJING_TZ = pytz.timezone("Asia/Shanghai")
OUTPUT_DIR = "public/data"

SYSTEM_PROMPT = """\
你是一位资深的AI工具测评博主，擅长判断一个产品是否适合做成视频内容。\
你的读者是"普通互联网用户"，不是技术人员。

请阅读以下 ProductHunt 产品信息，输出一个严格的 JSON：

{
  "name_zh": "产品名称地道中文翻译",
  "tagline_zh": "一句话标语的中文翻译（科普杂志风格）",
  "description_zh": "产品简介的中文翻译（通俗口语化，2-3句说清楚它是什么、给谁用）",
  "scores": {
    "video_suitability": {
      "score": <1-5整数>,
      "reason": "为什么适合/不适合拍视频（画面观感、演示效果、视觉冲击力）"
    },
    "beginner_friendly": {
      "score": <1-5整数>,
      "reason": "普通人能否看懂（概念复杂度、是否需要技术背景、使用门槛）"
    },
    "popularity": {
      "score": <1-5整数>,
      "reason": "热度判断（ProductHunt排名、票数、话题性）"
    }
  },
  "video_inspiration": {
    "title_idea": "视频标题灵感（B站/抖音风格，抓眼球）",
    "angle": "拍摄切入角度（开箱体验/对比测评/教程演示/行业解读/娱乐吐槽）",
    "shooting_tips": "拍摄具体建议（录哪些画面、突出什么卖点、用什么节奏）",
    "target_audience": "目标观众画像"
  },
  "overall_suggestion": "<强力推荐 | 可以做 | 谨慎考虑>",
  "overall_reason": "一句话总结理由"
}

评分标准：
- 🎬 视频化程度：有丰富UI/画面操作/前后对比 → 高分；纯文字/概念/后台API → 低分
- 🌱 小白友好度：普通人秒懂能上手 → 高分；需要编程/技术背景 → 低分
- 🔥 热度：PH前3名 → 5分；前10 → 4分；10名后 → 3分
- overall_suggestion：🎬≥4 且 🌱≥4 → 强力推荐；🎬≥2 → 可以做；其余 → 谨慎考虑

只输出 JSON，不要任何其他文字。"""


def get_producthunt_token():
    token = os.getenv("PRODUCTHUNT_DEVELOPER_TOKEN")
    if not token:
        raise RuntimeError("PRODUCTHUNT_DEVELOPER_TOKEN not set")
    return token


def fetch_top_products(token):
    """Fetch yesterday's top 6 products from ProductHunt GraphQL API."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "QiuzhiInspirationBoard/1.0",
    }

    retry_strategy = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)

    query = """
    query($postedAfter: DateTime!, $postedBefore: DateTime!, $first: Int!) {
      posts(
        order: VOTES
        postedAfter: $postedAfter
        postedBefore: $postedBefore
        first: $first
      ) {
        nodes {
          id
          name
          tagline
          description
          votesCount
          createdAt
          website
          url
          media { url type }
        }
      }
    }
    """

    variables = {
        "postedAfter": f"{date_str}T00:00:00Z",
        "postedBefore": f"{date_str}T23:59:59Z",
        "first": 6,
    }

    response = session.post(
        PH_GRAPHQL_URL,
        headers=headers,
        json={"query": query, "variables": variables},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")

    posts = data["data"]["posts"]["nodes"]
    print(f"Fetched {len(posts)} products for {date_str}")
    return date_str, posts


def score_product_with_deepseek(client, product, rank):
    """Score a single product using DeepSeek V4. Returns enriched product dict."""
    user_prompt = f"""\
产品排名：第{rank}名
产品名称：{product['name']}
标语：{product['tagline']}
描述：{product['description']}
票数：{product['votesCount']}"""

    print(f"  Scoring [{rank}] {product['name']}...")

    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()

        # Handle possible markdown code fences
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            if content.startswith("json"):
                content = content[4:].strip()

        scored = json.loads(content)

        # Derive overall_suggestion by rule if missing or override to ensure consistency
        vs = scored["scores"]["video_suitability"]["score"]
        bf = scored["scores"]["beginner_friendly"]["score"]
        if vs >= 4 and bf >= 4:
            scored["overall_suggestion"] = "强力推荐"
        elif vs >= 2:
            scored["overall_suggestion"] = "可以做"
        else:
            scored["overall_suggestion"] = "谨慎考虑"

        return scored
    except Exception as e:
        print(f"  ERROR scoring {product['name']}: {e}")
        traceback.print_exc()
        return {
            "name_zh": product["name"],
            "tagline_zh": product.get("tagline", ""),
            "description_zh": product.get("description", ""),
            "scores": {
                "video_suitability": {"score": 0, "reason": "评分失败"},
                "beginner_friendly": {"score": 0, "reason": "评分失败"},
                "popularity": {"score": 0, "reason": "评分失败"},
            },
            "video_inspiration": {
                "title_idea": "",
                "angle": "",
                "shooting_tips": "",
                "target_audience": "",
            },
            "overall_suggestion": "谨慎考虑",
            "overall_reason": "LLM 评分失败",
            "scoring_error": str(e),
        }


def get_image_url(media):
    """Extract image URL from ProductHunt media field."""
    try:
        if media and isinstance(media, list) and len(media) > 0:
            return media[0].get("url", "")
    except Exception:
        pass
    return ""


def main():
    # Validate environment
    ph_token = get_producthunt_token()
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    client = OpenAI(
        api_key=deepseek_key,
        base_url=DEEPSEEK_BASE_URL,
    )

    # Fetch
    print("Fetching ProductHunt Top 6...")
    date_str, posts = fetch_top_products(ph_token)

    # Score
    generation_error = False
    products = []
    for i, post in enumerate(posts, 1):
        scored = score_product_with_deepseek(client, post, i)
        product_entry = {
            "id": post["id"],
            "name": post["name"],
            "name_zh": scored.get("name_zh", post["name"]),
            "tagline_zh": scored.get("tagline_zh", post.get("tagline", "")),
            "description_zh": scored.get("description_zh", post.get("description", "")),
            "url": post["url"],
            "website": post.get("website", ""),
            "image_url": get_image_url(post.get("media")),
            "votes_count": post["votesCount"],
            "scores": scored.get("scores", {}),
            "video_inspiration": scored.get("video_inspiration", {}),
            "overall_suggestion": scored.get("overall_suggestion", "谨慎考虑"),
            "overall_reason": scored.get("overall_reason", ""),
        }
        if "scoring_error" in scored:
            generation_error = True
        products.append(product_entry)

    # Sort by overall_suggestion priority + votes
    priority = {"强力推荐": 0, "可以做": 1, "谨慎考虑": 2}
    products.sort(key=lambda p: (priority.get(p["overall_suggestion"], 3), -p["votes_count"]))

    # Generate output
    now_beijing = datetime.now(timezone.utc).astimezone(BEIJING_TZ)
    output = {
        "date": date_str,
        "generated_at": now_beijing.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "generation_error": generation_error,
        "products": products,
    }

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{date_str}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved: {output_path}")

    # Also update latest.json for convenience
    latest_path = os.path.join(OUTPUT_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"Saved: {latest_path}")

    # Update dates.json manifest
    dates_path = os.path.join(OUTPUT_DIR, "dates.json")
    existing_dates = []
    if os.path.exists(dates_path):
        try:
            with open(dates_path, "r", encoding="utf-8") as f:
                existing_dates = json.load(f).get("dates", [])
        except Exception:
            pass
    if date_str not in existing_dates:
        existing_dates.append(date_str)
        existing_dates.sort(reverse=True)
        with open(dates_path, "w", encoding="utf-8") as f:
            json.dump({"dates": existing_dates}, f, ensure_ascii=False, indent=2)
        print(f"Updated dates.json: {len(existing_dates)} dates")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: 使用模拟数据验证脚本可运行**

```bash
# 设置 fake 环境变量测试
export PRODUCTHUNT_DEVELOPER_TOKEN="test-token"
export DEEPSEEK_API_KEY="test-key"
# 脚本会因真实 API key 在 LLM 调用时报错，但应能跑到 fetch 阶段
python scripts/fetch_and_score.py
```

Expected: 脚本启动，尝试连接 ProductHunt API（可能因 token 无效报错，但证明代码语法正确，import 无缺失）。

- [ ] **Step 4: Commit**

```bash
git add scripts/
git commit -m "feat: add Python data pipeline script"
```

---

### Task 4: GitHub Actions 工作流

**Files:**
- Create: `.github/workflows/daily.yml`

**Interfaces:**
- Consumes: `scripts/fetch_and_score.py`, `scripts/requirements.txt`
- Produces: 每天 15:01 自动运行，或手动触发

- [ ] **Step 1: 创建 .github/workflows/daily.yml**

```yaml
name: Daily Fetch & Deploy

on:
  schedule:
    - cron: '01 7 * * *'
  workflow_dispatch:

jobs:
  fetch-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r scripts/requirements.txt

      - name: Fetch and Score
        env:
          PRODUCTHUNT_DEVELOPER_TOKEN: ${{ secrets.PRODUCTHUNT_DEVELOPER_TOKEN }}
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
        run: python scripts/fetch_and_score.py

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Node dependencies
        run: npm ci

      - name: Build Vue app
        run: npm run build

      - name: Deploy to CloudBase
        uses: TencentCloudBase/cloudbase-action@v2
        with:
          secretId: ${{ secrets.TCB_SECRET_ID }}
          secretKey: ${{ secrets.TCB_SECRET_KEY }}
          envId: ${{ secrets.TCB_ENV_ID }}
          staticSrcPath: dist

      - name: Commit generated data
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add public/data/
          git diff --staged --quiet || git commit -m "data: daily update $(date +%Y-%m-%d)"
          git push
```

- [ ] **Step 2: 验证 workflow 语法**

Run: `cat .github/workflows/daily.yml` (visual check)
确认缩进、引用正确。

- [ ] **Step 3: Commit**

```bash
git add .github/
git commit -m "ci: add daily fetch and deploy workflow"
```

---

### Task 5: useData composable（加载 JSON 数据）

**Files:**
- Create: `src/composables/useData.js`
- Create: `src/composables/__tests__/useData.test.js` (可选，因涉及 fetch)

**Interfaces:**
- Produces: `useData()` → `{ products: ref([]), date: ref(''), loading: ref(false), error: ref(''), generationError: ref(false), loadDate(dateStr): Promise, listAvailableDates(): Promise<string[]> }`

- [ ] **Step 1: 创建 src/composables/useData.js**

```javascript
import { ref } from 'vue'

const BASE = '/data/'

export function useData() {
  const products = ref([])
  const date = ref('')
  const loading = ref(false)
  const error = ref('')
  const generationError = ref(false)

  async function loadDate(dateStr) {
    loading.value = true
    error.value = ''
    generationError.value = false

    try {
      const url = `${BASE}${dateStr}.json`
      const resp = await fetch(url)
      if (!resp.ok) {
        if (resp.status === 404) {
          error.value = '该日期暂无数据'
        } else {
          error.value = `加载失败 (${resp.status})`
        }
        products.value = []
        date.value = dateStr
        return
      }
      const data = await resp.json()
      products.value = data.products || []
      date.value = dateStr
      generationError.value = data.generation_error || false
    } catch (e) {
      error.value = '网络加载失败，请检查网络后重试'
      products.value = []
      date.value = dateStr
    } finally {
      loading.value = false
    }
  }

  async function listAvailableDates() {
    // CloudBase static hosting doesn't support directory listing.
    // We ship a dates.json manifest updated by CI. Fallback: empty.
    try {
      const resp = await fetch(`${BASE}dates.json`)
      if (resp.ok) {
        const data = await resp.json()
        return data.dates || []
      }
    } catch {}
    return []
  }

  return { products, date, loading, error, generationError, loadDate, listAvailableDates }
}
```

- [ ] **Step 2: Commit**

```bash
git add src/composables/useData.js
git commit -m "feat: add useData composable for JSON loading"
```

---

### Task 6: 小组件（NavBar, ScoreBar, SuggestionTag, BookmarkButton）

**Files:**
- Create: `src/components/NavBar.vue`
- Create: `src/components/ScoreBar.vue`
- Create: `src/components/SuggestionTag.vue`
- Create: `src/components/BookmarkButton.vue`

**Interfaces:**
- `NavBar`: props `{ currentView: 'home' | 'workspace' }`, emits `['update:currentView']`
- `ScoreBar`: props `{ label: String, score: Number }` (score 0-5)
- `SuggestionTag`: props `{ suggestion: String }` ("强力推荐" | "可以做" | "谨慎考虑")
- `BookmarkButton`: props `{ productId: String, bookmarked: Boolean }`, emits `['toggle']`

- [ ] **Step 1: 创建 src/components/NavBar.vue**

```vue
<template>
  <nav class="navbar">
    <h1 class="navbar-title">秋芝选题站</h1>
    <div class="navbar-tabs">
      <button
        :class="{ active: currentView === 'home' }"
        @click="$emit('update:currentView', 'home')"
      >📊 榜单</button>
      <button
        :class="{ active: currentView === 'workspace' }"
        @click="$emit('update:currentView', 'workspace')"
      >💼 工作台</button>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  currentView: { type: String, required: true }
})
defineEmits(['update:currentView'])
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #e5e5e5;
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}
.navbar-tabs {
  display: flex;
  gap: 8px;
}
.navbar-tabs button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #f9f9f9;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  transition: all 0.2s;
}
.navbar-tabs button.active {
  background: #1a1a2e;
  color: #fff;
  border-color: #1a1a2e;
}
</style>
```

- [ ] **Step 2: 创建 src/components/ScoreBar.vue**

```vue
<template>
  <div class="score-bar">
    <span class="score-label">{{ label }}</span>
    <span class="score-stars">
      <span v-for="i in 5" :key="i" :class="{ filled: i <= score, empty: i > score }">
        {{ i <= score ? '★' : '☆' }}
      </span>
    </span>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  score: { type: Number, required: true }
})
</script>

<style scoped>
.score-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.score-label {
  color: #888;
  min-width: 80px;
}
.score-stars {
  color: #f5a623;
  letter-spacing: 2px;
}
.empty {
  color: #ddd;
}
</style>
```

- [ ] **Step 3: 创建 src/components/SuggestionTag.vue**

```vue
<template>
  <span :class="['suggestion-tag', tagClass]">{{ suggestion }}</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  suggestion: { type: String, required: true }
})

const tagClass = computed(() => {
  if (props.suggestion === '强力推荐') return 'tag-recommend'
  if (props.suggestion === '可以做') return 'tag-ok'
  return 'tag-caution'
})
</script>

<style scoped>
.suggestion-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}
.tag-recommend {
  background: #e8f5e9;
  color: #2e7d32;
}
.tag-ok {
  background: #fff3e0;
  color: #e65100;
}
.tag-caution {
  background: #fce4ec;
  color: #c62828;
}
</style>
```

- [ ] **Step 4: 创建 src/components/BookmarkButton.vue**

```vue
<template>
  <button
    :class="['bookmark-btn', { bookmarked }]"
    :title="bookmarked ? '取消收藏' : '收藏'"
    @click.stop="$emit('toggle')"
  >
    {{ bookmarked ? '⭐' : '☆' }}
  </button>
</template>

<script setup>
defineProps({
  bookmarked: { type: Boolean, default: false }
})
defineEmits(['toggle'])
</script>

<style scoped>
.bookmark-btn {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  transition: transform 0.2s;
  padding: 4px;
}
.bookmark-btn:hover {
  transform: scale(1.2);
}
.bookmark-btn.bookmarked {
  color: #f5a623;
}
</style>
```

- [ ] **Step 5: 验证：在 App.vue 中临时引入组件确认渲染**

Edit `src/App.vue` temporarily:

```vue
<template>
  <div>
    <NavBar currentView="home" />
    <div style="padding:20px;display:flex;gap:16px;flex-wrap:wrap;">
      <ScoreBar label="🎬 视频化" :score="4" />
      <ScoreBar label="🌱 小白友好" :score="5" />
      <ScoreBar label="🔥 热度" :score="3" />
      <SuggestionTag suggestion="强力推荐" />
      <SuggestionTag suggestion="可以做" />
      <SuggestionTag suggestion="谨慎考虑" />
      <BookmarkButton :bookmarked="false" />
      <BookmarkButton :bookmarked="true" />
    </div>
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
import ScoreBar from './components/ScoreBar.vue'
import SuggestionTag from './components/SuggestionTag.vue'
import BookmarkButton from './components/BookmarkButton.vue'
</script>
```

Run: `npm run dev`
Expected: 页面显示导航栏、星级、彩色标签、星标按钮。

- [ ] **Step 6: Commit**

```bash
git add src/components/NavBar.vue src/components/ScoreBar.vue src/components/SuggestionTag.vue src/components/BookmarkButton.vue src/App.vue
git commit -m "feat: add NavBar, ScoreBar, SuggestionTag, BookmarkButton components"
```

---

### Task 7: DatePicker 组件

**Files:**
- Create: `src/components/DatePicker.vue`

**Interfaces:**
- props: `{ modelValue: String, availableDates: String[] }`
- emits: `['update:modelValue']`

- [ ] **Step 1: 创建 src/components/DatePicker.vue**

```vue
<template>
  <div class="date-picker">
    <button class="dp-arrow" :disabled="!hasPrev" @click="goPrev">‹</button>
    <input
      type="date"
      :value="modelValue"
      :max="todayStr"
      @change="onDateChange"
      class="dp-input"
    />
    <button class="dp-arrow" :disabled="!hasNext" @click="goNext">›</button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, required: true },
  availableDates: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const todayStr = computed(() => {
  const d = new Date()
  return d.toISOString().slice(0, 10)
})

function formatDate(str) {
  const d = new Date(str + 'T00:00:00')
  if (isNaN(d.getTime())) return str
  return d.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' })
}

function onDateChange(e) {
  emit('update:modelValue', e.target.value)
}

function shift(days) {
  const d = new Date(props.modelValue + 'T00:00:00')
  if (isNaN(d.getTime())) return
  d.setDate(d.getDate() + days)
  emit('update:modelValue', d.toISOString().slice(0, 10))
}

const hasPrev = computed(() => true)
const hasNext = computed(() => props.modelValue < todayStr.value)

function goPrev() { shift(-1) }
function goNext() { shift(1) }
</script>

<style scoped>
.date-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dp-arrow {
  width: 32px;
  height: 32px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  font-size: 18px;
  cursor: pointer;
  color: #555;
}
.dp-arrow:disabled {
  opacity: 0.3;
  cursor: default;
}
.dp-input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
}
</style>
```

- [ ] **Step 2: 验证组件渲染**

Temporarily edit `src/App.vue` to include DatePicker:

```vue
<template>
  <div style="padding:20px;">
    <DatePicker modelValue="2026-07-19" />
  </div>
</template>

<script setup>
import DatePicker from './components/DatePicker.vue'
</script>
```

Run: `npm run dev`
Expected: 日期选择器显示，左右箭头可点击，日期输入框可编辑。

- [ ] **Step 3: Commit**

```bash
git add src/components/DatePicker.vue src/App.vue
git commit -m "feat: add DatePicker component"
```

---

### Task 8: ProductCard 组件

**Files:**
- Create: `src/components/ProductCard.vue`

**Interfaces:**
- props: `{ product: Object, rank: Number, bookmarked: Boolean }`
- emits: `['click', 'toggle-bookmark']`
- product 对象结构见 spec 3.4 节

- [ ] **Step 1: 创建 src/components/ProductCard.vue**

```vue
<template>
  <article class="product-card" @click="$emit('click')">
    <div class="card-rank">{{ rank }}</div>
    <div class="card-image">
      <img v-if="product.image_url" :src="product.image_url" :alt="product.name" loading="lazy" />
      <div v-else class="card-image-placeholder">📦</div>
    </div>
    <div class="card-body">
      <div class="card-header">
        <h3 class="card-name">{{ product.name_zh || product.name }}</h3>
        <span class="card-name-en">{{ product.name }}</span>
      </div>
      <p class="card-tagline">{{ product.tagline_zh }}</p>
      <div class="card-scores">
        <ScoreBar label="🎬 视频化" :score="product.scores?.video_suitability?.score || 0" />
        <ScoreBar label="🌱 小白友好" :score="product.scores?.beginner_friendly?.score || 0" />
        <ScoreBar label="🔥 热度" :score="product.scores?.popularity?.score || 0" />
      </div>
      <div class="card-footer">
        <SuggestionTag :suggestion="product.overall_suggestion || '谨慎考虑'" />
        <span class="card-votes">👍 {{ product.votes_count }}</span>
        <BookmarkButton
          :productId="product.id"
          :bookmarked="bookmarked"
          @toggle="$emit('toggle-bookmark')"
        />
      </div>
    </div>
  </article>
</template>

<script setup>
import ScoreBar from './ScoreBar.vue'
import SuggestionTag from './SuggestionTag.vue'
import BookmarkButton from './BookmarkButton.vue'

defineProps({
  product: { type: Object, required: true },
  rank: { type: Number, required: true },
  bookmarked: { type: Boolean, default: false }
})

defineEmits(['click', 'toggle-bookmark'])
</script>

<style scoped>
.product-card {
  display: flex;
  gap: 16px;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
}
.product-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  transform: translateY(-2px);
}
.card-rank {
  font-size: 28px;
  font-weight: 800;
  color: #1a1a2e;
  min-width: 40px;
  text-align: center;
  align-self: center;
}
.card-image {
  width: 160px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f5f5f5;
}
.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.card-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}
.card-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-name {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}
.card-name-en {
  font-size: 12px;
  color: #999;
}
.card-tagline {
  margin: 0;
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}
.card-scores {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.card-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: auto;
}
.card-votes {
  font-size: 13px;
  color: #999;
}
@media (max-width: 640px) {
  .product-card {
    flex-direction: column;
  }
  .card-image {
    width: 100%;
    height: 180px;
  }
  .card-rank {
    position: absolute;
    background: rgba(0,0,0,0.6);
    color: #fff;
    width: 32px;
    height: 32px;
    border-radius: 8px 0 8px 0;
    font-size: 16px;
    line-height: 32px;
  }
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ProductCard.vue
git commit -m "feat: add ProductCard component"
```

---

### Task 9: ProductDetail 弹窗（含 ScoreDetail, VideoInspiration, NotesEditor）

**Files:**
- Create: `src/components/ScoreDetail.vue`
- Create: `src/components/VideoInspiration.vue`
- Create: `src/components/NotesEditor.vue`
- Create: `src/components/ProductDetail.vue`

**Interfaces:**
- `ProductDetail`: props `{ product: Object|null, bookmarked: Boolean }`, emits `['close', 'prev', 'next', 'toggle-bookmark']`
- `ScoreDetail`: props `{ scores: Object }`
- `VideoInspiration`: props `{ inspiration: Object }`
- `NotesEditor`: props `{ productId: String }`

- [ ] **Step 1: 创建 src/components/ScoreDetail.vue**

```vue
<template>
  <div class="score-detail">
    <h4>📊 详细评估</h4>
    <div v-for="dim in dimensions" :key="dim.key" class="score-detail-item">
      <div class="sd-header">
        <span class="sd-label">{{ dim.label }}</span>
        <span class="sd-score">{{ '★'.repeat(scores[dim.key]?.score || 0) }}{{ '☆'.repeat(5 - (scores[dim.key]?.score || 0)) }}</span>
      </div>
      <p class="sd-reason">{{ scores[dim.key]?.reason || '暂无分析' }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  scores: { type: Object, default: () => ({}) }
})

const dimensions = [
  { key: 'video_suitability', label: '🎬 视频化程度' },
  { key: 'beginner_friendly', label: '🌱 小白友好度' },
  { key: 'popularity', label: '🔥 热度' }
]
</script>

<style scoped>
.score-detail { margin-bottom: 20px; }
.score-detail h4 { margin: 0 0 12px 0; font-size: 15px; }
.score-detail-item {
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
  margin-bottom: 8px;
}
.sd-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.sd-label { font-weight: 600; font-size: 14px; }
.sd-score { color: #f5a623; font-size: 14px; }
.sd-reason { margin: 0; font-size: 13px; color: #666; line-height: 1.6; }
</style>
```

- [ ] **Step 2: 创建 src/components/VideoInspiration.vue**

```vue
<template>
  <div class="video-inspiration">
    <h4>🎥 视频创作灵感</h4>
    <div class="vi-card">
      <div class="vi-field">
        <span class="vi-label">标题灵感</span>
        <span class="vi-value vi-title">{{ inspiration?.title_idea || '—' }}</span>
      </div>
      <div class="vi-field">
        <span class="vi-label">切入角度</span>
        <span class="vi-value">{{ inspiration?.angle || '—' }}</span>
      </div>
      <div class="vi-field">
        <span class="vi-label">拍摄建议</span>
        <span class="vi-value">{{ inspiration?.shooting_tips || '—' }}</span>
      </div>
      <div class="vi-field">
        <span class="vi-label">目标观众</span>
        <span class="vi-value">{{ inspiration?.target_audience || '—' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  inspiration: { type: Object, default: () => ({}) }
})
</script>

<style scoped>
.video-inspiration { margin-bottom: 20px; }
.video-inspiration h4 { margin: 0 0 12px 0; font-size: 15px; }
.vi-card {
  background: linear-gradient(135deg, #f0f4ff, #faf5ff);
  border: 1px solid #e0d8f0;
  border-radius: 10px;
  padding: 16px;
}
.vi-field { margin-bottom: 10px; }
.vi-field:last-child { margin-bottom: 0; }
.vi-label {
  display: block;
  font-size: 11px;
  color: #999;
  text-transform: uppercase;
  margin-bottom: 2px;
}
.vi-value { font-size: 14px; color: #333; line-height: 1.5; }
.vi-title { font-size: 16px; font-weight: 700; color: #1a1a2e; }
</style>
```

- [ ] **Step 3: 创建 src/components/NotesEditor.vue**

```vue
<template>
  <div class="notes-editor">
    <h4>📝 我的笔记</h4>
    <textarea
      :value="noteText"
      @input="onInput"
      placeholder="记录你的想法、拍摄思路、注意事项..."
      class="notes-textarea"
      rows="5"
    ></textarea>
    <span class="notes-saved">{{ saved ? '✅ 已自动保存' : '💾 正在保存...' }}</span>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useNotes } from '../composables/useNotes.js'

const props = defineProps({
  productId: { type: String, required: true }
})

const { getNote, saveNote } = useNotes()
const noteText = ref('')
const saved = ref(true)
let saveTimer = null

onMounted(() => {
  noteText.value = getNote(props.productId)
})

function onInput(e) {
  noteText.value = e.target.value
  saved.value = false
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    saveNote(props.productId, noteText.value)
    saved.value = true
  }, 500)
}
</script>

<style scoped>
.notes-editor h4 { margin: 0 0 8px 0; font-size: 15px; }
.notes-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}
.notes-textarea:focus { outline: none; border-color: #1a1a2e; }
.notes-saved { font-size: 11px; color: #aaa; }
</style>
```

- [ ] **Step 4: 创建 src/components/ProductDetail.vue**

```vue
<template>
  <Teleport to="body">
    <div v-if="product" class="detail-overlay" @click.self="$emit('close')">
      <div class="detail-panel">
        <button class="detail-close" @click="$emit('close')">✕</button>

        <div class="detail-image">
          <img v-if="product.image_url" :src="product.image_url" :alt="product.name" />
        </div>

        <div class="detail-content">
          <h2>{{ product.name_zh || product.name }}</h2>
          <p class="detail-name-en">{{ product.name }}</p>
          <p class="detail-desc">{{ product.description_zh }}</p>

          <div class="detail-meta">
            <span>👍 {{ product.votes_count }} 票</span>
            <a :href="product.url" target="_blank" rel="noopener">🔗 ProductHunt</a>
            <a v-if="product.website" :href="product.website" target="_blank" rel="noopener">🌐 官网</a>
            <SuggestionTag :suggestion="product.overall_suggestion || '谨慎考虑'" />
            <BookmarkButton
              :productId="product.id"
              :bookmarked="bookmarked"
              @toggle="$emit('toggle-bookmark')"
            />
          </div>

          <p class="detail-overall"><strong>综合建议：</strong>{{ product.overall_reason }}</p>

          <ScoreDetail :scores="product.scores" />
          <VideoInspiration :inspiration="product.video_inspiration" />
          <NotesEditor :productId="product.id" />
        </div>

        <div class="detail-nav">
          <button @click="$emit('prev')">‹ 上一个</button>
          <button @click="$emit('next')">下一个 ›</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import ScoreDetail from './ScoreDetail.vue'
import VideoInspiration from './VideoInspiration.vue'
import NotesEditor from './NotesEditor.vue'
import SuggestionTag from './SuggestionTag.vue'
import BookmarkButton from './BookmarkButton.vue'

defineProps({
  product: { type: Object, default: null },
  bookmarked: { type: Boolean, default: false }
})

defineEmits(['close', 'prev', 'next', 'toggle-bookmark'])
</script>

<style scoped>
.detail-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 200;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 40px 16px;
  overflow-y: auto;
}
.detail-panel {
  background: #fff;
  border-radius: 16px;
  max-width: 760px;
  width: 100%;
  position: relative;
  overflow: hidden;
}
.detail-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(0,0,0,0.5);
  color: #fff;
  border-radius: 50%;
  font-size: 16px;
  cursor: pointer;
  z-index: 10;
}
.detail-image img {
  width: 100%;
  max-height: 360px;
  object-fit: cover;
}
.detail-content { padding: 24px; }
.detail-content h2 { margin: 0; font-size: 22px; }
.detail-name-en { color: #999; font-size: 13px; margin: 4px 0 12px; }
.detail-desc { font-size: 14px; line-height: 1.7; color: #444; }
.detail-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin: 16px 0;
  font-size: 13px;
}
.detail-meta a { color: #1a73e8; text-decoration: none; }
.detail-overall {
  background: #fffde7;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
}
.detail-nav {
  display: flex;
  justify-content: space-between;
  padding: 0 24px 24px;
}
.detail-nav button {
  padding: 8px 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  font-size: 14px;
}
.detail-nav button:hover { background: #f5f5f5; }
</style>
```

- [ ] **Step 5: Commit**

```bash
git add src/components/ScoreDetail.vue src/components/VideoInspiration.vue src/components/NotesEditor.vue src/components/ProductDetail.vue
git commit -m "feat: add ProductDetail with ScoreDetail, VideoInspiration, NotesEditor"
```

---

### Task 10: HomePage（组装首页）

**Files:**
- Create: `src/components/HomePage.vue`

**Interfaces:**
- props: 无
- 使用 useData, useBookmarks composables
- URL search params: `?date=` 和 `?id=`

- [ ] **Step 1: 创建 src/components/HomePage.vue**

```vue
<template>
  <div class="home-page">
    <div class="home-header">
      <DatePicker v-model="selectedDate" />
      <span class="home-count" v-if="products.length">{{ products.length }} 个产品</span>
      <span class="home-updated" v-if="date">更新于 {{ date }}</span>
    </div>

    <div v-if="loading" class="home-status">⏳ 加载中...</div>
    <div v-else-if="error" class="home-status home-error">{{ error }}</div>
    <div v-else-if="!products.length" class="home-status">该日期暂无数据</div>

    <div v-else class="product-list">
      <ProductCard
        v-for="(p, i) in products"
        :key="p.id"
        :product="p"
        :rank="i + 1"
        :bookmarked="isBookmarked(p.id)"
        @click="openDetail(p)"
        @toggle-bookmark="toggleBookmark(p.id)"
      />
    </div>

    <ProductDetail
      :product="selectedProduct"
      :bookmarked="selectedProduct ? isBookmarked(selectedProduct.id) : false"
      @close="closeDetail"
      @prev="navDetail(-1)"
      @next="navDetail(1)"
      @toggle-bookmark="selectedProduct && toggleBookmark(selectedProduct.id)"
    />

    <div class="home-footer" v-if="date">
      数据更新时间：{{ date }}
      <span v-if="generationError" class="home-error-tip">⚠️ 本次生成过程存在部分错误</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useData } from '../composables/useData.js'
import { useBookmarks } from '../composables/useBookmarks.js'
import DatePicker from './DatePicker.vue'
import ProductCard from './ProductCard.vue'
import ProductDetail from './ProductDetail.vue'

const { products, date, loading, error, generationError, loadDate } = useData()
const { isBookmarked, toggleBookmark } = useBookmarks()

const selectedDate = ref(getInitialDate())
const selectedProduct = ref(null)

function getInitialDate() {
  const params = new URLSearchParams(window.location.search)
  if (params.get('date')) return params.get('date')
  const d = new Date()
  d.setDate(d.getDate() - 1) // default: yesterday
  return d.toISOString().slice(0, 10)
}

function updateURL() {
  const params = new URLSearchParams()
  if (selectedDate.value) params.set('date', selectedDate.value)
  const qs = params.toString()
  const newURL = qs ? `?${qs}` : window.location.pathname
  history.replaceState(null, '', newURL)
}

function openDetail(product) {
  selectedProduct.value = product
  const params = new URLSearchParams(window.location.search)
  params.set('id', product.id)
  history.replaceState(null, '', `?${params.toString()}`)
}

function closeDetail() {
  selectedProduct.value = null
  updateURL()
}

function navDetail(dir) {
  if (!selectedProduct.value) return
  const idx = products.value.findIndex(p => p.id === selectedProduct.value.id)
  const next = idx + dir
  if (next >= 0 && next < products.value.length) {
    openDetail(products.value[next])
  }
}

watch(selectedDate, (val) => {
  if (val) {
    loadDate(val)
    updateURL()
    closeDetail()
  }
}, { immediate: true })

// Check URL for initial detail open
onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const openId = params.get('id')
  if (openId && products.value.length) {
    const p = products.value.find(p => p.id === openId)
    if (p) selectedProduct.value = p
  }
})
</script>

<style scoped>
.home-page { max-width: 960px; margin: 0 auto; padding: 20px 16px; }
.home-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.home-count { font-size: 14px; color: #888; }
.home-updated { font-size: 12px; color: #bbb; margin-left: auto; }
.home-status { text-align: center; padding: 60px 0; color: #999; font-size: 15px; }
.home-error { color: #c62828; }
.product-list { display: flex; flex-direction: column; gap: 16px; }
.home-footer {
  text-align: center;
  padding: 32px 0 16px;
  font-size: 12px;
  color: #ccc;
}
.home-error-tip { color: #e65100; margin-left: 8px; }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/HomePage.vue
git commit -m "feat: add HomePage with data loading, date switching, and detail modal"
```

---

### Task 11: Workspace（工作台）

**Files:**
- Create: `src/components/BookmarkList.vue`
- Create: `src/components/NotesList.vue`
- Create: `src/components/DataExport.vue`
- Create: `src/components/Workspace.vue`

- [ ] **Step 1: 创建 src/components/BookmarkList.vue**

```vue
<template>
  <div class="bookmark-list">
    <h3>⭐ 我的收藏</h3>
    <p v-if="!items.length" class="empty-hint">还没有收藏任何产品</p>
    <div v-else v-for="item in items" :key="item.id" class="bm-item">
      <span class="bm-name">{{ item.name }}</span>
      <span class="bm-date">{{ item.date }}</span>
      <button @click="toggleBookmark(item.id)" class="bm-remove">取消收藏</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useBookmarks } from '../composables/useBookmarks.js'

const { bookmarkList, toggleBookmark } = useBookmarks()

const props = defineProps({
  productMap: { type: Object, default: () => ({}) }
})

const items = computed(() => {
  return bookmarkList.value.map(id => ({
    id,
    name: props.productMap[id]?.name_zh || props.productMap[id]?.name || id,
    date: props.productMap[id]?.date || ''
  }))
})
</script>

<style scoped>
.bookmark-list { margin-bottom: 32px; }
.empty-hint { color: #999; font-size: 14px; padding: 24px 0; text-align: center; }
.bm-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-bottom: 1px solid #f0f0f0; }
.bm-name { flex: 1; font-size: 14px; font-weight: 500; }
.bm-date { font-size: 12px; color: #999; }
.bm-remove { background: none; border: 1px solid #fce4ec; color: #c62828; border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 12px; }
</style>
```

- [ ] **Step 2: 创建 src/components/NotesList.vue**

```vue
<template>
  <div class="notes-list">
    <h3>📝 我的笔记</h3>
    <p v-if="!items.length" class="empty-hint">还没有写过笔记</p>
    <div v-for="item in items" :key="item.id" class="note-item" @click="expandedId = expandedId === item.id ? null : item.id">
      <span class="note-name">{{ getProductName(item.id) }}</span>
      <span class="note-summary">{{ expandedId === item.id ? item.text : item.summary }}</span>
      <span class="note-date">{{ item.date || '' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useNotes } from '../composables/useNotes.js'

const { notesList } = useNotes()
const expandedId = ref(null)

const props = defineProps({
  productMap: { type: Object, default: () => ({}) }
})

function getProductName(id) {
  return props.productMap[id]?.name_zh || props.productMap[id]?.name || id
}

const items = computed(() => {
  return notesList.value.map(n => ({
    ...n,
    date: props.productMap[n.id]?.date || ''
  }))
})
</script>

<script>
import { computed } from 'vue'
</script>

<style scoped>
.notes-list { margin-bottom: 32px; }
.empty-hint { color: #999; font-size: 14px; padding: 24px 0; text-align: center; }
.note-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.note-name { font-weight: 600; font-size: 14px; min-width: 120px; }
.note-summary { flex: 1; font-size: 13px; color: #666; }
.note-date { font-size: 11px; color: #bbb; }
</style>
```

Wait, this component has a bug — `computed` is imported in two `<script>` blocks. Let me fix this to use a single `<script setup>` block.

Actually let me rewrite NotesList.vue properly:

```vue
<template>
  <div class="notes-list">
    <h3>📝 我的笔记</h3>
    <p v-if="!items.length" class="empty-hint">还没有写过笔记</p>
    <div v-for="item in items" :key="item.id" class="note-item" @click="toggleExpand(item.id)">
      <span class="note-name">{{ getProductName(item.id) }}</span>
      <span class="note-summary">{{ expandedId === item.id ? item.text : item.summary }}</span>
      <span class="note-date">{{ item.date || '' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useNotes } from '../composables/useNotes.js'

const { notesList } = useNotes()
const expandedId = ref(null)

const props = defineProps({
  productMap: { type: Object, default: () => ({}) }
})

function getProductName(id) {
  return props.productMap[id]?.name_zh || props.productMap[id]?.name || id
}

function toggleExpand(id) {
  expandedId.value = expandedId.value === id ? null : id
}

const items = computed(() => {
  return notesList.value.map(n => ({
    ...n,
    date: props.productMap[n.id]?.date || ''
  }))
})
</script>
```

- [ ] **Step 3: 创建 src/components/DataExport.vue**

```vue
<template>
  <div class="data-export">
    <h3>💾 数据管理</h3>
    <div class="export-options">
      <label><input type="radio" v-model="scope" value="all" /> 全部数据</label>
      <label><input type="radio" v-model="scope" value="bookmarks" /> 仅收藏</label>
      <label><input type="radio" v-model="scope" value="notes" /> 仅笔记</label>
    </div>
    <button class="btn-export" @click="doExport">📥 导出 JSON</button>
    <button class="btn-clear" @click="confirmClear">🗑️ 清空数据</button>
    <p v-if="clearConfirm" class="clear-confirm">
      确定要清空所有数据吗？此操作不可撤销。
      <button @click="doClear">确认清空</button>
      <button @click="clearConfirm = false">取消</button>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useBookmarks } from '../composables/useBookmarks.js'
import { useNotes } from '../composables/useNotes.js'

const { bookmarkList } = useBookmarks()
const { notesList } = useNotes()

const scope = ref('all')
const clearConfirm = ref(false)

function doExport() {
  const data = {}
  if (scope.value === 'all' || scope.value === 'bookmarks') {
    data.bookmarks = [...bookmarkList.value]
  }
  if (scope.value === 'all' || scope.value === 'notes') {
    data.notes = notesList.value.reduce((acc, n) => {
      acc[n.id] = n.text
      return acc
    }, {})
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `qiuzhi-export-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  URL.revokeObjectURL(url)
}

function confirmClear() {
  clearConfirm.value = true
}

function doClear() {
  localStorage.clear()
  clearConfirm.value = false
  window.location.reload()
}
</script>

<style scoped>
.data-export h3 { margin-bottom: 12px; }
.export-options { display: flex; gap: 16px; margin-bottom: 16px; font-size: 14px; }
.btn-export, .btn-clear {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-right: 8px;
}
.btn-export { background: #1a1a2e; color: #fff; }
.btn-clear { background: #fff; color: #c62828; border: 1px solid #c62828; }
.clear-confirm { font-size: 13px; color: #c62828; margin-top: 12px; }
.clear-confirm button {
  margin-left: 8px;
  padding: 4px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  background: #fff;
  font-size: 12px;
}
</style>
```

- [ ] **Step 4: 创建 src/components/Workspace.vue**

```vue
<template>
  <div class="workspace">
    <BookmarkList :productMap="productMap" />
    <NotesList :productMap="productMap" />
    <DataExport />
  </div>
</template>

<script setup>
import BookmarkList from './BookmarkList.vue'
import NotesList from './NotesList.vue'
import DataExport from './DataExport.vue'

defineProps({
  productMap: { type: Object, default: () => ({}) }
})
</script>

<style scoped>
.workspace { max-width: 720px; margin: 0 auto; padding: 20px 16px; }
</style>
```

- [ ] **Step 5: Commit**

```bash
git add src/components/BookmarkList.vue src/components/NotesList.vue src/components/DataExport.vue src/components/Workspace.vue
git commit -m "feat: add Workspace with BookmarkList, NotesList, DataExport"
```

---

### Task 12: App.vue 最终组装

**Files:**
- Create: `public/data/dates.json` (sample)
- Modify: `src/App.vue`
- Modify: `src/main.js` (already done, verify)

- [ ] **Step 1: 创建示例数据文件 public/data/2026-07-19.json**

```json
{
  "date": "2026-07-19",
  "generated_at": "2026-07-20T15:01:00+08:00",
  "generation_error": false,
  "products": [
    {
      "id": "sample-1",
      "name": "SampleAI",
      "name_zh": "示例AI助手",
      "tagline_zh": "一键生成你的专属AI工作流",
      "description_zh": "SampleAI 让任何人都能在几分钟内创建自己的AI助手，无需编程。只需用自然语言描述你的需求，它就能自动生成工作流。",
      "url": "https://www.producthunt.com/posts/sample",
      "website": "https://example.com",
      "image_url": "",
      "votes_count": 834,
      "scores": {
        "video_suitability": { "score": 5, "reason": "丰富的UI界面，每一步操作都有视觉反馈，录屏效果极佳" },
        "beginner_friendly": { "score": 5, "reason": "完全零代码，用自然语言操作，任何人都能立马上手" },
        "popularity": { "score": 5, "reason": "当日PH第1名，834票，话题性极强" }
      },
      "video_inspiration": {
        "title_idea": "我真的震惊了！这个AI工具10分钟帮我做了3天的工作",
        "angle": "开箱体验+真人实测，强调'不用写代码'的反差感",
        "shooting_tips": "录制从注册→输入需求→生成结果的全过程，重点展示AI理解需求并产出的瞬间",
        "target_audience": "对AI好奇但不知道从何下手的普通人，学生/上班族"
      },
      "overall_suggestion": "强力推荐",
      "overall_reason": "热度极高+纯视觉演示+完全零门槛，是爆款选题的理想素材"
    }
  ]
}
```

- [ ] **Step 2: 创建 dates.json 清单文件 public/data/dates.json**

```json
{
  "dates": ["2026-07-19"]
}
```

- [ ] **Step 3: 更新 src/App.vue**

```vue
<template>
  <div class="app">
    <NavBar :currentView="currentView" @update:currentView="onViewChange" />
    <HomePage v-if="currentView === 'home'" />
    <Workspace v-else :productMap="productMap" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import NavBar from './components/NavBar.vue'
import HomePage from './components/HomePage.vue'
import Workspace from './components/Workspace.vue'
import { useBookmarks } from './composables/useBookmarks.js'

const currentView = ref('home')

function onViewChange(view) {
  currentView.value = view
  if (view === 'home') {
    history.replaceState(null, '', '/')
  } else {
    history.replaceState(null, '', '/workspace')
  }
}

// Build product map for workspace display
const { bookmarkList } = useBookmarks()
const productMap = computed(() => {
  // This is populated as users browse — bookmark IDs are the keys.
  // Names are extracted from stored bookmarks data if available.
  // For a more complete solution, the workspace could load date data on demand.
  try {
    const raw = localStorage.getItem('qiuzhi_product_names')
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
})
</script>

<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  background: #f7f7f9;
  color: #333;
  -webkit-font-smoothing: antialiased;
}
</style>
```

- [ ] **Step 4: 本地验证完整页面**

Run: `npm run dev`
Expected:
- 访问 `http://localhost:3000` → 加载示例数据，显示 1 张产品卡片
- 点击卡片 → 弹窗显示详情
- 点击"工作台" → 切换到工作台页面
- 点击"榜单" → 回到首页

- [ ] **Step 5: 验证构建**

Run: `npm run build`
Expected: 构建成功，无报错

- [ ] **Step 6: Commit**

```bash
git add src/App.vue public/data/2026-07-19.json public/data/dates.json
git commit -m "feat: assemble final App with routing and sample data"
```

---

### Task 13: 集成测试 & 收尾

**Files:**
- Modify: `scripts/fetch_and_score.py` (CI 更新 dates.json)
- Create: `.github/workflows/daily.yml` (最终确认)

- [ ] **Step 1: 运行完整测试套件**

Run: `npm test`
Expected: 所有单元测试通过

- [ ] **Step 2: 最终构建验证**

Run: `npm run build`
Expected: `dist/` 目录生成，包含 `index.html`, `assets/`, `data/`

- [ ] **Step 3: 将示例数据替换为真实占位**

删除示例文件 `public/data/2026-07-19.json`（CI 会生成真实数据）：

```bash
rm public/data/2026-07-19.json
```

保留 `public/data/dates.json` 但改为空列表：`{"dates": []}`

- [ ] **Step 4: 验证 Git 仓库结构**

Run: `git status`
Expected: 无意外改动

- [ ] **Step 5: 生成 `.gitkeep` 确保 CI 有写入权限**

```bash
touch public/data/.gitkeep
```

- [ ] **Step 6: 最终 Commit**

```bash
git add -A
git commit -m "chore: finalize integration, clean sample data"
```

---

## 执行顺序

任务应按编号顺序执行：1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13。

Task 3（Python 脚本）和 Task 4（GitHub Actions）可与前端任务（Task 5-11）并行开发，但考虑到前端需要真实数据格式，建议按序执行。
