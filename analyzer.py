from datetime import datetime, timezone, timedelta
import json
import os
import time
import google.generativeai as genai
from config import *

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

class Analyzer:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_pro = genai.GenerativeModel(MODEL_PRO)
        self.current_cost_estimate = 0.0

    def analyze_article(self, article):
        """
        1つの記事に対して、肯定・批判・編集長の3役による多角的分析を行う。
        """
        log(f"Analyzing: {article['title']}...")
        
        prompt = f"""
あなたは世界最高峰のIT新聞の編集部チーム（肯定派アナリスト、批判派アナリスト、編集長）です。
以下のニュース記事について、読み応えのある多角的な分析レポートを作成してください。

【ニュース内容】
タイトル: {article['title']}
ソース: {article['source']}
内容の要約: {article['summary']}

【出力指示】
以下の5つのセクションについて、日本語で詳細に出力してください。
各セクションの本文は300〜500文字程度の専門的かつ深い洞察を含めてください。

1. [肯定視点]
   このニュースの革新性、業界へのポジティブな影響、技術的メリットを強調して記述してください。
2. [批判的視点]
   あえて批判的な立場で、潜在的なリスク、隠れたコスト、実装の難易度、競合に対する優位性の欠如などを鋭く指摘してください。
3. [競合・市場比較]
   このニュースに関連する技術や企業を、競合（GPT-4, Claude, Llama等）と比較し、市場シェアや地政学的な文脈での立ち位置を分析してください。
4. [編集長まとめ]
   上記の両視点を踏まえ、一歩引いた視点から実務へのインパクトや未来予測を結論としてまとめてください。
5. [今日の基礎知識]
   この記事を理解するために重要な専門用語（1つ以上）を抜き出し、初心者にも分かりやすく解説してください。

出力形式: JSON形式で以下のキーを持つオブジェクトとして出力してください。
キー: "affirmative", "critical", "market", "editor_summary", "knowledge"
JSON以外のテキストは一切含めないでください。
"""
        try:
            response = self.model_pro.generate_content(prompt)
            # JSON部分の抽出 (稀にMarkdownのデコレーションが入るため)
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].strip()
            
            analysis_data = json.loads(text)
            return analysis_data
        except Exception as e:
            log(f"Error analyzing {article['title']}: {e}")
            return None

    def run(self, input_file, output_file):
        if not os.path.exists(input_file):
            log(f"Input file {input_file} not found.")
            return

        with open(input_file, "r", encoding="utf-8") as f:
            articles = json.load(f)

        analyzed_articles = []
        
        # 予算と時間の制限を考慮しつつ順次処理
        # (GitHub Actions のタイムアウトに注意し、必要に応じて記事数を制限)
        target_articles = articles[:TARGET_ARTICLE_COUNT]
        
        for article in target_articles:
            if self.current_cost_estimate >= DAILY_BUDGET_USD:
                log("Budget limit reached. Skipping remaining articles.")
                break
                
            analysis = self.analyze_article(article)
            if analysis:
                article["analysis"] = analysis
                analyzed_articles.append(article)
                self.current_cost_estimate += 0.005 # Gemini Pro の概算コスト
            
            # APIレート制限対策のインターバル
            time.sleep(2)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analyzed_articles, f, ensure_ascii=False, indent=2)
        
        log(f"Total {len(analyzed_articles)} articles analyzed and saved.")

if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.run("collected_news.json", "analysis_report.json")
