import pytz
from tzlocal import get_localzone

IS_DEBUG = True


class CommonVars:
    def __init__(self, data_root=''):
        self.START_DATE = '2016-01-01'
        self.local_tz = get_localzone()
        self.china_tz = pytz.timezone('Asia/Shanghai')
        self.AGENT_LIST = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                           '0': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                           '1': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/55.0.2883.87 Safari/537.36 '
                           }
        self.DAEMON = {'time_util': {'pid_path': '/tmp/stock/daemon/pid', 'data_path':
            '/tmp/stock/daemon/data/time_util'},
                       'news_hdl': {'pid_path': '/tmp/stock/daemon/pid', 'data_path':
                           '/tmp/stock/daemon/data/news_hdl'},
                       'basic_info_hdl': {'pid_path': '/tmp/stock/daemon/pid', 'data_path':
                           '/tmp/stock/daemon/data/basic_info_hdl'}
                       }
        self.POOL_SIZE = 128
        self.NEW_STOCK_IPO_DATE_THRESHOLD = '2017-01-01'
        if data_root == '':
            self.stock_data_root = '/home/zhangzhao/data/stock_data'
        else:
            self.stock_data_root = data_root
        self.back_up_root = "%s/%s " % (self.stock_data_root, 'back_up')
        self.daily_data_root = "%s/%s " % (self.stock_data_root, 'data')
        self.tick_data_root = "%s/%s " % (self.stock_data_root, 'tick_data')
        self.important_dates_root = "%s/%s " % (self.stock_data_root, 'dates')
        self.hist_file = './.console_history'
        self.hist_file_size = 100000
        self.QA_DIR = self.stock_data_root + "/quantitative_analysis"
        self.DIR_LIST = [self.stock_data_root + "/announcements",
                         self.stock_data_root + "/back_up/tick_data",
                         self.stock_data_root + "/back_up/data",
                         self.stock_data_root + "/dates/stock_suspend_days",
                         self.stock_data_root + "/plots",
                         self.stock_data_root + "/quantitative_analysis/adl",
                         self.stock_data_root + "/quantitative_analysis/atpd",
                         self.stock_data_root + "/quantitative_analysis/atpdr",
                         self.stock_data_root + "/quantitative_analysis/buy_point",
                         self.stock_data_root + "/quantitative_analysis/lms",
                         self.stock_data_root + "/quantitative_analysis/ma",
                         self.stock_data_root + "/quantitative_analysis/perceptron",
                         self.stock_data_root + "/quantitative_analysis/perceptron_params",
                         self.stock_data_root + "/quantitative_analysis/vhf",
                         self.stock_data_root + "/report/five_days_trend",
                         self.stock_data_root + "/trade_pause_date",
                         self.stock_data_root + "/news/gov",
                         self.stock_data_root + "/news/zjh"]

    def reload(self, data_root=''):
        self.__init__(data_root)


COMMON_VARS_OBJ = CommonVars()
