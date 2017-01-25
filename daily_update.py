#!/usr/bin/python3

from common_func import *
import subprocess

if __name__ == "__main__":
    update_basic_info()
    SYMBOL_LIST = load_symbol_list('../stock_data/basic_info.csv')
    mkdirs(SYMBOL_LIST)
    update_market_open_date_list()
    close_days = load_market_close_days_for_year(get_today().split('-')[0])
    subprocess.call("./get_daily_data.py --update", shell=True)
    subprocess.call("./get_tick_data.py %s" % get_today(), shell=True)
