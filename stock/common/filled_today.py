import os
import shutil

import xlrd
import pandas as pd
from stock.common.variables import COMMON_VARS_OBJ


# noinspection PyShadowingNames
def back_to_float(target_list, col_list):
    for line in target_list:
        for col in col_list:
            line[col] = float(line[col])
    return target_list


def csv_from_excel_filled_today():
    # FIXME buggy filled today and entrust today may not match
    try:
        wb = xlrd.open_workbook('%s/filled_today.xls' % COMMON_VARS_OBJ.stock_data_root, formatting_info=True)
    except FileNotFoundError:
        return
    sheet = wb.sheet_names()[0]
    sh = wb.sheet_by_name(sheet)

    b = sh.row_values(0)
    date = [f for f in b if f != ''][0].split(' ')[1]
    formatted_date = '%s-%s-%s' % (date[:4], date[4:6], date[6:8])

    dict_list = []
    title_list = sh.row_values(1)
    if sh.nrows > 2:
        for rownum in range(2, sh.nrows):
            tmp_dict = {}
            for (col_name, col_val) in zip(title_list, sh.row_values(rownum)):
                tmp_dict[col_name] = col_val
            dict_list.append(tmp_dict)

    col_list = ['成交价', '成交额', '成交数量']
    dict_list = back_to_float(dict_list, col_list)

    # load entrust today
    try:
        wb = xlrd.open_workbook('%s/entrust_today.xls' % COMMON_VARS_OBJ.stock_data_root, formatting_info=True)
    except FileNotFoundError:
        return

    sheet = wb.sheet_names()[0]
    sh = wb.sheet_by_name(sheet)

    b = sh.row_values(0)
    entrust_list = []
    title_list = sh.row_values(1)
    if sh.nrows > 2:
        for row_num in range(2, sh.nrows):
            tmp_dict = {}
            for (col_name, col_val) in zip(title_list, sh.row_values(row_num)):
                tmp_dict[col_name] = col_val
            entrust_list.append(tmp_dict)

    for (idx, line) in enumerate(dict_list):
        if entrust_list[idx]['类型'] == '买入':
            line['业务名称'] = '证券买入'
        elif entrust_list[idx]['类型'] == '卖出':
            line['业务名称'] = '证券卖出'

    a = pd.DataFrame(dict_list)
    a = a[a['交易类型'] == '普通成交']
    a.to_csv('%s/filled_today/%s.csv' % (COMMON_VARS_OBJ.stock_data_root, formatted_date), index=False)
