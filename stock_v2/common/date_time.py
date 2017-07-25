# Version 0.2.1
# Author Zhao Zhang<zz156@georgetown.edu>
# stock/common/date_time.py
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


import os
import re


def load_config(config_path):
    if os.path.isfile(config_path):
        with open(config_path) as f:
            raw_config = f.readlines()
    else:
        raw_config = ''
    config = []
    for line in raw_config:
        if len(line.lstrip().rstrip()) > 0:
            tmp_line = line.split('#')[0].lstrip().rstrip()
            split_line = re.split(r'[ \t]+', tmp_line)
            if (split_line[0] != '') & (split_line[0] != '#'):
                config.append(split_line)
    return config

