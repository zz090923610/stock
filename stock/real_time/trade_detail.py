import operator
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
        for k in self.history_dict.keys():
            self.history_dict[k].calc_partial_expect_sell_price()

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
                    self.history_dict[line['证券代码']].append_list(line['成交日期'], line['业务名称'], line['成交价格'],
                                                                line['成交数量'], line['成交金额'],
                                                                line['净佣金'],
                                                                line['规费'], line['印花税'], line['过户费'])
                else:
                    self.history_dict[line['证券代码']] = StockTradeHistory(line['证券代码'])
                    self.history_dict[line['证券代码']].append_list(line['成交日期'], line['业务名称'], line['成交价格'],
                                                                line['成交数量'], line['成交金额'],
                                                                line['净佣金'],
                                                                line['规费'], line['印花税'], line['过户费'])
        for line in self.filled_today_list:
            if (line['业务名称'] == '证券买入') | (line['业务名称'] == '证券卖出'):
                if line['证券代码'] in self.history_dict.keys():
                    self.history_dict[line['证券代码']].append_list(line['成交日期'], line['业务名称'], line['成交价'],
                                                                line['成交数量'], line['成交额'],
                                                                calc_trade_cost(line['证券代码'], line['成交价'], line['成交数量'],
                                                                                line['业务名称']),
                                                                0, 0, 0)
                else:
                    self.history_dict[line['证券代码']] = StockTradeHistory(line['证券代码'])
                    self.history_dict[line['证券代码']].append_list(line['成交日期'], line['业务名称'], line['成交价'],
                                                                line['成交数量'], line['成交额'],
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

    def get_current_position(self):
        self.reload()
        ret_list = []
        for stock in self.history_dict.keys():
            if self.history_dict[stock].current_quant != 0:
                ret_list.append(stock)
        return ret_list


def calc_trade_cost(stock, price, quantity, trade_type):
    fee = 0
    quantity = int(float(quantity))
    price = float(price)
    if BASIC_INFO.in_sse(stock):
        fee_ratio_sell = .00205 + .00001 + .001 + .00002  # 佣金 规费 印花税 过户费
    else:
        fee_ratio_sell = .00205 + .00001 + .001  # 佣金 规费 印花税
    fee_ratio_buy = .00205 + .00001  # 佣金 规费
    if trade_type == '证券买入':
        if quantity * price <= 2500:
            fee = 5 + .00001 * quantity * price
        else:
            fee = fee_ratio_buy * quantity * price
    elif trade_type == '证券卖出':
        if quantity * price <= 2500:
            fee = 5 + (.00001 + .001) * quantity * price
        else:
            fee = fee_ratio_sell * quantity * price
    return fee


def calc_arbitrary_safe_price_for_long_transaction(stock, price):
    if BASIC_INFO.in_sse(stock):
        fee_ratio = .00205 + .00001 + .001 + .00002  # 佣金 规费 印花税 过户费
    else:
        fee_ratio = .00205 + .00001 + .001  # 佣金 规费 印花税
    try:
        safe_price = price * (1 + fee_ratio) / (1 - fee_ratio)
    except ZeroDivisionError:
        safe_price = 0
    return safe_price


def calc_arbitrary_safe_price_for_short_transaction(stock, price):
    if BASIC_INFO.in_sse(stock):
        fee_ratio = .00205 + .00001 + .001 + .00002  # 佣金 规费 印花税 过户费
    else:
        fee_ratio = .00205 + .00001 + .001  # 佣金 规费 印花税
    try:
        safe_price = price * (1 - fee_ratio) / (1 + fee_ratio)
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
        self.unmatched_long = []
        self.unmatched_short = []

    def append_list(self, trade_date, trade_type, trade_price, trade_quant, trade_value, fee, gui_fei, tax,
                    account_fee):
        self.trade_list.append(
            {'trade_type': trade_type, 'trade_date': trade_date, 'trade_price': float(trade_price),
             'trade_quant': int(float(trade_quant)),
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
        if self.current_quant != 0:
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
            report += '%s %s 仓位 %d, 平仓保本价 %.2f' % (self.stock, BASIC_INFO.name_dict[self.stock],
                                                   self.current_quant, self.safe_price)
            report += '\n暂时无法进行盈利买卖抵消的交易:\n%s' % self.calc_partial_expect_sell_price()
        return report

    @staticmethod
    def short_summary(transaction):
        return transaction['trade_type'], transaction['trade_price'], transaction['trade_quant']

    def calc_partial_expect_sell_price(self):
        report_str = ''
        buy_list = [i for i in self.trade_list if i['trade_type'] == '证券买入']
        sell_list = [i for i in self.trade_list if i['trade_type'] == '证券卖出']
        unsuccessful_buy = []
        cnt = 0
        while len(buy_list) != 0:
            buy = buy_list[0]
            # check matching of this buy
            # print('H', self.short_summary(buy))
            sell_list_to_check = sell_list.copy()
            while len(sell_list_to_check) != 0:
                if buy['trade_quant'] == 0:
                    break
                cnt += 1
                if cnt == 100:
                    return
                sell = sell_list_to_check[0]
                # print('C', self.short_summary(sell))
                if sell['trade_price'] > calc_arbitrary_safe_price_for_long_transaction(self.stock,
                                                                                        buy['trade_price']):

                    max_quant = min(sell['trade_quant'], buy['trade_quant'])
                    # print('M', self.short_summary(buy), self.short_summary(sell), max_quant)
                    for s in sell_list:
                        if s == sell:
                            s['trade_quant'] -= max_quant
                            break
                    for b in buy_list:
                        if b == buy:
                            b['trade_quant'] -= max_quant
                            break
                    if sell['trade_quant'] == 0:
                        sell_list_to_check.remove(sell)
                        sell_list.remove(sell)

                else:
                    sell_list_to_check.remove(sell)
            if buy['trade_quant'] > 0:
                unsuccessful_buy.append(buy)
            buy_list.remove(buy)
        self.unmatched_short = sell_list.copy()
        self.unmatched_long = unsuccessful_buy

        unsuccessful_buy = [i for i in unsuccessful_buy if i['trade_quant'] > 0]
        unsuccessful_buy.sort(key=operator.itemgetter('trade_price'), reverse=True)
        for buy in unsuccessful_buy:
            trade_type, trade_price, trade_quant = self.short_summary(buy)
            report_str += '需一高于 %.2f 的 %d 股卖出实现对%s %.2f, %d 的盈利\n' % \
                          (calc_arbitrary_safe_price_for_long_transaction(self.stock, trade_price),
                           trade_quant, trade_type, trade_price, trade_quant)

        sell_list = [i for i in sell_list if i['trade_quant'] > 0]
        sell_list.sort(key=operator.itemgetter('trade_price'))
        for sell in sell_list:
            trade_type, trade_price, trade_quant = self.short_summary(sell)
            report_str += '需一低于 %.2f 的 %d 股买入实现对%s %.2f, %d 盈利\n' % \
                          (calc_arbitrary_safe_price_for_short_transaction(self.stock, trade_price), trade_quant,
                           trade_type, trade_price, trade_quant)
        return report_str
