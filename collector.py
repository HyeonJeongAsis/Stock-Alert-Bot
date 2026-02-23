import yfinance as yf
import pymysql
import time
import requests

# ======================
# 설정
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

WEBHOOK = "YOUR_WEBHOOK"

# ======================
# DB
# ======================


def db_conn():
    return pymysql.connect(**DB_CONFIG)


def get_global_alert():

    conn = db_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT alert_enabled FROM bot_settings LIMIT 1")
    result = cursor.fetchone()

    conn.close()

    return bool(result[0])
    


# ======================
# 가격
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

    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO stock_prices (ticker, price) VALUES (%s,%s)",
            (ticker, price),
        )

    conn.commit()
    conn.close()


# ======================
# Discord
# ======================


def send_discord(msg):

    requests.post(WEBHOOK, json={"content": msg})


# ======================
# 메인 루프
# ======================

print("🔥 COLLECTOR STARTED")

while True:

    alert_enabled = get_global_alert()

    print("GLOBAL ALERT:", alert_enabled)

    for ticker, target_price in WATCH_LIST.items():

        try:

            price = get_current_price(ticker)

            if price:

                save_to_db(ticker, price)

                # 🔥 여기 핵심
                if alert_enabled:

                    if price >= target_price:

                        send_discord(f"🚨 {ticker} 목표가 돌파!\n현재가: {price}")

                print(ticker, price)

        except Exception as e:

            print("ERROR:", e)

    time.sleep(60)
