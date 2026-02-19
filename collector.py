import yfinance as yf
import pymysql
import time
import requests

# ======================
# 설정
# ======================

ENABLE_ALERT = True

DB_CONFIG = {
    "host": "database-1.cqkity0bvpvd.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "mysqlmysql",
    "db": "stock_db",
}

WATCH_LIST = {
    "005930.KS": 180000,
    "042660.KS": 150000,
}

# ======================
# DB 연결
# ======================


def db_conn():
    return pymysql.connect(**DB_CONFIG)


# ======================
# 알람 상태 가져오기
# ======================


def get_alert_state(ticker):
    conn = db_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT alerted FROM alert_status WHERE ticker=%s", (ticker,)
            )
            result = cursor.fetchone()
            return result[0] if result else False
    finally:
        conn.close()


# ======================
# 알람 상태 저장
# ======================


def set_alert_state(ticker, state):
    conn = db_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE alert_status SET alerted=%s WHERE ticker=%s", (state, ticker)
            )
        conn.commit()
    finally:
        conn.close()


# ======================
# 가격 가져오기
# ======================


def get_current_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d", interval="1m")
    if not data.empty:
        return data["Close"].iloc[-1]
    return None


# ======================
# DB 저장
# ======================


def save_to_db(ticker, price):
    conn = db_conn()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO stock_prices (ticker, price) VALUES (%s, %s)"
            cursor.execute(sql, (ticker, price))
        conn.commit()
    finally:
        conn.close()


# ======================
# Discord
# ======================


def send_discord(msg):
    webhook_url = "YOUR_WEBHOOK"
    requests.post(webhook_url, json={"content": msg})


# ======================
# 메인 루프
# ======================

print("🔥 REAL TRADING BOT STARTED")

while True:

    for ticker, target_price in WATCH_LIST.items():

        try:
            price = get_current_price(ticker)

            if price:

                save_to_db(ticker, price)

                alerted = get_alert_state(ticker)

                if ENABLE_ALERT:

                    if price >= target_price and not alerted:

                        send_discord(f"🚨 {ticker} 목표가 돌파!\n현재가: {price}")

                        set_alert_state(ticker, True)

                    elif price < target_price:

                        set_alert_state(ticker, False)

                print(ticker, price)

        except Exception as e:
            print("ERROR:", e)

    time.sleep(60)
