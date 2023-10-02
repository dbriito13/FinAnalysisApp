import plotly
import json
import plotly.express as px


class TickerGraphs():
    def __init__(self, prices, ticker) -> None:
        self.prices = prices
        self.ticker = ticker

    def create_plot(self, df, y_axis, title):
        fig = px.line(df,
                      x=df.index,
                      y=df.columns
                      ).update_layout(xaxis_title="Date",
                                                  yaxis_title=y_axis,
                                                  title_text=title,
                                                  legend_title_text='Legend',
                                                  title_x=0.5)
        data = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return data

    def generate_plots(self):
        df_close = self.prices[['Adj Close', 'rolling_price_1M']] 
        df_close.columns = ['Closing Price', 'One-Month Rolling Mean']
        df_vol = self.prices[['Volume', 'rolling_volume_1M']]
        df_vol.columns = ['Volume', 'One-Month Rolling Mean']
        # Last year of data
        df_close = df_close.tail(365)
        df_vol = df_vol.tail(365)
        # Generate the plots from both
        plot_close = self.create_plot(df_close,
                                      "Price ($)",
                                      f"{self.ticker}'s price for"
                                      " the past 365 days")
        plot_vol = self.create_plot(df_vol,
                                    "Volume (M)",
                                    f"{self.ticker}'s traded volume"
                                    " for the past 365 days")
        return plot_close, plot_vol
