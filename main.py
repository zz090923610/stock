import os
import sys
import signal_daemon
from stock.common import time_util, basic_stock_info_fetcher
from stock.data import data_news_handler
from stock.trade_api import trade_api

if __name__ == '__main__':
    if sys.argv[1] == '--all':
        signal_daemon.main()
    if sys.argv[1] == '--td':
        time_util.main()
    elif sys.argv[1] == '--news':
        data_news_handler.main()
    elif sys.argv[1] == '--basic':
        basic_stock_info_fetcher.main()
    elif sys.argv[1] == '--trade':
        trade_api.main()
    elif sys.argv[1] == '--exit':
        for i in os.listdir('/tmp/stock/daemon/pid'):
            os.system('kill `cat %s/%s`' % ('/tmp/stock/daemon/pid', i))
    elif sys.argv[1] == '--touch':
        os.system("xsetwacom set `xinput list | grep 'Weida' | grep -Po '(?<=id=)[0-9]+'` MapToOutput DP1")