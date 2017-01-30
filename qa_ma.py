#!/usr/bin/python3
# Moving Average System

import subprocess
import multiprocessing as mp
import sys

from common_func import *
from variables import *


def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0] * p2[1] - p2[0] * p1[1])
    return A, B, -C


def intersection(L1, L2):
    D = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = Dx / D
        y = Dy / D
        return x, y
    else:
        return False


class ma_align:
    def __init__(self, stock, short, mid, long, calc_type='atpd'):
        self.stock = stock
        self.ma_short = calc_ma_for_stock(stock, short, calc_type=calc_type)
        self.ma_mid = calc_ma_for_stock(stock, mid, calc_type=calc_type)
        self.ma_long = calc_ma_for_stock(stock, long, calc_type=calc_type)
        self.dates = [i['date'] for i in self.ma_short]
        self.s = short
        self.m = mid
        self.l = long
        self.dict = dict(aver_line_long='均线多头排列', aver_line_short='均线空头排列',
                         short_intersect_mid_up='%s日线向上突破%s日线' % (short, mid),
                         short_intersect_mid_down='%s日线向下击穿%s日线' % (short, mid),
                         short_intersect_long_up='%s日线向上突破%s日线' % (short, long),
                         short_intersect_long_down='%s日线向下击穿%s日线' % (short, long),
                         mid_intersect_long_up='%s日线向上突破%s日线' % (mid, long),
                         mid_intersect_long_down='%s日线向下击穿%s日线' % (mid, long),
                         trend_change_short_up='%s日线转升' % short,
                         trend_change_short_down='%s日线转降' % short,
                         trend_change_mid_up='%s日线转升' % mid,
                         trend_change_mid_down='%s日线转降' % mid,
                         trend_change_long_up='%s日线转升' % long,
                         trend_change_long_down='%s日线转降' % long, )
        self.align_type = []

    def get_ma_for_day(self, day):
        ma_short = [i['ma%s' % self.s] for i in self.ma_short if i['date'] == day][0]
        ma_mid = [i['ma%s' % self.m] for i in self.ma_mid if i['date'] == day][0]
        ma_long = [i['ma%s' % self.l] for i in self.ma_long if i['date'] == day][0]
        ma_for_day = {'ma%s' % self.s: (ma_short is not None) and float(ma_short) or ma_short,
                      'ma%s' % self.m: (ma_mid is not None) and float(ma_mid) or ma_mid,
                      'ma%s' % self.l: (ma_long is not None) and float(ma_long) or ma_long}
        return ma_for_day

    def get_yesterday(self, day):
        try:
            return [self.dates[idx] for idx in range(len(self.ma_short) - 1) if self.dates[idx + 1] == day][0]
        except Exception as e:
            print(e)
            return ''

    def get_ma_for_yesterday(self, day):
        try:
            yesterday = [self.dates[idx] for idx in range(len(self.ma_short) - 1) if self.dates[idx + 1] == day][0]
        except Exception as e:
            print(e)
            return []
        return self.get_ma_for_day(yesterday)

    def calc_ma_slope(self, day):
        ma_day = self.get_ma_for_day(day)
        ma_yesterday = self.get_ma_for_yesterday(day)
        if None in ma_yesterday.values():
            return None, None
        normalize_scaler = 10000
        ma_slope = {'mak%s' % self.s: ma_day['ma%s' % self.s] - ma_yesterday['ma%s' % self.s],
                    'mak%s' % self.m: ma_day['ma%s' % self.m] - ma_yesterday['ma%s' % self.m],
                    'mak%s' % self.l: ma_day['ma%s' % self.l] - ma_yesterday['ma%s' % self.l]}
        ma_slope_normalized = {
            'makn%s' % self.s: ma_slope['mak%s' % self.s] / ma_yesterday['ma%s' % self.l] * normalize_scaler,
            'makn%s' % self.m: ma_slope['mak%s' % self.m] / ma_yesterday['ma%s' % self.l] * normalize_scaler,
            'makn%s' % self.l: ma_slope['mak%s' % self.l] / ma_yesterday['ma%s' % self.l] * normalize_scaler}
        return ma_slope, ma_slope_normalized

    def check_slope_trend(self, day):
        k, kn = self.calc_ma_slope(day)
        k_yesterday, kn_yesterday = self.calc_ma_slope(self.get_yesterday(day))
        if (k_yesterday is None) | (kn_yesterday is None):
            return
        if kn['makn%s' % self.s] * kn_yesterday['makn%s' % self.s] < 0:
            if kn['makn%s' % self.s] > 0:
                self.align_type.append('trend_change_short_up')
            elif kn['makn%s' % self.s] < 0:
                self.align_type.append('trend_change_short_down')
        if kn['makn%s' % self.m] * kn_yesterday['makn%s' % self.m] < 0:
            if kn['makn%s' % self.m] > 0:
                self.align_type.append('trend_change_mid_up')
            elif kn['makn%s' % self.m] < 0:
                self.align_type.append('trend_change_mid_down')
        if kn['makn%s' % self.l] * kn_yesterday['makn%s' % self.l] < 0:
            if kn['makn%s' % self.l] > 0:
                self.align_type.append('trend_change_long_up')
            elif kn['makn%s' % self.l] < 0:
                self.align_type.append('trend_change_long_down')

    def intersection_check(self, day):
        ma_day = self.get_ma_for_day(day)
        ma_yesterday = self.get_ma_for_yesterday(day)
        ls = line([0, ma_yesterday['ma%s' % self.s]], [1, ma_day['ma%s' % self.s]])
        lm = line([0, ma_yesterday['ma%s' % self.m]], [1, ma_day['ma%s' % self.m]])
        ll = line([0, ma_yesterday['ma%s' % self.l]], [1, ma_day['ma%s' % self.l]])
        rsm = intersection(ls, lm)
        rsl = intersection(ls, ll)
        rml = intersection(lm, ll)
        result = []
        if rsm:
            if (rsm[0] > 0) & (rsm[0] < 1):
                trend = ((ma_day['ma%s' % self.s] - ma_yesterday['ma%s' % self.s]) > 0) and 'up' or 'down'
                self.align_type.append('short_intersect_mid_%s' % trend)
                result.append('short_intersect_mid_%s' % trend)
        if rsl:
            if (rsl[0] > 0) & (rsl[0] < 1):
                trend = ((ma_day['ma%s' % self.s] - ma_yesterday['ma%s' % self.s]) > 0) and 'up' or 'down'
                self.align_type.append('short_intersect_long_%s' % trend)
                result.append('short_intersect_long_%s' % trend)
        if rml:
            if (rml[0] > 0) & (rml[0] < 1):
                trend = ((ma_day['ma%s' % self.m] - ma_yesterday['ma%s' % self.m]) > 0) and 'up' or 'down'
                self.align_type.append('mid_intersect_long_%s' % trend)
                result.append('mid_intersect_long_%s' % trend)
        return result

    def analysis_align_for_day(self, day):
        if day not in self.dates:
            return {}, '该日无交易'
        self.align_type = []
        for line in self.ma_long:
            if line['date'] == day:
                if line ['ma%s' % self.l] is None:
                    return {}, '并无足够数据'
        ma_day = self.get_ma_for_day(day)
        align = sorted(ma_day.keys(), key=ma_day.get, reverse=True)
        (ma_slope, ma_slope_norm) = self.calc_ma_slope(day)
        if (align[0] == 'ma%s' % self.s) & (align[1] == 'ma%s' % self.m) & (align[2] == 'ma%s' % self.l):
            self.align_type.append('aver_line_long')
        elif (align[2] == 'ma%s' % self.s) & (align[1] == 'ma%s' % self.m) & (align[0] == 'ma%s' % self.l):
            self.align_type.append('aver_line_short')
        self.check_slope_trend(day)
        self.intersection_check(day)
        align_output = ''
        for idx in range(len(self.align_type)):
            align_output += self.dict[self.align_type[idx]]
            align_output += (idx != len(self.align_type) - 1) and ', ' or ''
        result = {}
        for k in self.dict.keys():
            if k not in self.align_type:
                result[k] = '0'
            else:
                result[k] = '1'
        result.update(ma_slope)
        result.update(ma_slope_norm)
        return result, align_output

    def generate_ma_data_for_all_day(self):
        strict_dates=[]
        for line in self.ma_long:
            if line['ma%s' % self.l] is not None:
                strict_dates.append(line['date'])
        result=[]
        for d in strict_dates:
            try:
                r,a = self.analysis_align_for_day(d)
                result.append(r)
            except:
                print("error:", d)
        return result


def save_ma_for_stock(stock, ma_list, ma_params):
    subprocess.call("mkdir -p %s/qa/ma/%s" % (stock_data_root, ma_params), shell=True)
    with open("%s/qa/ma/%s/%s.pickle" % (stock_data_root, ma_params, stock), 'wb') as f:
        pickle.dump(ma_list, f, -1)


def calc_ma_for_stock(stock: str, days: int, calc_type: str = 'atpd') -> list:
    """
    :param stock:
    :param days:
    :param calc_type:'close', 'atpd'
    :return:
    """

    days = int(days)
    data_list = []
    assert days > 0
    if calc_type == 'close':
        # data_list = close data of a stock
        data_list = load_daily_data(stock)
    elif calc_type == 'atpd':
        # data_list = average trade price of day data of a stock
        data_list = load_atpd_data(stock)
    if len(data_list) < days:
        return []
    ma_list = []
    for (idx, line) in enumerate(data_list):
        if idx < days - 1:
            ma_list.append({'date': line['date'], 'ma%d' % days: None})
            continue
        ma5 = sum(float(i[calc_type]) for i in data_list[idx - days + 1: idx + 1]) / days
        ma_list.append({'date': line['date'], 'ma%d' % days: '%.3f' % ma5})
    save_ma_for_stock(stock, ma_list, '%s_%d' % (calc_type, days))
    return ma_list


def calc_ma_for_all_stock(days, calc_type='atpd'):
    pool = mp.Pool()
    for i in SYMBOL_LIST:
        pool.apply_async(calc_ma_for_stock, args=(i, days, calc_type))
    pool.close()
    pool.join()


if __name__ == '__main__':
    calc_ma_for_all_stock(sys.argv[1], sys.argv[2])
