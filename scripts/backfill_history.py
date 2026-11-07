#!/usr/bin/env python3
"""Regenerate historical analyses with checkpoints and per-report atomic writes."""

import argparse
import hashlib
import json
import os
import random
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from fetch_and_score import (
    DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, SYSTEM_PROMPT,
    derive_suggestion, extract_json_from_response, validate_analysis,
)

STYLE = "plain_language_v1"
ROOT = Path(__file__).resolve().parents[1]
PRIORITY = {"优先研究": 0, "值得参考": 1, "信息不足": 2, "暂缓研究": 3}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def source_product(product, rank):
    return {
        "id": product["id"], "name": product["name"], "rank": rank,
        "tagline": product.get("source_tagline", product.get("tagline", product.get("tagline_zh", ""))),
        "description": product.get("source_description", product.get("description", product.get("description_zh", ""))),
        "votes_count": product.get("votes_count", 0),
        "producthunt_url": product["url"], "website_url": product.get("website", ""),
        "source_note": "历史缓存简介，可能经过旧版 AI 翻译或改写，未重新访问原网页核验。",
    }


def cache_key(source, model):
    # Ranking and votes are context, not part of the research scoring criteria.
    stable = {key: value for key, value in source.items() if key not in ("rank", "votes_count")}
    return hashlib.sha256(json.dumps([SYSTEM_PROMPT, model, stable], ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def generate(client, model, source, attempts):
    for attempt in range(attempts):
        try:
            response = client.chat.completions.create(
                model=model, messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": "请分析以下历史缓存产品资料：\n" + json.dumps(source, ensure_ascii=False)},
                ], temperature=0.3, max_tokens=4096,
            )
            result = json.loads(extract_json_from_response(response.choices[0].message.content or ""))
            validate_analysis(result)
            result["overall_suggestion"] = derive_suggestion(result["scores"])
            return result
        except Exception as exc:
            if attempt + 1 == attempts:
                # No raw exception text: gateway responses can contain credentials.
                raise RuntimeError(f"{type(exc).__name__}, status={getattr(exc, 'status_code', None)}") from None
            time.sleep(min(30, 2 ** (attempt + 1)) + random.random())


def upgraded_report(original, analyses):
    if len(original["products"]) != len(analyses):
        raise ValueError("Analysis count must match the original report")
    products = []
    for product, analysis in zip(original["products"], analyses):
        result = dict(product)
        result.pop("video_inspiration", None)
        result.pop("scoring_error", None)
        result.update({key: analysis[key] for key in (
            "name_zh", "tagline_zh", "description_zh", "intro_zh", "scores",
            "product_analysis", "technical_analysis", "transferable_insights",
            "validation_questions", "category", "overall_reason", "overall_suggestion",
        )})
        # Preserve the exact cached input so future rewrites don't compound translations.
        source = source_product(product, 0)
        result["source_tagline"] = source["tagline"]
        result["source_description"] = source["description"]
        products.append(result)
    products.sort(key=lambda item: (PRIORITY[item["overall_suggestion"]], -item.get("votes_count", 0)))
    return {**original, "schema_version": 2, "analysis_style": STYLE,
            "source_mode": "cached_report", "generation_error": False,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "products": products}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.workers <= 32 or args.attempts < 1:
        parser.error("workers must be 1..32 and attempts must be positive")
    load_dotenv(ROOT / ".env", override=False)
    load_dotenv(ROOT / ".env.local", override=False)
    model = os.getenv("DEEPSEEK_MODEL", "").strip() or DEEPSEEK_MODEL
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        raise SystemExit("DEEPSEEK_API_KEY is not configured")
    client = OpenAI(api_key=key, base_url=os.getenv("DEEPSEEK_BASE_URL", "").strip() or DEEPSEEK_BASE_URL,
                    timeout=180, max_retries=0)
    state = ROOT / ".backfill"
    state.mkdir(exist_ok=True)
    # flock is released automatically if the process stops.
    import fcntl
    lock = (state / "run.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("A historical backfill is already running")
    data_dir = ROOT / "public" / "data"
    paths = sorted(data_dir.glob("????-??-??.json"), reverse=True)
    latest_date = paths[0].stem
    backup = state / "backups" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup.mkdir(parents=True)
    for path in [*paths, data_dir / "latest.json", data_dir / "dates.json"]:
        if path.exists():
            shutil.copy2(path, backup / path.name)
    pending, requests, ready, results, failures = {}, {}, {}, {}, {}
    for path in paths:
        original = json.loads(path.read_text())
        if original.get("analysis_style") == STYLE:
            continue
        sources = [source_product(p, 1 + sum(other.get("votes_count", 0) > p.get("votes_count", 0)
                    for other in original["products"])) for p in original["products"]]
        keys = [cache_key(source, model) for source in sources]
        pending[path.name] = {"path": path, "original": original, "keys": keys}
        for item, source in zip(keys, sources):
            requests[item] = source
            cached = state / "cache" / (item + ".json")
            if cached.exists():
                try:
                    value = json.loads(cached.read_text())
                    validate_analysis(value)
                    results[item] = value
                except (ValueError, KeyError, TypeError):
                    pass
    report_total = len(pending)
    last_status = 0

    def update():
        nonlocal last_status
        for name, job in pending.items():
            if name in ready or not all(item in results for item in job["keys"]):
                continue
            value = upgraded_report(job["original"], [results[item] for item in job["keys"]])
            write_json(job["path"], value)
            if value["date"] == latest_date:
                write_json(data_dir / "latest.json", value)
            ready[name] = True
            print(f"Updated {value['date']} ({len(ready)}/{report_total} reports)", flush=True)
        status = {"reports_total": report_total, "reports_updated": len(ready), "products_total": len(requests),
                  "products_completed": len(results), "failures": failures, "backup": str(backup)}
        write_json(state / "progress.json", status)
        if time.monotonic() - last_status >= 10:
            print(json.dumps({key: value for key, value in status.items() if key not in ("backup", "failures")}), flush=True)
            last_status = time.monotonic()

    update()
    print(f"Starting {len(requests) - len(results)} model calls with {args.workers} workers", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        jobs = {executor.submit(generate, client, model, source, args.attempts): item
                for item, source in requests.items() if item not in results}
        for future in as_completed(jobs):
            item = jobs[future]
            try:
                result = future.result()
                write_json(state / "cache" / (item + ".json"), result)
                results[item] = result
            except Exception as exc:
                failures[item] = str(exc)
                print(f"Generation failed: {str(exc)}", flush=True)
            update()
    print(json.dumps({"status": "complete" if len(ready) == report_total else "incomplete",
                      "reports_updated": len(ready), "reports_total": report_total, "failures": len(failures)}), flush=True)
    if len(ready) != report_total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
