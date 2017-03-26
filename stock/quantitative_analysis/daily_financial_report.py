#!/usr/bin/python3
import signal
import subprocess

from stock.common.communction import simple_publish
from stock.common.variables import COMMON_VARS_OBJ
from stock.common.common_func import BASIC_INFO
from stock.common.time_util import load_last_date, TimeUtil
from stock.quantitative_analysis.mqa_atpd import calc_atpd
from stock.quantitative_analysis.qa_atpdr import calc_atpdr_for_all_stock
from stock.quantitative_analysis.qa_ma import calc_ma_for_all_stock
from stock.quantitative_analysis.qa_trend5d import analysis_trend5d
from stock.quantitative_analysis.qa_vol_indi import calc_vol_indi_for_all_stock
from stock.quantitative_analysis.report_generator import report_generate
import multiprocessing as mp


def make_plots():
    simple_publish('qa_update','plot_start')
    subprocess.call("cd stock/visualization; ./template_k_plot.py", shell=True)
    from stock.visualization.k_plot import k_plot
    print('Plotting')
    subprocess.call("mkdir -p %s/plots; rm %s/plots/*" %(COMMON_VARS_OBJ.stock_data_root, COMMON_VARS_OBJ.stock_data_root), shell=True)
    # for stock in BASIC_INFO.symbol_list:
    #   k_plot(stock, 120)

    pool = mp.Pool()
    for stock in BASIC_INFO.symbol_list:
        pool.apply_async(k_plot, args=(stock, 120,))
    pool.close()
    pool.join()
    simple_publish('qa_update', 'plot_finished')


def financial_report_main():
    today = load_last_date()
    close_days = TimeUtil().load_market_close_days_for_year('2017')
    if today not in close_days:
        calc_atpd()
        calc_atpdr_for_all_stock()
        calc_ma_for_all_stock(3)
        calc_ma_for_all_stock(10)
        calc_ma_for_all_stock(20)
        calc_ma_for_all_stock(40)
        calc_vol_indi_for_all_stock()
        analysis_trend5d(100, 5, today)
        make_plots()
        print('Generating report')
        report_generate(today)


if __name__ == "__main__":
    financial_report_main()


