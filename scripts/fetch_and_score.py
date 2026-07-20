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
