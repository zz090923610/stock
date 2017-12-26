import os
import pandas as pd

from configs.path import DIRs


class ConditionalStatisticsHdl:
    def __init__(self, params, data_folder):
        self.param_list = params.split[" "]
        self.probability_dict = {}
        self.base_dir = self._validate_input_path(data_folder)
        self.symbol_list = os.listdir(self.base_dir)
        self.data = None

    @staticmethod
    def _validate_input_path(p):
        if os.path.isfile(p):
            return p
        elif p.split('/')[0] in os.listdir(DIRs.get("QA")):
            if os.path.exists(DIRs.get("QA") + '/' + p):
                return DIRs.get("QA") + '/' + p

        elif p.split('/')[0] in os.listdir(DIRs.get("DATA_ROOT")):
            if os.path.exists(DIRs.get("DATA_ROOT") + '/' + p):
                return DIRs.get("DATA_ROOT") + '/' + p
        else:
            return DIRs.get("QA") + '/' + p

    def generate_path_list(self):
        path_list = []
        for s in self.symbol_list:
            path_list.append(os.path.join(self.base_dir, s))
        return path_list

    def load_data(self, path):
        self.data = pd.read_csv(path)

    def handle_all_statistics(self, param):
        for p in self.generate_path_list():
            self.handle_single_statistics(param, p)

    def handle_single_statistics(self, param, path):
        self.load_data(path)
        targets = param.split("|")[0].split[","]
        givens = param.split("|")[1].split[","]
        self.counting(targets, givens)

    def counting(self, targets, givens):

        for g in givens:

