#!/usr/bin/python3
import signal

from common_func import *
from datetime import datetime, timedelta
from qa_ma import calc_ma_for_all_stock
from qa_trend_continue import calc_atpdr_for_all_stock, calc_atpd_for_all_stock
from k_plot import k_plot


def signal_handler(signal, frame):
    print('Ctrl+C detected, exiting')
    subprocess.call("killall qa_trend_continue.py 2>/dev/null", shell=True)
    exit(0)


signal.signal(signal.SIGINT, signal_handler)


def make_plots():
    print('Plotting')
    subprocess.call("mkdir -p ../stock_data/plots; rm ../stock_data/plots/*", shell=True)
    # for stock in BASIC_INFO.symbol_list:
    #   k_plot(stock, 120)

    pool = mp.Pool()
    for stock in BASIC_INFO.symbol_list:
        pool.apply_async(k_plot, args=(stock, 120,))
    pool.close()
    pool.join()
    subprocess.call("cd  ../stock_data/; tar czf plots.tar.gz plots/ ;mv plots.tar.gz upload/", shell=True)
    subprocess.call("cd  ../stock_data/upload; bypy syncup -v", shell=True)
    subprocess.call(
        "ssh zhangzhao@115.28.142.56 'cd upload/;bypy syncdown -v;\
                mv plots.tar.gz /var/www;\
                cd /var/www; tar -xvf plots.tar.gz; rm /var/www/plots.tar.gz'", shell=True)


if __name__ == "__main__":
    while True:
        today = get_today()
        close_days = load_market_close_days_for_year('2017')
        sleep_until('17:00:00')
        if today not in close_days:
            # update data
            subprocess.call("./daily_update.py", shell=True)
            # BASIC_INFO.get_announcement_all_stock_one_day(today)
            # calculate intermediate variables
            calc_atpd_for_all_stock()
            calc_atpdr_for_all_stock()
            calc_ma_for_all_stock(3)
            calc_ma_for_all_stock(10)
            calc_ma_for_all_stock(20)
            calc_ma_for_all_stock(40)
            subprocess.call("./qa_adl.py", shell=True)
            subprocess.call("./qa_vhf.py", shell=True)

            # plot
            make_plots()

            # generate report
            sleep_until('23:15:00')
            print('Generating report')
            subprocess.call("./qa_trend_continue.py 100 5 %s" % today, shell=True)
            # send email
            subprocess.call(
                " scp '/home/zhangzhao/data/stock_data/plots/%s.html' zhangzhao@115.28.142.56:/var/www/plots/" % today,
                shell=True)
            subprocess.call("./send_mail.py -n -s '610153443@qq.com' '连续五日日平均交易价格趋势 %s' "
                            "'../stock_data/report/five_days_trend/%s.txt'" % (today, today), shell=True)
            subprocess.call("./send_mail.py -n -s 'zzy6548@126.com' '连续五日日平均交易价格趋势 %s' "
                            "'../stock_data/report/five_days_trend/%s.txt'" % (today, today), shell=True)
            # subprocess.call("./data_news_handler.py %s" % today, shell=True)
            print('All set')
        time.sleep(30)
