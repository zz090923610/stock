import os

from stock.common.common_func import BASIC_INFO
from stock.common.communction import simple_publish
from stock.common.file_operation import load_csv
from stock.common.variables import COMMON_VARS_OBJ


class HistoryTradeDetail:
    def __init__(self):
        self.total_money_transferred_in = 0
        self.finished_net_gain = 0
        self.trade_list = load_csv('%s/trade_details.csv' % COMMON_VARS_OBJ.stock_data_root)
        self.filled_today_list = []
        self.load_filled_today()
        self.long_dict = {}
        self.history_dict = {}
        if self.trade_list:
            self.calc_total_money_transferred_in()
            self.analysis_line()
        for stock in self.history_dict.keys():
            self.history_dict[stock].analysis_stock_status()
        self.generate_long_dict()
        if self.trade_list:
            self.calc_finished_net_gain()

    def calc_total_money_transferred_in(self):
        for line in self.trade_list:
            if line['业务名称'] == '银行转证券':
                self.total_money_transferred_in += float(line['清算金额'])
            elif line['业务名称'] == '证券转银行':
                self.total_money_transferred_in -= float(line['清算金额'])

    def analysis_line(self):
        for line in self.trade_list:
            if (line['业务名称'] == '证券买入') | (line['业务名称'] == '证券卖出'):
                if line['证券代码'] in self.history_dict.keys():
                    self.history_dict[line['证券代码']].append_list(line['业务名称'], line['成交价格'], line['成交数量'], line['成交金额'],
                                                                line['净佣金'],
                                                                line['规费'], line['印花税'], line['过户费'])
                else:
                    self.history_dict[line['证券代码']] = StockTradeHistory(line['证券代码'])
                    self.history_dict[line['证券代码']].append_list(line['业务名称'], line['成交价格'], line['成交数量'], line['成交金额'],
                                                                line['净佣金'],
                                                                line['规费'], line['印花税'], line['过户费'])
        for line in self.filled_today_list:
            if (line['业务名称'] == '证券买入') | (line['业务名称'] == '证券卖出'):
                if line['证券代码'] in self.history_dict.keys():
                    self.history_dict[line['证券代码']].append_list(line['业务名称'], line['成交价'], line['成交数量'], line['成交额'],
                                                                calc_trade_cost(line['证券代码'], line['成交价'], line['成交数量'],
                                                                                line['业务名称']),
                                                                0, 0, 0)
                else:
                    self.history_dict[line['证券代码']] = StockTradeHistory(line['证券代码'])
                    self.history_dict[line['证券代码']].append_list(line['业务名称'], line['成交价'], line['成交数量'], line['成交额'],
                                                                calc_trade_cost(line['证券代码'], line['成交价'], line['成交数量'],
                                                                                line['业务名称']),
                                                                0, 0, 0)

    def load_filled_today(self):
        if os.path.isdir('%s/filled_today' % COMMON_VARS_OBJ.stock_data_root):
            try:
                filled_file = os.listdir('%s/filled_today' % COMMON_VARS_OBJ.stock_data_root)[0]
            except IndexError:
                return []
            self.filled_today_list = load_csv('%s/filled_today/%s' % (COMMON_VARS_OBJ.stock_data_root, filled_file))

    def reload(self):
        self.__init__()

    def generate_long_dict(self):
        for stock in self.history_dict.keys():
            if self.history_dict[stock].current_quant != 0:
                self.long_dict[stock] = self.history_dict[stock]

    def calc_finished_net_gain(self):
        for stock in self.history_dict.keys():
            if self.history_dict[stock].current_quant == 0:
                self.finished_net_gain += self.history_dict[stock].net_gain

    def print_report(self):
        print('已平仓净收益 %.2f' % self.finished_net_gain)
        for stock in self.history_dict.keys():
            if self.history_dict[stock].current_quant == 0:
                print(self.history_dict[stock].generate_report())
        for stock in self.history_dict.keys():
            if self.history_dict[stock].current_quant != 0:
                print(self.history_dict[stock].generate_report())

    def mqtt_report(self):
        self.reload()
        msg = ''
        msg += '已平仓净收益 %.2f\n' % self.finished_net_gain
        for stock in self.history_dict.keys():
            if self.history_dict[stock].current_quant != 0:
                msg += '%s\n' % self.history_dict[stock].generate_report()
        simple_publish('trade_detail_update', msg)


def calc_trade_cost(stock, price, quant, trade_type):
    quant = int(float(quant))
    price = float(price)
    if BASIC_INFO.in_sse(stock):
        fee_ratio_sell = .00205 + .00001 + .001 + .00002  # 佣金 规费 印花税 过户费
    else:
        fee_ratio_sell = .00205 + .00001 + .001  # 佣金 规费 印花税
    fee_ratio_buy = .00205 + .00001  # 佣金 规费
    if trade_type == '证券买入':
        if quant * price <= 2500:
            fee = 5 + .00001 * quant * price
        else:
            fee = fee_ratio_buy * quant * price
    elif trade_type == '证券卖出':
        if quant * price <= 2500:
            fee = 5 + (.00001 + .001) * quant * price
        else:
            fee = fee_ratio_sell * quant * price
    return fee


def calc_arbitrary_safe_price(stock, price):
    if BASIC_INFO.in_sse(stock):
        fee_ratio = .00205 + .00001 + .001 + .00002  # 佣金 规费 印花税 过户费
    else:
        fee_ratio = .00205 + .00001 + .001  # 佣金 规费 印花税
    try:
        unfinished_cost = price * (1 + fee_ratio)
        safe_price = unfinished_cost / (1 - fee_ratio)
    except ZeroDivisionError:
        safe_price = 0
    return safe_price


class StockTradeHistory:
    def __init__(self, stock):
        self.stock = stock
        self.trade_list = []
        self.safe_price = 0
        self.net_gain = 0
        self.current_quant = 0

    def append_list(self, trade_type, trade_price, trade_quant, trade_value, fee, gui_fei, tax, account_fee):
        self.trade_list.append(
            {'trade_type': trade_type, 'trade_price': float(trade_price), 'trade_quant': int(float(trade_quant)),
             'trade_value': float(trade_value), 'fee': float(fee),
             'gui_fei': float(gui_fei), 'tax': float(tax), 'account_fee': float(account_fee)})
        if trade_type == '证券买入':
            self.current_quant += float(trade_quant)
        elif trade_type == '证券卖出':
            self.current_quant -= float(trade_quant)

    def calc_net_gain(self):
        for line in self.trade_list:
            if line['trade_type'] == '证券买入':
                self.net_gain -= (line['trade_price'] * line['trade_quant'] + line['fee'] + line['gui_fei'] +
                                  line['tax'] + line['account_fee'])
            elif line['trade_type'] == '证券卖出':
                self.net_gain += line['trade_price'] * line['trade_quant']
                self.net_gain -= (line['fee'] + line['gui_fei'] + line['tax'] + line['account_fee'])

    def calc_safe_price(self):
        for line in self.trade_list:
            if line['trade_type'] == '证券买入':
                self.net_gain -= (line['trade_price'] * line['trade_quant'] + line['fee'] + line['gui_fei'] +
                                  line['tax'] + line['account_fee'])
            elif line['trade_type'] == '证券卖出':
                self.net_gain += line['trade_price'] * line['trade_quant']
                self.net_gain -= (line['fee'] + line['gui_fei'] + line['tax'] + line['account_fee'])
        unfinished_cost = 0 - self.net_gain
        self.net_gain = 0
        if BASIC_INFO.in_sse(self.stock):
            fee_ratio = .00205 + .00001 + .001 + .00002  # 佣金 规费 印花税 过户费
        else:
            fee_ratio = .00205 + .00001 + .001  # 佣金 规费 印花税
        try:
            self.safe_price = unfinished_cost / ((1 - fee_ratio) * self.current_quant)
        except ZeroDivisionError:
            self.safe_price = 0

    def analysis_stock_status(self):
        if self.current_quant == 0:
            self.calc_net_gain()
        else:
            self.calc_safe_price()

    def generate_report(self):
        report = ''
        if self.current_quant == 0:
            report += '%s %s 已平仓, 净收益 %.2f' % (self.stock, BASIC_INFO.name_dict[self.stock], self.net_gain)
        else:
            report += '%s %s 现持有 %d, 保本价 %.2f' % (self.stock, BASIC_INFO.name_dict[self.stock],
                                                  self.current_quant, self.safe_price)
        return report
