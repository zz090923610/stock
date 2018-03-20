# -*- coding: utf-8 -*-

import os

from mkt_monitor.rules import Rule
from tools.data.file_hdl import save_text, load_text
from tools.data.path_hdl import directory_ensure, path_expand, file_exist
from tools.date_util.market_calendar_cn import MktCalendar


# REGDIR ( stock_feature )

class StockFeature:
    def __init__(self, symbol, cal: MktCalendar):
        self.rules = {}
        self.symbol = symbol
        self.cal = cal
        self.stock_monitor_rules_dir = path_expand("stock_feature")
        directory_ensure(self.stock_monitor_rules_dir)

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
        content = ''
        for r in self.rules.keys():
            content += "%s\n" % self.rules[r].generate_line()
        save_text(os.path.join(self.stock_monitor_rules_dir, "%s.rules" % self.symbol), content)

    def load_rules(self, path):
        if not file_exist(path):
            raw_rules = ''
        else:
            raw_rules = load_text(path)
        for line in raw_rules:
            line = line.strip()
            if len(line):
                new_rule = Rule(self.cal)
                new_rule.parse_line(line)
                self.rules[new_rule.name] = new_rule

    def check_rules(self, val_now):
        for rule in self.rules.values():
            callbacks = rule.check_val(val_now)
            for cb in callbacks:
                (cb_action, cb_obj) = cb.split("_")
                if cb_obj in self.rules.keys():
                    self.rules[cb_obj] = {"pend": "pending", "finish": "finished", "activate": "active"}[cb_action]

    def generate_output(self):
        out_str = self.symbol + "\n"
        for k in self.rules.keys():
            out_str += "%s: %s\n" % (k, self.rules[k].generate_line())
        return out_str
