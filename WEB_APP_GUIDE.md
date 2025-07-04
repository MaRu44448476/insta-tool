# 📱 Instagram Trend Tool - Webアプリ使用ガイド

## 🎉 完成しました！

**プログラミング知識ゼロでも使える**スマホ対応のWebアプリが完成しました！

## 🚀 起動方法

### 方法1: 簡単起動（推奨）

#### Windows の場合
```bash
# ダブルクリックで起動
run_app.bat
```

#### Mac/Linux の場合
```bash
# ターミナルで実行
./run_app.sh
```

### 方法2: 手動起動

```bash
# 1. 依存関係をインストール
pip install -r requirements-streamlit.txt

# 2. Webアプリを起動
streamlit run app.py

# または
python run_app.py
```

## 📱 アクセス方法

### 🖥️ PCから
起動後、ブラウザで自動的に開きます
- URL: `http://localhost:8501`

### 📱 スマホから
同じWiFiネットワーク内なら、スマホからもアクセス可能！
- PCのIPアドレスを確認: `ipconfig` (Windows) または `ifconfig` (Mac/Linux)
- スマホのブラウザで: `http://[PCのIPアドレス]:8501`

例: `http://192.168.1.100:8501`

## 🎯 使い方（超簡単！）

### 1. ハッシュタグを入力
```
travel, food, fashion
```
※ #マークは不要です

### 2. 期間を選択
- 過去7日間
- 過去30日間  
- 過去3ヶ月
- カスタム期間

### 3. 設定を調整
- **取得件数**: 10〜200件
- **出力形式**: Excel（推奨）、CSV、JSON

### 4. 分析開始！
大きな青いボタンをクリック

### 5. 結果をダウンロード
分析完了後、「📥 結果をダウンロード」ボタンが表示されます

## 📊 スマホでの使用例

```
🔍 検索設定
┌─────────────────────────────┐
│ ハッシュタグ                │
│ travel, cafe, tokyo         │
├─────────────────────────────┤
│ 📅 期間: 過去30日間         │
│ 📊 取得件数: 50             │
│ 📄 出力形式: Excel          │
└─────────────────────────────┘

      🚀 分析開始

📊 分析結果
✅ 総投稿数: 150件
📈 平均エンゲージメント: 1.2K
❤️ 平均いいね数: 980

      📥 結果をダウンロード
```

## 💡 便利な機能

### 📋 リアルタイムプレビュー
- 分析結果の一部をブラウザで確認
- ダウンロード前に内容をチェック可能

### 📊 統計情報表示
- 総投稿数
- 平均エンゲージメント
- 平均いいね数

### 🎛️ 詳細設定（サイドバー）
- 最小いいね数フィルタ
- 詳細ログ表示

### 📖 内蔵ガイド
- 使い方ガイド
- トラブルシューティング
- FAQ

## 🌐 クラウドデプロイ（上級者向け）

### Streamlit Cloud（無料）
1. GitHubにプッシュ
2. [Streamlit Cloud](https://streamlit.io/cloud) でアカウント作成
3. リポジトリを連携
4. `app.py` を指定してデプロイ

### Heroku
```bash
# Procfileを作成
echo "web: streamlit run app.py --server.port \$PORT" > Procfile

# デプロイ
heroku create your-app-name
git push heroku main
```

## 🎯 実用例

### 📈 マーケティング担当者
```
ハッシュタグ: fashion, ootd, style
期間: 過去30日間
→ 業界トレンドを週次レポートで分析
```

### 🏪 店舗運営者
```
ハッシュタグ: cafe, tokyo, coffee
期間: 過去7日間
→ 地域の人気店をチェック
```

### 📱 インフルエンサー
```
ハッシュタグ: travel, photography, nature
期間: 過去3ヶ月
→ バイラルコンテンツを分析
```

## 🆘 トラブルシューティング

### ❌ アプリが起動しない
```bash
# 依存関係を再インストール
pip install -r requirements-streamlit.txt

# Pythonバージョン確認（3.10+が必要）
python --version
```

### 📱 スマホからアクセスできない
1. PCとスマホが同じWiFiに接続されているか確認
2. PCのファイアウォール設定を確認
3. IPアドレスが正しいか確認

### 🐌 分析が遅い
- 取得件数を減らす（50件以下）
- 期間を短くする（7日間以下）
- 時間をおいて再実行（レート制限回避）

## 🎉 これで完成！

**誰でも簡単にInstagramトレンド分析ができるWebアプリ**が完成しました！

- ✅ プログラミング知識不要
- ✅ スマホ対応
- ✅ 直感的な操作
- ✅ プロフェッショナルな分析結果
- ✅ 複数の出力形式対応

マーケティング、競合分析、コンテンツ企画など、様々な用途でご活用ください！ 📊✨