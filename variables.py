import pytz
from tzlocal import get_localzone

START_DATE = '2012-01-01'
# get local timezone
local_tz = get_localzone()

china_tz = pytz.timezone('Asia/Shanghai')
AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}
POOL_SIZE = 128

stock_data_root = '../stock_data/%s'
back_up_root = stock_data_root % 'back_up'
daily_data_root = stock_data_root % 'data'
tick_data_root = stock_data_root % 'tick_data'
important_dates_root = stock_data_root % 'dates'

hist_file = './.console_history'
hist_file_size = 100000

