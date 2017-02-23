import pytz
from tzlocal import get_localzone

START_DATE = '2016-01-01'
# get local timezone
local_tz = get_localzone()

china_tz = pytz.timezone('Asia/Shanghai')
AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
         '1': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
         }
POOL_SIZE = 128
NEW_STOCK_IPO_DATE_THRESHOLD = '2017-01-01'
stock_data_root = '../stock_data'
back_up_root = "%s/%s " % (stock_data_root, 'back_up')
daily_data_root = "%s/%s " % (stock_data_root, 'data')
tick_data_root = "%s/%s " % (stock_data_root, 'tick_data')
important_dates_root = "%s/%s " % (stock_data_root, 'dates')

hist_file = './.console_history'
hist_file_size = 100000
DIR_LIST = ["../stock_data/announcements",
            "../stock_data/back_up/tick_data",
            "../stock_data/back_up/data",
            "../stock_data/dates/stock_suspend_days",
            "../stock_data/plots",
            "../stock_data/qa/adl",
            "../stock_data/qa/atpd",
            "../stock_data/qa/atpdr",
            "../stock_data/qa/buy_point",
            "../stock_data/qa/lms",
            "../stock_data/qa/ma",
            "../stock_data/qa/perceptron",
            "../stock_data/qa/perceptron_params",
            "../stock_data/qa/vhf",
            "../stock_data/report/five_days_trend",
            "../stock_data/trade_pause_date",
            "../stock_data/news/gov",
            "../stock_data/news/zjh"]
