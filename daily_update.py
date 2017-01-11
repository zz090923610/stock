#!/usr/bin/python3

from common_func import update_market_open_date_list, update_basic_info, mkdirs, load_symbol_list,get_today
import subprocess

if __name__ == "__main__":
    update_basic_info()
    SYMBOL_LIST = load_symbol_list('../stock_data/basic_info.csv')
    mkdirs(SYMBOL_LIST)
    update_market_open_date_list()
    subprocess.call("cd ~/stock;./get_daily_data.py --update", shell=True)
    subprocess.call("cd ~/stock;./get_tick_data.py %s" % get_today(), shell=True)
