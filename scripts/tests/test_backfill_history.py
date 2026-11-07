import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import backfill_history as backfill
from test_fetch_and_score import analysis, response


class BackfillTests(unittest.TestCase):
    def setUp(self):
        self.product = {
            "id": "old", "name": "Example", "tagline_zh": "旧标语", "description_zh": "旧介绍",
            "votes_count": 23, "url": "https://example.com/ph", "website": "https://example.com",
            "image_url": "https://example.com/img.png", "video_inspiration": {"angle": "old"},
            "scoring_error": "old failure",
        }

    def test_upgrade_preserves_identity_and_original_source_removes_legacy_fields(self):
        original = {"date": "2026-11-05", "products": [self.product], "generation_error": True}
        enriched = analysis()
        enriched["overall_suggestion"] = "优先研究"
        result = backfill.upgraded_report(original, [enriched])
        product = result["products"][0]
        for key in ("id", "name", "votes_count", "url", "website", "image_url"):
            self.assertEqual(product[key], self.product[key])
        self.assertEqual(product["source_description"], "旧介绍")
        self.assertEqual(backfill.source_product(product, 1)["description"], "旧介绍")
        self.assertNotIn("video_inspiration", product)
        self.assertNotIn("scoring_error", product)
        self.assertFalse(result["generation_error"])
        self.assertIn("video_inspiration", original["products"][0])
        with self.assertRaises(ValueError):
            backfill.upgraded_report(original, [])

    def test_generation_retries_incomplete_responses_and_validates_before_returning(self):
        client = Mock()
        client.chat.completions.create.side_effect = [response({}), response(analysis())]
        with patch.object(backfill.time, "sleep"):
            result = backfill.generate(client, "test-model", backfill.source_product(self.product, 1), 2)
        self.assertEqual(result["overall_suggestion"], "优先研究")
        self.assertEqual(client.chat.completions.create.call_count, 2)

    def test_atomic_write_and_stable_cache_key(self):
        source = backfill.source_product(self.product, 1)
        changed = {**source, "rank": 3, "votes_count": 99}
        self.assertEqual(backfill.cache_key(source, "model"), backfill.cache_key(changed, "model"))
        self.assertNotEqual(backfill.cache_key(source, "model"), backfill.cache_key(source, "different"))
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "test.json"
            backfill.write_json(target, {"text": "中文"})
            self.assertEqual(json.loads(target.read_text()), {"text": "中文"})
            self.assertFalse(target.with_name("test.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
