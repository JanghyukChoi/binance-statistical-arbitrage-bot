from binance.client import Client
import pandas as pd

def get_ohlcv_data(symbol: str, interval: str = '1h', limit: int = 200) -> pd.Series:
    """
    바이낸스 선물 OHLCV 데이터에서 'close' 가격만 추출하여 Series로 반환
    """
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    closes = [float(entry[4]) for entry in klines]  # 4번째가 종가(close)
    return pd.Series(closes, name=symbol)

client = Client()

def get_usdt_perpetual_symbols():
    exchange_info = client.futures_exchange_info()
    symbols = []

    for s in exchange_info['symbols']:
        if (
            s['quoteAsset'] == 'USDT'
            and s['contractType'] == 'PERPETUAL'
            and s['status'] == 'TRADING'
        ):
            symbols.append(s['symbol'])

    return symbols

if __name__ == "__main__":
    symbols = get_usdt_perpetual_symbols()
    sample_symbol = symbols[0]  # 예: BTCUSDT

    close_prices = get_ohlcv_data(sample_symbol)
    print(f"[{sample_symbol}] 종가 데이터 ({len(close_prices)}개):")
    print(close_prices.head())