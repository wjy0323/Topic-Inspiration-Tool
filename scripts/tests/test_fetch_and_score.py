import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fetch_and_score as report


def analysis(scores=(4, 4, 3)):
    return {
        "name_zh": "Example",
        "tagline_zh": "标语",
        "description_zh": "据产品介绍，自动整理资料。",
        "intro_zh": "整理资料的工作流值得研究。",
        "category": "效率工具",
        "overall_reason": "工作流值得研究，但实际收益待验证。",
        "scores": {key: {"score": value, "reason": "信息不足" if value is None else "依据产品介绍"}
                   for key, value in zip(report.SCORE_KEYS, scores)},
        "product_analysis": {field: "据产品介绍，整理用户资料。" for field in report.ANALYSIS_FIELDS["product_analysis"]},
        "technical_analysis": {field: "未披露，待验证。" for field in report.ANALYSIS_FIELDS["technical_analysis"]},
        "transferable_insights": ["借鉴自动分类工作流，用于资料归档。"],
        "validation_questions": ["上传一组资料，检查分类准确性。", "重复提交，检查是否重复建档。"],
    }


def response(value):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(value, ensure_ascii=False)))])


PRODUCT = {"id": "one", "name": "Example", "tagline": "Organize notes", "description": "Sort notes automatically",
           "votesCount": 12, "url": "https://example.com/product", "website": "https://example.com"}


class ReportTests(unittest.TestCase):
    def test_model_output_uses_new_research_criteria_and_preserves_unknown(self):
        client = Mock()
        client.chat.completions.create.return_value = response(analysis((4, None, 4)))
        result = report.score_product_with_deepseek(client, PRODUCT, 1)
        self.assertEqual(result["overall_suggestion"], "信息不足")
        self.assertIsNone(result["scores"]["technical_insight"]["score"])
        messages = client.chat.completions.create.call_args.kwargs["messages"]
        self.assertEqual(messages[0]["content"], report.SYSTEM_PROMPT)
        self.assertIn(PRODUCT["url"], messages[1]["content"])
        self.assertNotIn("video_inspiration", result)

    def test_research_recommendations(self):
        for values, expected in [((4, 4, 3), "优先研究"), ((3, 3, 3), "值得参考"),
                                 ((2, 2, 2), "暂缓研究"), ((5, None, 5), "信息不足")]:
            with self.subTest(values=values):
                self.assertEqual(report.derive_suggestion(analysis(values)["scores"]), expected)

    def test_malformed_scores_and_missing_analysis_are_rejected(self):
        for invalid in (True, "4", 0, 6):
            with self.subTest(invalid=invalid):
                value = analysis()
                value["scores"]["product_value"]["score"] = invalid
                with self.assertRaises(ValueError):
                    report.validate_analysis(value)
        value = analysis()
        del value["technical_analysis"]["unknowns"]
        with self.assertRaises(KeyError):
            report.validate_analysis(value)

    def test_failed_model_call_is_not_a_negative_product_judgment(self):
        client = Mock()
        client.chat.completions.create.side_effect = RuntimeError("Test authentication failure")
        with patch.object(report.time, "sleep"), patch.object(report.traceback, "print_exc"), redirect_stdout(io.StringIO()):
            result = report.score_product_with_deepseek(client, PRODUCT, 1)
        self.assertEqual(result["overall_suggestion"], "生成失败")
        self.assertTrue(all(item["score"] is None for item in result["scores"].values()))
        self.assertIn("scoring_error", result)

    def test_daily_pipeline_saves_analysis_and_sorts_research_before_votes(self):
        low = copy.deepcopy(PRODUCT)
        low.update(id="popular", votesCount=999)
        client = Mock()
        client.chat.completions.create.side_effect = [response(analysis((2, 2, 2))), response(analysis())]
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(report, "OUTPUT_DIR", directory), patch.object(report, "get_producthunt_token", return_value="test"), \
                 patch.dict(report.os.environ, {"DEEPSEEK_API_KEY": "test"}), patch.object(report, "OpenAI", return_value=client), \
                 patch.object(report, "fetch_top_products", return_value=("2026-11-06", [low, PRODUCT])), \
                 patch.object(report.time, "sleep"), redirect_stdout(io.StringIO()):
                report.main([])
            saved = json.loads((Path(directory) / "latest.json").read_text())
            self.assertEqual(saved["schema_version"], 2)
            self.assertFalse(saved["generation_error"])
            self.assertEqual([p["id"] for p in saved["products"]], ["one", "popular"])
            self.assertEqual(saved["products"][0]["technical_analysis"], analysis()["technical_analysis"])
            self.assertEqual(saved, json.loads((Path(directory) / "2026-11-06.json").read_text()))
            self.assertEqual(json.loads((Path(directory) / "dates.json").read_text()), {"dates": ["2026-11-06"]})

    def test_cached_report_regenerates_without_producthunt_credentials(self):
        client = Mock()
        client.chat.completions.create.return_value = response(analysis())
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.json"
            source.write_text(json.dumps({"date": "2026-11-06", "products": [{
                "id": "one", "name": "Example", "tagline_zh": "标语", "description_zh": "原有介绍",
                "votes_count": 12, "url": PRODUCT["url"], "image_url": "https://example.com/image.png"
            }]}))
            with patch.object(report, "OUTPUT_DIR", directory), patch.object(report, "get_producthunt_token") as token, \
                 patch.dict(report.os.environ, {"DEEPSEEK_API_KEY": "test", "DEEPSEEK_BASE_URL": "https://gateway.example/v1", "DEEPSEEK_MODEL": "provider-model"}), patch.object(report, "OpenAI", return_value=client) as factory, \
                 redirect_stdout(io.StringIO()):
                report.main(["--input", str(source)])
            token.assert_not_called()
            self.assertEqual(factory.call_args.kwargs["base_url"], "https://gateway.example/v1")
            self.assertEqual(client.chat.completions.create.call_args.kwargs["model"], "provider-model")
            saved = json.loads((Path(directory) / "latest.json").read_text())
            self.assertEqual(saved["source_mode"], "cached_report")
            self.assertEqual(saved["products"][0]["image_url"], "https://example.com/image.png")
            self.assertIn("原有介绍", client.chat.completions.create.call_args.kwargs["messages"][1]["content"])


if __name__ == "__main__":
    unittest.main()
