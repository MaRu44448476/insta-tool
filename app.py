"""
Instagram Trend Tool - Streamlit Web App
スマホ対応のWebインターフェース
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from pathlib import Path
import time
import logging

# Optional imports with fallbacks
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# Instagram分析のための直接インポート
INSTA_MODULES_AVAILABLE = False
IMPORT_ERROR_MSG = ""

try:
    import instaloader
    st.info("✅ instaloader インポート成功")
except ImportError as e:
    IMPORT_ERROR_MSG += f"❌ instaloader: {e}\n"

try:
    from insta_trend_tool.config import Config
    st.info("✅ config インポート成功")
except ImportError as e:
    IMPORT_ERROR_MSG += f"❌ config: {e}\n"

try:
    from insta_trend_tool.models import TrendAnalysisResult, InstagramPost
    st.info("✅ models インポート成功")
except ImportError as e:
    IMPORT_ERROR_MSG += f"❌ models: {e}\n"

try:
    from insta_trend_tool.fetcher import InstagramFetcher
    st.info("✅ fetcher インポート成功")
except ImportError as e:
    IMPORT_ERROR_MSG += f"❌ fetcher: {e}\n"

try:
    from insta_trend_tool.processor import TrendProcessor
    st.info("✅ processor インポート成功")
except ImportError as e:
    IMPORT_ERROR_MSG += f"❌ processor: {e}\n"

try:
    from insta_trend_tool.exporter import TrendExporter
    st.info("✅ exporter インポート成功")
    INSTA_MODULES_AVAILABLE = True
except ImportError as e:
    IMPORT_ERROR_MSG += f"❌ exporter: {e}\n"

if IMPORT_ERROR_MSG:
    st.error(f"モジュールインポートエラー:\n{IMPORT_ERROR_MSG}")
    st.info("デバッグ: 現在の作業ディレクトリとPythonパスを確認中...")
    
    # デバッグ情報表示
    import sys
    st.write("Python path:", sys.path)
    st.write("Current working directory:", os.getcwd())
    
    # ディレクトリ構造確認
    try:
        import glob
        st.write("ファイル一覧:", glob.glob("*"))
        if os.path.exists("insta_trend_tool"):
            st.write("insta_trend_tool内容:", glob.glob("insta_trend_tool/*"))
    except Exception as e:
        st.write(f"ディレクトリ確認エラー: {e}")

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# スマホ対応の設定
st.set_page_config(
    page_title="Instagram Trend Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSSでモバイル最適化
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        border-radius: 10px;
    }
    .stSelectbox > div > div {
        font-size: 1.1rem;
    }
    .metric-container {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .result-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    /* モバイル対応 */
    @media (max-width: 768px) {
        .main > div {
            padding-top: 0.5rem;
        }
        .stButton > button {
            height: 2.5rem;
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def init_output_dir():
    """出力ディレクトリを作成"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir

def run_analysis(hashtags, period_days, top_count, output_format, min_likes=0):
    """Instagram分析を実行"""
    if not INSTA_MODULES_AVAILABLE:
        return False, "", "必要なモジュールが利用できません"
    
    try:
        # 設定の初期化
        config = Config()
        
        # データ収集期間の計算
        since_date = None
        if period_days > 0:
            since_date = datetime.now() - timedelta(days=period_days)
        
        # 分析結果を格納するリスト
        all_posts = []
        
        # 各ハッシュタグについて分析
        fetcher = InstagramFetcher(config)
        processor = TrendProcessor(config)
        
        for hashtag in hashtags:
            # ハッシュタグからデータ取得
            hashtag_clean = hashtag.strip().replace('#', '')
            
            try:
                result = fetcher.fetch_hashtag_posts(
                    hashtag_clean, 
                    top_count, 
                    since_date
                )
                
                if result.posts:
                    all_posts.extend(result.posts)
                    
            except Exception as e:
                continue
        
        if not all_posts:
            return False, "", "投稿データが取得できませんでした"
        
        # データ処理
        analysis_result = TrendAnalysisResult(
            hashtags=hashtags,
            posts=all_posts,
            total_posts=len(all_posts),
            collection_date=datetime.now()
        )
        
        # 最小いいね数でフィルタリング
        if min_likes > 0:
            analysis_result.posts = [
                post for post in analysis_result.posts 
                if post.likes >= min_likes
            ]
        
        # 処理とソート
        processed_result = processor.process_posts(analysis_result)
        
        # エクスポート
        exporter = TrendExporter(config)
        output_path = exporter.export_data(processed_result, output_format)
        
        return True, f"分析完了: {len(processed_result.posts)}件の投稿を処理", ""
        
    except Exception as e:
        logging.error(f"分析エラー: {str(e)}")
        return False, "", f"分析エラー: {str(e)}"

def get_latest_output_file(output_format):
    """最新の出力ファイルを取得"""
    output_dir = Path("output")
    if not output_dir.exists():
        return None
    
    files = list(output_dir.glob(f"*.{output_format}"))
    if not files:
        return None
    
    # 最新ファイルを返す
    return max(files, key=lambda f: f.stat().st_mtime)

def preview_csv_data(file_path, max_rows=5):
    """CSVデータのプレビューを生成"""
    try:
        df = pd.read_csv(file_path)
        return df.head(max_rows)
    except Exception:
        return None

def format_number(num):
    """数値をフォーマット"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)

# メインUI
st.title("📊 Instagram Trend Analyzer")
st.markdown("**スマホからでも簡単にInstagramトレンド分析！**")

# 出力ディレクトリ初期化
output_dir = init_output_dir()

# サイドバーで詳細設定（PCユーザー向け）
with st.sidebar:
    st.header("⚙️ 詳細設定")
    advanced_mode = st.checkbox("詳細設定を表示")
    
    if advanced_mode:
        min_likes = st.number_input("最小いいね数", min_value=0, value=0)
        verbose_mode = st.checkbox("詳細ログを表示")
    else:
        min_likes = 0
        verbose_mode = False

# メイン入力セクション
with st.container():
    st.subheader("🔍 検索設定")
    
    # ハッシュタグ入力
    hashtags_input = st.text_input(
        "ハッシュタグ（カンマ区切り）",
        value="travel, food",
        help="例: travel, fashion, food（#は不要）",
        placeholder="travel, food, photography"
    )
    
    # 期間選択（モバイルフレンドリー）
    col1, col2 = st.columns([2, 1])
    with col1:
        period_option = st.selectbox(
            "📅 期間",
            ["過去7日間", "過去30日間", "過去3ヶ月", "カスタム期間"],
            help="分析する期間を選択してください"
        )
    
    with col2:
        if period_option == "カスタム期間":
            custom_days = st.number_input("日数", min_value=1, max_value=365, value=30)
        else:
            period_mapping = {
                "過去7日間": 7,
                "過去30日間": 30,
                "過去3ヶ月": 90
            }
            custom_days = period_mapping[period_option]
    
    # その他設定
    col3, col4 = st.columns(2)
    with col3:
        top_count = st.selectbox(
            "📊 取得件数",
            [10, 20, 50, 100, 200],
            index=2,
            help="上位何件を取得するか"
        )
    
    with col4:
        output_format = st.selectbox(
            "📄 出力形式",
            ["excel", "csv", "json"],
            format_func=lambda x: {
                "csv": "📊 CSV",
                "excel": "📈 Excel（推奨）", 
                "json": "💻 JSON"
            }[x]
        )

# 分析実行セクション
st.markdown("---")

# 実行ボタン
if st.button("🚀 分析開始", type="primary", use_container_width=True):
    # バリデーション
    if not hashtags_input.strip():
        st.error("❌ ハッシュタグを入力してください")
    else:
        hashtag_list = [tag.strip() for tag in hashtags_input.split(",") if tag.strip()]
        
        if not hashtag_list:
            st.error("❌ 有効なハッシュタグを入力してください")
        else:
            # 分析実行
            with st.container():
                st.subheader("🔄 分析中...")
                
                # プログレスバーとステータス
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # ステップ1: 設定確認
                status_text.markdown("⚙️ **設定を確認中...**")
                progress_bar.progress(10)
                time.sleep(0.5)
                
                # 設定表示
                st.info(f"""
                📋 **分析設定**
                - ハッシュタグ: {', '.join([f'#{tag}' for tag in hashtag_list])}
                - 期間: 過去{custom_days}日間
                - 取得件数: {top_count}件
                - 出力形式: {output_format.upper()}
                {f'- 最小いいね数: {min_likes}' if min_likes > 0 else ''}
                """)
                
                # ステップ2: データ取得
                status_text.markdown("🔍 **Instagram投稿を取得中...**")
                progress_bar.progress(30)
                
                # 分析実行
                success, message, error = run_analysis(
                    hashtag_list, custom_days, top_count, output_format, min_likes
                )
                
                progress_bar.progress(70)
                status_text.markdown("📊 **データを処理中...**")
                time.sleep(0.5)
                
                progress_bar.progress(90)
                status_text.markdown("📄 **結果を準備中...**")
                time.sleep(0.5)
                
                progress_bar.progress(100)
                
                if success:
                    status_text.markdown("✅ **分析完了！**")
                    st.success(f"🎉 {message}")
                    
                    # 結果ファイル取得
                    result_file = get_latest_output_file(output_format)
                    
                    if result_file:
                        # 結果表示セクション
                        st.markdown("---")
                        st.subheader("📊 分析結果")
                        
                        # ファイル情報
                        file_size = result_file.stat().st_size
                        file_size_mb = file_size / 1024 / 1024
                        
                        # 結果カード
                        st.markdown(f"""
                        <div class="result-card">
                        <h4>📄 結果ファイル</h4>
                        <p><strong>ファイル名:</strong> {result_file.name}</p>
                        <p><strong>サイズ:</strong> {file_size_mb:.2f} MB</p>
                        <p><strong>作成日時:</strong> {datetime.fromtimestamp(result_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # CSVの場合はプレビュー表示
                        if output_format in ["csv", "excel"]:
                            try:
                                if output_format == "csv":
                                    df_preview = pd.read_csv(result_file)
                                else:
                                    df_preview = pd.read_excel(result_file)
                                
                                if not df_preview.empty:
                                    st.markdown("**📋 データプレビュー（上位5件）**")
                                    
                                    # 主要カラムのみ表示（モバイル対応）
                                    display_columns = ['owner_username', 'likes', 'comments', 'engagement_score']
                                    available_columns = [col for col in display_columns if col in df_preview.columns]
                                    
                                    if available_columns:
                                        preview_df = df_preview[available_columns].head(5)
                                        
                                        # 数値をフォーマット
                                        for col in ['likes', 'comments', 'engagement_score']:
                                            if col in preview_df.columns:
                                                preview_df[col] = preview_df[col].apply(format_number)
                                        
                                        st.dataframe(preview_df, use_container_width=True)
                                    
                                    # 統計情報
                                    if 'engagement_score' in df_preview.columns:
                                        avg_engagement = df_preview['engagement_score'].mean()
                                        total_posts = len(df_preview)
                                        
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("📊 総投稿数", f"{total_posts:,}")
                                        with col2:
                                            st.metric("📈 平均エンゲージメント", format_number(int(avg_engagement)))
                                        with col3:
                                            if 'likes' in df_preview.columns:
                                                avg_likes = df_preview['likes'].mean()
                                                st.metric("❤️ 平均いいね数", format_number(int(avg_likes)))
                            except Exception as e:
                                st.warning(f"プレビューの生成に失敗しました: {str(e)}")
                        
                        # ダウンロードボタン
                        with open(result_file, "rb") as file:
                            file_data = file.read()
                            
                            # MIMEタイプの設定
                            mime_types = {
                                "csv": "text/csv",
                                "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                "json": "application/json"
                            }
                            
                            st.download_button(
                                label="📥 結果をダウンロード",
                                data=file_data,
                                file_name=result_file.name,
                                mime=mime_types.get(output_format, "application/octet-stream"),
                                use_container_width=True
                            )
                        
                        # 詳細ログ表示（デバッグ用）
                        if verbose_mode and message:
                            with st.expander("📋 詳細ログを表示"):
                                st.text(message)
                    else:
                        st.warning("⚠️ 結果ファイルが見つかりませんでした。")
                        if error:
                            st.error(f"エラー詳細: {error}")
                else:
                    st.error("❌ 分析中にエラーが発生しました")
                    if error:
                        st.error(f"**エラー詳細:** {error}")
                    
                    # よくあるエラーの対処法
                    st.markdown("""
                    **💡 トラブルシューティング:**
                    - ハッシュタグのスペルを確認してください
                    - 期間を短くしてみてください
                    - 取得件数を減らしてみてください
                    - しばらく時間をおいてから再試行してください
                    """)

# フッター
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("📱 **スマホ対応**")
with col2:
    st.markdown("💻 **PC対応**")
with col3:
    st.markdown("🔄 **リアルタイム分析**")

# 使い方ガイド
with st.expander("📖 使い方ガイド"):
    st.markdown("""
    ### 🔍 基本的な使い方
    
    1. **ハッシュタグを入力**: `travel, food, fashion` のようにカンマ区切りで入力
    2. **期間を選択**: 過去7日間〜3ヶ月の範囲で選択
    3. **取得件数を設定**: 10〜200件の範囲で選択
    4. **分析開始**: ボタンをクリックして分析実行
    5. **結果をダウンロード**: Excel、CSV、JSON形式で保存
    
    ### 📊 出力形式の選び方
    
    - **Excel**: グラフ作成や詳細分析に最適
    - **CSV**: 他のツールとの連携に便利
    - **JSON**: プログラマー向け、API連携用
    
    ### 💡 効果的な使い方
    
    - **競合分析**: 同業他社のハッシュタグを調査
    - **トレンド把握**: 業界の人気コンテンツを分析
    - **コンテンツ企画**: エンゲージメントの高い投稿を参考に
    """)

# サポート情報
with st.expander("🆘 サポート"):
    st.markdown("""
    ### ❓ よくある質問
    
    **Q: ハッシュタグが見つからないと言われます**
    A: ハッシュタグのスペルを確認し、実際に存在するタグか確認してください
    
    **Q: 分析に時間がかかります**
    A: 取得件数や期間を減らすと高速化できます
    
    **Q: エラーが発生します**
    A: しばらく時間をおいてから再試行してください（レート制限の可能性）
    
    ### 📞 お問い合わせ
    - GitHub Issues: [https://github.com/MaRu44448476/insta-tool/issues](https://github.com/MaRu44448476/insta-tool/issues)
    - 詳細ドキュメント: README.md を参照
    """)