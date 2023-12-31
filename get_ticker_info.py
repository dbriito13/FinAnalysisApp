import pandas as pd
import requests
import io


class TickerFetcher:
    def __init__(self, ticker) -> None:
        self.ticker = ticker

    def fetch_prices(self, ticker):
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        url = "https://query1.finance.yahoo.com/v7/finance/download/"
        url += str(ticker)
        url += "?period1=1030060800&period2=1684368000&interval=1d&events="
        "history&includeAdjustedClose=true"
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None
        pds = pd.read_csv(io.StringIO(r.text), index_col=0, parse_dates=True)
        return pds

    def get_ticker_info(self, ticker):
        '''
        Given a ticker prices calculates it's statistics, including:
        3MT graph of volume and closing price, monthly rolling mean .
        '''
        df = self.fetch_prices(ticker)
        if df is None:
            raise Exception

        # Add monthly rolling mean for volume and closing prices
        df["rolling_price_1M"] = df["Adj Close"].rolling(30).mean()
        df["rolling_volume_1M"] = df["Volume"].rolling(30).mean()

        prev_close = df["Adj Close"].iloc[-2]
        daily_change = ((df["Adj Close"].iloc[-1] -
                        df["Adj Close"].iloc[-2])
                        / df["Adj Close"].iloc[-2]) * 100.0

        prev_vol = df["Volume"].iloc[-2]
        daily_change_vol = ((df["Volume"].iloc[-1] -
                        df["Volume"].iloc[-2])
                        / df["Volume"].iloc[-2]) * 100.0

        # Limit number of decimal places to 4
        prev_close = "{:.4f}".format(prev_close)
        daily_change = "{:.4f}".format(daily_change)

        return prev_close, daily_change, prev_vol, daily_change_vol, df
