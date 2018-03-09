# DEPENDENCY( pandas )
# WINDOWS_GUARANTEED
import math
import os

import pandas as pd

from analysis.models.conditional_freqency import ConditionalFreqHdl
# USEDIR( slice )
# REGDIR( naive_score )
from tools.data.path_hdl import path_expand, directory_ensure

out_dir = path_expand("naive_score")
directory_ensure(path_expand("naive_score"))


def validate_output_path(data, date, type):
    return os.path.join(out_dir, "%s_%s_%s.csv" % (data, type, date))


def calc_score_turnover(data, date):

    path = os.path.join(path_expand("slice"), "%s_%s.csv" % (data, date))
    cond_buy = ConditionalFreqHdl("cond_buy", None, None)
    cond_buy.load()
    cond_sell = ConditionalFreqHdl("cond_sell", None, None)
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
    r.to_csv(os.path.join(out_dir, "%s_%s_%s.csv" % (data, "turnover", date)), index=False,
             columns=['name', 'symbol', 'score'])


def calc_score_amount(data, date):
    path = os.path.join(path_expand("slice"), "%s_%s.csv" % (data, date))
    raw_data = pd.read_csv(path)
    result_list = raw_data.to_dict('records')
    for l in result_list:
        score = l['AMOUNT_SCALAR']
        l['score'] = score
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='score', ascending=False)
    r.to_csv(os.path.join(out_dir, "%s_%s_%s.csv" % (data, "amount", date)), index=False,
             columns=['name', 'symbol', 'score'])
