#!/usr/bin/python3
import signal

from common_func import *
from get_daily_data import get_update_for_all_stock
from k_plot import k_plot
from qa_ma import calc_ma_for_all_stock
from qa_atpdr import calc_atpdr_for_all_stock


# noinspection PyUnusedLocal,PyShadowingNames
def signal_handler(signal, frame):
    print('Ctrl+C detected, exiting')
    subprocess.call("killall python3 2>/dev/null", shell=True)
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
    sleep = False
    update = False
    calc = False
    plot = False
    send_email = False

    for loop in range(1, len(sys.argv)):
        if sys.argv[loop] == '--sleep':
            sleep = True
        elif sys.argv[loop] == '--update':
            update = True
        elif sys.argv[loop] == '--calc':
            calc = True
        elif sys.argv[loop] == '--plot':
            plot = True
        elif sys.argv[loop] == '--send':
            send_email = True
        elif sys.argv[loop] == '--all':
            sleep = True
            update = True
            calc = True
            plot = True
            send_email = True
            break
    while True:
        today = get_today()
        close_days = load_market_close_days_for_year('2017')
        if sleep:
            sleep_until('19:00:00')
        if today not in close_days:
            if update:
                update_basic_info()
                update_market_open_date_list()
                get_update_for_all_stock()
                subprocess.call("./get_tick_data.py %s" % today, shell=True)
                # BASIC_INFO.get_announcement_all_stock_one_day(today)
            if calc:
                subprocess.call('python3 -m scoop --hostfile hostfile mqa_atpd.py', shell=True)
                calc_atpdr_for_all_stock()
                calc_ma_for_all_stock(3)
                calc_ma_for_all_stock(10)
                calc_ma_for_all_stock(20)
                calc_ma_for_all_stock(40)
                subprocess.call("./qa_adl.py", shell=True)
                subprocess.call("./qa_vhf.py", shell=True)
            if plot:
                make_plots()

            if sleep:
                sleep_until('23:15:00')
            if calc:
                print('Generating report')
                subprocess.call("./qa_trend_continue.py 100 5 %s" % today, shell=True)
                subprocess.call(
                  " scp '/home/zhangzhao/data/stock_data/plots/%s.html' zhangzhao@115.28.142.56:/var/www/plots/" %
                  today, shell=True)
            if send_email:
                subprocess.call("./send_mail.py -n -s '610153443@qq.com' '连续五日日平均交易价格趋势 %s' "
                               "'../stock_data/report/five_days_trend/%s.txt'" % (today, today), shell=True)
                subprocess.call("./send_mail.py -n -s 'zzy6548@126.com' '连续五日日平均交易价格趋势 %s' "
                               "'../stock_data/report/five_days_trend/%s.txt'" % (today, today), shell=True)
                subprocess.call("./data_news_handler.py %s" % today, shell=True)
            print('All set')
        time.sleep(30)
        if sleep:
            sleep_until('18:00:00')
        else:
            break
