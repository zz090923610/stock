import os
from stock.common.variables import COMMON_VARS_OBJ
from stock.common.file_operation import mkdirs

if __name__ == '__main__':
    mkdirs(None)
    from stock.common.time_util import update_market_open_date_list

    update_market_open_date_list()
    from stock.common.basic_stock_info_fetcher import BasicInfoUpdater
    os.system('wget http://115.28.142.56/plots/dates/market_close_days_2017.pickle -O /tmp/market_close_days_2017.pickle'
              ' && mv /tmp/market_close_days_2017.pickle %s/dates/' % COMMON_VARS_OBJ.stock_data_root)
    a = BasicInfoUpdater()
    a.update()
