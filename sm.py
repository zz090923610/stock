#!/usr/bin/env python3
import os
import pickle
import subprocess
from time import sleep

from termcolor import colored
import sys

import signal
from  common_func import get_time

import tushare as ts


def signal_handler(signal, frame):
    print('Ctrl+C detected, exiting')
    exit(0)


signal.signal(signal.SIGINT, signal_handler)





def bell():
    subprocess.call(["bell.sh", "2>>/dev/null"])


def run_monitor(trade_list):
    while True:
        show_gain(trade_list, cls=True)
        check_gain(trade_list)
        sleep(1)


def check_belonging_market(code):
    file = 'shanghai_list.txt'
    with open(file, 'rb') as f:
        sh_data = str(f.readlines()).strip()
    file = 'shenzhen_list.txt'
    with open(file, 'rb') as f:
        sz_data = str(f.readlines()).strip()
    if code in sh_data:
        return 'H'
    elif code in sz_data:
        return 'S'
    else:
        return 'N'


def check_gain(trade_list):
    for trade in trade_list:
        if trade.expect * trade.cost <= (trade.cost + trade.gain):
            print('!!!!' + trade.name)
            bell()


class Trade(object):
    def __init__(self, code, cost, quantity, expect=1.05, buy_in_time=''):
        self.code = code
        self.name = ''
        self.cost = float(cost)
        self.quantity = int(quantity)
        self.expect = float(expect)
        self.buy_in_time = buy_in_time
        self.gain = 0


class NetGain(object):
    def __init__(self):
        self.val = 0

    def load_net_gain(self, file='netgain.pickle'):
        try:
            with open(file, 'rb') as f:
                self.val = pickle.load(f)
        except:
            self.val = 0

    def save_net_gain(self, file='netgain.pickle'):
        with open(file, 'wb') as f:
            pickle.dump(self.val, f, -1)


def save_trade(trade_list):
    file = 'trades.pickle'
    with open(file, 'wb') as f:
        pickle.dump(trade_list, f, -1)


def load_trade(file='trades.pickle'):
    with open(file, 'rb') as f:
        trade_list = pickle.load(f)
    return trade_list


def create_trade(code, cost, quantity, expect):
    new_trade = Trade(code, cost, quantity, expect)
    data = ts.get_realtime_quotes([new_trade.code])
    new_trade.name = data.iloc[0]['name']
    new_trade.gain = float(float(cost) - float(data.iloc[0]['price']))
    return new_trade


def print_trade(trade):
    print('Code: %s, Name: %s, Cost:%.2f, Quantity: %d, Expect: %.2f,Expect Gain: %.2f' % (
        trade.code, trade.name, trade.cost, trade.quantity, trade.expect,
        (trade.expect - 1) * trade.cost * trade.quantity))


def calculate_sell_fee(code, quantity, price):
    market = check_belonging_market(code)
    gain_before_fee = quantity * price
    if market == 'H':
        guo_hu_fee = .001 * gain_before_fee
    else:
        guo_hu_fee = 0
    brokerage = max(.0021 * gain_before_fee, 5)
    tax = .001 * gain_before_fee
    return brokerage + guo_hu_fee + tax


def calculate_current_sell_fee(code):
    for trade in trade_list:
        if trade.code == code:
            return calculate_sell_fee(code, trade.quantity, trade.cost + trade.gain)
    return 0


def print_gain_of_trade(trade):
    color = 'green'
    if trade.gain > 0:
        color = 'red'
    elif trade.gain + trade.cost == 0:
        color = 'grey'
    market = check_belonging_market(trade.code)
    sell_fee = calculate_sell_fee(trade.code, trade.quantity, trade.cost + trade.gain)
    if trade.cost + trade.gain == 0:
        print(colored('[ %s %s ] %s\t成本/现价:%.2f/停牌 量: %04d\t浮动/清仓: 停牌/停牌' % (trade.code, market, trade.name, trade.cost,  trade.quantity), color))
    else:
        print(colored('[ %s %s ] %s\t成本/现价:%.2f/%.2f 量: %04d\t浮动/清仓: %.2f/%.02f' % (
        trade.code, market, trade.name, trade.cost, trade.cost + trade.gain, trade.quantity,
        trade.gain * trade.quantity,
        trade.gain * trade.quantity - sell_fee), color))


def update_current_price(trade_list):
    code_list = []
    for loop in trade_list:
        code_list.append(loop.code)
    code_list = [l for l in set(code_list)]
    try:
        data = ts.get_realtime_quotes(code_list)
        for trade in trade_list:
            new_price = float(data.iloc[code_list.index(trade.code)]['price'])
            trade.gain = new_price - trade.cost
    except:
        print('Connection lost')


def show_gain(trade_list, cls=False):
    update_current_price(trade_list)
    netgain = NetGain()
    netgain.load_net_gain()
    totalfloatgain = calculate_float_gain(trade_list)
    totalcleargain = calculate_clear_all_gain(trade_list)
    trade_list.sort(key=lambda x: x.gain * x.quantity, reverse=True)
    if cls:
        os.system('clear')
    print('%s, 已成交净收益: %.02f, 当前浮动收益: %.02f, 当前清仓收益: %.02f' % (
        get_time(), netgain.val, totalfloatgain, totalcleargain))
    for trade in trade_list:
        if trade.quantity > 100:
            print_gain_of_trade(trade)
    for trade in trade_list:
        if trade.quantity == 100:
            print_gain_of_trade(trade)


def calculate_float_gain(trade_list):
    total_float_gain = 0
    for trade in trade_list:
        if trade.cost + trade.gain == 0:
            continue
        total_float_gain += trade.gain * trade.quantity
    return total_float_gain


def calculate_clear_all_gain(trade_list):
    total_clear_gain = 0
    for trade in trade_list:
        if trade.cost + trade.gain == 0:
            continue
        total_clear_gain += trade.gain * trade.quantity
        total_clear_gain -= calculate_current_sell_fee(trade.code)
    return total_clear_gain


def sell(trade_list, code, price, quantity):
    price = float(price)
    quantity = int(quantity)
    net_gain = NetGain()
    net_gain.load_net_gain()
    sell_fee = calculate_sell_fee(code, quantity, price)
    gain_of_trans = 0
    for trade in trade_list:
        if trade.code == code:
            trade.quantity -= quantity
            gain_of_trans = (price - trade.cost) * quantity - sell_fee
            net_gain.val += gain_of_trans
            if trade.quantity <= 0:
                try:
                    trade_list.remove(trade)
                except:
                    pass
    net_gain.save_net_gain()
    save_trade(trade_list)
    print('Net gain: %.2f, Sell Fee and Tax %.2f, Net Gain of this transaction: %.02f' % (
        net_gain.val, sell_fee, gain_of_trans))


def modify_net_gain(new_val):
    net_gain = NetGain()
    net_gain.val = new_val
    net_gain.save_net_gain()


def reset_expectation(trade_list, expect):
    for trade in trade_list:
        trade.expect = expect


def remove(code):
    tl = load_trade()
    for trade in tl:
        if trade.code == code:
            try:
                print()
                tl.remove(trade)
            except:
                pass
    save_trade(tl)


if __name__ == "__main__":
    try:
        trade_list = load_trade()
    except:
        trade_list = []
    argc = len(sys.argv)
    if argc == 1:
        run_monitor(trade_list)
    else:
        add_trade = False
        sale_trade = False
        modify_trade = False
        price = ''
        code = ''
        cost = ''
        quantity = ''
        expect = ''
        for loop in range(1, len(sys.argv)):
            if sys.argv[loop] == '-a':
                add_trade = True
                code = sys.argv[loop + 1]
            if sys.argv[loop] == 'check':
                print(check_belonging_market(sys.argv[loop + 1]))
            if sys.argv[loop] == 'reset':
                if sys.argv[loop + 1] == '-e':
                    reset_expectation(trade_list, float(sys.argv[loop + 2]))
                    save_trade(trade_list)
                    exit()
            if sys.argv[loop] == '-s':
                sale_trade = True
                code = sys.argv[loop + 1]
            if sys.argv[loop] == '-m':
                modify_trade = True
                code = sys.argv[loop + 1]
            if sys.argv[loop] == '-r':
                remove(sys.argv[loop + 1])
            if sys.argv[loop] == '-l':
                for trade in trade_list:
                    print_trade(trade)
                exit()
                code = sys.argv[loop + 1]
            if sys.argv[loop] == '-p':
                price = sys.argv[loop + 1]
            if sys.argv[loop] == '-c':
                cost = sys.argv[loop + 1]
            if sys.argv[loop] == '-q':
                quantity = sys.argv[loop + 1]
            if sys.argv[loop] == '-e':
                expect = sys.argv[loop + 1]
            if sys.argv[loop] == '-g':
                show_gain(trade_list)
                exit()
        # print(add_trade, sale_trade, price, code, cost, quantity, expect)

        if add_trade:
            try:
                trade_list = load_trade()
            except:
                trade_list = []
            new_trade = create_trade(code, cost, quantity, expect)

            trade_list.append(new_trade)
            save_trade(trade_list)
        if sale_trade:
            try:
                trade_list = load_trade()
            except:
                trade_list = []
            sell(trade_list, code, price, quantity)
        if modify_trade:
            for trade in trade_list:
                if trade.code == code:
                    if quantity is not '':
                        trade.quantity = int(quantity)
                    if cost is not '':
                        trade.cost = float(cost)
                    if expect is not '':
                        trade.expect = float(expect)
                    trade.gain = 0
                    save_trade(trade_list)
                    print_trade(trade)
                    exit()
