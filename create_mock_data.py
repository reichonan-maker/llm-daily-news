import json
import os

# テスト用の偽の分析レポートデータを作成
mock_analysis = {
    "affirmative": "これは肯定的なテスト分析です。最新のAI技術は非常に有望です。",
    "critical": "これは批判的なテスト分析です。計算リソースの消費が課題です。",
    "market": "GPT-4と比較して、このモデルは特定のタスクで優れています。",
    "editor_summary": "全体として、この技術は業界に大きな影響を与えるでしょう。",
    "knowledge": "LLMとは大規模言語モデルのことです。"
}

mock_articles = [
    {
        "title": "ローカルテスト記事 1",
        "link": "https://example.com/test1",
        "source": "Test Source",
        "region": "Japan",
        "summary": "これはテスト記事1の要約です。",
        "analysis": mock_analysis
    }
]

with open("analysis_report.json", "w", encoding="utf-8") as f:
    json.dump(mock_articles, f, ensure_ascii=False, indent=2)

print("Created mock analysis_report.json for testing publisher.py")
