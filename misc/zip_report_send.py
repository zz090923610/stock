# DEP_APT( zip )
import sys


def generate_zip_cmd(day):
    # todo ugly
    from tools.date_util.market_calendar_cn import MktCalendar
    calendar = MktCalendar()
    day = calendar.validate_date(day)
    return "zip -j ~/%s.zip " \
           '/home/zhangzhao/data/stockdata/naive_score/summary_%s_turnover.csv ' \
           '/home/zhangzhao/data/stockdata/naive_score/summary_%s_amount.csv ' \
           '/home/zhangzhao/data/stockdata/slice/analysis_v2_%s.csv ' \
           '/home/zhangzhao/data/stockdata/slice/anomaly_%s.csv' % (day, day, day, day, day)


def generate_send_report_cmd(day):
    return "wccmd -f /home/zhangzhao/%s.zip 张志远" % day


if __name__ == '__main__':
    res = generate_zip_cmd(sys.argv[1]) + "&&" + generate_send_report_cmd(sys.argv[1])
    print(res)
