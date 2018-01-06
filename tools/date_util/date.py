# Version 0.2.1
# Author Zhao Zhang<zz156@georgetown.edu>
# 日期/时间模块
# 一切日期时间相关函数的集成模块. 提供当前时刻不同市场的状态.
# 对于已开盘市场, 提供已开盘时长, 当日剩余交易时长, 剩余时长/已开盘时长　等信息
# 对于任意市场, 提供最近一次已完成交易日日期.
# 对于任意市场, 提供开市日历.
# 基本市场信息配置文件格式:
# MARKET CHN/US
# BASIC_OPEN_DATE WEEKDAY
# SPECIAL_CLOSE_DATE_FILE path/to/file
# STATUS PRE_MARKET/OPEN/AFTER_HOUR/CLOSE
# BEGIN 06:00:00
# END 09:29:55
# 特殊开休市时间列表的格式转换/获取

###################################
#
# 　１，查询某特定市场当前状态的函数
#       def get_market_status(mkt_code):
#       input: market code
#       return: period, status, time_avail_today, time_elapsed_today,
#               time_elapsed_today/(time_avail_today+time_elapsed_today)
#
# 　２，查询某特定市场最近一个已结束的交易日期
#       def get_latest_closed_date(mkt_code):
#       input: market code
#       return: last_trade_date
#
#   ３，市场交易日历
#       def get_market_calendar(mkt_code):
#       input: market code
#       return: list of (date, status) pair
#
#
#
#
#


import datetime
import time
from datetime import date
from datetime import timedelta as td

import pytz

I18N = 'CHN'  # FIXME: need to implement full i18n support





def str2date(str_date):
    """
    generate a date obj given an date in string format, YYYY-MM-DD
    :param str_date: given an date in string format, YYYY-MM-DD
    :return: date object
    """
    str_date_in_list = [int(i) for i in str_date.split('-')]
    return date(str_date_in_list[0], str_date_in_list[1], str_date_in_list[2])


def date_offset(start_date='', offset=-7, tz='Asia/Shanghai'):
    start_date = get_today(tz=tz) if start_date == '' else start_date
    target_date = str2date(start_date) + datetime.timedelta(offset)
    return str(target_date)


def check_weekday(target_date):
    target_date = str2date(target_date) if type(target_date) == str else target_date
    if target_date.weekday() in range(0, 5):
        return True
    else:
        return False

