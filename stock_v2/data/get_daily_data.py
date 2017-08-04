#!/usr/bin/env python3

from multiprocessing import Pool

import tushare as ts

from stock.common.common_func import *
from stock_v2.common.communication import simple_publish

ohcl_dir = '../stock_data/quantitative_analysis/ohcl'
mqtt_msg_topic = 'data/ohcl'


def get_ohcl_data_one_stock(stock, start, end):
    df = ts.get_hist_data(stock, start=start, end=end)
    if df is None:
        simple_publish(mqtt_msg_topic, '%s/%s_failed' % (mqtt_msg_topic, stock))
        return
    df = df.reindex(index=df.index[::-1])
    df.to_csv('%s/%s.csv' % (ohcl_dir, stock))
    simple_publish(mqtt_msg_topic, '%s/%s_success' % (mqtt_msg_topic, stock))


def get_ohcl_data_all_stock(start, end):
    simple_publish(mqtt_msg_topic, '%s/start_%d' % (mqtt_msg_topic, len(BASIC_INFO.symbol_list)))
    pool = mp.Pool(16)
    for i in BASIC_INFO.symbol_list:
        pool.apply_async(get_ohcl_data_one_stock, args=(i, start, end))
    pool.close()
    pool.join()
    simple_publish(mqtt_msg_topic, '%s/finish' % mqtt_msg_topic)


class DividendInfo:
    """
    分红配股
    """

    def __init__(self):
        self.info_dict = {}
