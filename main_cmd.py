#!/usr/bin/python3
from cmd import Cmd
from common_func import *
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

    def do_print_market_close_days(self, args):
        args = _cvt_args_to_list(args)
        if len(args) == 0:
            today_year = get_today().split('-')[0]
            close_days = load_market_close_days_for_year(today_year)
        else:
            close_days = load_market_close_days_for_year(args[0])
        for d in close_days:
            print(d)


if __name__ == '__main__':
    prompt = MyPrompt('%s >>> ' % get_time_of_a_day())
    prompt.cmdloop('加载股票分析系统...')
