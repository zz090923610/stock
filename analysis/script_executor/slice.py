import os

import itertools
import pandas as pd
import multiprocessing as mp

from analysis.script_executor.TranslateHdl import TranslateHdl
from configs.path import DIRs
from tools.io import logging


def slice_one(in_path, date):
    try:
        result = pd.read_csv(in_path)
        result = result[result['date'] == date]
        logging("SLICING", "sliced %s" % in_path)
        return result
    except Exception as e:
        logging("ERROR", "slicing %s %s" % (in_path, e))
        return None


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


def validate_output_path(output_file_name, date):
        return os.path.join(DIRs.get("SLICE"), "%s_%s.csv" % (output_file_name, date))


def slice_all(input_path, out_path, date, rename):
    input_path = validate_input_path(input_path)
    out_path = validate_output_path(out_path, date)
    from tools.symbol_list_china_hdl import SymbolListHDL
    symbol_dict = SymbolListHDL()
    symbol_dict.load()
    result_list = []

    pool = mp.Pool()
    for i in symbol_dict.symbol_list:
        pool.apply_async(slice_one, args=(os.path.join(input_path, "%s.csv" % i), date), callback=result_list.append)
    pool.close()
    pool.join()
    result = pd.DataFrame()
    for i in result_list:
        result = pd.concat([result, i], axis=0)
    try:
        result = result.drop('Unnamed: 0', 1)
    except Exception as e:
        pass
    columns = []
    trans = TranslateHdl()
    trans.load()
    for c in trans.order_list:
        if c in result.columns.values:
            columns.append(c)
    for c in result.columns.values:
        if c not in columns:
            columns.append(c)
    result.to_csv(out_path, index=False, columns=columns)
    if rename:
        rename_csv(out_path)


def rename_csv(file_path):
    data = pd.read_csv(file_path)
    translate_hdl = TranslateHdl()
    translate_hdl.load()
    data = data.rename(index=str, columns=translate_hdl.dict)
    data.to_csv(file_path, index=False)
