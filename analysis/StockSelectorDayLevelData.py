# DEPENDENCY ( pandas )

import pandas as pd


class SelectHdl:
    def __init__(self, csv_path):
        self.full_data = pd.read_csv(csv_path)
        self.condition_list = []
        self.inter_mid_data = self.full_data.copy()

    def parse_conditions(self, line):
        self.condition_list = line.split(" ")

    def add_condition(self, condition):
        if condition not in self.condition_list:
            self.condition_list.append(condition)

    def clear(self):
        self.inter_mid_data = self.full_data.copy()
        self.condition_list.clear()

    def apply_conditions(self):
        for c in self.condition_list:
            self.inter_mid_data = self.inter_mid_data[self.inter_mid_data[c] == True]

    def get_result(self, json_format=False):
        if json_format:
            pass # TODO implement
        else:
            return len(self.inter_mid_data), ' '.join(self.inter_mid_data['代码'].tolist())


