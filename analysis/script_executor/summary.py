# DEPENDENCY( pandas )
import os

import pandas as pd
import sys

from configs.path import DIRs
from tools.symbol_list_china_hdl import SymbolListHDL

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
            'TWOREDONEBLACK':'两红夹一黑',
            'LOWERSHADOW':'下影线',
            'BOXLENGTH':'实体长',
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
        self.result['symbol'] = self.symbol_str
        self.result['name'] = self.name_str
        self.result = self.result.rename(index=str, columns=self.translate_dict)

    def write_out_summary(self):
        self.result.to_csv('/tmp/test.csv')

    def get_result(self):
        return self.result


def summary_all(date, out_path):
    symbol_dict = SymbolListHDL()
    symbol_dict.load()
    result = pd.DataFrame()
    for s in symbol_dict.symbol_list:
        try:
            print(s)
            symbol_str = symbol_dict.market_symbol_of_stock(s)
            name = symbol_dict.name_dict.get(s)

            a = DayLevelSummary(s, date, symbol_str, name)
            a.load_file()
            a.merge_data()
            res = a.get_result()
            result = pd.concat([result, res], axis=0)
        except FileNotFoundError:
            continue
    result = result.drop_duplicates(['代码'], keep='last')
    result.to_csv(out_path)


if __name__ == '__main__':
    summary_all(sys.argv[1], sys.argv[2])
