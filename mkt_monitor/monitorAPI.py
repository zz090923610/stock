import os

from mkt_monitor.stock_feature import stock_monitor_rules_dir, StockFeature
from tools.date_util.market_calendar_cn import MktCalendar


class MonitorAPI:
    def __init__(self):
        self.stock_feature_dict = {}
        self.cal = MktCalendar()
        self.removed_symbols = []

    def add_stock_feature(self, feature_str):
        (symbol, line) = feature_str.split(" ", 1)
        if symbol not in self.stock_feature_dict.keys():
            feature = StockFeature(symbol, self.cal)
            feature.create_rule(line)
            self.stock_feature_dict[symbol] = feature
        else:
            self.stock_feature_dict[symbol].create_rule(line)

    def remove_stock_feature(self, symbol, rule_name):
        if symbol in self.stock_feature_dict.keys():
            if rule_name in self.stock_feature_dict[symbol].rules:
                del self.stock_feature_dict[symbol].rules[rule_name]
            if len(self.stock_feature_dict[symbol].rules.keys()) == 0:
                del self.stock_feature_dict[symbol]
                self.removed_symbols.append(symbol)

    def load_stock_features(self):
        symbol_observed_list = [i.split(".")[0] for i in os.listdir(stock_monitor_rules_dir)]
        for s in symbol_observed_list:
            feature = StockFeature(s, self.cal)
            feature.load_rules(os.path.join(stock_monitor_rules_dir, "%s.rules" % s))
            self.stock_feature_dict[s] = feature

    def save_stock_features(self):
        for f in self.stock_feature_dict.values():
            f.save_rules()
        for s in self.removed_symbols:
            if os.path.exists(os.path.join(stock_monitor_rules_dir, "%s.rules" % s)):
                os.remove(os.path.join(stock_monitor_rules_dir, "%s.rules" % s))

    def generate_output(self):
        final_str = ""
        for symbol in self.stock_feature_dict.keys():
            final_str += self.stock_feature_dict[symbol].generate_output()
        print(final_str)
