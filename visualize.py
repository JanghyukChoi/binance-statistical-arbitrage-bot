import matplotlib.pyplot as plt
import statsmodels.api as sm
from fetch_data import get_ohlcv_data

def calculate_spread(series1, series2, hedge_ratio):
    return series1 - hedge_ratio * series2

def plot_cointegrated_pair(symbol1, symbol2, interval='1h', limit=200):
    # 가격 데이터 로딩
    s1 = get_ohlcv_data(symbol1, interval=interval, limit=limit)
    s2 = get_ohlcv_data(symbol2, interval=interval, limit=limit)

    # 회귀로 hedge ratio 추정
    model = sm.OLS(s1, sm.add_constant(s2)).fit()
    hedge_ratio = model.params.iloc[1]

    # 스프레드 및 Z-score 계산
    spread = calculate_spread(s1, s2, hedge_ratio)
    zscore = (spread - spread.mean()) / spread.std()

    # 그래프 1: 종가
    plt.figure(figsize=(14, 6))
    plt.subplot(2, 1, 1)
    plt.plot(s1, label=symbol1)
    plt.plot(s2 * hedge_ratio, label=f"{symbol2} x {hedge_ratio:.2f}")
    plt.title(f'Price Chart: {symbol1} vs {symbol2}')
    plt.legend()

    # 그래프 2: Z-score
    plt.subplot(2, 1, 2)
    plt.plot(zscore, label='Z-score')
    plt.axhline(0, color='black', linestyle='--')
    plt.axhline(1.0, color='red', linestyle='--')
    plt.axhline(-1.0, color='green', linestyle='--')
    plt.axhline(2.0, color='red', linestyle=':')
    plt.axhline(-2.0, color='green', linestyle=':')
    plt.title('Z-score (mean reversion signal)')
    plt.legend()

    plt.tight_layout()
    plt.show()
