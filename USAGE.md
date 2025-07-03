# Instagram Trend Tool - 使用方法

## インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/MaRu44448476/insta-tool.git
cd insta-tool
```

### 2. 仮想環境の作成
```bash
python3 -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

## 基本的な使用方法

### 最小限の実行例
```bash
python insta_trend.py --tags travel
```

### よく使用するオプション
```bash
# 複数のハッシュタグで検索
python insta_trend.py --tags travel --tags food --tags photography

# 期間を指定
python insta_trend.py --tags travel --since 2025-06-01 --until 2025-06-30

# 上位20件を取得してJSON出力
python insta_trend.py --tags fashion --top 20 --output json

# 最低いいね数でフィルタ
python insta_trend.py --tags travel --min-likes 1000

# すべての形式で出力
python insta_trend.py --tags travel --output all
```

## コマンドラインオプション

| オプション | 短縮形 | 説明 | デフォルト |
|-----------|-------|------|-----------|
| `--tags` | `-t` | 検索するハッシュタグ（#なし）複数指定可 | 必須 |
| `--since` | | 開始日（YYYY-MM-DD） | 30日前 |
| `--until` | | 終了日（YYYY-MM-DD） | 今日 |
| `--top` | `-n` | 取得する上位投稿数 | 50 |
| `--min-likes` | | 最低いいね数フィルタ | 0 |
| `--output` | `-o` | 出力形式（csv/json/excel/all） | csv |
| `--login` | | Instagramログインを使用 | false |
| `--verbose` | `-v` | 詳細ログを有効化 | false |
| `--quiet` | `-q` | エラー以外の出力を抑制 | false |
| `--config` | `-c` | 設定ファイルのパス | |
| `--no-slack` | | Slack通知を無効化 | false |
| `--output-dir` | | カスタム出力ディレクトリ | |

## 設定方法

### 環境変数による設定（.env ファイル）

`.env.example`をコピーして`.env`ファイルを作成：

```bash
cp .env.example .env
```

`.env`ファイルを編集：

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

`config.yml.example`をコピーして`config.yml`を作成：

```bash
cp config.yml.example config.yml
```

```yaml
# Instagram認証情報
instagram_username: your_username
instagram_password: your_password

# Slack通知
slack_webhook_url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# デフォルト設定
default_top_count: 50
default_days_back: 30
request_delay_min: 2.0
request_delay_max: 5.0
max_retries: 3
retry_delay: 10.0

# 出力設定
output_dir: output

# ログ設定
log_level: INFO
log_file: instagram_trend.log
```

## 出力形式

### CSV形式
- Excel互換（UTF-8 BOM付き）
- 主要なメトリクスを含む表形式

### JSON形式
- 構造化データ
- メタデータと分析結果を含む
- APIとの連携に適している

### Excel形式
- 複数シート
  - Posts: 投稿データ
  - Summary: 統計サマリー
  - Top Hashtags: 共起ハッシュタグ

## よくあるエラーと対処法

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

### ハッシュタグエラー
```
🔍 Hashtag Error: Hashtag #wrongtag not found
```
**対処法**: ハッシュタグのスペルを確認

### 接続エラー
```
❌ Error: Connection error while fetching
```
**対処法**: インターネット接続を確認、VPN使用時は無効化

## パフォーマンス最適化

### リクエスト遅延の調整
```env
REQUEST_DELAY_MIN=1.0
REQUEST_DELAY_MAX=3.0
```

### 取得件数の制限
```bash
python insta_trend.py --tags travel --top 20
```

### ログインの使用
```bash
python insta_trend.py --tags travel --login
```
※ログインすると取得可能なデータが増える場合があります

## トラブルシューティング

### 詳細ログの有効化
```bash
python insta_trend.py --tags travel --verbose
```

### ログファイルの確認
```bash
tail -f instagram_trend.log
```

### テストの実行
```bash
pip install -r requirements-dev.txt
pytest tests/
```

## 開発者向け情報

### モジュールとして実行
```bash
python -m insta_trend_tool --tags travel
```

### パッケージのインストール
```bash
pip install -e .
insta-trend --tags travel
```

### カスタム設定での実行
```bash
python insta_trend.py --config custom_config.yml --tags travel
```