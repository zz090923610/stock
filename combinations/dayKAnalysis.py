import sys

from analysis.script_executor.parser import engine
from analysis.script_executor.summary import summary_all
from tools.fetch_day_level_quotes_china import *
from tools.internal_func_entry import update_symbol_list

if __name__ == '__main__':
   #  update_symbol_list()
    #a = DayLevelQuoteUpdaterTushare()
    # TODO specify better start date
    #a.get_data_all_stock(start='2001-01-01', end=sys.argv[1])
    engine('./scripts/short_period_buypoint.txt')
    #engine('./scripts/ma.txt')
    #engine('./scripts/candle_stick_shape_analysis.txt')
    #summary_all(sys.argv[1], '~/' + sys.argv[1] + ".csv")













