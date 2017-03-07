import sys

from stock.common import variables, time_util, basic_stock_info_fetcher
from stock.data import data_news_handler


if __name__ == '__main__':
    if sys.argv[1] == '--td':
        time_util.main()
    elif sys.argv[1] == '--news':
        data_news_handler.main()
    elif sys.argv[1] == '--basic':
        basic_stock_info_fetcher.main()
