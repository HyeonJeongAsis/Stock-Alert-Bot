import streamlit as st
import pandas as pd
import pymysql
import time
import plotly.graph_objects as go

# ======================
# 설정
# ======================

st.set_page_config(page_title="HTS PRO", layout="wide")

st.title("🔥Let's GO!")

DB_CONFIG = {
    "host": "database-1.cqkity0bvpvd.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "mysqlmysql",
    "db": "stock_db",
}

TICKER_NAMES = {"005930.KS": "삼성전자", "042660.KS": "한화오션"}

# ======================
# DB
# ======================


def get_data(ticker):

    conn = pymysql.connect(**DB_CONFIG)

    query = f"""
    SELECT *
    FROM stock_prices
    WHERE ticker='{ticker}'
    ORDER BY created_at DESC
    LIMIT 1000
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# ======================
# Sidebar
# ======================

st.sidebar.header("종목")

target_stock = st.sidebar.selectbox("Select", list(TICKER_NAMES.keys()))

realtime = st.sidebar.checkbox("실시간 모드", True)

stock_name = TICKER_NAMES[target_stock]

# ======================
# 데이터
# ======================

df = get_data(target_stock)

if not df.empty:

    df["created_at"] = pd.to_datetime(df["created_at"])

    candle = df.resample("1min", on="created_at").agg(
        {"price": ["first", "max", "min", "last", "count"]}
    )

    candle.columns = ["open", "high", "low", "close", "volume"]
    candle = candle.dropna()

    # 이동평균선
    candle["ma5"] = candle["close"].rolling(5).mean()
    candle["ma20"] = candle["close"].rolling(20).mean()
    candle["ma60"] = candle["close"].rolling(60).mean()

    latest = candle["close"].iloc[-1]
    prev = candle["close"].iloc[-2]

    change = latest - prev
    pct = (change / prev) * 100

    color = "red" if change >= 0 else "blue"
    arrow = "▲" if change >= 0 else "▼"

    # ======================
    # HTS Header
    # ======================

    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        st.markdown(f"## {stock_name} ({target_stock})")

    with col2:
        st.markdown(
            f"<h1 style='color:{color}'>{latest:,.0f}</h1>", unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"<h2 style='color:{color}'>{arrow} {pct:.2f}%</h2>", unsafe_allow_html=True
        )

    # ======================
    # 캔들차트
    # ======================

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=candle.index,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            increasing_line_color="red",
            decreasing_line_color="blue",
        )
    )

    # 이동평균선
    fig.add_trace(go.Scatter(x=candle.index, y=candle.ma5, name="MA5"))
    fig.add_trace(go.Scatter(x=candle.index, y=candle.ma20, name="MA20"))
    fig.add_trace(go.Scatter(x=candle.index, y=candle.ma60, name="MA60"))

    # Y축 압축
    high = candle.high.tail(100).max()
    low = candle.low.tail(100).min()

    pad = (high - low) * 0.2

    fig.update_layout(
        template="plotly_dark",
        height=600,
        xaxis_rangeslider_visible=False,
        yaxis=dict(range=[low - pad, high + pad]),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ======================
    # 거래량
    # ======================

    vol_fig = go.Figure()

    vol_fig.add_bar(x=candle.index, y=candle.volume)

    vol_fig.update_layout(template="plotly_dark", height=200)

    st.plotly_chart(vol_fig, use_container_width=True)

    # Raw
    with st.expander("체결 데이터"):
        st.dataframe(df)

else:
    st.warning("데이터 없음")

# ======================
# auto refresh
# ======================

if realtime:
    time.sleep(60)
    st.rerun()
