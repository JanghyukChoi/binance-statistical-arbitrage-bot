import pandas as pd
import statsmodels.api as sm
import numpy as np

# 로컬 테스트용 데이터 수집 함수 (실제 바이낸스 fetch_data 대체)
def get_ohlcv_data(symbol: str, interval: str = '1h', limit: int = 200):
    np.random.seed(hash(symbol) % 1000)
    prices = np.cumsum(np.random.randn(limit)) + 100
    return pd.Series(prices, name=symbol)

# 스프레드 계산
def calculate_spread(series1, series2, hedge_ratio):
    return series1 - hedge_ratio * series2

# 백테스트 데이터 생성
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

# 전략 시뮬레이션
def simulate_strategy(df, entry_threshold=2.0, exit_threshold=0.0):
    position = 0
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

# CSV 로드 후 전체 백테스트
def backtest_from_csv(csv_path):
    df_pairs = pd.read_csv(csv_path)
    summary = []

    for _, row in df_pairs.iterrows():
        s1 = row['symbol_1']
        s2 = row['symbol_2']
        try:
            df = get_backtest_data(s1, s2)
            pnl = simulate_strategy(df)
            summary.append({
                'pair': f"{s1}-{s2}",
                'trades': len(pnl),
                'total_pnl': round(sum(pnl), 4),
                'mean_pnl': round(np.mean(pnl), 4) if pnl else 0,
                'win_rate': round(np.mean([1 if x > 0 else 0 for x in pnl]), 2) if pnl else 0
            })
        except Exception as e:
            summary.append({
                'pair': f"{s1}-{s2}",
                'error': str(e)
            })

    return pd.DataFrame(summary)

# 실행
results = backtest_from_csv('cointegrated_pairs.csv')
results.head()
