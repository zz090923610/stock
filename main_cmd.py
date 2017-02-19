#!/usr/bin/python3
import os.path
import readline
from cmd import Cmd

from common_func import *
from get_tick_data import align_tick_data_stock
from qa_buy_point import get_buy_point_for_stock
from qa_ma import calc_ma_for_stock

from variables import *


def _cvt_args_to_list(args):
    args = args.split(' ')
    return [i.strip() for i in args]


def get_market_status():
    today = get_today()
    today_year = get_today().split('-')[0]
    close_days = load_market_close_days_for_year(today_year)
    is_trade_day = True
    if today in close_days:
        is_trade_day = False
    if is_trade_day:
        return u'今日开市'
    else:
        return u'今日休市'


def do_pause_date(args):
    args = _cvt_args_to_list(args)
    for i in args:
        days = load_trade_pause_date_list_for_stock(i)
        print(days)


class MyPrompt(Cmd):
    def __init__(self, promp):
        # noinspection PyCompatibility
        super().__init__()
        self.prompt = promp

    def preloop(self):
        curr_time = get_time()
        print('%s %s' % (curr_time, get_market_status()))
        if readline and os.path.exists(hist_file):
            readline.read_history_file(hist_file)

    def postloop(self):
        if readline:
            readline.set_history_length(hist_file_size)
            readline.write_history_file(hist_file)
            # print('postloop()')

    def parseline(self, line):
        # print('parseline(%s) =>' % line, end=' ')
        ret = Cmd.parseline(self, line)
        # print(ret)
        return ret

    def onecmd(self, s):
        # print('onecmd(%s)' % s)
        return Cmd.onecmd(self, s)

    def emptyline(self):
        # print('emptyline()')
        return Cmd.emptyline(self)

    def default(self, line):
        # print('default(%s)' % line)
        return Cmd.default(self, line)

    def precmd(self, line):
        # print('precmd(%s)' % line)
        self.prompt = '%s >>> ' % get_time_of_a_day()
        return Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        # print('postcmd(%s, %s)' % (stop, line))
        self.prompt = '%s >>> ' % get_time_of_a_day()
        return Cmd.postcmd(self, stop, line)

    # noinspection PyUnusedLocal
    @staticmethod
    def do_quit(args):
        """Quits the program."""
        print("Quitting.")
        if readline:
            readline.set_history_length(hist_file_size)
            readline.write_history_file(hist_file)
        raise SystemExit

    # noinspection PyUnusedLocal
    @staticmethod
    def do_q(args):
        """Quits the program."""
        print("Quitting.")
        if readline:
            readline.set_history_length(hist_file_size)
            readline.write_history_file(hist_file)
        raise SystemExit

    # noinspection PyUnusedLocal
    @staticmethod
    def do_exit(args):
        """Quits the program."""
        print("Quitting.")
        if readline:
            readline.set_history_length(hist_file_size)
            readline.write_history_file(hist_file)
        raise SystemExit

    @staticmethod
    def do_data_print_market_close_days(args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            today_year = get_today().split('-')[0]
            close_days = load_market_close_days_for_year(today_year)
        else:
            close_days = load_market_close_days_for_year(args[0])
        for d in close_days:
            print(d)

    @staticmethod
    def do_data_remove_pause_date(args):
        args = _cvt_args_to_list(args)
        print(args)
        for s in BASIC_INFO.symbol_list:
            days = load_trade_pause_date_list_for_stock(s)
            if len(days) > 0:
                for day in args:
                    try:
                        days.remove(day)
                    except ValueError:
                        pass
            save_trade_pause_date_date_list_for_stock(s, days)

    @staticmethod
    def do_data_update_daily_data(args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            pass
        else:
            for s in args:
                from get_daily_data import get_daily_data_for_stock_yahoo
                get_daily_data_for_stock_yahoo(s, get_today(), get_today())


    @staticmethod
    def do_data_check_missing_tick(args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            pass
        else:
            for s in args:
                date_list_daily = load_stock_date_list_from_daily_data(s)
                date_list_tick = load_stock_date_list_from_tick_files(s)
                for i in date_list_daily:
                    if i not in date_list_tick:
                        print(i)

    @staticmethod
    def do_data_align_tick(args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            pass
        else:
            for s in args:
                align_tick_data_stock(s)

    @staticmethod
    def do_qa_buy_point_of_stock(args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            return
        try:
            stock = args[0]
            pre_days = int(args[1])
            future_days = int(args[2])
            scale = float(args[3])
        except Exception as e:
            print("Error : %s" % e)
            print("用法: qa_buy_point_of_stock 股票代码 买点前统计天数 买点后观察天数 涨幅 [是否合并相邻天]")
            print("示例: qa_buy_point_of_stock 002263 6 30 1.3 retract")
            print("示例: qa_buy_point_of_stock 002263 6 30 1.3")
            return
        # noinspection PyBroadException
        try:
            retract = True
        except:
            retract = False
        buy_point_list = get_buy_point_for_stock(stock, pre_days, future_days, scale, retract=retract)
        print(buy_point_list)

    @staticmethod
    def do_qa_ma(args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            return
        stock = None
        days = None
        ma_type = 'atpd'
        try:
            for loop in range(len(args)):
                if args[loop] == '-s':
                    stock = args[loop + 1]
                elif args[loop] == '-d':
                    days = int(args[loop + 1])
                elif args[loop] == '-t':
                    ma_type = args[loop + 1]

            calc_ma_for_stock(stock, days, ma_type)
        except Exception as e:
            print("Error : %s" % e)
            print('用法: qa_ma 股票代码 天数 [数据类型(close, atpd)]')
            print("示例: qa_ma 5 atpd")

    @staticmethod
    def do_qa_moving_average(args):
        from qa_ma import ma_align
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            return
        stock = None
        day = None
        short = None
        mid = None
        long = None
        calc_type = 'atpd'
        try:
            for loop in range(len(args)):
                if args[loop] == '-s':
                    stock = args[loop + 1]
                elif args[loop] == '-d':
                    day = args[loop + 1]
                elif args[loop] == '--map':
                    short = int(args[loop + 1])
                    mid = int(args[loop + 2])
                    long = int(args[loop + 3])
                elif args[loop] == '-t':
                    calc_type = args[loop + 1]
            a = ma_align(stock, short, mid, long, calc_type=calc_type)
            r, out = a.analysis_align_for_day(day)
            if len(out) > 0:
                print(out)
            else:
                print(r)
        except Exception as e:
            print("Error : %s" % e)
            print('用法: qa_moving_average -s 股票代码 --map 短天数 中天数 长天数 -d 某交易日 [-t 数据类型(close, atpd)]')
            print("示例: qa_moving_average -s 002263 --map 10 20 40 -d 2017-01-20 -t atpd")

    # noinspection PyBroadException
    @staticmethod
    def do_qa_ma_all_stock(args):
        from qa_ma import ma_align
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            return
        day = None
        short = None
        mid = None
        long = None
        calc_type = 'atpd'
        try:
            for loop in range(len(args)):
                if args[loop] == '-d':
                    day = args[loop + 1]
                elif args[loop] == '--map':
                    short = int(args[loop + 1])
                    mid = int(args[loop + 2])
                    long = int(args[loop + 3])
                elif args[loop] == '-t':
                    calc_type = args[loop + 1]
            for stock in BASIC_INFO.symbol_list:
                # noinspection PyUnusedLocal
                try:
                    a = ma_align(stock, short, mid, long, calc_type=calc_type)
                    r, out = a.analysis_align_for_day(day)
                    if len(out) > 0:
                        print(stock, day, out)
                except Exception as e:
                    print(stock, day, '并无足够数据')
        except Exception as e:
            print("Error : %s" % e)
            print('用法: qa_moving_average --map 短天数 中天数 长天数 -d 某交易日 [-t 数据类型(close, atpd)]')
            print("示例: qa_moving_average --map 10 20 40 -d 2017-01-20 -t atpd")

    @staticmethod
    def do_load_ma(args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            return
        stock = args[0]
        params = args[1]
        print(load_ma_for_stock(stock, params))


if __name__ == '__main__':
    prompt = MyPrompt('%s >>> ' % get_time_of_a_day())
    prompt.cmdloop('加载股票分析系统...')
