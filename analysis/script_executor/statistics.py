import os
import pandas as pd
import multiprocessing as mp
from configs.path import DIRs
from tools.io import logging


class ConditionalStatisticsHdl:
    def __init__(self, params, data_folder):
        self.params = params
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

    def statistic(self):
        path_list = self.generate_path_list()
        tmp = []
        # for i in path_list:
        #    tmp.append(counting(i, self.params))
        pool = mp.Pool()
        for i in path_list:
            pool.apply_async(counting, args=(i, self.params), callback=tmp.append)
        pool.close()
        pool.join()
        ks = tmp[0].keys()
        result = {k: 0 for k in ks}
        division = len(tmp) if len(tmp) != 0 else 1
        for l in tmp:
            for p in l.keys():
                result[p] += l[p]
        for k in ks:
            result[k] /= division
        print(result)


def counting(path, params):
    result = {}
    param_list = params.split(" ")
    d = pd.read_csv(path)
    for p in param_list:
        data = d.copy()
        targets = p.split("|")[0].split(",")
        given = p.split("|")[1].split(",")
        for g in given:
            data = data[data[g] == True]
        given_cnt = len(data.index)
        for t in targets:
            data = data[data[t] == True]
        target_cnt = len(data.index)
        result[p] = target_cnt / given_cnt if given_cnt != 0 else 0
    logging("Counting", "applied_%s" % path.split("/")[-1].split(".")[0])

    return result


if __name__ == '__main__':
    a = ConditionalStatisticsHdl(
        "QUICK_BUYPOINT|CROSS QUICK_BUYPOINT|TSHAPE QUICK_BUYPOINT|REVERSETSHAPE QUICK_BUYPOINT|ONESHAPE QUICK_BUYPOINT|JUMPHIGHOPEN QUICK_BUYPOINT|JUMPLOWOPEN QUICK_BUYPOINT|LARGEK QUICK_BUYPOINT|MIDK QUICK_BUYPOINT|SMALLK QUICK_BUYPOINT|MORNINGCROSS QUICK_BUYPOINT|MORNINGSTAR QUICK_BUYPOINT|FRIENDLYFIRE QUICK_BUYPOINT|HOPEOFDAWN QUICK_BUYPOINT|RAISINGSUN QUICK_BUYPOINT|REVERSEHAMMER QUICK_BUYPOINT|HAMMER QUICK_BUYPOINT|FLATFLOOR QUICK_BUYPOINT|CONTINUETHREEJUMPYIN QUICK_BUYPOINT|TRIPLEREDARMY QUICK_BUYPOINT|UPWARDTWOSTARS QUICK_BUYPOINT|JUMPUPWARD QUICK_BUYPOINT|JUMPUPWARDYANG QUICK_BUYPOINT|JUMPDOWNWARDTHREESTARS QUICK_BUYPOINT|TRIPLEUPWARDS QUICK_BUYPOINT|TWOREDONEBLACK QUICK_BUYPOINT|TWILICROSS QUICK_BUYPOINT|TWILISTAR QUICK_BUYPOINT|FRIENDLYPUSHBACK QUICK_BUYPOINT|INCOMINGCLOUDS QUICK_BUYPOINT|HEAVYRAIN QUICK_BUYPOINT|SHOOTINGSTAR QUICK_BUYPOINT|HANGWIRE QUICK_BUYPOINT|FLATROOF QUICK_BUYPOINT|DOUBLECROWS QUICK_BUYPOINT|TRIPLECROWS QUICK_BUYPOINT|HEADSFEETYIN QUICK_BUYPOINT|HEADSFEETYANG QUICK_BUYPOINT|DOWNWARDCOVER QUICK_BUYPOINT|TRIPLEBLKARMY QUICK_BUYPOINT|MILDDOWNWARDS QUICK_BUYPOINT|RUSHINGAWAY QUICK_BUYPOINT|DOWNWARDTRIPLESTARS QUICK_BUYPOINT|DOWNWARDTRIPLESWANS QUICK_BUYPOINT|TRIPLEDOWNWARDSYANG QUICK_BUYPOINT|JUMPHIGHTRIPLEYANG QUICK_BUYPOINT|UPWARDRESISTENCE QUICK_BUYPOINT|UPWARDPAUSE QUICK_BUYPOINT|LAMPYANG QUICK_BUYPOINT|BLKREDBLK QUICK_BUYPOINT|LONGCROSS QUICK_BUYPOINT|PROPELLER QUICK_BUYPOINT|EOFUPWARD QUICK_BUYPOINT|EOFDOWNWARD QUICK_BUYPOINT|PREGNANTYANG QUICK_BUYPOINT|PREGNANTYIN QUICK_BUYPOINT|MAALIGNUPWARD QUICK_BUYPOINT|MAALIGNDOWNWARD QUICK_BUYPOINT|GOLDCROSS510 QUICK_BUYPOINT|GOLDCROSS520 QUICK_BUYPOINT|GOLDCROSS1020 QUICK_BUYPOINT|LOSECROSS510 QUICK_BUYPOINT|LOSECROSS520 QUICK_BUYPOINT|LOSECROSS1020 QUICK_BUYPOINT|GOLDVALLEY QUICK_BUYPOINT|LOSEVALLEY QUICK_BUYPOINT|DRAGONOUT QUICK_BUYPOINT|LOSEEVERYTHING",
        "merged")
    a.statistic()
