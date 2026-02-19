import streamlit as st
import pandas as pd
import pymysql
import time
import plotly.graph_objects as go

# ======================
# 설정
# ======================

st.set_page_config(page_title="HTS PRO", layout="wide")

st.title("🔥 Let's GO HTS PRO")

DB_CONFIG = {
    "host": "database-1.cqkity0bvpvd.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "mysqlmysql",
    "db": "stock_db",
}

TICKER_NAMES = {
    "005930.KS": "삼성전자",
    "042660.KS": "한화오션",
}

NAME_TO_TICKER = {v: k for k, v in TICKER_NAMES.items()}

# ======================
# DB
# ======================


def db_conn():
    return pymysql.connect(**DB_CONFIG)


@st.cache_data(ttl=10)
def get_data(ticker):

    conn = db_conn()

    query = """
    SELECT *
    FROM stock_prices
    WHERE ticker=%s
    ORDER BY created_at DESC
    LIMIT 1000
    """

    df = pd.read_sql(query, conn, params=(ticker,))
    conn.close()

    return df


def get_global_alert():

    conn = db_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT alert_enabled FROM bot_settings LIMIT 1")
    result = cursor.fetchone()

    conn.close()

    return bool(result[0])


def set_global_alert(state):

    conn = db_conn()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE bot_settings SET alert_enabled=%s WHERE id=1",
        (state,),
    )

    conn.commit()
    conn.close()


# ======================
# Sidebar
# ======================

st.sidebar.header("📊 종목 선택")

selected_name = st.sidebar.selectbox(
    "종목",
    list(NAME_TO_TICKER.keys()),
)

target_stock = NAME_TO_TICKER[selected_name]
stock_name = selected_name

realtime = st.sidebar.checkbox("🔥 실시간 모드", True)

# ======================
# ALERT CONTROL
# ======================

st.sidebar.markdown("---")
st.sidebar.subheader("🚨 ALERT CONTROL")

# 최초 한번만 DB에서 가져오기
if "alert_state" not in st.session_state:
    st.session_state.alert_state = get_global_alert()

new_alert = st.sidebar.toggle(
    "알람 ON/OFF",
    value=st.session_state.alert_state,
)

if new_alert != st.session_state.alert_state:

    set_global_alert(new_alert)

    st.session_state.alert_state = new_alert

    st.sidebar.success("알람 상태 변경됨")

# ======================
# 데이터
# ======================

df = get_data(target_stock)

if not df.empty:

    df["created_at"] = (
        pd.to_datetime(df["created_at"])
        .dt.tz_localize("UTC")
        .dt.tz_convert("Asia/Seoul")
    )

    candle = df.resample("1min", on="created_at").agg(
        {"price": ["first", "max", "min", "last", "count"]}
    )

    candle.columns = ["open", "high", "low", "close", "volume"]
    candle = candle.dropna()

    candle["ma5"] = candle["close"].rolling(5).mean()
    candle["ma20"] = candle["close"].rolling(20).mean()
    candle["ma60"] = candle["close"].rolling(60).mean()

    latest = candle["close"].iloc[-1]
    prev = candle["close"].iloc[-2]

    change = latest - prev
    pct = (change / prev) * 100

    color = "red" if change >= 0 else "blue"
    arrow = "▲" if change >= 0 else "▼"

    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        st.markdown(f"## {stock_name} ({target_stock})")

    with col2:
        st.markdown(
            f"<h1 style='color:{color}'>{latest:,.0f}</h1>",
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"<h2 style='color:{color}'>{arrow} {pct:.2f}%</h2>",
            unsafe_allow_html=True,
        )

    # 캔들차트

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

    fig.add_trace(go.Scatter(x=candle.index, y=candle.ma5, name="MA5"))
    fig.add_trace(go.Scatter(x=candle.index, y=candle.ma20, name="MA20"))
    fig.add_trace(go.Scatter(x=candle.index, y=candle.ma60, name="MA60"))

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

    # 거래량

    vol_fig = go.Figure()
    vol_fig.add_bar(x=candle.index, y=candle.volume)
    vol_fig.update_layout(template="plotly_dark", height=200)

    st.plotly_chart(vol_fig, use_container_width=True)

    with st.expander("📑 체결 데이터"):
        st.dataframe(df)

else:
    st.warning("데이터 없음")

# ======================
# AUTO REFRESH
# ======================

if realtime:
    time.sleep(60)
    st.rerun()
