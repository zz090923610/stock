
# WINDOWS_GUARANTEED

import multiprocessing as mp
import os

import pandas as pd

from analysis.script_executor.TranslateHdl import TranslateHdl
from tools.data.path_hdl import path_expand, directory_ensure, file_exist
from tools.io import logging

# DIRREG( slice )
out_dir = path_expand("slice")
directory_ensure(out_dir)


def slice_one(in_path, date):
    try:
        if not file_exist(in_path):
            logging("ERROR", "file not exist %s" % in_path)
            return None
        result = pd.read_csv(in_path)
        result = result[result['date'] == date]
        logging("SLICING", "sliced %s" % in_path)
        return result
    except Exception as e:
        logging("ERROR", "slicing %s %s" % (in_path, e))
        return None


def slice_all(input_path, out_path, date, rename):
    input_path = path_expand(input_path)
    out_path = os.path.join(out_dir, "%s_%s.csv" % (out_path, date))
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
