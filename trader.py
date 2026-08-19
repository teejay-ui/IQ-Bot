from ejtraderIQ import IQOption
from dotenv import load_dotenv
from strategies import get_signal
import pandas as pd
import requests
import os
import csv
import time
from datetime import datetime

load_dotenv()

# Connect to IQ Option
api = IQOption(os.environ.get('IQ_EMAIL'), os.environ.get('IQ_PASSWORD'), 'DEMO')

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Assets to trade
ASSETS = ['EURUSD', 'GBPUSD', 'USDJPY', 'EURJPY', 'AUDUSD', 'EURGBP']

# Performance tracker
performance = {}
for asset in ASSETS:
    performance[asset] = {'wins': 0, 'losses': 0, 'win_rate': 0.0, 'status': 'active'}

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open('bot_log.txt', 'a', encoding='utf-8') as f:
        f.write(entry + '\n')

def save_trade(asset, signal, amount, result, profit):
    file = 'trades.csv'
    file_exists = os.path.exists(file)
    with open(file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'asset', 'signal', 'amount', 'result', 'profit'])
        writer.writerow([datetime.now(), asset, signal, amount, result, profit])

def update_performance(asset, result):
    if result == 'WIN':
        performance[asset]['wins'] += 1
    else:
        performance[asset]['losses'] += 1

    total = performance[asset]['wins'] + performance[asset]['losses']
    if total > 0:
        performance[asset]['win_rate'] = performance[asset]['wins'] / total

    # Update status based on win rate
    if total >= 20:
        win_rate = performance[asset]['win_rate']
        if win_rate >= 0.60:
            performance[asset]['status'] = 'active'
        elif win_rate >= 0.50:
            performance[asset]['status'] = 'cautious'
        else:
            performance[asset]['status'] = 'paused'

def get_trade_amount(asset):
    balance = api.balance()
    status = performance[asset]['status']
    if status == 'active':
        return round(balance * 0.05, 2)   # 5% aggressive
    elif status == 'cautious':
        return round(balance * 0.02, 2)   # 2% cautious
    else:
        return 0                           # paused

def get_best_signal():
    best_asset = None
    best_score = 0

    for asset in ASSETS:
        if performance[asset]['status'] == 'paused':
            log(f"{asset} is paused - skipping")
            continue

        try:
            api.subscribe(asset, 'M1')
            candles = api.history(asset, 'M1', 100)
            df = pd.DataFrame(candles)
            signal = get_signal(df)

            if signal != 'HOLD':
                win_rate = performance[asset]['win_rate']
                score = win_rate if win_rate > 0 else 0.5
                if score > best_score:
                    best_score = score
                    best_asset = (asset, signal)

        except Exception as e:
            log(f"Error scanning {asset}: {e}")

    return best_asset

def run_trade():
    balance = api.balance()
    log(f"Balance: ${balance}")
    log("Scanning all pairs...")

    result = get_best_signal()

    if result is None:
        log("No strong signals found - HOLD")
        send_telegram(f"Scan complete - No opportunity found\nBalance: ${balance}")
        return

    asset, signal = result
    amount = get_trade_amount(asset)

    if amount == 0:
        log(f"{asset} is paused")
        return

    log(f"Trading {asset} - {signal} - Amount: ${amount}")

    # Place trade with 1 minute expiry
    trade_id, status = api.buy(asset, amount, signal, 1)

    if status:
        log(f"Trade placed: {asset} {signal} ${amount}")
        send_telegram(f"TRADE PLACED\nAsset: {asset}\nDirection: {signal}\nAmount: ${amount}\nBalance: ${balance}")

        # Wait for trade result
        time.sleep(65)
        result = api.check_win(trade_id)

        if result > 0:
            log(f"WIN: +${result}")
            send_telegram(f"RESULT: WIN\nAsset: {asset}\nProfit: +${result}\nBalance: ${api.balance()}")
            update_performance(asset, 'WIN')
            save_trade(asset, signal, amount, 'WIN', result)
        else:
            log(f"LOSS: -${amount}")
            send_telegram(f"RESULT: LOSS\nAsset: {asset}\nLoss: -${amount}\nBalance: ${api.balance()}")
            update_performance(asset, 'LOSS')
            save_trade(asset, signal, amount, 'LOSS', -amount)
    else:
        log(f"Trade failed to place for {asset}")

# Bot loop
log("Bot started")
send_telegram("IQ Option Bot Started\nDemo Balance: $10,000\nScanning 6 pairs with 8 strategies")

while True:
    try:
        run_trade()
        log("-" * 60)
        time.sleep(60)
    except Exception as e:
        log(f"Error: {e}")
        send_telegram(f"Bot Error: {e}")
        time.sleep(30)