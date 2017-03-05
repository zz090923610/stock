#!/usr/bin/python3
import pickle
import pandas as pd

from stock.common.common_func import logging
from stock.common.variables import stock_data_root


class AnalysisResult:
    def __init__(self, stock):
        self.stock = stock
        df = pd.read_csv('%s/data/%s.csv' % (stock_data_root, stock))
        self.date_list = df.date.tolist()
        self.result = {day: [] for day in self.date_list}
        self.load_result()

    def load_result(self):
        try:
            with open('%s/analysis_result/%s.pickle' % (stock_data_root, self.stock), 'rb') as f:
                self.result = pickle.load(f)
        except FileNotFoundError as e:
            self.result = {day: [] for day in self.date_list}

    def append_result_for_day(self, day, result):
        try:
            current_result = self.result[day]
        except KeyError:
            current_result = []
        if result not in current_result:
            try:
                self.result[day].append(result)
                with open('%s/analysis_result/%s.pickle' % (stock_data_root, self.stock), 'wb') as f:
                    pickle.dump(self.result, f, -1)
            except KeyError:
                self.result[day] = []
                self.result[day].append(result)
                with open('%s/analysis_result/%s.pickle' % (stock_data_root, self.stock), 'wb') as f:
                    pickle.dump(self.result, f, -1)


def add_analysis_result_one_stock_one_day(stock, day, result):
    # print('adding', stock, day, result)
    a = AnalysisResult(stock)
    a.append_result_for_day(day, result)
