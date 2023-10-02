import get_ticker_info
import unittest
from unittest.mock import patch, PropertyMock, Mock
import pandas as pd


class TestTickerInfo(unittest.TestCase):
    def setUp(self) -> None:
        self.tickerFetcher = get_ticker_info.TickerFetcher("TIKR")
        self.url = "https://query1.finance.yahoo.com/v7/finance"
        f"/download/{self.tickerFetcher}?period1=1030060800&"
        "period2=1684368000&interval=1d&events=history"
        "&includeAdjustedClose=true"

    @patch('requests.get')
    def test_fetch_prices(self, mocked_get):
        mock_response = Mock()
        mocked_get.return_value = mock_response
        mock_response.text = ("Date,Open,High,Low,Close,Adj Close,Volume\n"
                              "2002-08-23,0.283929,0.284464,0.275893,"
                              "0.280893,0.238421,163245600")

        expected = pd.DataFrame([['2002-08-23', '0.283929', '0.284464',
                                  '0.275893', '0.280893',
                                  '0.238421', '163245600']],
                                columns=['Date', 'Open', 'High', 'Low',
                                'Close', 'Adj Close', 'Volume'])

        expected.set_index('Date', inplace=True)
        expected = expected.astype({'Open': 'float64', 'High': 'float64',
                                    'Low': 'float64', 'Close': 'float64',
                                    'Adj Close': 'float64', 'Volume': 'int64'})

        expected.index = pd.to_datetime(expected.index)
        result = self.tickerFetcher.fetch_prices("TIKR")
        self.assertTrue(expected.equals(result))
