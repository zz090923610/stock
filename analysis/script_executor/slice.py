import os

import itertools
import pandas as pd
import multiprocessing as mp

from analysis.script_executor.TranslateHdl import TranslateHdl
from configs.path import DIRs
from tools.io import logging


# TODO currently ugly implementation
class DayLevelSummary:
    def __init__(self, symbol, date, symbol_str, name_str):
        self.symbol = symbol
        self.target_date = date
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
        self.result = self.result.rename(index=str, columns=self.translate_hdl.dict)

    def get_result(self):
        return self.result


def slice_one(in_path, date):
    result = pd.read_csv(in_path)
    try:
        result = result[result['date'] == date]
    except KeyError:
        pass
    return result


def validate_input_path(input_path):
    if os.path.isfile(input_path):
        return input_path
    elif input_path.split('/')[0] in os.listdir(DIRs.get("QA")):
        if os.path.exists(DIRs.get("QA") + '/' + input_path):
            return DIRs.get("QA") + '/' + input_path
    elif input_path.split('/')[0] in os.listdir(DIRs.get("DATA_ROOT")):
        if os.path.exists(DIRs.get("DATA_ROOT") + '/' + input_path):
            return DIRs.get("DATA_ROOT") + '/' + input_path
    else:
        return input_path


def slice_all(input_path, out_path, date):
    input_path = validate_input_path(input_path)
    from tools.symbol_list_china_hdl import SymbolListHDL
    symbol_dict = SymbolListHDL()
    symbol_dict.load()
    result = pd.DataFrame()
    pool = mp.Pool()
    for i in dir_list:

    pool.close()
    pool.join()
    for s in symbol_dict.symbol_list:
        full_path = os.path.join(input_path, "%s.csv" % s)
        pool.apply_async(execute_script, args=(input_dir + '/' + i, script, output_dir + '/' + i, output_cols))
        try:
            logging("slicing", full_path)

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
