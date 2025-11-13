import upstox_client
from upstox_client.rest import ApiException
from datetime import datetime, timedelta
import json
import pandas as pd


def get_price(instrument_key):
    # Your access token from the previous step
    YOUR_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI0TkNXMjgiLCJqdGkiOiI2OTE0OWYxYmI1OWI0OTY0ODA2ZDg3NDAiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2Mjk1OTEzMSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyOTg0ODAwfQ.qUZBsBEp6IdUH_kLuPR2NYJlvkKDdMCn_OjP90Xgs60' # Keep your token

    configuration = upstox_client.Configuration()
    configuration.access_token = YOUR_ACCESS_TOKEN
    api_instance = upstox_client.HistoryApi(upstox_client.ApiClient(configuration))

    api_version = '2.0'
    target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        # 3. Call the historical data method
        api_response = api_instance.get_historical_candle_data1(
            instrument_key=instrument_key,
            interval='day',      # '1d' for one day
            to_date=target_date,  # Set 'to' and 'from' to the same date
            from_date=target_date,
            api_version=api_version
        )

        # --- Pro-tip: Uncomment this to see the full response ---
        # print(api_response.data)

        # 4. The data is inside a list called 'candles'
        # Each candle is a list: [timestamp, open, high, low, close, volume, OI]

        # Get the first (and only) candle from the list
        if api_response.data.candles:
            candle = api_response.data.candles[0]
            closing_price = candle[4] # Index 4 is the 'close' price

            print(f"The closing price for {instrument_key} on {target_date} was: {closing_price}")
        else:
            print(f"No data found for {instrument_key} on {target_date}.")
            print("This could be a trading holiday.")

    except ApiException as e:
        print(f"Exception when calling HistoryApi->get_historical_candle_data1: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_instrument_key(trading_symbol, exchange):

    try:

        with open('complete.json', 'rt', encoding='utf-8') as f:
            data = json.load(f)

        df = pd.DataFrame(data)

        if exchange == 'NSE':
            segment = 'NSE_EQ' # NSE_EQ for equities
        elif exchange == 'BSE':
            segment = 'BSE_EQ' # BSE_EQ for equities
        else:
            segment = exchange # For indices like 'NSE_INDEX'

        result = df[
            (df['trading_symbol'] == trading_symbol) &
            (df['segment'] == segment)
            ]

        # 6. Get the key
        if not result.empty:
            instrument_key = result.iloc[0]['instrument_key']
            return instrument_key
        else:
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


symbol_to_find = input('Enter stock symbol to find: ')
ex = input('Enter exchange code: ')
ikey = get_instrument_key(symbol_to_find, ex)
if ikey:
    print(f"\nFound Key for {symbol_to_find} ({ex}): {ikey}")
else:
    print(f"\nCould not find key for {symbol_to_find} ({ex}).")

get_price(ikey)