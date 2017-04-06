import pandas as pd
import xlrd

from stock.common.variables import COMMON_VARS_OBJ


# noinspection PyBroadException
def back_to_str(target_list, col_list):
    for line in target_list:
        for col in col_list:
            try:
                line[col] = str(int(line[col]))
            except:
                line[col] = str(line[col])
            if (col == '证券代码') & (len(line[col]) != 6):
                line[col] = '0' * (6 - len(line[col])) + line[col]
    return target_list


def csv_from_excel(in_xls):
    wb = xlrd.open_workbook(in_xls, formatting_info=True, encoding_override="gbk")
    sheet = wb.sheet_names()[0]
    sh = wb.sheet_by_name(sheet)
    dict_list = []
    title_list = sh.row_values(6)
    if sh.nrows > 7:
        for row_num in range(7, sh.nrows):
            tmp_dict = {}
            for (col_name, col_val) in zip(title_list, sh.row_values(row_num)):
                tmp_dict[col_name] = col_val
            dict_list.append(tmp_dict)

    col_list = ['合同号', '证券代码', '资金账号', '交收日期']
    dict_list = back_to_str(dict_list, col_list)

    a = pd.DataFrame(dict_list)

    a = a.rename(columns={'交收日期': '成交日期', '合同号': '成交编号', '交易类别': '业务名称', '证券余额': '剩余数量', '资金发生数': '清算金额',
                          '资金余额': '剩余金额', '清算费': '结算费'})
    a.to_csv('%s/trade_details.csv' % COMMON_VARS_OBJ.stock_data_root)
    # os.chmod('%s/trade_details.csv' % COMMON_VARS_OBJ.stock_data_root, 777)
