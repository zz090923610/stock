#!/usr/bin/python3

from tick_data_integrity_check import *
from quantity_analysis import *

stock=sys.argv[1]
check_one_stock_integrity(stock)
a=calculate_detailed_trade_quantity_for_stock(stock)
plot_log_quantity_idx(stock, .5, 'overall,buy_large,buy_small,sell_large,sell_small')