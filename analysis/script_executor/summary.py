# DEPENDENCY( pandas )
import os

import math
import pandas as pd
import sys

from configs.path import DIRs
from tools.io import logging
from tools.symbol_list_china_hdl import SymbolListHDL
import multiprocessing as mp


# TODO currently ugly implementation
class DayLevelSummary:
    def __init__(self, symbol, date, symbol_str, name_str):
        self.symbol = symbol
        self.target_date = date
        self.symbol_str = symbol_str
        self.name_str = name_str
        self.day_quotes = pd.DataFrame
        self.ma_result = pd.DataFrame
        self.candle_stick = pd.DataFrame
        self.result = pd.DataFrame
        self.translate_dict = {
            'symbol': '代码',
            'name': '名称',
            'date': '日期',
            'open': '开盘',
            'high': '高值',
            'close': '收盘',
            'low': '低值',
            'volume': '成交量',
            'price_change': '价格变动',
            'p_change': '涨跌幅',
            'ma5': '价ma5',
            'ma10': '价ma10',
            'ma20': '价ma20',
            'v_ma5': '量ma5',
            'v_ma10': '量ma10',
            'v_ma20': '量ma20',
            'turnover': '换手率',
            'MAALIGNUPWARD': '均线多头排列',
            'MAALIGNDOWNWARD': '均线空头排列',
            'GOLDCROSS510': '均线金叉5穿10',
            'GOLDCROSS520': '均线金叉5穿20',
            'GOLDCROSS1020': '均线金叉10穿20',
            'LOSECROSS510': '均线死叉5穿10',
            'LOSECROSS520': '均线死叉5穿20',
            'LOSECROSS1020': '均线死叉10穿20',
            'GOLDVALLEY': '金山谷',
            'LOSEVALLEY': '死亡谷',
            'DRAGONOUT': '蛟龙出海',
            'LOSEEVERYTHING': '断头铡刀',
            'YIN': '阴线',
            'YANG': '阳线',
            'LARGEYANG': '大阳线',
            'MIDYANG': '中阳线',
            'SMALLYANG': '小阳线',
            'LARGEYIN': '大阴线',
            'MIDYIN': '中阴线',
            'SMALLYIN': '小阴线',
            'BOXHIGH': '实体高值',
            'BOXLOW': '实体低值',
            'CLOP': '实体长度',
            'UPPERSHADOW': '上影线长',
            'BOXLOW': '下影线长',
            'CROSS': '十字线',
            'TSHAPE': 'T字线',
            'REVERSETSHAPE': '反T字线',
            'ONESHAPE': '一字线',
            'JUMPHIGHOPEN': '跳高开盘',
            'JUMPLOWOPEN': '跳低开盘',
            'LARGEK': '大K线',
            'MIDK': '中K线',
            'SMALLK': '小K线',
            'MORNINGCROSS': '晨十字星',
            'MORNINGSTAR': '清晨之星',
            'FRIENDLYFIRE': '好友反攻',
            'HOPEOFDAWN': '曙光初现',
            'RAISINGSUN': '旭日东升',
            'REVERSEHAMMER': '倒锤头线',
            'HAMMER': '锤头线',
            'FLATFLOOR': '平底',
            'CONTINUETHREEJUMPYIN': '连续跳空三阴线',
            'TRIPLEREDARMY': '红三兵',
            'UPWARDTWOSTARS': '上涨两颗星',
            'JUMPUPWARD': '跳空上扬/升势鹤鸦',
            'JUMPUPWARDYANG': '跳高并排阳线',
            'JUMPDOWNWARDTHREESTARS': '跳空下跌三颗星',
            'TRIPLEUPWARDS': '上升三部曲/升势三鸦',
            'TWILICROSS': '黄昏十字星',
            'TWILISTAR': '黄昏之星',
            'FRIENDLYPUSHBACK': '淡友反攻',
            'INCOMINGCLOUDS': '乌云盖顶',
            'HEAVYRAIN': '倾盆大雨',
            'SHOOTINGSTAR': '射击之星',
            'HANGWIRE': '吊颈线',
            'FLATROOF': '平顶',
            'DOUBLECROWS': '双飞乌鸦',
            'TRIPLECROWS': '三只乌鸦',
            'HEADSFEETYIN': '穿头破脚阴包阳',
            'HEADSFEETYANG': '穿头破脚阳包阴',
            'DOWNWARDCOVER': '下降覆盖线',
            'TRIPLEBLKARMY': '黑三兵',
            'MILDDOWNWARDS': '徐缓下跌',
            'RUSHINGAWAY': '高开出逃',
            'DOWNWARDTRIPLESTARS': '下跌三颗星',
            'DOWNWARDTRIPLESWANS': '降势三鹤',
            'TRIPLEDOWNWARDSYANG': '倒三阳',
            'JUMPHIGHTRIPLEYANG': '跳空三阳线',
            'UPWARDRESISTENCE': '升势受阻',
            'UPWARDPAUSE': '升势停顿',
            'LAMPYANG': '阳线瘸腿形',
            'BLKREDBLK': '两黑夹一红',
            'LONGCROSS': '长十字线',
            'PROPELLER': '螺旋桨',
            'EOFUPWARD': '涨势尽头线',
            'EOFDOWNWARD': '跌势尽头线',
            'PREGNANTYANG': '身怀六甲阳包阴',
            'PREGNANTYIN': '身怀六甲阴包阳',
            'TWOREDONEBLACK': '两红夹一黑',
            'LOWERSHADOW': '下影线',
            'BOXLENGTH': '实体长',
        }

    def load_file(self):
        # load day quotes
        day_quotes_path = os.path.join(DIRs.get("DAY_LEVEL_QUOTES_CHINA"), self.symbol + ".csv")
        self.day_quotes = pd.read_csv(day_quotes_path)
        # load ma result
        ma_path = os.path.join("/home/zhangzhao/data/stockdata/qa/ma", self.symbol + ".csv")
        self.ma_result = pd.read_csv(ma_path)
        # load candle stick analysis result
        candle_stick_path = os.path.join("/home/zhangzhao/data/stockdata/qa/candle_stick_shape_analysis",
                                         self.symbol + ".csv")
        self.candle_stick = pd.read_csv(candle_stick_path)

    def merge_data(self):
        day_quote_line = self.day_quotes[self.day_quotes['date'] == self.target_date]
        ma_line = self.ma_result[self.ma_result['date'] == self.target_date]
        candle_line = self.candle_stick[self.candle_stick['date'] == self.target_date]

        day_quote_line = day_quote_line.set_index('date')
        ma_line = ma_line.set_index('date')
        candle_line = candle_line.set_index('date')
        self.result = pd.concat([day_quote_line, ma_line, candle_line], axis=1)

    def rename(self):
        self.result['symbol'] = self.symbol_str
        self.result['name'] = self.name_str
        self.result = self.result.rename(index=str, columns=self.translate_dict)

    def get_result(self):
        return self.result


def calc_score(date, out_path):
    symbol_dict = SymbolListHDL()
    symbol_dict.load()

    translate_dict = {
        'symbol': '代码',
        'name': '名称',
        'date': '日期',
        'open': '开盘',
        'high': '高值',
        'close': '收盘',
        'low': '低值',
        'volume': '成交量',
        'price_change': '价格变动',
        'p_change': '涨跌幅',
        'ma5': '价ma5',
        'ma10': '价ma10',
        'ma20': '价ma20',
        'v_ma5': '量ma5',
        'v_ma10': '量ma10',
        'v_ma20': '量ma20',
        'turnover': '换手率',
        'MAALIGNUPWARD': '均线多头排列',
        'MAALIGNDOWNWARD': '均线空头排列',
        'GOLDCROSS510': '均线金叉5穿10',
        'GOLDCROSS520': '均线金叉5穿20',
        'GOLDCROSS1020': '均线金叉10穿20',
        'LOSECROSS510': '均线死叉5穿10',
        'LOSECROSS520': '均线死叉5穿20',
        'LOSECROSS1020': '均线死叉10穿20',
        'GOLDVALLEY': '金山谷',
        'LOSEVALLEY': '死亡谷',
        'DRAGONOUT': '蛟龙出海',
        'LOSEEVERYTHING': '断头铡刀',
        'YIN': '阴线',
        'YANG': '阳线',
        'LARGEYANG': '大阳线',
        'MIDYANG': '中阳线',
        'SMALLYANG': '小阳线',
        'LARGEYIN': '大阴线',
        'MIDYIN': '中阴线',
        'SMALLYIN': '小阴线',
        'BOXHIGH': '实体高值',
        'BOXLOW': '实体低值',
        'CLOP': '实体长度',
        'UPPERSHADOW': '上影线长',
        'BOXLOW': '下影线长',
        'CROSS': '十字线',
        'TSHAPE': 'T字线',
        'REVERSETSHAPE': '反T字线',
        'ONESHAPE': '一字线',
        'JUMPHIGHOPEN': '跳高开盘',
        'JUMPLOWOPEN': '跳低开盘',
        'LARGEK': '大K线',
        'MIDK': '中K线',
        'SMALLK': '小K线',
        'MORNINGCROSS': '晨十字星',
        'MORNINGSTAR': '清晨之星',
        'FRIENDLYFIRE': '好友反攻',
        'HOPEOFDAWN': '曙光初现',
        'RAISINGSUN': '旭日东升',
        'REVERSEHAMMER': '倒锤头线',
        'HAMMER': '锤头线',
        'FLATFLOOR': '平底',
        'CONTINUETHREEJUMPYIN': '连续跳空三阴线',
        'TRIPLEREDARMY': '红三兵',
        'UPWARDTWOSTARS': '上涨两颗星',
        'JUMPUPWARD': '跳空上扬/升势鹤鸦',
        'JUMPUPWARDYANG': '跳高并排阳线',
        'JUMPDOWNWARDTHREESTARS': '跳空下跌三颗星',
        'TRIPLEUPWARDS': '上升三部曲/升势三鸦',
        'TWILICROSS': '黄昏十字星',
        'TWILISTAR': '黄昏之星',
        'FRIENDLYPUSHBACK': '淡友反攻',
        'INCOMINGCLOUDS': '乌云盖顶',
        'HEAVYRAIN': '倾盆大雨',
        'SHOOTINGSTAR': '射击之星',
        'HANGWIRE': '吊颈线',
        'FLATROOF': '平顶',
        'DOUBLECROWS': '双飞乌鸦',
        'TRIPLECROWS': '三只乌鸦',
        'HEADSFEETYIN': '穿头破脚阴包阳',
        'HEADSFEETYANG': '穿头破脚阳包阴',
        'DOWNWARDCOVER': '下降覆盖线',
        'TRIPLEBLKARMY': '黑三兵',
        'MILDDOWNWARDS': '徐缓下跌',
        'RUSHINGAWAY': '高开出逃',
        'DOWNWARDTRIPLESTARS': '下跌三颗星',
        'DOWNWARDTRIPLESWANS': '降势三鹤',
        'TRIPLEDOWNWARDSYANG': '倒三阳',
        'JUMPHIGHTRIPLEYANG': '跳空三阳线',
        'UPWARDRESISTENCE': '升势受阻',
        'UPWARDPAUSE': '升势停顿',
        'LAMPYANG': '阳线瘸腿形',
        'BLKREDBLK': '两黑夹一红',
        'LONGCROSS': '长十字线',
        'PROPELLER': '螺旋桨',
        'EOFUPWARD': '涨势尽头线',
        'EOFDOWNWARD': '跌势尽头线',
        'PREGNANTYANG': '身怀六甲阳包阴',
        'PREGNANTYIN': '身怀六甲阴包阳',
        'TWOREDONEBLACK': '两红夹一黑',
        'LOWERSHADOW': '下影线',
        'BOXLENGTH': '实体长',
    }
    result_list = []
    pool = mp.Pool()
    for s in symbol_dict.symbol_list:
        pool.apply_async(_calc_score, args=(s, symbol_dict, date), callback=result_list.append)
    pool.close()
    pool.join()

    r = pd.DataFrame(result_list)
    r.to_csv(out_path, index=False)


def _calc_score(s, symbol_dict, date):
    try:
        logging("score", "applied_%s" % s)
        symbol_str = symbol_dict.market_symbol_of_stock(s)
        name = symbol_dict.name_dict.get(s)
        a = DayLevelSummary(s, date, symbol_str, name)
        a.load_file()
        a.merge_data()
        res = a.get_result()
        score_dict = {'QUICK_BUYPOINT|GOLDCROSS520': 0.35714250433503475,
                      'QUICK_BUYPOINT|UPWARDTWOSTARS': 0.39778851884548166,
                      'QUICK_BUYPOINT|JUMPUPWARDYANG': 0.39990296753986326, 'QUICK_BUYPOINT|TSHAPE': 0.275087330568556,
                      'QUICK_BUYPOINT|BLKREDBLK': 0.44619630844528685,
                      'QUICK_BUYPOINT|TRIPLEBLKARMY': 0.26489488861196087,
                      'QUICK_BUYPOINT|PROPELLER': 0.36069967887173054, 'QUICK_BUYPOINT|RAISINGSUN': 0.48258350964926094,
                      'QUICK_BUYPOINT|EOFDOWNWARD': 0.37002970356597287,
                      'QUICK_BUYPOINT|HOPEOFDAWN': 0.46737830763555765,
                      'QUICK_BUYPOINT|CROSS': 0.3041070003885104, 'QUICK_BUYPOINT|LOSECROSS510': 0.3913124422246791,
                      'QUICK_BUYPOINT|HEADSFEETYANG': 0.37273562238680935,
                      'QUICK_BUYPOINT|GOLDCROSS1020': 0.3488525179657613, 'QUICK_BUYPOINT|MIDK': 0.39717013180597494,
                      'QUICK_BUYPOINT|JUMPDOWNWARDTHREESTARS': 0.18932482345318427,
                      'QUICK_BUYPOINT|MAALIGNDOWNWARD': 0.36761049104789767,
                      'QUICK_BUYPOINT|MILDDOWNWARDS': 0.4105465375089931,
                      'QUICK_BUYPOINT|JUMPLOWOPEN': 0.3818808185999626,
                      'QUICK_BUYPOINT|ONESHAPE': 0.6431629942446192, 'QUICK_BUYPOINT|HAMMER': 0.3275531139748295,
                      'QUICK_BUYPOINT|DOWNWARDTRIPLESTARS': 0.06304808711573671,
                      'QUICK_BUYPOINT|SHOOTINGSTAR': 0.3878771084215621,
                      'QUICK_BUYPOINT|TWOREDONEBLACK': 0.42386713106068596,
                      'QUICK_BUYPOINT|HEADSFEETYIN': 0.3688485026613727, 'QUICK_BUYPOINT|EOFUPWARD': 0.4011345020838225,
                      'QUICK_BUYPOINT|TWILICROSS': 0.06959622241495615,
                      'QUICK_BUYPOINT|LOSEEVERYTHING': 0.3648834112969763,
                      'QUICK_BUYPOINT|REVERSETSHAPE': 0.2655410087326827,
                      'QUICK_BUYPOINT|MORNINGCROSS': 0.08664835694323987,
                      'QUICK_BUYPOINT|TRIPLECROWS': 0.1124588719558364,
                      'QUICK_BUYPOINT|UPWARDPAUSE': 0.41187842630276894,
                      'QUICK_BUYPOINT|TWILISTAR': 0.37235438263191967,
                      'QUICK_BUYPOINT|LARGEK': 0.4492362091658933,
                      'QUICK_BUYPOINT|TRIPLEDOWNWARDSYANG': 0.008094825093957791,
                      'QUICK_BUYPOINT|LOSEVALLEY': 0.36432574832727593,
                      'QUICK_BUYPOINT|TRIPLEREDARMY': 0.28341160763743994,
                      'QUICK_BUYPOINT|HANGWIRE': 0.3275531139748295, 'QUICK_BUYPOINT|REVERSEHAMMER': 0.3878771084215621,
                      'QUICK_BUYPOINT|DRAGONOUT': 0.3878132383266897,
                      'QUICK_BUYPOINT|FRIENDLYPUSHBACK': 0.348176359472977,
                      'QUICK_BUYPOINT|DOWNWARDCOVER': 0.2693041804490204,
                      'QUICK_BUYPOINT|LOSECROSS520': 0.3654521591763239,
                      'QUICK_BUYPOINT|LONGCROSS': 0.3402207241539418,
                      'QUICK_BUYPOINT|MAALIGNUPWARD': 0.3997194383847155,
                      'QUICK_BUYPOINT|DOUBLECROWS': 0.1512768622916064,
                      'QUICK_BUYPOINT|CONTINUETHREEJUMPYIN': 0.3971654457777617,
                      'QUICK_BUYPOINT|GOLDCROSS510': 0.3786569163479664,
                      'QUICK_BUYPOINT|GOLDVALLEY': 0.3374444045046236,
                      'QUICK_BUYPOINT|UPWARDRESISTENCE': 0.39143832792300276,
                      'QUICK_BUYPOINT|LAMPYANG': 0.35416342025789355, 'QUICK_BUYPOINT|JUMPUPWARD': 0.3912770413602981,
                      'QUICK_BUYPOINT|TRIPLEUPWARDS': 0.07266069191481159, 'QUICK_BUYPOINT|SMALLK': 0.3422467447459768,
                      'QUICK_BUYPOINT|RUSHINGAWAY': 0.0, 'QUICK_BUYPOINT|MORNINGSTAR': 0.3534690147916702,
                      'QUICK_BUYPOINT|PREGNANTYANG': 0.3697257109044533,
                      'QUICK_BUYPOINT|FLATFLOOR': 0.32100146050142997,
                      'QUICK_BUYPOINT|FRIENDLYFIRE': 0.0, 'QUICK_BUYPOINT|JUMPHIGHTRIPLEYANG': 0.40549272689342103,
                      'QUICK_BUYPOINT|JUMPHIGHOPEN': 0.41676581946930447,
                      'QUICK_BUYPOINT|INCOMINGCLOUDS': 0.43140396152850896,
                      'QUICK_BUYPOINT|FLATROOF': 0.3199121393513137,
                      'QUICK_BUYPOINT|DOWNWARDTRIPLESWANS': 0.1917076226269636,
                      'QUICK_BUYPOINT|PREGNANTYIN': 0.3994077689688982, 'QUICK_BUYPOINT|HEAVYRAIN': 0.4355045697831692,
                      'QUICK_BUYPOINT|LOSECROSS1020': 0.3583432920306435}
        score = 0
        for target in score_dict.keys():
            try:
                ori_turnover = res['turnover'].tolist()[0]
                if ori_turnover > 20:
                    ori_turnover = 15 - math.log(ori_turnover / 20)
                turnover = ori_turnover / 25
            except IndexError:
                turnover = 0
            score += score_dict[target] * (1 + turnover) if res[target.split("|")[1]].tolist()[0] else 0
        return {"symbol": symbol_str, "score": score}
    except FileNotFoundError:
        return {}


def summary_all(date, out_path):
    symbol_dict = SymbolListHDL()
    symbol_dict.load()
    result = pd.DataFrame()
    for s in symbol_dict.symbol_list:
        try:
            logging("summary", "applied_%s" % s)
            symbol_str = symbol_dict.market_symbol_of_stock(s)
            name = symbol_dict.name_dict.get(s)

            a = DayLevelSummary(s, date, symbol_str, name)
            a.load_file()
            a.merge_data()
            a.rename()
            res = a.get_result()
            result = pd.concat([result, res], axis=0)
        except FileNotFoundError:
            continue
    result = result.drop_duplicates(['代码'], keep='last')
    result.to_csv(out_path)


if __name__ == '__main__':
    summary_all(sys.argv[1], sys.argv[2])
