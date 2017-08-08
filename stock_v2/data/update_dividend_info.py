#!/usr/bin/python3
# FIXME old stock reference here
import time

import os

from stock.common.common_func import BASIC_INFO_DICT
from stock_v2.common.communication import simple_publish
from stock_v2.data.http_hdl import HttpHdl


def update_dividend_info(stock):
    simple_publish('data/update_dividend_info', 'data/update_dividend_info/got_%s' % stock)
    a = HttpHdl('./configs/data/dividend.cfg', {'stock': stock})
    a.apply()


def update_all(refresh=False):
    stock_list = list(BASIC_INFO_DICT.keys())
    dir_list = [i.split('.')[0] for i in os.listdir('../stock_data/basic/split_dividend')]
    work_list = list(set(stock_list) - set(dir_list))
    simple_publish('data/update_dividend_info', 'data/update_dividend_info/start_%d' % len(work_list))
    for i in work_list:
        try:
            update_dividend_info(i)
        except:
            simple_publish('data/update_dividend_info', 'data/update_dividend_info/error_%s' % i)
            update_all(refresh=refresh)
            return

    simple_publish('data/update_dividend_info', 'data/update_dividend_info/finish')


if __name__ == '__main__':
    update_all()
