import feedparser
import json
import time
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google import genai
from config import *

# --- Logger (簡易版) ---
def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# --- Phase 1: RSS Collection ---
def collect_rss():
    log("Starting RSS collection (Unconditional Mode)...")
    articles = []
    
    for source in RSS_SOURCES:
        try:
            log(f"Fetching from {source['name']}...")
            feed = feedparser.parse(source["url"])
            if not feed.entries:
                log(f"  Warning: No entries found in feed for {source['name']}")
                continue
                
            # 日付判定を完全に削除し、最新の5件を無条件で取得
            count = 0
            for entry in feed.entries[:5]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get("summary", entry.get("description", "")),
                    "source": source["name"],
                    "region": source["region"],
                    "priority": source.get("priority", "normal")
                })
                count += 1
            log(f"  Collected {count} latest articles from {source['name']}.")
        except Exception as e:
            log(f"Error collecting from {source['name']}: {e}")
            # エラーが起きても他のソースへ進む
            
    log(f"TOTAL articles collected from RSS: {len(articles)}")
    return articles

# --- Phase 1: Google Search Monitor ---
def collect_search():
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_CX:
        log("Google Search API keys missing. Skipping search monitor.")
        return []

    log("Starting Google Search monitor (Unconditional Mode)...")
    service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
    articles = []
    
    for source in SEARCH_MONITOR_SOURCES:
        try:
            query = f"site:{source['domain']}"
            res = service.cse().list(
                q=query,
                cx=GOOGLE_SEARCH_CX
                # 日付制限 (dateRestrict) も念のため削除または緩和
            ).execute()
            
            if "items" in res:
                # 検索結果からも最新の5件を取得
                for item in res["items"][:5]:
                    articles.append({
                        "title": item["title"],
                        "link": item["link"],
                        "summary": item.get("snippet", ""),
                        "source": source["name"],
                        "region": source["region"],
                        "priority": source.get("priority", "normal")
                    })
        except Exception as e:
            log(f"Error collecting from {source['name']} via search: {e}")
            
    log(f"Collected {len(articles)} articles from Search.")
    return articles

# --- Phase 2: Selection (Filtering with Gemini) ---
def select_articles(articles):
    if not articles:
        log("Selection Phase: No articles provided. Skipping.")
        return []

    log(f"Starting selection phase for {len(articles)} articles using {MODEL_FLASH}...")
    
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 重複排除 (URL基準)
    unique_articles = {a["link"]: a for a in articles}.values()
    candidate_list = list(unique_articles)[:100]
    
    prompt = f"""
以下のニュース記事リストから、AI関連の最新動向として重要度が高いものを {TARGET_ARTICLE_COUNT} 件選別してください。

出力形式: 選別した記事のURLを1行1件ずつ、プレーンテキストで出力してください。説明は不要です。

記事リスト:
"""
    for a in candidate_list:
        prompt += f"- TITLE: {a['title']}\n  URL: {a['link']}\n"

    try:
        response = client.models.generate_content(
            model=MODEL_FLASH,
            contents=prompt
        )
        
        selected_urls = [line.strip() for line in response.text.strip().split("\n") if "http" in line]
        selected_articles = [a for a in candidate_list if a["link"] in selected_urls]
        
        log(f"Gemini selected {len(selected_articles)} articles.")
        return selected_articles
    except Exception as e:
        log(f"Error in selection phase: {e}")
        # エラー時はフォールバックとして最初の数件を返す
        return candidate_list[:MIN_ARTICLE_COUNT]

def main():
    # 1. 収集
    rss_articles = collect_rss()
    search_articles = collect_search()
    all_articles = rss_articles + search_articles
    
    if not all_articles:
        log("Critical Error: No articles collected at all.")
        return

    # 2. 選別
    selected = select_articles(all_articles)
    
    # 3. 中間保存
    with open("collected_news.json", "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)
    
    log(f"Job 1 completed. {len(selected)} articles saved to collected_news.json.")

if __name__ == "__main__":
    main()
