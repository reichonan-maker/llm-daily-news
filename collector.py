import feedparser
import json
import time
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from google import genai
from config import *

# --- Logger (簡易版) ---
def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

# --- Phase 1: RSS Collection ---
def collect_rss():
    log("Starting RSS collection...")
    articles = []
    threshold = datetime.now(timezone.utc) - timedelta(hours=48)
    
    for source in RSS_SOURCES:
        try:
            log(f"Fetching from {source['name']}...")
            feed = feedparser.parse(source["url"])
            if not feed.entries:
                log(f"  Warning: No entries found in feed for {source['name']}")
                continue
                
            count = 0
            for entry in feed.entries:
                # 日付取得と判定 (48時間以内に緩和)
                published = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                
                # 日付が不明な場合は念のため「本日のニュース」として扱う
                if published is None or published >= threshold:
                    articles.append({
                        "title": entry.title,
                        "link": entry.link,
                        "summary": entry.get("summary", entry.get("description", "")),
                        "source": source["name"],
                        "region": source["region"],
                        "priority": source.get("priority", "normal")
                    })
                    count += 1
            log(f"  Collected {count} new/recent articles from {source['name']}.")
        except Exception as e:
            import traceback
            log(f"Error collecting from {source['name']}: {e}")
            log(traceback.format_exc())
            
    log(f"TOTAL articles collected from RSS: {len(articles)}")
    return articles

# --- Phase 1: Google Search Monitor ---
def collect_search():
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_CX:
        log("Google Search API keys missing. Skipping search monitor.")
        return []

    log("Starting Google Search monitor for non-RSS sites...")
    service = build("customsearch", "v1", developerKey=GOOGLE_SEARCH_API_KEY)
    articles = []
    
    for source in SEARCH_MONITOR_SOURCES:
        try:
            query = f"site:{source['domain']}"
            res = service.cse().list(
                q=query,
                cx=GOOGLE_SEARCH_CX,
                dateRestrict="d1"  # 過去24時間
            ).execute()
            
            if "items" in res:
                for item in res["items"]:
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
    if not articles:
        log("Warning: No articles found via Google Search monitor.")
    return articles

# --- Phase 2: Selection (Filtering with Gemini) ---
def select_articles(articles):
    if not articles:
        return []

    log(f"Starting selection phase for {len(articles)} articles using {MODEL_FLASH}...")
    
    # 最新の google-genai SDK への移行
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 重複排除 (URL基準)
    unique_articles = {a["link"]: a for a in articles}.values()
    candidate_list = list(unique_articles)[:100]
    
    prompt = f"""
以下のニュース記事リストから、AI関連の最新動向として重要度が高いものを {TARGET_ARTICLE_COUNT} 件選別してください。
特に Global South（アフリカ、ラテンアメリカ、東南アジア、中東、インド）や欧州の規制、中国の動向に関する記事は、日本・米国以外の視点として高く評価してください。

出力形式: 選別した記事のURLを1行1件ずつ、プレーンテキストで出力してください。説明は不要です。

記事リスト:
"""
    for a in candidate_list:
        prompt += f"- TITLE: {a['title']}\n  URL: {a['link']}\n  REGION: {a['region']}\n\n"

    try:
        # 最新の SDK 文法で generate_content を呼び出し
        response = client.models.generate_content(
            model=MODEL_FLASH,
            contents=prompt
        )
        
        selected_urls = [line.strip() for line in response.text.strip().split("\n") if "http" in line]
        
        # URLを元に元の記事情報を紐付け
        selected_articles = [a for a in candidate_list if a["link"] in selected_urls]
        log(f"Gemini selected {len(selected_articles)} articles.")
        return selected_articles
    except Exception as e:
        import traceback
        log(f"Error in selection phase: {e}")
        log(traceback.format_exc())
        # エラー時はフォールバックとして最初の数件を返す
        return candidate_list[:MIN_ARTICLE_COUNT]

def main():
    # 1. 収集
    rss_articles = collect_rss()
    search_articles = collect_search()
    all_articles = rss_articles + search_articles
    
    # 2. 選別
    selected = select_articles(all_articles)
    
    # 3. 中間保存 (Job 2へ引き継ぐ)
    with open("collected_news.json", "w", encoding="utf-8") as f:
        json.dump(selected, f, ensure_ascii=False, indent=2)
    
    log(f"Job 1 completed. {len(selected)} articles saved to collected_news.json.")

if __name__ == "__main__":
    main()
