from datetime import datetime, timezone, timedelta
import json
import os
import google.generativeai as genai
from config import *

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

class Analyzer:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_pro = genai.GenerativeModel("gemini-1.5-pro")
        self.model_flash = genai.GenerativeModel("gemini-1.5-flash")
        self.total_cost_usd = 0.0

    def analyze(self, articles):
        if not articles:
            return "ニュースが収集されなかったため、本日の分析はありません。"

        log("Starting detailed analysis with Gemini Pro and Flash...")
        
        # コストチェック (開始前 - Gemini は比較的安価だが一応ロジック維持)
        if self.total_cost_usd >= DAILY_BUDGET_USD:
            return "予算上限に達したため、詳細分析をスキップしました。"

        # コンテキスト作成
        context = "\n".join([f"- {a['title']} ({a['source']}): {a['link']}\n  {a['summary'][:200]}" for a in articles])

        results = {}

        # 1. 肯定視点 (Gemini Pro)
        log("Analyzing positive aspects with Gemini Pro...")
        try:
            resp = self.model_pro.generate_content(f"以下のAI関連ニュースに基づき、業界の進歩やポジティブな側面を強調した分析を行ってください：\n\n{context}")
            results["positive"] = resp.text
            self.total_cost_usd += 0.005 # 概算
        except Exception as e:
            results["positive"] = f"分析エラー: {e}"

        # 2. 批判・分析視点 (Gemini Pro) - DeepSeek から移行
        log("Analyzing critical aspects with Gemini Pro...")
        try:
            resp_crit = self.model_pro.generate_content(f"以下のニュースについて、倫理的懸念、技術的限界、地政学的なリスクなどの『批判的・分析的視点』で考察してください：\n\n{context}")
            results["critical"] = resp_crit.text
            self.total_cost_usd += 0.005 # 概算
        except Exception as e:
            results["critical"] = f"分析エラー: {e}"

        # 3. 競合・市場比較 (Gemini Pro) - DeepSeek から移行
        log("Analyzing market competition with Gemini Pro...")
        try:
            resp_market = self.model_pro.generate_content(f"これらのニュースを元に、各企業の競合状況や市場シェアへの影響、投資動向を分析してください：\n\n{context}")
            results["market"] = resp_market.text
            self.total_cost_usd += 0.005 # 概算
        except Exception as e:
            results["market"] = f"分析エラー: {e}"

        # 4. 編集長まとめ (Gemini Pro)
        log("Creating editor's summary with Gemini Pro...")
        try:
            resp_summary = self.model_pro.generate_content(f"本日のAIニュース全体の流れを俯瞰し、編集長としての総括コメントを作成してください：\n\n{context}")
            results["summary"] = resp_summary.text
            self.total_cost_usd += 0.002
        except Exception as e:
            results["summary"] = "本日のAI動向は多岐にわたりました。"

        # 5. 世界の辺境から / 今日の基礎知識 (Gemini Flash)
        log("Creating supplementary sections with Gemini Flash...")
        try:
            resp_extra = self.model_flash.generate_content(f"以下のニュースの中から、特に『世界の辺境（Global South）』に関するトピックの深掘りと、関連する『今日の基礎知識（専門用語解説）』を1つ作成してください：\n\n{context}")
            results["extra"] = resp_extra.text
            self.total_cost_usd += 0.001
        except Exception as e:
            results["extra"] = "追加情報なし"
        
        return results

def main():
    if not os.path.exists("collected_news.json"):
        log("No news data found. Exiting.")
        return

    with open("collected_news.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    analyzer = Analyzer()
    report = analyzer.analyze(articles)
    
    with open("analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    log("Analysis completed using Gemini only.")

if __name__ == "__main__":
    main()
