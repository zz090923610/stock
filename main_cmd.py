#!/usr/bin/python3
import subprocess
from cmd import Cmd
from common_func import *
from get_tick_data import align_tick_data_stock
from qa_buy_point import get_buy_point_for_stock
from qa_trend_continue import calc_average_trade_price_for_stock
from variables import *
import os.path
import readline


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

    def do_quit(self, args):
        """Quits the program."""
        print("Quitting.")
        if readline:
            readline.set_history_length(hist_file_size)
            readline.write_history_file(hist_file)
        raise SystemExit

    def do_q(self, args):
        """Quits the program."""
        print("Quitting.")
        if readline:
            readline.set_history_length(hist_file_size)
            readline.write_history_file(hist_file)
        raise SystemExit

    def do_exit(self, args):
        """Quits the program."""
        print("Quitting.")
        if readline:
            readline.set_history_length(hist_file_size)
            readline.write_history_file(hist_file)
        raise SystemExit

    def do_data_print_market_close_days(self, args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            today_year = get_today().split('-')[0]
            close_days = load_market_close_days_for_year(today_year)
        else:
            close_days = load_market_close_days_for_year(args[0])
        for d in close_days:
            print(d)

    def do_data_remove_pause_date(self, args):
        args = _cvt_args_to_list(args)
        print(args)
        for s in SYMBOL_LIST:
            days = load_trade_pause_date_list_for_stock(s)
            if len(days) > 0:
                for day in args:
                    try:
                        days.remove(day)
                    except ValueError:
                        pass
            save_trade_pause_date_date_list_for_stock(s, days)

    def do_data_update_daily_data(self, args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            pass
        else:
            for s in args:
                from get_daily_data import get_update_for_one_stock
                get_update_for_one_stock(s)

    def do_qa_calc_average_trade_price(self, args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            pass
        else:
            for s in args:
                calc_average_trade_price_for_stock(s)

    def do_data_check_missing_tick(self, args):
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

    def do_data_align_tick(self, args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            pass
        else:
            for s in args:
                align_tick_data_stock(s)

    def do_qa_buy_point_of_stock(self, args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            return
        try:
            stock = args[0]
            pre_days = int(args[1])
            future_days = int(args[2])
            scale = float(args[3])
        except Exception as e:
            print("Error : %s" %e)
            print("用法: qa_buy_point_of_stock 股票代码 买点前统计天数 买点后观察天数 涨幅 [是否合并相邻天]")
            print("示例: qa_buy_point_of_stock 002263 6 30 1.3 retract")
            print("示例: qa_buy_point_of_stock 002263 6 30 1.3")
            return
        try:
            retract= args[4]
            retract = True
        except:
            retract = False
        buy_point_list = get_buy_point_for_stock(stock, pre_days, future_days, scale, retract=retract)
        print(buy_point_list)

if __name__ == '__main__':
    prompt = MyPrompt('%s >>> ' % get_time_of_a_day())
    prompt.cmdloop('加载股票分析系统...')
