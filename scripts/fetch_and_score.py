#!/usr/bin/env python3
"""Fetch ProductHunt Top 10, score with DeepSeek V4, output JSON."""

import os
import json
import time
import traceback
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytz
import requests
from openai import OpenAI
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"
PH_GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"
BEIJING_TZ = pytz.timezone("Asia/Shanghai")
OUTPUT_DIR = "public/data"

SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "product_analysis.md").read_text(encoding="utf-8")
SCORE_KEYS = ("product_value", "technical_insight", "transferability")
ANALYSIS_FIELDS = {
    "product_analysis": ("target_problem", "workflow", "ai_value", "differentiation"),
    "technical_analysis": ("disclosed_facts", "possible_approach", "tradeoffs", "unknowns"),
}


def validate_analysis(scored):
    """Reject incomplete model output before saving a report."""
    for key in ("name_zh", "tagline_zh", "description_zh", "intro_zh", "category", "overall_reason"):
        if not isinstance(scored.get(key), str) or not scored[key].strip():
            raise ValueError(f"Missing or invalid {key}")
    for key in SCORE_KEYS:
        dim = scored["scores"][key]
        score = dim["score"]
        if score is not None and (type(score) is not int or not 1 <= score <= 5):
            raise ValueError(f"Invalid score for {key}")
        if not isinstance(dim.get("reason"), str) or not dim["reason"].strip():
            raise ValueError(f"Missing reason for {key}")
    for section, fields in ANALYSIS_FIELDS.items():
        for key in fields:
            value = scored[section][key]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Missing or invalid {section}.{key}")
    for key, minimum, maximum in (("transferable_insights", 1, 2), ("validation_questions", 2, 3)):
        items = scored[key]
        if not isinstance(items, list) or not minimum <= len(items) <= maximum:
            raise ValueError(f"Invalid {key}")
        if any(not isinstance(item, str) or not item.strip() for item in items):
            raise ValueError(f"Invalid item in {key}")


def derive_suggestion(scores):
    values = [scores[key]["score"] for key in SCORE_KEYS]
    if any(value is None for value in values):
        return "信息不足"
    if min(values) >= 3 and sum(value >= 4 for value in values) >= 2:
        return "优先研究"
    if sum(values) >= 9:
        return "值得参考"
    return "暂缓研究"


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
        "first": 10,
    }

    response = session.post(
        PH_GRAPHQL_URL,
        headers=headers,
        json={"query": query, "variables": variables},
        timeout=30,
    )
    if not response.ok:
        print(f"ProductHunt API returned {response.status_code}")
        print(f"Response body: {response.text[:500]}")
        print(f"Request headers (sanitized): Authorization: Bearer {token[:8]}...{token[-4:]}")
        response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")

    posts = data["data"]["posts"]["nodes"]
    print(f"Fetched {len(posts)} products for {date_str}")
    return date_str, posts


def extract_json_from_response(content):
    """Robustly extract JSON from LLM response, handling markdown fences and extra text."""
    # Strip leading/trailing whitespace
    content = content.strip()

    # Remove markdown code fences: ```json ... ``` or ``` ... ```
    if content.startswith("```"):
        # Find first newline to strip the opening fence
        first_nl = content.find("\n")
        if first_nl != -1:
            content = content[first_nl + 1:]
        # Strip closing fence
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        # Strip optional "json" language tag
        if content.startswith("json\n"):
            content = content[5:].strip()

    # If still not valid JSON, try to extract the outermost { ... } block
    if not content.startswith("{"):
        brace_start = content.find("{")
        if brace_start != -1:
            brace_end = content.rfind("}")
            if brace_end > brace_start:
                content = content[brace_start:brace_end + 1]

    return content


def score_product_with_deepseek(client, product, rank):
    """Score a single product using DeepSeek V4. Returns enriched product dict."""
    source = {
        "rank": rank,
        "name": product["name"],
        "tagline": product.get("tagline", ""),
        "description": product.get("description", ""),
        "votes_count": product["votesCount"],
        "producthunt_url": product.get("url", ""),
        "website_url": product.get("website", ""),
    }
    user_prompt = "请按约定结构分析以下产品资料（未独立验证的厂商自述）：\n" + json.dumps(source, ensure_ascii=False)

    print(f"  Scoring [{rank}] {product['name']}...")

    last_error = None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=os.getenv("DEEPSEEK_MODEL", "").strip() or DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=4096,
                temperature=0.3,
            )
            content = response.choices[0].message.content.strip()

            # Handle possible markdown code fences
            content = extract_json_from_response(content)

            scored = json.loads(content)

            validate_analysis(scored)
            scored["overall_suggestion"] = derive_suggestion(scored["scores"])

            return scored

        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s exponential backoff
                print(f"  Retry {attempt + 1}/{max_retries - 1} for {product['name']} in {wait}s: {e}")
                time.sleep(wait)
            else:
                print(f"  ERROR scoring {product['name']}: {e}")
                traceback.print_exc()

    return {
        "name_zh": product["name"],
        "tagline_zh": product.get("tagline", ""),
        "description_zh": product.get("description", ""),
        "scores": {key: {"score": None, "reason": "分析生成失败"} for key in SCORE_KEYS},
        **{section: {} for section in ANALYSIS_FIELDS},
        "transferable_insights": [],
        "validation_questions": [],
        "overall_suggestion": "生成失败",
        "overall_reason": "产品分析生成失败，暂无法判断研究价值",
        "category": "",
        "scoring_error": str(last_error),
    }


def get_image_url(media):
    """Extract image URL from ProductHunt media field."""
    try:
        if media and isinstance(media, list) and len(media) > 0:
            return media[0].get("url", "")
    except Exception:
        pass
    return ""


def load_cached_products(path):
    """Reuse saved product descriptions without fetching Product Hunt again."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    date_str = data["date"]
    datetime.strptime(date_str, "%Y-%m-%d")
    posts = []
    for product in data["products"]:
        posts.append({
            "id": product["id"],
            "name": product["name"],
            "tagline": product.get("tagline", product.get("tagline_zh", "")),
            "description": product.get("description", product.get("description_zh", "")),
            "votesCount": product.get("votes_count", 0),
            "url": product["url"],
            "website": product.get("website", ""),
            "media": [{"url": product.get("image_url", "")}],
        })
    if not posts:
        raise ValueError("Cached report has no products")
    return date_str, posts


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate AI product analysis")
    parser.add_argument("--input", help="Regenerate a saved report JSON without a Product Hunt token")
    args = parser.parse_args(argv)
    # Process environment takes precedence, followed by .env and .env.local.
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env", override=False)
    load_dotenv(project_root / ".env.local", override=False)
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")

    client = OpenAI(
        api_key=deepseek_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL", "").strip() or DEEPSEEK_BASE_URL,
    )

    # Fetch
    if args.input:
        print("Reusing cached product descriptions; no new Product Hunt fetch.")
        date_str, posts = load_cached_products(args.input)
    else:
        print("Fetching ProductHunt Top 10...")
        date_str, posts = fetch_top_products(get_producthunt_token())

    # Score
    generation_error = False
    products = []
    for i, post in enumerate(posts, 1):
        # Cached reports were sorted by recommendation, so restore PH rank by votes.
        rank = 1 + sum(p["votesCount"] > post["votesCount"] for p in posts) if args.input else i
        scored = score_product_with_deepseek(client, post, rank)
        product_entry = {
            "id": post["id"],
            "name": post["name"],
            "name_zh": scored.get("name_zh", post["name"]),
            "tagline_zh": scored.get("tagline_zh", post.get("tagline", "")),
            "description_zh": scored.get("description_zh", post.get("description", "")),
            "intro_zh": scored.get("intro_zh", ""),
            "url": post["url"],
            "website": post.get("website", ""),
            "image_url": get_image_url(post.get("media")),
            "votes_count": post["votesCount"],
            "scores": scored.get("scores", {}),
            "product_analysis": scored.get("product_analysis", {}),
            "technical_analysis": scored.get("technical_analysis", {}),
            "transferable_insights": scored.get("transferable_insights", []),
            "validation_questions": scored.get("validation_questions", []),
            "category": scored.get("category", ""),
            "overall_suggestion": scored.get("overall_suggestion", "信息不足"),
            "overall_reason": scored.get("overall_reason", ""),
        }
        if "scoring_error" in scored:
            generation_error = True
            product_entry["scoring_error"] = scored["scoring_error"]
        products.append(product_entry)

        # Rate-limit: wait 2s between products to avoid DeepSeek throttling
        if i < len(posts):
            time.sleep(2)

    # Sort by overall_suggestion priority + votes
    priority = {"优先研究": 0, "值得参考": 1, "信息不足": 2, "暂缓研究": 3, "生成失败": 4}
    products.sort(key=lambda p: (priority.get(p["overall_suggestion"], 5), -p["votes_count"]))

    # Generate output
    now_beijing = datetime.now(timezone.utc).astimezone(BEIJING_TZ)
    output = {
        "date": date_str,
        "schema_version": 2,
        "analysis_style": "plain_language_v1",
        "source_mode": "cached_report" if args.input else "producthunt_api",
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
        except (json.JSONDecodeError, KeyError):
            pass
    if date_str not in existing_dates:
        existing_dates.append(date_str)
        existing_dates.sort(reverse=True)
        with open(dates_path, "w", encoding="utf-8") as f:
            json.dump({"dates": existing_dates}, f, ensure_ascii=False, indent=2)
        print(f"Updated dates.json: {len(existing_dates)} dates")


if __name__ == "__main__":
    main()
