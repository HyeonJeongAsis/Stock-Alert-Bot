import streamlit as st
import pandas as pd
import pymysql
import time
import plotly.graph_objects as go

# ======================
# 페이지 설정
# ======================

st.set_page_config(page_title="Stock-Watch HTS", layout="wide")

st.title("🔥 Stock-Watch HTS Pro")

# ======================
# DB
# ======================

DB_CONFIG = {
    "host": "database-1.cqkity0bvpvd.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "mysqlmysql",
    "db": "stock_db",
}


def get_data(ticker):

    conn = pymysql.connect(**DB_CONFIG)

    query = f"""
    SELECT *
    FROM stock_prices
    WHERE ticker = '{ticker}'
    ORDER BY created_at ASC
    LIMIT 500
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


# ======================
# 사이드바
# ======================

st.sidebar.header("⚙️ Settings")

target_stock = st.sidebar.selectbox("종목 선택", ["005930.KS", "042660.KS"])

realtime = st.sidebar.checkbox("🔥 실시간 모드", value=True)

# ======================
# 회사명 (확정 매핑)
# ======================

TICKER_NAMES = {"005930.KS": "삼성전자", "042660.KS": "한화오션"}

stock_name = TICKER_NAMES.get(target_stock, target_stock)

# ======================
# 데이터 로드
# ======================

df = get_data(target_stock)

if not df.empty:

    df["created_at"] = pd.to_datetime(df["created_at"])

    # 🔥 1분 캔들 생성
    candle = df.resample("1min", on="created_at").agg(
        {"price": ["first", "max", "min", "last"]}
    )

    candle.columns = ["open", "high", "low", "close"]
    candle = candle.dropna()

    latest = candle["close"].iloc[-1]
    prev = candle["close"].iloc[-2] if len(candle) > 1 else latest

    change = latest - prev
    pct = (change / prev) * 100 if prev != 0 else 0

    # ======================
    # HTS 상단 UI
    # ======================

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(f"## {stock_name} ({target_stock})")

    color = "red" if change >= 0 else "blue"
    arrow = "▲" if change >= 0 else "▼"

    with col2:
        st.markdown(
            f"<h2 style='color:{color}'>{latest:,.0f}</h2>", unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"<h3 style='color:{color}'>{arrow} {change:,.0f} ({pct:.2f}%)</h3>",
            unsafe_allow_html=True,
        )

    # ======================
    # 🔥 HTS 캔들차트
    # ======================

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=candle.index,
            open=candle["open"],
            high=candle["high"],
            low=candle["low"],
            close=candle["close"],
            increasing_line_color="red",
            decreasing_line_color="blue",
        )
    )

    # 🔥 진짜 HTS 방식 Y축 자동 압축
    recent_high = candle["high"].tail(50).max()
    recent_low = candle["low"].tail(50).min()

    padding = (recent_high - recent_low) * 0.2

    ymin = recent_low - padding
    ymax = recent_high + padding

    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        yaxis=dict(range=[ymin, ymax]),
    )

    # crosshair 느낌
    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)

    st.plotly_chart(fig, use_container_width=True)

    # ======================
    # Raw Data
    # ======================

    with st.expander("📑 Raw Data"):
        st.dataframe(df)

else:
    st.warning("데이터 없음")

# ======================
# 자동 refresh
# ======================

if realtime:
    time.sleep(60)
    st.rerun()
