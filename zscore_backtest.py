# 백테스트 준비용 스크립트: zscore_backtest.py
'''
Z > 2 → 숏 진입
Z < -2 → 롱 진입
Z ≈ 0 → 청산
'''
import pandas as pd
import statsmodels.api as sm
from fetch_data import get_ohlcv_data
from cointegration import calculate_spread


def get_backtest_data(symbol1, symbol2, interval='1h', limit=200):
    s1 = get_ohlcv_data(symbol1, interval, limit)
    s2 = get_ohlcv_data(symbol2, interval, limit)

    model = sm.OLS(s1, sm.add_constant(s2)).fit()
    hedge_ratio = model.params.iloc[1]

    spread = calculate_spread(s1, s2, hedge_ratio)
    zscore = (spread - spread.mean()) / spread.std()

    df = pd.DataFrame({
        f'{symbol1}_price': s1,
        f'{symbol2}_price': s2,
        'spread': spread,
        'zscore': zscore
    })
    return df


def simulate_strategy(df, entry_threshold=2.0, exit_threshold=0.0):
    position = 0  # 1: long, -1: short, 0: no position
    pnl = []
    entry_price_s1 = entry_price_s2 = 0
    hedge_ratio = df['spread'].iloc[-1] / (df.iloc[:, 1] - df.iloc[:, 0]).mean()

    for i in range(1, len(df)):
        z = df['zscore'].iloc[i]
        p1 = df.iloc[i, 0]
        p2 = df.iloc[i, 1]

        if position == 0:
            if z > entry_threshold:
                position = -1
                entry_price_s1 = p1
                entry_price_s2 = p2
            elif z < -entry_threshold:
                position = 1
                entry_price_s1 = p1
                entry_price_s2 = p2
        elif position == 1:
            if z >= exit_threshold:
                pnl.append((p1 - entry_price_s1) - hedge_ratio * (p2 - entry_price_s2))
                position = 0
        elif position == -1:
            if z <= -exit_threshold:
                pnl.append((entry_price_s1 - p1) - hedge_ratio * (entry_price_s2 - p2))
                position = 0

    return pnl


def export_backtest_csv(symbol1, symbol2, filename='backtest_data.csv'):
    df = get_backtest_data(symbol1, symbol2)
    df.to_csv(filename)
    print(f"[+] 백테스트용 CSV 저장 완료: {filename}")
    pnl = simulate_strategy(df)
    print(f"[+] 전략 수익률 샘플: 총 {len(pnl)}회 거래, 누적 수익: {round(sum(pnl), 4)}")


if __name__ == '__main__':
    export_backtest_csv('BTCUSDT', 'ETHUSDT')
