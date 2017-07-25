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

I18N = 'CHN'  # FIXME: need to implement full i18n support


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


class Period:
    def __init__(self, name, status, begin, end):
        self.name = name
        self.status = status
        self.begin = begin
        self.end = end
        self.time_str = self.begin + '_' + self.end

    def summary(self):
        return self.name, self.status, self.begin, self.end


class MktInfo:
    def __init__(self):
        self.mkt = ''
        self.timezone = ''
        self.special_close_day_list = None
        self.special_open_day_list = None
        self.basic_mkt_open_day_rule = ''
        self.period_dict_key_name = {}
        self.period_dict_key_time = {}


def load_special_date_file(path):
    return True


def parsing_cfg(cfg):
    mkt_info = MktInfo()
    i18n_dict = {}
    for (idx, line) in enumerate(cfg):
        if line[0] == 'MARKET':
            mkt_info.mkt = line[1]
        elif line[0] == 'TIME_ZONE':
            mkt_info.timezone = line[1]
        elif line[0] == 'SPECIAL_CLOSE_DATE_FILE':
            mkt_info.special_close_day_list = load_special_date_file(line[1])
        elif line[0] == 'SPECIAL_OPEN_DATE_FILE':
            mkt_info.special_open_day_list = load_special_date_file(line[1])
        elif line[0] == 'BASIC_OPEN_DATE':
            mkt_info.basic_mkt_open_day_rule = line[1]
        elif line[0] == 'PERIOD':
            name = line[1]
            status = cfg[idx + 1][1]
            begin = cfg[idx + 2][1]
            end = cfg[idx + 3][1]
            new_period = Period(name, status, begin, end)
            mkt_info.period_dict_key_name[name] = new_period
            mkt_info.period_dict_key_time[new_period.time_str] = new_period
        elif line[0] == 'I18N':
            key = line[1]
            translate_dict = {}
            for i in line[2:]:
                lang = i.split(':')[0]
                trans = i.split(':')[1]
                translate_dict[lang] = trans
            i18n_dict[key] = translate_dict
    return mkt_info, i18n_dict


def get_trans(target, i18n_dict):
    # FIXME need more properly i18n support
    return i18n_dict[target][I18N]
