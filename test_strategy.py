from ejtraderIQ import IQOption
from dotenv import load_dotenv
from strategies import get_signal
import pandas as pd
import os

load_dotenv()

api = IQOption(os.environ.get('IQ_EMAIL'), os.environ.get('IQ_PASSWORD'), 'DEMO')

assets = ['EURUSD', 'GBPUSD', 'USDJPY', 'EURJPY', 'AUDUSD', 'EURGBP']

for asset in assets:
    try:
        api.subscribe(asset, 'M1')
        candles = api.history(asset, 'M1', 100)
        df = pd.DataFrame(candles)
        print(f"\n{asset}:")
        signal = get_signal(df)
        print(f"Signal: {signal}")
    except Exception as e:
        print(f"{asset}: ERROR - {e}")