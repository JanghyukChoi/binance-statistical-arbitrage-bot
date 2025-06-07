import pandas as pd
import numpy as np
import os
import json
import requests
from binance.client import Client

# ========== [설정] ==========
from dotenv import load_dotenv

# == .env file ==
load_dotenv()

# API key
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


client = Client()

CSV_PATH = "top5_cointegrated_pairs.csv"
POSITION_FILE = "open_positions.json"

# ========== [텔레그램 전송] ==========
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"[텔레그램 응답 오류] 코드: {response.status_code}, 응답: {response.text}")
    except Exception as e:
        print(f"[텔레그램 요청 실패] {e}")

# ========== [포지션 상태 저장/불러오기] ==========
def load_positions():
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, "r") as f:
            return json.load(f)
    return {}

def save_positions(positions):
    with open(POSITION_FILE, "w") as f:
        json.dump(positions, f)

# ========== [실시간 데이터 수집] ==========
def get_price_series(symbol, interval='1h', limit=200):
    try:
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        closes = [float(entry[4]) for entry in klines]
        return pd.Series(closes)
    except Exception as e:
        print(f"[데이터 오류] {symbol}: {e}")
        return None

# ========== [Z-score 계산] ==========
def calculate_zscore(y, x, hedge_ratio):
    spread = y - hedge_ratio * x
    zscore = (spread - spread.mean()) / spread.std()
    return zscore.iloc[-1]

# ========== [시그널 생성 로직] ==========
def generate_signals(df):
    positions = load_positions()
    updated_positions = {}
    ignored_list = []  # 아무 시그널도 없고 포지션도 없었던 쌍들

    for _, row in df.iterrows():
        sym1 = row['symbol_1']
        sym2 = row['symbol_2']
        hedge_ratio = row['hedge_ratio']
        key = f"{sym1}_{sym2}"

        s1 = get_price_series(sym1)
        s2 = get_price_series(sym2)
        if s1 is None or s2 is None or len(s1) != len(s2):
            continue

        z = calculate_zscore(s1, s2, hedge_ratio)
        msg = f"[{sym1} - {sym2}]\nZ-score: {round(z, 3)}\n"

        if z > 2:
            if key not in positions:
                send_telegram(msg + "📉 진입 신호: SHORT 첫번째 / LONG 두번째")
            updated_positions[key] = "short"

        elif z < -2:
            if key not in positions:
                send_telegram(msg + "📈 진입 신호: LONG 첫번째 / SHORT 두번째")
            updated_positions[key] = "long"

        elif abs(z) < 0.5 and key in positions:
            send_telegram(msg + "✅ 포지션 종료 시그널: 평균 회귀 도달")
            # 포지션 제거 (종료)

        elif key in positions:
            updated_positions[key] = positions[key]  # 기존 포지션 유지
                
                # 완전 무시된 쌍 (진입X, 청산X, 포지션X)
        elif key not in positions:
            ignored_list.append(f"- {sym1} - {sym2} | Z-score: {round(z, 3)}")

    # 무시된 쌍 전체를 한 번에 전송
    if ignored_list:
        ignored_msg = "🔍 신호도, 포지션도 없는 감시중인 쌍 :\n" + "\n".join(ignored_list)
        send_telegram(ignored_msg)

    save_positions(updated_positions)

# ========== [실행] ==========
if __name__ == "__main__":
    try:
        df = pd.read_csv(CSV_PATH)
        df = df[df['hedge_ratio'].abs() < 10000]  # 극단값 필터링
        generate_signals(df)
    except Exception as e:
        print(f"[실행 오류] {e}")
        send_telegram(f"❌ 시그널 생성 실패: {e}")
