#!/usr/bin/python3

from commom_func import update_market_open_date_list, update_basic_info, mkdirs, load_symbol_list

if __name__ == "__main__":
    update_basic_info()
    SYMBOL_LIST = load_symbol_list('../stock_data/basic_info.csv')
    mkdirs(SYMBOL_LIST)
    update_market_open_date_list()
