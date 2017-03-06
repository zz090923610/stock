import sys

from stock.common import variables, time_util
from stock.data import data_news_handler

if __name__ == '__main__':
    if sys.argv[1] == '--td':
        time_util.main()
    elif sys.argv[1] == '--news':
        data_news_handler.main()
