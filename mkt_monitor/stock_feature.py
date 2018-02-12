# REGISTER_DATA_DIR {"stock_monitor_rules_dir": "%root/stock_feature/rules"}
# TODO: handle dir register, init.
import os

from mkt_monitor.rules import Rule
from tools.date_util.market_calendar_cn import MktCalendar

stock_monitor_rules_dir = "/home/zhangzhao/data/stockdata/stock_feature/rules"  # REMOVE_WHEN_DIR_REGISTER


# TODO: remove dir from file

class StockFeature:
    def __init__(self, symbol,  cal: MktCalendar):
        self.rules = {}
        self.info = {}
        self.symbol = symbol
        self.cal = cal

    def create_rule(self, line):
        new_rule = Rule(self.cal)
        new_rule.parse_line(line)
        self.rules[new_rule.name] = new_rule

    def add_rule(self, key, rule):
        self.rules[key] = rule

    def remove_rule(self, key):
        if key in self.rules.keys():
            self.rules.pop(key)

    def replace_rule(self, key, new_rule):
        self.rules[key] = new_rule

    def save_rules(self):
        os.makedirs(stock_monitor_rules_dir, exist_ok=True)
        with open(os.path.join(stock_monitor_rules_dir, "%s.rules" % self.symbol), 'w') as f:
            for r in self.rules.keys():
                f.write(self.rules[r].generate_line())
                f.write("\n")
            f.flush()

    def load_rules(self, path):
        if not os.path.exists(stock_monitor_rules_dir):
            os.makedirs(stock_monitor_rules_dir, exist_ok=True)

        if os.path.isfile(path):
            with open(path) as f:
                raw_rules = f.readlines()
        else:
            raw_rules = ''
        for line in raw_rules:
            new_rule = Rule(self.cal)
            new_rule.parse_line(line)
            self.rules[new_rule.name] = new_rule

    def load_info(self):
        pass

    def check_rules(self, val_now):
        for rule in self.rules.values():
            callbacks = rule.check_val(val_now)
            for cb in callbacks:
                (cb_action, cb_obj) = cb.split("_")
                if cb_obj in self.rules.keys():
                    self.rules[cb_obj] = {"pend": "pending", "finish": "finished", "activate": "active"}[cb_action]
