from notion_client import Client
import json
import os
from datetime import datetime, timezone, timedelta
from config import *

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def publish_to_notion():
    if not os.path.exists("analysis_report.json") or not os.path.exists("collected_news.json"):
        log("Missing data for publication.")
        return

    with open("analysis_report.json", "r", encoding="utf-8") as f:
        report = json.load(f)
    with open("collected_news.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    notion = Client(auth=NOTION_TOKEN)
    
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y-%m-%d")

    # 記事ごとの要約とデータベース登録
    log("Registering articles to Notion database...")
    for article in articles:
        try:
            notion.pages.create(
                parent={"database_id": NOTION_DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": article["title"]}}]},
                    "Date": {"date": {"start": today}},
                    "URL": {"url": article["link"]},
                    "Source": {"select": {"name": article["source"][:100]}}, # 100文字制限
                    "Tags": {"multi_select": [{"name": article["region"]}]}
                },
                children=[
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"text": {"content": article["summary"][:2000]}}]}
                    }
                ]
            )
        except Exception as e:
            log(f"Error publishing article {article['title']}: {e}")

    # 分析レポートの作成 (必要に応じて既存のページの子ページとして作成なども検討可)
    # ここではデータベースへの登録のみとする（要件：データベース形式）
    log(f"Published {len(articles)} articles to Notion.")

if __name__ == "__main__":
    publish_to_notion()
