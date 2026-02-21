from datetime import datetime, timezone, timedelta
import json
import os
from openai import OpenAI
import google.generativeai as genai
from config import *

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

class Analyzer:
    def __init__(self):
        self.client_ds = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_pro = genai.GenerativeModel("gemini-1.5-pro")
        self.total_cost_usd = 0.0

    def analyze(self, articles):
        if not articles:
            return "ニュースが収集されなかったため、本日の分析はありません。"

        log("Starting detailed analysis with Gemini Pro and DeepSeek...")
        
        # コストチェック (開始前)
        if self.total_cost_usd >= DAILY_BUDGET_USD:
            return "予算上限に達したため、詳細分析をスキップしました。"

        # コンテキスト作成
        context = "\n".join([f"- {a['title']} ({a['source']}): {a['link']}\n  {a['summary'][:200]}" for a in articles])

        results = {}

        # 1. 肯定視点 (Gemini Pro)
        try:
            resp = self.model_pro.generate_content(f"以下のAI関連ニュースに基づき、業界の進歩やポジティブな側面を強調した分析を行ってください：\n\n{context}")
            results["positive"] = resp.text
            self.total_cost_usd += 0.01 # 概算
        except Exception as e:
            results["positive"] = f"分析エラー: {e}"

        # 2. 批判・分析視点 & 競合市場 (DeepSeek)
        if self.total_cost_usd < DAILY_BUDGET_USD:
            try:
                # 批判・分析
                resp_crit = self.client_ds.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": f"以下のニュースについて、倫理的懸念、技術的限界、地政学的リスクなどの『批判的・分析的視点』で考察してください：\n\n{context}"}]
                )
                results["critical"] = resp_crit.choices[0].message.content
                self.total_cost_usd += 0.02 # 概算
                
                # 競合比較
                resp_market = self.client_ds.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": f"これらのニュースを元に、各企業の競合状況や市場シェアへの影響を分析してください：\n\n{context}"}]
                )
                results["market"] = resp_market.choices[0].message.content
                self.total_cost_usd += 0.02 # 概算
            except Exception as e:
                results["critical"] = f"DeepSeekエラー: {e}"
                results["market"] = "分析不可"

        # 編集長まとめなど
        results["summary"] = "本日のAI動向は、加速する技術革新とそれに対する規制の動きがより鮮明になった一日でした。"
        
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
    
    log("Analysis completed.")

if __name__ == "__main__":
    main()
