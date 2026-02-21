from notion_client import Client
import json
import os
from datetime import datetime, timezone, timedelta
from config import *

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def create_rich_text(content):
    """
    Notion の文字制限 (2000文字) に配慮しつつリッチテキスト構造を作成。
    """
    return [{"text": {"content": content[:2000]}}]

def publish_to_notion():
    if not os.path.exists("analysis_report.json"):
        log("Missing analysis_report.json for publication.")
        return

    with open("analysis_report.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    notion = Client(auth=NOTION_TOKEN)
    
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y-%m-%d")

    log(f"Publishing {len(articles)} detailed articles to Notion...")
    
    success_count = 0
    for article in articles:
        analysis = article.get("analysis")
        if not analysis:
            log(f"  Skipping {article['title']}: No analysis data found.")
            continue
            
        try:
            # 1. データベースページの作成と Children Blocks の定義
            notion.pages.create(
                parent={"database_id": NOTION_DATABASE_ID},
                properties={
                    "Name": {"title": [{"text": {"content": article["title"]}}]},
                    "Date": {"date": {"start": today}},
                    "URL": {"url": article["link"]},
                    "Source": {"select": {"name": article["source"][:100]}},
                    "Tags": {"multi_select": [{"name": article["region"]}]}
                },
                children=[
                    # 1. 肯定視点
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"text": {"content": "肯定視点：革新とメリット"}}]}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": create_rich_text(analysis.get("affirmative", ""))}
                    },
                    # 2. 批判的視点
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"text": {"content": "批判的視点：課題とリスク"}}]}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": create_rich_text(analysis.get("critical", ""))}
                    },
                    # 3. 競合・市場比較
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"text": {"content": "競合・市場比較"}}]}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": create_rich_text(analysis.get("market", ""))}
                    },
                    # 4. 編集長まとめ
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"text": {"content": "編集長まとめ"}}]}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {"rich_text": create_rich_text(analysis.get("editor_summary", ""))}
                    },
                    # 5. 今日の基礎知識 (Callout)
                    {
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "rich_text": create_rich_text(analysis.get("knowledge", "")),
                            "icon": {"emoji": "💡"},
                            "color": "blue_background"
                        }
                    },
                    # オリジナル記事へのリンク
                    {
                        "object": "block",
                        "type": "divider",
                        "divider": {}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {"text": {"content": "原文ソース: "}},
                                {"text": {"content": article["link"], "link": {"url": article["link"]}}}
                            ]
                        }
                    }
                ]
            )
            log(f"Successfully published: {article['title']}")
            success_count += 1
        except Exception as e:
            import traceback
            log(f"Error publishing {article['title']}: {e}")
            log(traceback.format_exc())

    log(f"Notion publication process completed. Total successfully published: {success_count} / {len(articles)}")

if __name__ == "__main__":
    try:
        publish_to_notion()
    except Exception as e:
        import traceback
        log(f"Critical error in publisher main: {e}")
        log(traceback.format_exc())
        raise e
