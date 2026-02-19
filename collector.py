import yfinance as yf
import pymysql
import time
import requests

# ======================
# DB 설정
# ======================

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

WEBHOOK_URL = "YOUR_WEBHOOK"

# ======================
# DB 연결
# ======================


def db_conn():
    return pymysql.connect(**DB_CONFIG)


# ======================
# 글로벌 알람 ON/OFF (웹에서 제어)
# ======================


def is_alert_enabled():
    conn = db_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT alert_enabled FROM bot_settings LIMIT 1")
            result = cursor.fetchone()
            return result[0] if result else False
    finally:
        conn.close()


# ======================
# 종목별 알람 상태
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


def set_alert_state(ticker, state):
    conn = db_conn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE alert_status SET alerted=%s WHERE ticker=%s",
                (state, ticker),
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
# Discord 알람
# ======================


def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})


# ======================
# MAIN LOOP
# ======================

print("🔥 REAL TRADING BOT STARTED")

while True:

    try:

        # 🔥 웹에서 알람 OFF 하면 여기서 차단
        if not is_alert_enabled():
            print("🚫 ALERT OFF (웹에서 비활성화됨)")

        for ticker, target_price in WATCH_LIST.items():

            price = get_current_price(ticker)

            if price:

                save_to_db(ticker, price)

                print(f"{ticker} {price}")

                # 글로벌 알람 ON일 때만 실행
                if is_alert_enabled():

                    alerted = get_alert_state(ticker)

                    if price >= target_price and not alerted:

                        send_discord(f"🚨 {ticker} 목표가 돌파!\n현재가: {price}")

                        set_alert_state(ticker, True)

                    elif price < target_price:

                        set_alert_state(ticker, False)

    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)
