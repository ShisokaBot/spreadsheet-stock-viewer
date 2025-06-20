import streamlit as st
import pandas as pd
import yfinance as yf
import datetime

st.set_page_config(page_title="📊 銘柄データ横展開ビュー", layout="wide")
st.title("📈 スプレッドシート形式の株価データ表示")

# 入力欄
symbols_input = st.text_input("銘柄コード（カンマ区切り）", "7181.T,4661.T,8113.T")
# start_date = st.date_input("開始日", datetime.date.today() - datetime.timedelta(days=7))
start_date = st.date_input("開始日", datetime.date(2025, 6, 2))
end_date = st.date_input("終了日", datetime.date.today())

if start_date > end_date:
    st.error("開始日は終了日より前である必要があります。")

if st.button("🔍 データ取得"):
    with st.spinner("データを取得中..."):
        symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
        try:
            df = yf.download(
                tickers=symbols,
                start=start_date,
                end=end_date,
                group_by="ticker",
                auto_adjust=True,
                threads=True
            )

            all_data = []
            for symbol in symbols:
                try:
                    df_symbol = df[symbol].copy()
                    df_symbol["Ticker"] = symbol
                    df_symbol["Date"] = df_symbol.index
                    df_melt = df_symbol.melt(
                        id_vars=["Ticker", "Date"],
                        value_vars=["Open", "High", "Low", "Close", "Volume"],
                        var_name="Filter",
                        value_name="Value"
                    )
                    all_data.append(df_melt)
                except KeyError:
                    st.warning(f"{symbol} のデータが取得できませんでした。")

            if all_data:
                full_df = pd.concat(all_data)

                # ピボットで日付を右方向に展開
                pivot_df = full_df.pivot_table(
                    index=["Ticker", "Filter"],
                    columns="Date",
                    values="Value"
                ).reset_index()

                # 日付列をフォーマット（YYYY-MM-DD）
                pivot_df.columns = [
                    col.strftime("%Y-%m-%d") if isinstance(col, pd.Timestamp) else col
                    for col in pivot_df.columns
                ]

                st.success("データ取得＆変換完了！")
                st.dataframe(pivot_df)

            else:
                st.warning("データがありません。")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

# streamlit run main_improving.py