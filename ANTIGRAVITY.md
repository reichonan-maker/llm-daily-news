# ANTIGRAVITY.md (プロジェクト憲法)

## 1. プロジェクト概要
- **名称**: LLM 日刊紙 (LLM Daily Newspaper)
- **目的**: 世界の最新AIニュースを自動収集・分析し、多角的な視点を持つニュースレターとしてNotionに配信する。
- **ターゲット**: AIの最新動向を効率的に、かつ多角的な視点（肯定・批判・比較）で把握したいユーザー。

## 2. 技術スタック
- **言語**: Python 3.10+
- **インフラ**: GitHub Actions (Ubuntu)
- **AI / LLM API**:
  - Google Gemini (Flash & Pro)
  - DeepSeek API (OpenAI互換)
- **外部サービス**:
  - Google Custom Search API (RSSなしサイトの監視、有料記事補完)
  - Notion API (データベース出力)
  - Feedparser (RSS収集)

## 3. MVP（最小構成）の範囲
1. **ハイブリッド収集**: 30箇所以上のソースからRSS収集 + Google Search site検索によるサイト監視。
2. **優先度制御**: 記事不足時は非主要国（Global South）や重要タグのスコアを優先。
3. **API予算管理**: 1日 $0.25 (約38円) 上限。超過時は現データでソフトランディング。
4. **Notion通知**: データベース形式。Date, Tags, Summary, URL, Source プロパティを保持。
5. **GitHub Actions**: 22:00 (Job 1) と 01:30 (Job 2) の2段階実行。

## 4. セキュリティ & 安全管理
- APIキーは GitHub Secrets で管理。
- 検索API（100回/日）の割り当て管理（監視用 10-20回、補完用 80回）。
- 「守りの三柱」監査（RLS/規約/HTTPS）の実施。

## 5. 現在のステップ
- [Step 1] 要件定義と詳細ヒアリング（進行中）
- [Step 2] 収集・選別ロジックのプロトタイプ作成
- [Step 3] 分析・出力ロジックの統合
- [Step 4] GitHub Actions 定時実行テスト
