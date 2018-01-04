# DEPENDENCY( pandas )
import os

import math
import pandas as pd
import sys

from analysis.script_executor.TranslateHdl import TranslateHdl
from analysis.script_executor.statistics import ConditionalStatisticsHdl
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
        self.result = pd.DataFrame
        self.translate_hdl = TranslateHdl()
        self.translate_hdl.load()

    def load_file(self):
        summary_path = os.path.join(DIRs.get("QA"), "summary", self.symbol + ".csv")
        self.result = pd.read_csv(summary_path)
        try:
            self.result = self.result[self.result['date'] == self.target_date]
        except KeyError:
            pass

    def rename(self):
        self.result['symbol'] = self.symbol_str
        self.result['name'] = self.name_str

        self.result = self.result.rename(index=str, columns=self.translate_hdl.dict)

    def get_result(self):
        return self.result


def calc_score(date, out_path):
    symbol_dict = SymbolListHDL()
    symbol_dict.load()
    result_list = []
    pool = mp.Pool()
    cond_buy = ConditionalStatisticsHdl("", 'merged', 'cond_buy')
    cond_buy.load()
    cond_sell = ConditionalStatisticsHdl("", 'merged', 'cond_sell')
    cond_sell.load()
    for s in symbol_dict.symbol_list:
        pool.apply_async(_calc_score,
                         args=(s, symbol_dict, date, cond_buy.probability_dict, cond_sell.probability_dict),
                         callback=result_list.append)
    pool.close()
    pool.join()
    result_list = [l for l in result_list if len(l.keys()) != 0]
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='score', ascending=False)
    r.to_csv(out_path, index=False)


def _calc_score(s, symbol_dict, date, cond_buy_dict, cond_sell_dict):
    try:
        logging("score", "applied_%s" % s)
        symbol_str = symbol_dict.market_symbol_of_stock(s)
        name = symbol_dict.name_dict.get(s)
        a = DayLevelSummary(s, date, symbol_str, name)
        a.load_file()
        res = a.get_result()
        if len(res.index) == 0:
            logging('WARNING', "no data for %s" % s)
            return {}
        upwardscore_dict = cond_buy_dict
        downward_score_dict = cond_sell_dict
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


def calc_score_vol_ratio(date, out_path):
    symbol_dict = SymbolListHDL()
    symbol_dict.load()
    result_list = []
    pool = mp.Pool()
    for s in symbol_dict.symbol_list:
        pool.apply_async(_calc_score_vol_ration, args=(s, symbol_dict, date), callback=result_list.append)
    pool.close()
    pool.join()
    result_list = [l for l in result_list if len(l.keys()) != 0]
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='score_vol_ratio', ascending=False)
    r.to_csv(out_path, index=False)


def _calc_score_vol_ration(s, symbol_dict, date):
    try:
        logging("score", "applied_%s" % s)
        symbol_str = symbol_dict.market_symbol_of_stock(s)
        name = symbol_dict.name_dict.get(s)
        a = DayLevelSummary(s, date, symbol_str, name)
        a.load_file()
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

        try:
            ori_prev_turnover = res['PREV_TURNOVER'].tolist()[0]
            if ori_prev_turnover > 20:
                ori_prev_turnover = 15 - math.log(ori_prev_turnover / 20)
            prev_turnover = ori_prev_turnover / 25
        except IndexError:
            prev_turnover = 0

        for target in upwardscore_dict.keys():
            score += (upwardscore_dict[target] * turnover / prev_turnover / 2 * (1 + turnover) if
            res[target.split("|")[1]].tolist()[0] else 0)
        for target in downward_score_dict.keys():
            score -= (downward_score_dict[target] if res[target.split("|")[1]].tolist()[0] else 0)
        if score == 0:
            score -= 5
        return {"symbol": symbol_str, "score_vol_ratio": score}
    except FileNotFoundError:
        return {}


def calc_score_amount(date, out_path):
    symbol_dict = SymbolListHDL()
    symbol_dict.load()
    result_list = []
    pool = mp.Pool()
    for s in symbol_dict.symbol_list:
        pool.apply_async(_calc_score_amount, args=(s, symbol_dict, date), callback=result_list.append)
    pool.close()
    pool.join()
    result_list = [l for l in result_list if len(l.keys()) != 0]
    r = pd.DataFrame(result_list)
    r = r.sort_values(by='score_amount', ascending=False)
    r.to_csv(out_path, index=False)


def _calc_score_amount(s, symbol_dict, date):
    try:
        logging("score", "applied_%s" % s)
        symbol_str = symbol_dict.market_symbol_of_stock(s)
        name = symbol_dict.name_dict.get(s)
        a = DayLevelSummary(s, date, symbol_str, name)
        a.load_file()
        res = a.get_result()
        if len(res.index) == 0:
            logging('WARNING', "no data for %s" % s)
            return {}
        try:
            amount_scalar = res['AMOUNT_SCALAR'].tolist()[0]
            amount_scalar += 1
        except IndexError:
            amount_scalar = 1
        score = amount_scalar
        return {"symbol": symbol_str, "score_amount": score}
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
            a.rename()
            res = a.get_result()
            result = pd.concat([result, res], axis=0)
        except FileNotFoundError:
            continue
        except AssertionError as e:
            logging('WARNING', "merge failed %s %s" % (s, e))
    result = result.drop_duplicates(['代码'], keep='last')
    try:
        result = result.drop('Unnamed: 0', 1)
    except Exception as e:
        pass
    columns = []
    trans = TranslateHdl()
    trans.load()
    for c in trans.order_list:
        if trans.dict[c] in result.columns.values:
            columns.append(trans.dict[c])
    result = result.sort_values(by="代码", ascending=True)
    result.to_csv(out_path, index=False, columns=columns)


if __name__ == '__main__':
    summary_all(sys.argv[1], sys.argv[2])
