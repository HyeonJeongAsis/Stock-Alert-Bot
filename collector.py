import yfinance as yf
import pymysql
import time
import requests

# RDS 및 접속 정보는 기존 설정 유지
DB_CONFIG = {
    "host": "database-1.cqkity0bvpvd.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "mysqlmysql",
    "db": "stock_db",
}

# 감시할 종목 리스트와 목표가 설정
WATCH_LIST = {
    "005930.KS": 180000,  # 삼성전자
    "042660.KS": 150000,  # 한화오션 (예시 목표가)
}


def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d", interval="1m")
    if not data.empty:
        return data["Close"].iloc[-1]
    return None


def send_discord(msg):
    webhook_url = "https://discordapp.com/api/webhooks/1473898810391396480/w823-4YaAKf5J9u_2xxMYtjqd31IHAL10aqI8Xq7xVL0ciwC5DX5dFDivMFf9n7lIluz"
    requests.post(webhook_url, json={"content": msg})


def save_to_db(ticker, price):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO stock_prices (ticker, price) VALUES (%s, %s)"
            cursor.execute(sql, (ticker, price))
        conn.commit()
    finally:
        conn.close()


# 메인 루프
while True:
    for ticker, target_price in WATCH_LIST.items():
        try:
            current_price = get_current_price(ticker)
            if current_price:
                save_to_db(ticker, current_price)
                print(f"[{ticker}] 현재가: {current_price}")

                if current_price >= target_price:
                    send_discord(f"🚨 {ticker} 목표가 달성! 현재가: {current_price}")
        except Exception as e:
            print(f"{ticker} 에러 발생: {e}")

    time.sleep(60)  # 1분마다 전체 종목 갱신
