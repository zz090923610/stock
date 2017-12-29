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
    result_list = []
    pool = mp.Pool()
    for s in symbol_dict.symbol_list:
        pool.apply_async(_calc_score, args=(s, symbol_dict, date), callback=result_list.append)
    pool.close()
    pool.join()
    result_list = [l for l in result_list if len(l.keys()) != 0]
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='score', ascending=False)
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
        if len(res.index) == 0:
            logging('WARNING', "no data for %s" % s)
            return {}
        upwardscore_dict = {
            'QUICK_BUYPOINT|DOWNWARDTRIPLESWANS': 0.1905855725705481, 'QUICK_BUYPOINT|PREGNANTYIN': 0.38270520772351124,
            'QUICK_BUYPOINT|GOLDCROSS520': 0.35408616194100284, 'QUICK_BUYPOINT|UPWARDRESISTENCE': 0.39416727661014744,
            'QUICK_BUYPOINT|GOLDCROSS510': 0.38234275487233077, 'QUICK_BUYPOINT|JUMPHIGHOPEN': 0.41575194463029624,
            'QUICK_BUYPOINT|LOSEEVERYTHING': 0.35431376463734066, 'QUICK_BUYPOINT|JUMPUPWARD': 0.4047883238261734,
            'QUICK_BUYPOINT|DOWNWARDTRIPLESTARS': 0.057329288259655206,
            'QUICK_BUYPOINT|JUMPDOWNWARDTHREESTARS': 0.18762502145195006,
            'QUICK_BUYPOINT|DOUBLECROWS': 0.16255417509390346, 'QUICK_BUYPOINT|TRIPLECROWS': 0.10750608824864819,
            'QUICK_BUYPOINT|JUMPUPWARDYANG': 0.40384912234229764, 'QUICK_BUYPOINT|HEADSFEETYIN': 0.3818771262669915,
            'QUICK_BUYPOINT|MAALIGNDOWNWARD': 0.3650566978616487, 'QUICK_BUYPOINT|LONGCROSS': 0.33828436884634516,
            'QUICK_BUYPOINT|EOFUPWARD': 0.4078845624972309, 'QUICK_BUYPOINT|GOLDVALLEY': 0.3323179741377699,
            'QUICK_BUYPOINT|FLATROOF': 0.3215581886524042, 'QUICK_BUYPOINT|DOWNWARDCOVER': 0.28115559357974923,
            'QUICK_BUYPOINT|RAISINGSUN': 0.4572722580396098, 'QUICK_BUYPOINT|FRIENDLYPUSHBACK': 0.37224502839931906,
            'QUICK_BUYPOINT|INCOMINGCLOUDS': 0.4425301256771677, 'QUICK_BUYPOINT|PREGNANTYANG': 0.37589485072085477,
            'QUICK_BUYPOINT|REVERSEHAMMER': 0.39144234581533077, 'QUICK_BUYPOINT|RUSHINGAWAY': 0.0,
            'QUICK_BUYPOINT|LOSECROSS520': 0.3549205624673164, 'QUICK_BUYPOINT|LAMPYANG': 0.3463537738721172,
            'QUICK_BUYPOINT|MAALIGNUPWARD': 0.39879371013899967, 'QUICK_BUYPOINT|FRIENDLYFIRE': 0.0,
            'QUICK_BUYPOINT|JUMPLOWOPEN': 0.3759728927462323, 'QUICK_BUYPOINT|LOSECROSS1020': 0.35778443851677916,
            'QUICK_BUYPOINT|REVERSETSHAPE': 0.4169554858445353, 'QUICK_BUYPOINT|CROSS': 0.3057464135864725,
            'QUICK_BUYPOINT|HOPEOFDAWN': 0.44345749234990095, 'QUICK_BUYPOINT|DRAGONOUT': 0.3751150552623674,
            'QUICK_BUYPOINT|GOLDCROSS1020': 0.3551575253354787, 'QUICK_BUYPOINT|HAMMER': 0.3277754824089353,
            'QUICK_BUYPOINT|TRIPLEREDARMY': 0.29730050911980443, 'QUICK_BUYPOINT|TSHAPE': 0.25379058332726917,
            'QUICK_BUYPOINT|CONTINUETHREEJUMPYIN': 0.41626886629053655, 'QUICK_BUYPOINT|TWILISTAR': 0.36274301399265274,
            'QUICK_BUYPOINT|EOFDOWNWARD': 0.369347167389515, 'QUICK_BUYPOINT|TRIPLEDOWNWARDSYANG': 0.008379081190407396,
            'QUICK_BUYPOINT|TWILICROSS': 0.06729268997399596, 'QUICK_BUYPOINT|TWOREDONEBLACK': 0.4054615838952108,
            'QUICK_BUYPOINT|BLKREDBLK': 0.44872289593512926, 'QUICK_BUYPOINT|MORNINGCROSS': 0.08991139362419338,
            'QUICK_BUYPOINT|LOSECROSS510': 0.3846662031279021, 'QUICK_BUYPOINT|MILDDOWNWARDS': 0.4022453959326362,
            'QUICK_BUYPOINT|HEADSFEETYANG': 0.3641060721042533, 'QUICK_BUYPOINT|SHOOTINGSTAR': 0.39144234581533077,
            'QUICK_BUYPOINT|HEAVYRAIN': 0.44402621831468125, 'QUICK_BUYPOINT|UPWARDTWOSTARS': 0.37871128023115724,
            'QUICK_BUYPOINT|UPWARDPAUSE': 0.4312424790494826, 'QUICK_BUYPOINT|LOSEVALLEY': 0.3554550991287603,
            'QUICK_BUYPOINT|TRIPLEUPWARDS': 0.07358181643070404,
            'QUICK_BUYPOINT|JUMPHIGHTRIPLEYANG': 0.4386844893496753, 'QUICK_BUYPOINT|PROPELLER': 0.36234920859755476,
            'QUICK_BUYPOINT|MORNINGSTAR': 0.3500587551839907, 'QUICK_BUYPOINT|FLATFLOOR': 0.3200194297847053,
            'QUICK_BUYPOINT|TRIPLEBLKARMY': 0.25788707384817655, 'QUICK_BUYPOINT|HANGWIRE': 0.3277754824089353}
        downward_score_dict = {
            'QUICK_SELLPOINT|FRIENDLYPUSHBACK': 0.5404356438450625, 'QUICK_SELLPOINT|UPWARDPAUSE': 0.5694544668371698,
            'QUICK_SELLPOINT|CROSS': 0.4208703680100474, 'QUICK_SELLPOINT|TSHAPE': 0.3568599222235542,
            'QUICK_SELLPOINT|HEAVYRAIN': 0.6193826533806998, 'QUICK_SELLPOINT|PREGNANTYIN': 0.48496525176658045,
            'QUICK_SELLPOINT|JUMPDOWNWARDTHREESTARS': 0.3286950833685882,
            'QUICK_SELLPOINT|HEADSFEETYANG': 0.5481662804248675, 'QUICK_SELLPOINT|MILDDOWNWARDS': 0.46049992506280313,
            'QUICK_SELLPOINT|RAISINGSUN': 0.530011243761766, 'QUICK_SELLPOINT|EOFDOWNWARD': 0.48119901034830276,
            'QUICK_SELLPOINT|BLKREDBLK': 0.6044093486978899, 'QUICK_SELLPOINT|JUMPUPWARDYANG': 0.5493897401227008,
            'QUICK_SELLPOINT|JUMPLOWOPEN': 0.5261370142214983, 'QUICK_SELLPOINT|FLATFLOOR': 0.43396343854500713,
            'QUICK_SELLPOINT|DOUBLECROWS': 0.19394683617451602, 'QUICK_SELLPOINT|HOPEOFDAWN': 0.5497874051904974,
            'QUICK_SELLPOINT|MORNINGCROSS': 0.12180005778676682, 'QUICK_SELLPOINT|UPWARDTWOSTARS': 0.4456949335541885,
            'QUICK_SELLPOINT|TWILICROSS': 0.07474718289511703, 'QUICK_SELLPOINT|EOFUPWARD': 0.4930844071283533,
            'QUICK_SELLPOINT|MORNINGSTAR': 0.48471171111653155, 'QUICK_SELLPOINT|FLATROOF': 0.41842865924931305,
            'QUICK_SELLPOINT|HEADSFEETYIN': 0.4800218029130862,
            'QUICK_SELLPOINT|JUMPHIGHTRIPLEYANG': 0.47140890103715444, 'QUICK_SELLPOINT|HANGWIRE': 0.47778436515344685,
            'QUICK_SELLPOINT|DRAGONOUT': 0.5348289896432342, 'QUICK_SELLPOINT|TRIPLECROWS': 0.09461069605536523,
            'QUICK_SELLPOINT|MAALIGNDOWNWARD': 0.4885962865683421, 'QUICK_SELLPOINT|HAMMER': 0.47778436515344685,
            'QUICK_SELLPOINT|TRIPLEBLKARMY': 0.38341861271467303, 'QUICK_SELLPOINT|INCOMINGCLOUDS': 0.6061745987210155,
            'QUICK_SELLPOINT|TRIPLEUPWARDS': 0.09390349609939322, 'QUICK_SELLPOINT|MAALIGNUPWARD': 0.5497314486143838,
            'QUICK_SELLPOINT|DOWNWARDCOVER': 0.3498439944914954,
            'QUICK_SELLPOINT|CONTINUETHREEJUMPYIN': 0.5286172562068258,
            'QUICK_SELLPOINT|LOSEEVERYTHING': 0.47502617759057086, 'QUICK_SELLPOINT|PROPELLER': 0.5008174080141683,
            'QUICK_SELLPOINT|TRIPLEDOWNWARDSYANG': 0.00722334585379948,
            'QUICK_SELLPOINT|TWOREDONEBLACK': 0.611697019477196, 'QUICK_SELLPOINT|RUSHINGAWAY': 0.0,
            'QUICK_SELLPOINT|LAMPYANG': 0.5400387170835853, 'QUICK_SELLPOINT|LOSECROSS520': 0.5142821164607415,
            'QUICK_SELLPOINT|LOSECROSS510': 0.4914612751850981, 'QUICK_SELLPOINT|TRIPLEREDARMY': 0.39057746858901027,
            'QUICK_SELLPOINT|FRIENDLYFIRE': 0.0, 'QUICK_SELLPOINT|PREGNANTYANG': 0.5348228218164652,
            'QUICK_SELLPOINT|TWILISTAR': 0.3897404411056534, 'QUICK_SELLPOINT|JUMPUPWARD': 0.5213920971628274,
            'QUICK_SELLPOINT|LONGCROSS': 0.41838375916676995,
            'QUICK_SELLPOINT|DOWNWARDTRIPLESTARS': 0.12245979004141386,
            'QUICK_SELLPOINT|LOSEVALLEY': 0.5105885904096393, 'QUICK_SELLPOINT|GOLDCROSS510': 0.5034070705228144,
            'QUICK_SELLPOINT|SHOOTINGSTAR': 0.4789251151493531, 'QUICK_SELLPOINT|GOLDVALLEY': 0.5201682064296835,
            'QUICK_SELLPOINT|JUMPHIGHOPEN': 0.5049444341132441, 'QUICK_SELLPOINT|REVERSEHAMMER': 0.4789251151493531,
            'QUICK_SELLPOINT|LOSECROSS1020': 0.5365740828060034, 'QUICK_SELLPOINT|UPWARDRESISTENCE': 0.5171075358951319,
            'QUICK_SELLPOINT|DOWNWARDTRIPLESWANS': 0.25548492728498534,
            'QUICK_SELLPOINT|GOLDCROSS1020': 0.5044866108996416, 'QUICK_SELLPOINT|REVERSETSHAPE': 0.37023305036162624,
            'QUICK_SELLPOINT|GOLDCROSS520': 0.5098471210604967}
        score = 0
        try:
            ori_turnover = res['turnover'].tolist()[0]
            if ori_turnover > 20:
                ori_turnover = 15 - math.log(ori_turnover / 20)
            turnover = ori_turnover / 25
        except IndexError:
            turnover = 0
        for target in upwardscore_dict.keys():
            score += (upwardscore_dict[target] * (1 + turnover) if res[target.split("|")[1]].tolist()[0] else 0)
        for target in downward_score_dict.keys():
            score -= (downward_score_dict[target] if res[target.split("|")[1]].tolist()[0] else 0)
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
        except AssertionError as e:
            logging('WARNING', "merge failed %s %s" % (s, e))
    result = result.drop_duplicates(['代码'], keep='last')
    result.to_csv(out_path)


if __name__ == '__main__':
    summary_all(sys.argv[1], sys.argv[2])
