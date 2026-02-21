import os

# --- API Keys & IDs (GitHub Secrets を想定) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = "2f004f93e9a98084a920c64d21777baf"

# --- AI Models ---
MODEL_PRO = "gemini-3-flash"
MODEL_FLASH = "gemini-3-flash"

# --- Budget & Limits ---
DAILY_BUDGET_USD = 0.25
GOOGLE_SEARCH_DAILY_LIMIT = 100
GOOGLE_SEARCH_MONITOR_RESERVE = 20  # RSSなしサイトの監視用に予約する回数

# --- News Sources (RSS) ---
RSS_SOURCES = [
    {"name": "Arxiv (CS.AI)", "url": "http://export.arxiv.org/rss/cs.AI", "region": "North America", "priority": "high"},
    {"name": "Hugging Face Daily Papers", "url": "https://huggingface.co/papers/feed", "region": "North America", "priority": "high"},
    {"name": "Hacker News", "url": "https://news.ycombinator.com/rss", "region": "North America", "priority": "high"},
    {"name": "Reddit (LocalLlama)", "url": "https://www.reddit.com/r/LocalLLaMA/.rss", "region": "North America"},
    {"name": "Reddit (MachineLearning)", "url": "https://www.reddit.com/r/MachineLearning/.rss", "region": "North America"},
    {"name": "The Batch", "url": "https://www.deeplearning.ai/the-batch/feed/", "region": "North America"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "region": "North America"},
    {"name": "Google AI Blog", "url": "http://googleaiblog.blogspot.com/atom.xml", "region": "North America"},
    {"name": "Meta AI Blog", "url": "https://ai.facebook.com/blog/rss/", "region": "North America"},
    {"name": "South China Morning Post (Tech)", "url": "https://www.scmp.com/rss/91/feed", "region": "China"},
    {"name": "Nikkei Asia (Tech)", "url": "https://asia.nikkei.com/rss/feed/nar", "region": "Japan"},
    {"name": "Tech.eu", "url": "https://tech.eu/feed/", "region": "Europe"},
    {"name": "The Register (AI)", "url": "https://www.theregister.com/software/ai/headlines.atom", "region": "Europe"},
    {"name": "Sifted", "url": "https://sifted.eu/feed/", "region": "Europe"},
    {"name": "Rest of World", "url": "https://restofworld.org/feed/", "region": "Global South", "priority": "high"},
    {"name": "Wamda (MENA)", "url": "https://www.wamda.com/feed/json", "region": "Global South"},
    {"name": "TechCabal", "url": "https://techcabal.com/feed/", "region": "Global South"},
    {"name": "TechPoint Africa", "url": "https://techpoint.africa/feed/", "region": "Global South"},
    {"name": "Inc42", "url": "https://inc42.com/feed/", "region": "Global South"},
    {"name": "LatamList", "url": "https://latamlist.com/feed/", "region": "Global South"},
    {"name": "Zenn (Tech)", "url": "https://zenn.dev/feed", "region": "Japan"},
    {"name": "Qiita (Tag: AI)", "url": "https://qiita.com/tags/ai/feed", "region": "Japan"},
    {"name": "Hatena Bookmark (IT)", "url": "https://b.hatena.ne.jp/hotentry/it.rss", "region": "Japan"},
    {"name": "PC Watch", "url": "https://rss.itmedia.co.jp/rss/2.0/pcuser.xml", "region": "Japan"},
    {"name": "ITmedia AI+", "url": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml", "region": "Japan"},
    {"name": "note (Tag: AI)", "url": "https://note.com/hashtag/AI/rss", "region": "Japan"},
]

# --- News Sources (Google Search Monitor) ---
SEARCH_MONITOR_SOURCES = [
    {"name": "Jiqizhixin", "domain": "jiqizhixin.com", "region": "China", "priority": "high"},
    {"name": "QbitAI", "domain": "qbitai.com", "region": "China"},
    {"name": "36Kr", "domain": "36kr.com", "region": "China"},
    {"name": "The Information", "domain": "theinformation.com", "region": "North America"},
    {"name": "WSJ", "domain": "wsj.com", "region": "North America"},
]

# --- Selection Parameters ---
TARGET_ARTICLE_COUNT = 30
MIN_ARTICLE_COUNT = 10
MAX_ARTICLE_COUNT = 50

# --- Prompt Settings ---
REGION_SCORE_BOOST = {
    "Global South": 1.5,
    "China": 1.2,
    "Europe": 1.2,
    "North America": 1.0,
    "Japan": 1.0
}
