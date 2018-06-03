# -*- coding: utf-8 -*-

import multiprocessing as mp
import os
import pickle
import pandas as pd
from tools.data.path_hdl import path_expand, directory_ensure, directory_exists
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import logging

# This model calculates short term total return of all candlestick shapes.
# total return for one specific shape is calculated as average of return if you purchase at such dates and sell in 20
# days.

# Train phase:
# calc average return if you long for every time a shape appears.

# Eval phase:
# say we have same number of people as shapes where everybody represents a shape, they only long if their shapes appear.
# we calculate the expect total return rate of all those people.


# Related files:
# analysis/models/candlestick_total_ret.py
# ctrls/candlestick_total_ret_eval.ctrl
# ctrls/candlestick_total_ret_train.ctrl
# scripts/short_term_return_rate.txt

# USEDIR( qa/candlestick_total_ret_input  )
# REGDIR ( models/candlestick_total_ret )
calendar = MktCalendar()


def calc_total_ret_kernel(input_path, shapes):
    res_dict = {}
    raw_data = pd.read_csv(input_path)
    if raw_data.empty:
        logging("CandlestickTotalRetKernel", "[ WARNING ] input file %s empty" % input_path, method="all")
        return {}
    for s in shapes:
        ds_shape = raw_data[raw_data[s] == True]
        val = ds_shape['SHORT_TERM_RET_RATE'].sum()
        cnt = len(ds_shape.index)
        res_dict[s] = "%s_%s" % (val, cnt)
    logging("CandlestickTotalRetKernel", "[ INFO ] applied %s" % input_path)
    return res_dict


class CandlestickTotalRetHdl:
    def __init__(self, shapes):
        """
                :param shapes: string of shapes, separated by space
        """
        self.input_dir = path_expand("qa/candlestick_total_ret_input")

        if not directory_exists(self.input_dir):
            logging("CandlestickTotalRetHdl", "[ ERROR ]input dir %s not exist" % self.input_dir, method="all")
        self.storage_dir = path_expand("models/candlestick_total_ret")
        directory_ensure(self.storage_dir)
        if shapes is not None:
            self.shapes = shapes.split(" ")
        else:
            self.shapes = None
        self.ret_dict = {}
        self.cnt_dict = {}
        if self.input_dir:
            self.input_files = [os.path.join(self.input_dir, i) for i in os.listdir(self.input_dir)]
        else:
            self.input_files = []
        self.data = None

    def train(self):
        """
        only call this when you need to generate new models.
        """
        tmp = []
        pool = mp.Pool()
        for i in self.input_files:
            pool.apply_async(calc_total_ret_kernel, args=(i, self.shapes), callback=tmp.append)
        pool.close()
        pool.join()
        for line in tmp:
            for s in self.shapes:
                try:
                    ret, cnt = [float(i) for i in line[s].split("_")]
                except KeyError:
                    ret = 0
                    cnt = 0
                try:
                    self.ret_dict[s] += ret
                    self.cnt_dict[s] += cnt
                except KeyError:
                    self.ret_dict[s] = ret
                    self.cnt_dict[s] = cnt

        for s in self.shapes:
            try:
                self.ret_dict[s] /= self.cnt_dict[s]
            except ZeroDivisionError:
                self.ret_dict[s] = 0
            print("%s: %f" % (s, self.ret_dict[s]))
        self.save()

    def save(self):
        with open('%s' % (os.path.join(self.storage_dir, "candlestick_total_ret.pickle")), 'wb') as f:
            pickle.dump(self.ret_dict, f, -1)

    def load(self):
        try:
            with open('%s' % (os.path.join(self.storage_dir, "candlestick_total_ret.pickle")), 'rb') as f:
                self.ret_dict = pickle.load(f)
        except FileNotFoundError as e:
            logging("ConditionalFreqHdl", "[ ERROR ] model not found %s" % e, method='all')
            self.ret_dict = {}


# CMDEXPORT ( CSTR TRAIN {shapes[2:]} ) CandlestickTotalRetTrain
def CandlestickTotalRetTrain(shapes):
    a = CandlestickTotalRetHdl(shapes)
    a.train()


# CMDEXPORT ( CSTR EVAL {data} {date}) exp_return_on_shape
def exp_return_on_shape(data, date):
    """
    :param data:    string, specify which file to load by proving keyword data
    :param date:    string, YYYY-MM-DD
    """
    out_dir = path_expand("exp_ret")
    directory_ensure(out_dir)
    date = calendar.parse_date(date)
    path = os.path.join(path_expand("slice"), "%s_%s.csv" % (data, date))
    model_hdl = CandlestickTotalRetHdl(None)
    model_hdl.load()
    shapes = model_hdl.ret_dict.keys()
    raw_data = pd.read_csv(path)
    result_list = raw_data.to_dict('records')
    for l in result_list:
        exp_ret = 0
        for s in shapes:
            if l[s] == True:
                exp_ret += model_hdl.ret_dict[s]
        l['exp_ret'] =(1 +  exp_ret) * ((l['AMOUNT_SCALAR'] - 1) / 5 + 1)
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='exp_ret', ascending=False)
    r.to_csv(os.path.join(out_dir, "%s_%s.csv" % ("exp_ret", date)), index=False,
             columns=['name', 'symbol', 'exp_ret'])
    logging("CSTR EVAL", "[ INFO ] applied %s %s" % (data, date))
