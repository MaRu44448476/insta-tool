# Instagram Trend Tool 📊

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/MaRu44448476/insta-tool)
[![CI](https://github.com/MaRu44448476/insta-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/MaRu44448476/insta-tool/actions/workflows/ci.yml)

指定した期間内におけるハッシュタグ単位の"伸びている"Instagram投稿を収集し、いいね数・コメント数でランキング化してCSV/JSON/Excelとして出力するツールです。SNS企画立案や競合分析に活用できるデータを提供します。

## ✨ 主な機能

- 🔍 **ハッシュタグベース検索**: 複数のハッシュタグで同時検索
- 📅 **期間フィルタリング**: 指定した日付範囲での投稿収集
- 📈 **エンゲージメント分析**: いいね数・コメント数による自動ランキング
- 📊 **多様な出力形式**: CSV、JSON、Excel形式での出力
- 💬 **Slack通知**: 分析結果の自動通知
- ⚙️ **柔軟な設定**: 環境変数・設定ファイルによるカスタマイズ
- 🛡️ **エラーハンドリング**: レート制限対応と堅牢な例外処理
- 📝 **詳細ログ**: カラー出力とファイルログ機能

## 🚀 クイックスタート

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/MaRu44448476/insta-tool.git
cd insta-tool

# 仮想環境を作成・有効化
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
```

### 基本的な使用方法

```bash
# 最小限の実行例
python insta_trend.py --tags travel

# 複数ハッシュタグで検索
python insta_trend.py --tags travel --tags food --tags photography

# 期間指定での検索
python insta_trend.py --tags travel --since 2025-06-01 --until 2025-06-30

# JSON形式で出力
python insta_trend.py --tags fashion --top 20 --output json

# 最低いいね数でフィルタ
python insta_trend.py --tags travel --min-likes 1000
```

## 📋 コマンドオプション

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|-------|------|-----------|
| `--tags` | `-t` | 検索するハッシュタグ（#なし、複数指定可） | 必須 |
| `--since` | | 開始日（YYYY-MM-DD） | 30日前 |
| `--until` | | 終了日（YYYY-MM-DD） | 今日 |
| `--top` | `-n` | 取得する上位投稿数 | 50 |
| `--min-likes` | | 最低いいね数フィルタ | 0 |
| `--output` | `-o` | 出力形式（csv/json/excel/all） | csv |
| `--login` | | Instagramログインを使用 | false |
| `--verbose` | `-v` | 詳細ログを有効化 | false |
| `--quiet` | `-q` | エラー以外の出力を抑制 | false |

## ⚙️ 設定方法

### 環境変数設定（.env）

```bash
cp .env.example .env
```

```env
# Instagram認証情報（ログインが必要な場合のみ）
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Slack通知用Webhook URL
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# デフォルト設定
DEFAULT_TOP_COUNT=50
DEFAULT_DAYS_BACK=30
REQUEST_DELAY_MIN=2
REQUEST_DELAY_MAX=5
```

### YAML設定ファイル

```bash
cp config.yml.example config.yml
```

詳細な設定オプションについては [USAGE.md](USAGE.md) を参照してください。

## 📊 出力例

### CSV出力
```
post_url,shortcode,posted_at,likes,comments,engagement_score,owner_username,caption,hashtags,post_type
https://instagram.com/p/ABC123/,ABC123,2025-07-01 12:00:00,1500,45,1545,travel_blogger,"Beautiful sunset in Tokyo! #travel #japan",travel, japan,photo
```

### JSON出力
```json
{
  "metadata": {
    "export_timestamp": "2025-07-03T13:00:00",
    "total_posts": 50,
    "tool_version": "1.0.0"
  },
  "posts": [...],
  "analysis": {
    "summary": {
      "total_posts_analyzed": 150,
      "average_engagement": 892.5,
      "hashtags_searched": ["travel", "food"]
    }
  }
}
```

## 🧪 テスト実行

```bash
# 開発用依存関係をインストール
pip install -r requirements-dev.txt

# テストを実行
pytest tests/

# カバレッジレポート付き実行
pytest tests/ --cov=insta_trend_tool
```

## 📁 プロジェクト構造

```
instagram_trend_tool/
├── insta_trend_tool/          # メインパッケージ
│   ├── __init__.py
│   ├── cli.py                 # CLIインターフェース
│   ├── config.py              # 設定管理
│   ├── models.py              # データモデル
│   ├── fetcher.py             # Instagram取得
│   ├── processor.py           # データ処理
│   ├── exporter.py            # エクスポート機能
│   ├── exceptions.py          # カスタム例外
│   └── logging_config.py      # ログ設定
├── tests/                     # テストコード
├── docs/                      # ドキュメント
├── requirements.txt           # 依存関係
├── requirements-dev.txt       # 開発用依存関係
├── setup.py                   # パッケージ設定
├── USAGE.md                   # 詳細使用方法
└── CHANGELOG.md               # 変更履歴
```

## 🚨 よくあるエラーと対処法

### 認証エラー
```
🔐 Authentication Error: Invalid Instagram credentials
```
**対処法**: `.env`ファイルのInstagram認証情報を確認

### レート制限エラー
```
⏱️ Rate Limit Error: Too many requests
```
**対処法**: 時間をおいてから再実行、またはリクエスト遅延を増加

詳細なトラブルシューティングは [USAGE.md](USAGE.md) を参照してください。

## 🔧 技術仕様

- **対応Python**: 3.10+
- **主要ライブラリ**: instaloader, pandas, click
- **出力形式**: CSV, JSON, Excel
- **設定方式**: 環境変数, YAML
- **ログ機能**: ファイルローテーション, カラー出力
- **テスト**: pytest, カバレッジ測定

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスのもとで公開されています。詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 📞 サポート

- 🐛 **バグレポート**: [Issues](https://github.com/MaRu44448476/insta-tool/issues)
- 💡 **機能提案**: [Issues](https://github.com/MaRu44448476/insta-tool/issues)
- 📖 **詳細ドキュメント**: [USAGE.md](USAGE.md)

## 🙏 謝辞

このプロジェクトは以下のオープンソースプロジェクトを使用しています：
- [instaloader](https://instaloader.github.io/) - Instagram APIライブラリ
- [pandas](https://pandas.pydata.org/) - データ処理ライブラリ
- [click](https://click.palletsprojects.com/) - CLIフレームワーク

---

**⭐ このプロジェクトが役に立った場合は、スターをつけていただけると嬉しいです！**