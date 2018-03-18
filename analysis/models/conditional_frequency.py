# -*- coding: utf-8 -*-
# WINDOWS_GUARANTEED

import multiprocessing as mp
import os
import pickle
import pandas as pd
from tools.data.path_hdl import path_expand, directory_ensure, directory_exists
from tools.io import logging


# As a model, it should follow some general export format.
# Since this is a general model, input directory for training should be user specified.

# USEDIR( $USER_SPECIFIED )
# REGDIR ( models/cond_freq )

# Model should be trained, then saved at first before using. So at using phase it should be loaded from somewhere.
# which means 3 general methods should be provided, they are train, save and load. How to use the model should totally
# decided by user, say maybe they just need to search some values from it.


def calc_cond_freq(model_name, path, params):
    """
    This function counts frequency of given params out of the csv file specified by path, then calculate an estimated
    conditional probability using these counts. Currently only support naive params(use , as and) with bool value.
    TODO: implement composite params handler.
    :param model_name: name of model, used when load/save as model_name.pickle
    :param path: absolute path to the input csv file
    :param params: target1|given1 target2|given2 target3|given3 target4|given4 ...
    :return: a dict of conditional probabilities { "target1|given1":0.001, "target2|given2":0.001,
                                                    "target3|given3":0.001, "target4|given4":0.001, ...}
    """
    result = {}
    param_list = params.split(" ")
    d = pd.read_csv(path)
    cols = list(d.columns.values)
    for p in param_list:
        data = d.copy()
        targets = p.split("|")[0].split(",")
        given = p.split("|")[1].split(",")
        for g in given:
            if g not in cols:
                logging("COND_FREQ_HDL", "[ ERROR ] %s (from param %s) not exists in data cols" % (g, p))
                continue
            data = data[data[g] == True]
        given_cnt = len(data.index)
        for t in targets:
            if t not in cols:
                logging("COND_FREQ_HDL", "[ ERROR ] %s (from param %s) not exists in data cols" % (t, p))
                continue
            data = data[data[t] == True]
        target_cnt = len(data.index)
        result[p] = target_cnt / given_cnt if given_cnt != 0 else 0
    logging("COND_FREQ_HDL", "[ INFO ] %s applied_%s" % (model_name, path.split("/")[-1].split(".")[0]))

    return result


class ConditionalFreqHdl:
    def __init__(self, model_name, use_dir, params):
        self.model_name = model_name
        if use_dir is None:
            self.base_dir = None
        else:
            self.base_dir = path_expand(use_dir)
            if not directory_exists(self.base_dir):
                logging("COND_FREQ_HDL", "[ ERROR ] when init %s, specified input dir %s not exist" % (self.model_name,
                                                                                                       self.base_dir))
                self.base_dir = None
        self.storage_dir = path_expand("models/cond_freq")
        directory_ensure(self.storage_dir)
        self.params = params
        self.probability_dict = {}
        if self.base_dir:
            self.input_files = [os.path.join(self.base_dir, i) for i in os.listdir(self.base_dir)]
        else:
            self.input_files = []
        self.data = None

    def train(self):
        tmp = []
        pool = mp.Pool()
        for i in self.input_files:
            pool.apply_async(calc_cond_freq, args=(self.model_name, i, self.params), callback=tmp.append)
        pool.close()
        pool.join()
        ks = tmp[0].keys()
        result = {k: 0 for k in ks}
        division = len(tmp) if len(tmp) != 0 else 1
        # we use the average Cond Prob of all stocks
        for l in tmp:
            for p in l.keys():
                result[p] += l[p]
        for k in ks:
            result[k] /= division
        self.probability_dict = result
        print(result)
        self.save()

    def save(self):
        with open('%s' % (os.path.join(self.storage_dir, "%s.pickle" % self.model_name)), 'wb') as f:
            pickle.dump(self.probability_dict, f, -1)

    def load(self):
        try:
            with open('%s' % (os.path.join(self.storage_dir, "%s.pickle" % self.model_name)), 'rb') as f:
                self.probability_dict = pickle.load(f)
        except FileNotFoundError:
            self.probability_dict = {}


# CMDEXPORT ( CONDFREQ TRAIN {model_name} {use_dir} {params[4:]} ) cond_freq_train
def cond_freq_train(model_name, use_dir, params):
    c = ConditionalFreqHdl(model_name, use_dir, params)
    c.train()


# Examples:
# if __name__ == '__main__':
#    c = ConditionalFreqHdl("cond_buy", "qa/cond_freq_input",
#                           "QUICK_BUYPOINT|CROSS QUICK_BUYPOINT|TSHAPE QUICK_BUYPOINT|REVERSETSHAPE QUICK_BUYPOINT|ONESHAPE QUICK_BUYPOINT|JUMPHIGHOPEN QUICK_BUYPOINT|JUMPLOWOPEN QUICK_BUYPOINT|MORNINGCROSS QUICK_BUYPOINT|MORNINGSTAR QUICK_BUYPOINT|FRIENDLYFIRE QUICK_BUYPOINT|HOPEOFDAWN QUICK_BUYPOINT|RAISINGSUN QUICK_BUYPOINT|REVERSEHAMMER QUICK_BUYPOINT|HAMMER QUICK_BUYPOINT|FLATFLOOR QUICK_BUYPOINT|CONTINUETHREEJUMPYIN QUICK_BUYPOINT|TRIPLEREDARMY QUICK_BUYPOINT|UPWARDTWOSTARS QUICK_BUYPOINT|JUMPUPWARD QUICK_BUYPOINT|JUMPUPWARDYANG QUICK_BUYPOINT|JUMPDOWNWARDTHREESTARS QUICK_BUYPOINT|TRIPLEUPWARDS QUICK_BUYPOINT|TWOREDONEBLACK QUICK_BUYPOINT|TWILICROSS QUICK_BUYPOINT|TWILISTAR QUICK_BUYPOINT|FRIENDLYPUSHBACK QUICK_BUYPOINT|INCOMINGCLOUDS QUICK_BUYPOINT|HEAVYRAIN QUICK_BUYPOINT|SHOOTINGSTAR QUICK_BUYPOINT|HANGWIRE QUICK_BUYPOINT|FLATROOF QUICK_BUYPOINT|DOUBLECROWS QUICK_BUYPOINT|TRIPLECROWS QUICK_BUYPOINT|HEADSFEETYIN QUICK_BUYPOINT|HEADSFEETYANG QUICK_BUYPOINT|DOWNWARDCOVER QUICK_BUYPOINT|TRIPLEBLKARMY QUICK_BUYPOINT|MILDDOWNWARDS QUICK_BUYPOINT|RUSHINGAWAY QUICK_BUYPOINT|DOWNWARDTRIPLESTARS QUICK_BUYPOINT|DOWNWARDTRIPLESWANS QUICK_BUYPOINT|TRIPLEDOWNWARDSYANG QUICK_BUYPOINT|JUMPHIGHTRIPLEYANG QUICK_BUYPOINT|UPWARDRESISTENCE QUICK_BUYPOINT|UPWARDPAUSE QUICK_BUYPOINT|LAMPYANG QUICK_BUYPOINT|BLKREDBLK QUICK_BUYPOINT|LONGCROSS QUICK_BUYPOINT|PROPELLER QUICK_BUYPOINT|EOFUPWARD QUICK_BUYPOINT|EOFDOWNWARD QUICK_BUYPOINT|PREGNANTYANG QUICK_BUYPOINT|PREGNANTYIN QUICK_BUYPOINT|MAALIGNUPWARD QUICK_BUYPOINT|MAALIGNDOWNWARD QUICK_BUYPOINT|GOLDCROSS510 QUICK_BUYPOINT|GOLDCROSS520 QUICK_BUYPOINT|GOLDCROSS1020 QUICK_BUYPOINT|LOSECROSS510 QUICK_BUYPOINT|LOSECROSS520 QUICK_BUYPOINT|LOSECROSS1020 QUICK_BUYPOINT|GOLDVALLEY QUICK_BUYPOINT|LOSEVALLEY QUICK_BUYPOINT|DRAGONOUT QUICK_BUYPOINT|LOSEEVERYTHING")
#    c.train()
#    d = ConditionalFreqHdl('cond_sell', "qa/cond_freq_input",
#                           "QUICK_SELLPOINT|CROSS QUICK_SELLPOINT|TSHAPE QUICK_SELLPOINT|REVERSETSHAPE QUICK_SELLPOINT|ONESHAPE QUICK_SELLPOINT|JUMPHIGHOPEN QUICK_SELLPOINT|JUMPLOWOPEN QUICK_SELLPOINT|MORNINGCROSS QUICK_SELLPOINT|MORNINGSTAR QUICK_SELLPOINT|FRIENDLYFIRE QUICK_SELLPOINT|HOPEOFDAWN QUICK_SELLPOINT|RAISINGSUN QUICK_SELLPOINT|REVERSEHAMMER QUICK_SELLPOINT|HAMMER QUICK_SELLPOINT|FLATFLOOR QUICK_SELLPOINT|CONTINUETHREEJUMPYIN QUICK_SELLPOINT|TRIPLEREDARMY QUICK_SELLPOINT|UPWARDTWOSTARS QUICK_SELLPOINT|JUMPUPWARD QUICK_SELLPOINT|JUMPUPWARDYANG QUICK_SELLPOINT|JUMPDOWNWARDTHREESTARS QUICK_SELLPOINT|TRIPLEUPWARDS QUICK_SELLPOINT|TWOREDONEBLACK QUICK_SELLPOINT|TWILICROSS QUICK_SELLPOINT|TWILISTAR QUICK_SELLPOINT|FRIENDLYPUSHBACK QUICK_SELLPOINT|INCOMINGCLOUDS QUICK_SELLPOINT|HEAVYRAIN QUICK_SELLPOINT|SHOOTINGSTAR QUICK_SELLPOINT|HANGWIRE QUICK_SELLPOINT|FLATROOF QUICK_SELLPOINT|DOUBLECROWS QUICK_SELLPOINT|TRIPLECROWS QUICK_SELLPOINT|HEADSFEETYIN QUICK_SELLPOINT|HEADSFEETYANG QUICK_SELLPOINT|DOWNWARDCOVER QUICK_SELLPOINT|TRIPLEBLKARMY QUICK_SELLPOINT|MILDDOWNWARDS QUICK_SELLPOINT|RUSHINGAWAY QUICK_SELLPOINT|DOWNWARDTRIPLESTARS QUICK_SELLPOINT|DOWNWARDTRIPLESWANS QUICK_SELLPOINT|TRIPLEDOWNWARDSYANG QUICK_SELLPOINT|JUMPHIGHTRIPLEYANG QUICK_SELLPOINT|UPWARDRESISTENCE QUICK_SELLPOINT|UPWARDPAUSE QUICK_SELLPOINT|LAMPYANG QUICK_SELLPOINT|BLKREDBLK QUICK_SELLPOINT|LONGCROSS QUICK_SELLPOINT|PROPELLER QUICK_SELLPOINT|EOFUPWARD QUICK_SELLPOINT|EOFDOWNWARD QUICK_SELLPOINT|PREGNANTYANG QUICK_SELLPOINT|PREGNANTYIN QUICK_SELLPOINT|MAALIGNUPWARD QUICK_SELLPOINT|MAALIGNDOWNWARD QUICK_SELLPOINT|GOLDCROSS510 QUICK_SELLPOINT|GOLDCROSS520 QUICK_SELLPOINT|GOLDCROSS1020 QUICK_SELLPOINT|LOSECROSS510 QUICK_SELLPOINT|LOSECROSS520 QUICK_SELLPOINT|LOSECROSS1020 QUICK_SELLPOINT|GOLDVALLEY QUICK_SELLPOINT|LOSEVALLEY QUICK_SELLPOINT|DRAGONOUT QUICK_SELLPOINT|LOSEEVERYTHING")
#    d.train()
