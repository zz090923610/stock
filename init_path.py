
from stock.common.file_operation import mkdirs


if __name__ == '__main__':
    mkdirs(None)
    from stock.common.time_util import update_market_open_date_list

    update_market_open_date_list()
#    from stock.common.basic_stock_info_fetcher import BasicInfoUpdater
#
#    a=BasicInfoUpdater()
#    a.update()