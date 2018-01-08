# DEPENDENCY( pandas )
import os

import math
import pandas as pd
import sys

from analysis.script_executor.TranslateHdl import TranslateHdl
from analysis.script_executor.statistics import ConditionalStatisticsHdl
from configs.path import DIRs
from tools.io import logging
from tools.symbol_list_china_hdl import SymbolListHDL
import multiprocessing as mp


def validate_input_path(data, date):
    return os.path.join(DIRs.get("DATA_ROOT"), "slice", "%s_%s.csv" % (data, date))


def validate_output_path(data, date, type):
    return os.path.join(DIRs.get("DATA_ROOT"), "naive_score", "%s_%s_%s.csv" % (data, type, date))


def calc_score_turnover(data, date):
    path = validate_input_path(data, date)
    cond_buy = ConditionalStatisticsHdl("", 'merged', 'cond_buy')
    cond_buy.load()
    cond_sell = ConditionalStatisticsHdl("", 'merged', 'cond_sell')
    cond_sell.load()
    raw_data = pd.read_csv(path)
    result_list = raw_data.to_dict('records')
    for l in result_list:
        ori_turnover = l['turnover']
        if ori_turnover > 20:
            ori_turnover = 15 - math.log(ori_turnover / 20)
        turnover = ori_turnover / 25
        score = 0
        for target in cond_buy.probability_dict.keys():
            score += (cond_buy.probability_dict[target] * (1 + turnover) if l[target.split("|")[1]] else 0)
        for target in cond_sell.probability_dict.keys():
            score -= (cond_sell.probability_dict[target] if l[target.split("|")[1]] else 0)
        l['score'] = score
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='score', ascending=False)
    r.to_csv(validate_output_path(data, "turnover", date), index=False, columns=['name', 'symbol', 'score'])


def calc_score_amount(data, date):
    path = validate_input_path(data, date)
    raw_data = pd.read_csv(path)
    result_list = raw_data.to_dict('records')
    for l in result_list:
        score = l['AMOUNT_SCALAR']
        l['score'] = score
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='score', ascending=False)
    r.to_csv(validate_output_path(data, "amount", date), index=False, columns=['name', 'symbol', 'score'])
