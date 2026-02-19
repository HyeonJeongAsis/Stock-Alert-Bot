import streamlit as st
import pandas as pd
import pymysql

# 상단 제목
st.set_page_config(page_title="Stock-Watch Dashboard", layout="wide")
st.title("📈 Stock-Watch 실시간 대시보드")

# DB 접속 설정 (collector.py와 동일하게 설정)
DB_CONFIG = {
    "host": "database-1.cqkity0bvpvd.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "mysqlmysql",
    "db": "stock_db",
}


def get_data(ticker):
    conn = pymysql.connect(**DB_CONFIG)
    # 특정 종목(ticker)만 필터링해서 최근 100개 가져오기
    query = f"SELECT * FROM stock_prices WHERE ticker = '{ticker}' ORDER BY created_at DESC LIMIT 100"
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# 사이드바에서 종목 선택
st.sidebar.header("설정")
target_stock = st.sidebar.selectbox("조회할 종목", ["005930.KS", "042660.KS"])

# 데이터 불러오기
data = get_data(target_stock)

if not data.empty:
    # 차트 출력
    st.subheader(f"📊 {target_stock} 최근 시세 현황")
    chart_data = data.set_index("created_at")[["price"]]
    st.line_chart(chart_data)

    # 테이블 출력
    st.subheader("📑 상세 데이터")
    st.dataframe(data, use_container_width=True)
else:
    st.warning(
        "데이터가 아직 수집되지 않았습니다. collector.py가 작동 중인지 확인하세요."
    )
