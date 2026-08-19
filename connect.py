from ejtraderIQ import IQOption
from dotenv import load_dotenv
import os

load_dotenv()

email = os.environ.get('IQ_EMAIL')
password = os.environ.get('IQ_PASSWORD')

print("Connecting to IQ Option...")
api = IQOption(email, password, 'DEMO')

balance = api.balance()
print(f"Connected successfully!")
print(f"Demo Balance: ${balance}")