# -*- coding: utf-8 -*-
# DEPENDENCY( pandas )
# WINDOWS_GUARANTEED
import math
import os
import pandas as pd
from models.candle_stock_analysis_legacy.pythons.conditional_frequency import ConditionalFreqHdl
from tools.data.path_hdl import path_expand, directory_ensure
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import logging

out_dir = path_expand("naive_score")
directory_ensure(path_expand("naive_score"))
calendar = MktCalendar()


# USEDIR( $USER_SPECIFIED )
# REGDIR ( naive_score )

# this model using the result of conditional_frequency.

def generate_output_path(data, date, score_type):
    """
    :param data:        string
    :param date:        string
    :param score_type:  string
    :return:            string
    """
    return os.path.join(out_dir, "%s_%s_%s.csv" % (data, score_type, date))


# CMDEXPORT ( NAIVESCORE TURNOVER {data} {date}) naive_score_turnover
def naive_score_turnover(data, date):
    """
    Export this function to Control Framework, a control command like:
        NAIVESCORE TURNOVER summary LASTCLOSEDTRADEDAY
    can be added to .ctrl batch file to save some work.

    Score all stocks using conditional_frequency model.

    :param data:    string, specify which file to load by proving keyword data
    :param date:    string, YYYY-MM-DD
    """
    date = calendar.parse_date(date)
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
        score = -999 if score == 0 else score
        print(score)
        l['score'] = score
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='score', ascending=False)
    r.to_csv(os.path.join(out_dir, "%s_%s_%s.csv" % (data, "turnover", date)), index=False,
             columns=['name', 'symbol', 'score'])
    logging("NAIVESCORE TURNOVER", "[ INFO ] applied %s %s" % (data, date))


# CMDEXPORT ( NAIVESCORE AMOUNT {data} {date}) naive_score_amount
def naive_score_amount(data, date):
    """
    Export this function to Control Framework, a control command like:
        NAIVESCORE AMOUNT summary LASTCLOSEDTRADEDAY
    can be added to .ctrl batch file to save some work.

    Score all stocks using AMOUNT_SCALAR model.

    :param data:    string, specify which file to load by proving keyword data
    :param date:    string, YYYY-MM-DD
    """
    date = calendar.parse_date(date)
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
    logging("NAIVESCORE AMOUNT", "[ INFO ] applied %s %s" % (data, date))
