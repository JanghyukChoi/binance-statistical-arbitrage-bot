from fetch_data import get_usdt_perpetual_symbols, get_ohlcv_data
from cointegration import calculate_cointegration
import pandas as pd
from itertools import combinations
import time
from visualize import plot_cointegrated_pair


def run_cointegration_scan(symbols, price_data):
    results = []

    for sym1, sym2 in combinations(symbols, 2):
        try:
            s1 = price_data.get(sym1)
            s2 = price_data.get(sym2)

            # 둘 중 하나라도 데이터 없거나 길이 다르면 생략
            if s1 is None or s2 is None or len(s1) != len(s2):
                continue

            result = calculate_cointegration(s1, s2)

            if result['cointegration_flag'] == 1:
                result.update({
                    'symbol_1': sym1,
                    'symbol_2': sym2
                })
                results.append(result)

        except Exception as e:
            print(f"Error: {sym1}-{sym2}: {e}")
            continue

    return pd.DataFrame(results)

def export_results_to_csv(df, filename='cointegrated_pairs.csv'):
    df.sort_values(by=['p_value', 'zero_crossings'], ascending=[True, False]).to_csv(filename, index=False)
    print(f"[+] 저장 완료: {filename}")

if __name__ == "__main__":
    print("🔍 바이낸스 심볼 목록 가져오는 중...")
    symbols = get_usdt_perpetual_symbols()
    symbols = symbols[:50]  # 실전에서는 100개까지 가능

    print(f"총 {len(symbols)}개 심볼 수집 완료. OHLCV 수집 중...")
    price_data = {}
    for symbol in symbols:
        try:
            price_data[symbol] = get_ohlcv_data(symbol, interval='1h', limit=200)
            time.sleep(0.1)  # API 과부하 방지
        except Exception as e:
            print(f"{symbol} 데이터 수집 실패: {e}")

    print("코인통합 분석 시작...")
    results_df = run_cointegration_scan(symbols, price_data)

    print(f"총 {len(results_df)}개 쌍이 통합됨. CSV로 저장합니다.")
    export_results_to_csv(results_df)
    print(results_df.head())
