import pandas as pd
import yfinance as yf
import datetime as dt

class Stock:
    def __init__(self, stocks):
        self.stocks = stocks
        self.data = self.get_data()

    def get_data(self):
        stock_data = yf.download(self.stocks, period="5d", interval='1d', group_by='ticker')
        return stock_data

    def calc_returns(self):
        return_df = pd.DataFrame(columns=['Ticker', 'Returns'])
        for ticker in self.data.columns.levels[0]:
            start_price = self.data[ticker]['Close'].iloc[0]
            end_price = self.data[ticker]['Close'].iloc[-1]
            delta = end_price - start_price
            return_df.loc[len(return_df)] = [ticker, delta]
        return return_df