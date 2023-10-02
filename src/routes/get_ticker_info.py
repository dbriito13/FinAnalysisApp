import pandas as pd
import requests
import io
import yfinance as yf


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
        pds = pd.read_csv(io.StringIO(r.text), index_col=0, parse_dates=True)
        return pds

    def fetch_metrics(self, ticker):
        '''
        Given a ticker calculates it's earnings per share from yfinance 
        and P/E from this.
        '''
        eps_ttm = yf.Ticker(ticker).info['trailingEps']
        pe_ratio = yf.Ticker(ticker).info['trailingPE']

        return eps_ttm, pe_ratio

    def get_ticker_info(self, ticker):
        '''
        Given a ticker prices calculates it's statistics, including:
        3MT graph of volume and closing price, monthly rolling mean .
        '''
        df = self.fetch_prices(ticker)

        # Add monthly rolling mean for volume and closing prices
        df["rolling_price_1M"] = df["Adj Close"].rolling(30).mean()
        df["rolling_volume_1M"] = df["Volume"].rolling(30).mean()

        prev_close = df["Adj Close"].iloc[-2]
        daily_change = ((df["Adj Close"].iloc[-1] -
                        df["Adj Close"].iloc[-2])
                        / df["Adj Close"].iloc[-2]) * 100.0

        eps_ttm, pe_ratio = self.fetch_metrics(ticker)

        # Limit number of decimal places to 4
        prev_close = "{:.4f}".format(prev_close)
        daily_change = "{:.4f}".format(daily_change)
        eps_ttm = "{:.4f}".format(eps_ttm)
        pe_ratio = "{:.4f}".format(pe_ratio)

        return prev_close, daily_change, eps_ttm, pe_ratio, df
