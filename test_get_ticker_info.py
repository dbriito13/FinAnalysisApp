import get_ticker_info
import unittest
from unittest.mock import patch, PropertyMock, Mock
import pandas as pd


class TestTickerInfo(unittest.TestCase):
    def setUp(self) -> None:
        self.tickerFetcher = get_ticker_info.TickerFetcher("TIKR")

    @patch('requests.get')
    def test_fetch_prices(self, mocked_get):
        mock_response = Mock()
        mock_response.text = ("Date,Open,High,Low,Close,Adj Close,Volume\n"
                              "2002-08-23,0.283929,0.284464,0.275893,"
                              "0.280893,0.238421,163245600")
        mock_response.status_code = 200
        mocked_get.return_value = mock_response
        
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
