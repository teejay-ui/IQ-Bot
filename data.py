from ejtraderIQ import IQOption
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

email = os.environ.get('IQ_EMAIL')
password = os.environ.get('IQ_PASSWORD')

api = IQOption(email, password, 'DEMO')

def get_candles(asset, timeframe='M1', count=100):
    api.subscribe(asset, timeframe)
    candles = api.history(asset, timeframe, count)
    df = pd.DataFrame(candles)
    return df

# Test all assets we plan to trade
assets = ['EURUSD', 'GBPUSD', 'USDJPY', 'EURJPY', 'AUDUSD', 'EURGBP']

for asset in assets:
    try:
        df = get_candles(asset)
        print(f"{asset}: {len(df)} candles fetched - Latest close: {df['close'].iloc[-1]}")
    except Exception as e:
        print(f"{asset}: FAILED - {e}")