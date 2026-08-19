import pandas as pd
import ta

def calculate_indicators(df):
    # Strategy 1: RSI
    df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

    # Strategy 2: Bollinger Bands
    bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()

    # Strategy 3: MACD
    macd = ta.trend.MACD(df['close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    # Strategy 4: EMA Crossover
    df['EMA_10'] = ta.trend.EMAIndicator(df['close'], window=10).ema_indicator()
    df['EMA_30'] = ta.trend.EMAIndicator(df['close'], window=30).ema_indicator()

    # Strategy 5: Stochastic
    stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
    df['STOCH_k'] = stoch.stoch()
    df['STOCH_d'] = stoch.stoch_signal()

    # Strategy 6: CCI
    df['CCI'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close']).cci()

    # Strategy 7: Williams %R
    df['WILLIAMS'] = ta.momentum.WilliamsRIndicator(df['high'], df['low'], df['close']).williams_r()

    # Strategy 8: ADX
    adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'])
    df['ADX'] = adx.adx()
    df['ADX_pos'] = adx.adx_pos()
    df['ADX_neg'] = adx.adx_neg()

    return df

def get_signal(df):
    df = calculate_indicators(df)
    last = df.iloc[-1]

    buy_signals = 0
    sell_signals = 0

    # Strategy 1: RSI
    if last['RSI'] < 30:
        buy_signals += 1
    elif last['RSI'] > 70:
        sell_signals += 1

    # Strategy 2: Bollinger Bands
    if last['close'] < last['BB_lower']:
        buy_signals += 1
    elif last['close'] > last['BB_upper']:
        sell_signals += 1

    # Strategy 3: MACD
    if last['MACD'] > last['MACD_signal']:
        buy_signals += 1
    elif last['MACD'] < last['MACD_signal']:
        sell_signals += 1

    # Strategy 4: EMA Crossover
    if last['EMA_10'] > last['EMA_30']:
        buy_signals += 1
    elif last['EMA_10'] < last['EMA_30']:
        sell_signals += 1

    # Strategy 5: Stochastic
    if last['STOCH_k'] < 20:
        buy_signals += 1
    elif last['STOCH_k'] > 80:
        sell_signals += 1

    # Strategy 6: CCI
    if last['CCI'] < -100:
        buy_signals += 1
    elif last['CCI'] > 100:
        sell_signals += 1

    # Strategy 7: Williams %R
    if last['WILLIAMS'] < -80:
        buy_signals += 1
    elif last['WILLIAMS'] > -20:
        sell_signals += 1

    # Strategy 8: ADX — confirms trend strength
    trend_strong = last['ADX'] > 25

    total_signals = buy_signals + sell_signals
    print(f"Buy signals: {buy_signals}/8 | Sell signals: {sell_signals}/8 | ADX trend strong: {trend_strong}")

    # Need majority of signals + strong trend to trade
    if buy_signals >= 5 and trend_strong:
        return 'CALL'
    elif sell_signals >= 5 and trend_strong:
        return 'PUT'
    else:
        return 'HOLD'