# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

import multiprocessing as mp
import os
import pandas as pd
from analysis.script_executor.TranslateHdl import TranslateHdl
from tools.data.path_hdl import path_expand, directory_ensure, file_exist
from tools.date_util.market_calendar_cn import MktCalendar
from tools.io import logging

# USEDIR( $USER_SPECIFIED )
# REGDIR( slice )
out_dir = path_expand("slice")
directory_ensure(out_dir)
calendar = MktCalendar()


def slice_one(in_path, date):
    """
    Slice rows from in_path file with specified date
    :param in_path: string
    :param date:    string, YYYY-MM-HH
    :return:        Dataframe, rows
    """
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


# CMDEXPORT ( SLICECOMBINE {input_path} {out_path} {date} {rename} ) slice_combine
def slice_combine(input_path, out_path, date, rename):
    """
    Slice rows from every file in in_path file with specified date, then append them horizontally.
    :param input_path:  string
    :param out_path:    where to save combined file, string
    :param date:        string, YYYY-MM-HH
    :param rename:      whether to rename columns using translate_dict before output, boolean
    """
    date = calendar.parse_date(date)
    rename = True if rename == 'TRUE' else False
    input_path = path_expand(input_path)
    out_path = os.path.join(out_dir, "%s_%s.csv" % (out_path, date))
    from tools.data.mkt_chn.symbol_list_china_hdl import SymbolListHDL
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
    # noinspection PyBroadException,PyUnusedLocal
    try:
        result = result.drop('Unnamed: 0', 1)
    except Exception as e:
        pass
    columns = []
    trans = TranslateHdl()
    trans.load()
    # sort column titles using order info from translate dict.
    for c in trans.order_list:
        if c in result.columns.values:  # if titles are not translated
            columns.append(c)
    for c in result.columns.values:  # if titles are translated
        if c not in columns:
            columns.append(c)
    result.to_csv(out_path, index=False, columns=columns)
    if rename:
        rename_column_title(out_path)


# CMDEXPORT ( RENAMECOL {file_path} ) rename_column_title
def rename_column_title(file_path):
    """
    Export this function to Control Framework, a control command like:
        RENAMECOL OHCL/000001.csv
    can be added to .ctrl batch file to save some work.

    Rename columns of a csv file using translate_dict inplace.
    :param file_path:   string
    """
    data = pd.read_csv(file_path)
    translate_hdl = TranslateHdl()
    translate_hdl.load()
    data = data.rename(index=str, columns=translate_hdl.dict)
    data.to_csv(file_path, index=False)
