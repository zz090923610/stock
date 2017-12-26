# DEPENDENCY( pandas )
import os

import pandas as pd
import sys

from configs.path import DIRs
from tools.symbol_list_china_hdl import SymbolListHDL

# TODO currently ugly implementation
class DayLevelSummary:
    def __init__(self, symbol, date, symbol_str, name_str):
        self.symbol = symbol
        self.target_date = date
        self.symbol_str = symbol_str
        self.name_str = name_str
        self.day_quotes = pd.DataFrame
        self.ma_result = pd.DataFrame
        self.candle_stick = pd.DataFrame
        self.result = pd.DataFrame

    def load_file(self):
        # load day quotes
        day_quotes_path = os.path.join(DIRs.get("DAY_LEVEL_QUOTES_CHINA"), self.symbol + ".csv")
        self.day_quotes = pd.read_csv(day_quotes_path)
        # load ma result
        ma_path = os.path.join("/home/zhangzhao/data/stockdata/qa/ma", self.symbol + ".csv")
        self.ma_result = pd.read_csv(ma_path)
        # load candle stick analysis result
        candle_stick_path = os.path.join("/home/zhangzhao/data/stockdata/qa/candle_stick_shape_analysis",
                                         self.symbol + ".csv")
        self.candle_stick = pd.read_csv(candle_stick_path)

    def merge_data(self):
        day_quote_line = self.day_quotes[self.day_quotes['date'] == self.target_date]
        ma_line = self.ma_result[self.ma_result['date'] == self.target_date]
        candle_line = self.candle_stick[self.candle_stick['date'] == self.target_date]

        day_quote_line = day_quote_line.set_index('date')
        ma_line = ma_line.set_index('date')
        candle_line = candle_line.set_index('date')
        self.result = pd.concat([day_quote_line, ma_line, candle_line], axis=1)
        self.result['symbol'] = self.symbol_str
        self.result['name'] = self.name_str
        self.result = self.result.rename(index=str, columns=self.translate_dict)

    def write_out_summary(self):
        self.result.to_csv('/tmp/test.csv')

    def get_result(self):
        return self.result


def summary_all(date, out_path):
    symbol_dict = SymbolListHDL()
    symbol_dict.load()
    result = pd.DataFrame()
    for s in symbol_dict.symbol_list:
        try:
            print(s)
            symbol_str = symbol_dict.market_symbol_of_stock(s)
            name = symbol_dict.name_dict.get(s)

            a = DayLevelSummary(s, date, symbol_str, name)
            a.load_file()
            a.merge_data()
            res = a.get_result()
            result = pd.concat([result, res], axis=0)
        except FileNotFoundError:
            continue
    result = result.drop_duplicates(['代码'], keep='last')
    result.to_csv(out_path)


if __name__ == '__main__':
    summary_all(sys.argv[1], sys.argv[2])
