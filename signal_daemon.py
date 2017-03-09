import os
import subprocess

import schedule
import time
import daemon.pidfile
from stock.common.common_func import simple_publish
from stock.common.time_util import update_market_open_date_list
from stock.common.variables import COMMON_VARS_OBJ
from stock.data.new_get_data import get_daily_data_signal_daemon_callable
from stock.data.new_get_tick_data import download_tick


def update_basic_info():
    simple_publish('basic_info_req', 'update')


def update_news_info():
    simple_publish('news_hdl_req', 'update')


schedule.every().day.at("03:30").do(update_market_open_date_list)
schedule.every().day.at("03:45").do(get_daily_data_signal_daemon_callable)
schedule.every().day.at("06:45").do(download_tick)
schedule.every().day.at("11:15").do(update_basic_info)
schedule.every().day.at("11:55").do(update_news_info)


# schedule.every(10).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)

def main():
    os.system('python3 ./main.py --td')
    os.system('python3 ./main.py --news')
    os.system('python3 ./main.py --basic')
    os.system('python3 ./main.py --trade')
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile(
                        '%s/signal_hdl.pid' % COMMON_VARS_OBJ.DAEMON['basic_info_hdl']['pid_path'])):
        while True:
            schedule.run_pending()
            time.sleep(1)
