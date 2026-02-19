import streamlit as st
import pandas as pd
import pymysql
import time

# =========================
# 페이지 설정
# =========================
st.set_page_config(
    page_title="실시간 주식 모니터링 대시보드",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# 스타일 (진짜 트레이딩 느낌)
# =========================
st.markdown(
    """
<style>
.big-font {
    font-size:28px !important;
    font-weight:700;
}

.price-up {
    color:#00c853;
    font-weight:bold;
    font-size:26px;
}

.price-down {
    color:#ff1744;
    font-weight:bold;
    font-size:26px;
}

.metric-card {
    background-color:#111;
    padding:20px;
    border-radius:10px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("📈 Stock-Watch PRO Dashboard")

# =========================
# DB 설정
# =========================
DB_CONFIG = {
    "host": "database-1.cqkity0bvpvd.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "mysqlmysql",
    "db": "stock_db",
}


# =========================
# 데이터 가져오기
# =========================
@st.cache_data(ttl=3)  # 3초 캐싱 = 실시간 느낌
def get_data(ticker):

    conn = pymysql.connect(**DB_CONFIG)

    query = """
    SELECT *
    FROM stock_prices
    WHERE ticker=%s
    ORDER BY created_at DESC
    LIMIT 100
    """

    df = pd.read_sql(query, conn, params=[ticker])

    conn.close()

    return df


# =========================
# 사이드바
# =========================
st.sidebar.header("⚙️ Settings")

target_stock = st.sidebar.selectbox("종목 선택", ["005930.KS", "042660.KS"])

auto_refresh = st.sidebar.checkbox("🔥 실시간 모드", value=True)


# =========================
# 데이터 로드
# =========================
data = get_data(target_stock)

if not data.empty:

    data = data.sort_values("created_at")

    latest_price = data["price"].iloc[-1]
    prev_price = data["price"].iloc[-2] if len(data) > 1 else latest_price

    # 상승 하락 판단
    if latest_price > prev_price:
        price_class = "price-up"
        arrow = "▲"
    elif latest_price < prev_price:
        price_class = "price-down"
        arrow = "▼"
    else:
        price_class = ""
        arrow = "-"

    # =========================
    # 상단 가격 UI
    # =========================
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f'<div class="big-font">{target_stock}</div>', unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="{price_class}">{latest_price:.2f} {arrow}</div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.metric(
            label="변동",
            value=f"{latest_price:.2f}",
            delta=f"{latest_price-prev_price:.2f}",
        )

    # =========================
    # 차트
    # =========================
    st.subheader("📊 실시간 가격 차트")

    chart_data = data.set_index("created_at")[["price"]]

    st.line_chart(chart_data, use_container_width=True)

    # =========================
    # 데이터 테이블
    # =========================
    with st.expander("📑 Raw Data"):
        st.dataframe(data, use_container_width=True)

else:
    st.warning("데이터 없음 — collector 확인")

# =========================
# 🔥 자동 새로고침 (애니메이션 느낌)
# =========================
if auto_refresh:
    time.sleep(60)
    st.rerun()
