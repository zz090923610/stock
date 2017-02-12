#!/usr/bin/python3
from common_func import *
from datetime import datetime, timedelta

from qa_ma import calc_ma_for_all_stock
from qa_trend_continue import calc_atpdr_for_all_stock, calc_atpd_for_all_stock

if __name__ == "__main__":
    while True:
        today = get_today()
        close_days = load_market_close_days_for_year('2017')
        next_wake_up_time = datetime(int(today.split('-')[0]), int(today.split('-')[1]), int(today.split('-')[2]), 23,
                                     15, 00) + timedelta(days=1)
        local_date = get_today()
        local_time = get_time_of_a_day()
        ln = datetime(int(local_date.split('-')[0]), int(local_date.split('-')[1]), int(local_date.split('-')[2]),
                      int(local_time.split(':')[0]), int(local_time.split(':')[1]), int(local_time.split(':')[2]))
        seconds = next_wake_up_time - ln
        print("now is " + get_time_of_a_day())
        print("sleeping %d" % seconds.seconds)
        time.sleep(seconds.seconds)
        if today not in close_days:
            # update data
            subprocess.call("./daily_update.py", shell=True)
            BASIC_INFO.get_all_announcements()
            # calculate intermediate variables
            calc_atpd_for_all_stock()
            calc_atpdr_for_all_stock()
            calc_ma_for_all_stock(10)
            calc_ma_for_all_stock(20)
            calc_ma_for_all_stock(40)
            # generate report
            subprocess.call("./qa_trend_continue.py 100 5 %s" % today, shell=True)
            # send email
            subprocess.call("./send_mail.py -s '610153443@qq.com' '连续五日日平均交易价格趋势 %s' "
                            "'../stock_data/report/five_days_trend/%s.txt'" % (today, today), shell=True)
            subprocess.call("./send_mail.py -s 'zzy6548@126.com' '连续五日日平均交易价格趋势 %s' "
                            "'../stock_data/report/five_days_trend/%s.txt'" % (today, today), shell=True)
            subprocess.call("./data_news_handler.py %s" % today, shell=True)
