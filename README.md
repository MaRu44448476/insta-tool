# Instagram Trend Research Script

## 1. 目的 (Purpose)
指定した期間内におけるハッシュタグ単位の“伸びている”Instagram投稿を収集し、いいね数・コメント数でランキング化して CSV/JSON として出力する。SNS 企画立案や競合分析に活用できるデータを提供する。

---

## 2. 要件定義 (Requirements)

### 2.1 入力仕様 (CLI Parameters)
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--tags`      | list[str] | ✔ | 対象ハッシュタグ (複数可、`#` 無し) |
| `--since`     | YYYY-MM-DD |   | 期間開始 (デフォルト: 30日前) |
| `--until`     | YYYY-MM-DD |   | 期間終了 (デフォルト: 今日) |
| `--top`       | int |   | 上位 N 件取得 (デフォルト: 50) |
| `--min-likes` | int |   | 最低いいね数フィルタ (0=無効) |
| `--output`    | csv / json |   | 出力フォーマット (デフォルト: csv) |
| `--login`     | flag |   | ログインして取得するか (デフォルト: false) |
| `--verbose`   | flag |   | 進捗詳細ログ |

### 2.2 出力仕様
1. **ファイル**: CSV または JSON (UTF-8-SIG)
   * 必須列: `post_url`, `shortcode`, `posted_at`, `likes`, `comments`, `owner_username`, `caption`
2. **CLI 表示**: トップ N 件を表形式で表示
3. **オプション**: Slack Webhook へ通知

### 2.3 機能要件 (Functional)
F-1 ハッシュタグ検索 → 投稿メタデータ取得  
F-2 期間フィルタ (`since` / `until`)  
F-3 エンゲージメント順ソート & 上位 N 件抽出  
F-4 CSV/JSON エクスポート  
F-5 CLI オプション受取  
F-6 進捗・エラーログ  
F-7 (任意) Slack 通知  
F-8 (任意) バッチ実行設定読み込み

### 2.4 非機能要件 (Non-Functional)
* Python 3.10+ / PEP8 準拠
* 1 タグ 100 件取得で 1 分以内 (NW 依存)
* `.env` or `config.yml` で設定外部化
* 仮想環境完結、外部 DB 不要
* MIT / Apache-2.0 ライブラリのみ使用

### 2.5 技術構成 (Tech Stack)
* **Language**: Python
* **Main libs**: instaloader, pandas, dateutil, click (CLI), (optional) slack-sdk
* **Structure**:
  ```text
  insta_trend_tool/
    |- cli.py        # 引数処理
    |- fetcher.py    # Instaloader ラッパ
    |- processor.py  # フィルタ & ソート
    |- exporter.py   # エクスポート/通知
  ```

---

## 3. 想定課題・リスクと緩和策 (Risks & Mitigations)
| ID | リスク | 潜在エラー | 主な緩和策 |
|----|--------|-----------|-----------|
| 1 | Instagram ブロック / UI 変更 | 429, パース失敗 | 2–5 s ランダム遅延, パーサ集中管理, 3 回リトライ&スキップ |
| 2 | ログイン必須化 / 認証失効 | LoginRequiredException | デフォルト非ログイン, cookie キャッシュ, 自動再ログイン |
| 3 | 大量投稿でメモリ枯渇 | OOM | ストリーム処理 + `heapq.nlargest` で上位 N 件のみ保持 |
| 4 | 無効タグ | ProfileNotExistsException | `try/except` でタグ別に捕捉し警告一覧表示 |
| 5 | 日付パース & TZ ずれ | 期間外混入 | `dateutil.isoparse`→UTC, 曖昧入力はエラーで例示 |
| 6 | ファイル書込権限/文字化け | PermissionError, CSV 破損 | 出力前に書込確認, CSV utf-8-sig, JSON `ensure_ascii=False` |
| 7 | Slack 通知失敗 | HTTP 4xx/5xx | 非同期送信(5 s timeout), 失敗ログ & 再送案内 |
| 8 | 依存ライブラリ更新 | API 変更 | `requirements.txt` でバージョン固定, CI でサンプル取得テスト |
| 9 | ユーザー入力ミス | 無効日付, negative top | CLI バリデータ + `validate_args()` で整合性確認 |
|10 | Unicode/絵文字 | EncodingError | 全文字列 `str()` キャスト, `errors="replace"` で書出 |
|11 | 未処理例外 | スクリプト強制終了 | `main()` を `try/except Exception` で囲み、`--debug` でスタックトレース |

---

## 4. 品質向上のための開発規律 (Coding Practices)
* **型安全**: `@dataclass` + type hints, `mypy --strict`
* **静的解析**: `ruff` でコードスタイル & lint
* **テスト**: pytest + responses モック (HTTP), 辺縁値テスト
* **CI**: lint → mypy → pytest → サンプルタグ取得テスト
* **ドキュメント**: README に「よくあるエラーと対処法」を記載

---

## 5. スケジュール (Rough)
| 作業 | 日数 |
|------|------|
| 要件定義 | 0.5 |
| 詳細設計 | 0.5 |
| 実装 (F-1〜F-6) | 1 |
| オプション機能 | 0.5 |
| テスト & README | 0.5 |
| **合計** | **約 3 日** |

---

### CLI Usage Example
```bash
python insta_trend.py \
  --tags travel food \
  --since 2025-06-01 --until 2025-06-30 \
  --top 20 --output json
```

---
このドキュメントは要件とリスクを統合して一元管理するための Markdown 版です。CI や GitHub 上のプレビューで可読性を保ちつつ、`spec_risks.yaml` は機械処理用に存続させます。
