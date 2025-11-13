import upstox_client
from upstox_client.rest import ApiException
from datetime import datetime, timedelta
import json
import pandas as pd

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


def get_price(symbol_to_find, ex, target_date=None):
    instrument_key = get_instrument_key(symbol_to_find, ex)
    # Your access token from the previous step
    YOUR_ACCESS_TOKEN = 'eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI0TkNXMjgiLCJqdGkiOiI2OTE0OWYxYmI1OWI0OTY0ODA2ZDg3NDAiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc2Mjk1OTEzMSwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzYyOTg0ODAwfQ.qUZBsBEp6IdUH_kLuPR2NYJlvkKDdMCn_OjP90Xgs60' # Keep your token

    configuration = upstox_client.Configuration()
    configuration.access_token = YOUR_ACCESS_TOKEN
    api_instance = upstox_client.HistoryApi(upstox_client.ApiClient(configuration))

    api_version = '2.0'
    if target_date is None:
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

        if api_response.data.candles:
            candle = api_response.data.candles[0]
            closing_price = candle[4] # Index 4 is the 'close' price

            print(f"The closing price for {instrument_key} on {target_date} was: {closing_price}")
            return closing_price

        else:
            print(f"No data found for {instrument_key} on {target_date}.")
            print("This could be a trading holiday.")
            return None

    except ApiException as e:
        print(f"Exception when calling HistoryApi->get_historical_candle_data1: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
