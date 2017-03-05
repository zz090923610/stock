#!/usr/bin/python3
import random
import sys

from common_func import *
from qa_adl import load_adl_data
from qa_buy_point import get_buy_point_for_stock
from qa_ma import ma_align
from qa_tick_lms import load_lms
from qa_vhf import load_vhf_data


def save_perceptron_data_for_stock(stock, data_list):
    subprocess.call("mkdir -p ../stock_data/quantitative_analysis/perceptron", shell=True)
    with open('../stock_data/quantitative_analysis/perceptron/%s.pickle' % stock, 'wb') as f:
        pickle.dump(data_list, f, -1)


def load_perceptron_data_for_stock(stock):
    # noinspection PyBroadException
    try:
        with open('../stock_data/quantitative_analysis/perceptron/%s.pickle' % stock, 'rb') as f:
            return pickle.load(f)
    except:
        return []


# noinspection PyUnusedLocal
def data_calculation_phase(vhf_n=5):
    pass
    # calc_atpd_for_all_stock(refresh=False)
    # calc_atpdr_for_all_stock()
    # calc_lms_for_all_stock()
    # calc_adl_for_all_stock()
    # calc_vhf_for_all_stock(vhf_n)


def prepare_ma_lms_adl_for_stock(stock, short, mid, long):
    print('Load adl for %s' % stock)
    adl = load_adl_data(stock)
    adl_dict = {}
    for line in adl:
        adl_dict[line['date']] = line['adl']
    print('Load vhf for %s' % stock)
    vhf = load_vhf_data(stock)
    vhf_dict = {}
    for line in vhf:
        vhf_dict[line['date']] = line['vhf']
    lms = load_lms(stock)
    lms_dict = {}
    for line in lms:
        lms_dict[line['date']] = {'buy_large': line['buy_large'], 'sell_large': line['sell_large'],
                                  'buy_mid': line['buy_mid'], 'sell_mid': line['sell_mid'],
                                  'buy_small': line['buy_small'], 'sell_small': line['sell_small'],
                                  'undirected_trade': line['undirected_trade']}
    buy_point_list = get_buy_point_for_stock(stock, 10, 30, 1.2, retract=True)
    m = ma_align(stock, short, mid, long)
    date_valid_list = m.date_valid
    ma_list = []
    for d in date_valid_list:
        r, o = m.analysis_align_for_day(d)
        r.update(lms_dict[d])
        r['adl'] = adl_dict[d]
        r['vhf'] = vhf_dict[d]
        if d in buy_point_list:
            r['buy_point'] = True
        else:
            r['buy_point'] = False
        r['stock'] = stock
        ma_list.append(r)
    save_perceptron_data_for_stock(stock, ma_list)


def data_preparation():
    pool = mp.Pool()
    for i in BASIC_INFO.symbol_list:
        pool.apply_async(prepare_ma_lms_adl_for_stock, args=(i, 10, 20, 40))
    pool.close()
    pool.join()


def load_preparation_data(train=7, dev=2, test=1):
    raw_data_list = []
    for i in BASIC_INFO.symbol_list:
        raw_data_list += load_perceptron_data_for_stock(i)
    randomized_data_list = random.sample(raw_data_list, len(raw_data_list))
    train_data = randomized_data_list[0:int(train / (train + dev + test) * len(randomized_data_list))]
    dev_data = randomized_data_list[int(train / (train + dev + test) * len(randomized_data_list)):
        int((train + dev) / (train + dev + test) * len(randomized_data_list))]
    test_data = randomized_data_list[int((train + dev) / (train + dev + test) * len(randomized_data_list)):
        len(randomized_data_list)]
    features = [i for i in randomized_data_list[0].keys() if i not in ['stock', 'date', 'buy_point']]
    return train_data, dev_data, test_data, features


class Perceptron:
    def __init__(self, MAX_ITERATIONS=20):
        self.CLASSES = [True, False]
        self.MAX_ITERATIONS = MAX_ITERATIONS
        self.train_data, self.dev_data, self.test_data, self.features = load_preparation_data()
        self.weights = {i: 1 for i in self.features}
        self.theta = {i: 1 for i in self.features}
        self.eta = 0.618
        self.y = 'buy_point'

    def learn(self):
        for iteration in range(self.MAX_ITERATIONS):
            nUpdates = 0
            print('iteration:', iteration, end=' ', file=sys.stderr)
            for line in self.train_data:
                if line['buy_point'] == 'True':
                    line['buy_point'] = 1
                elif line['buy_point'] == 'False':
                    line['buy_point'] = -1
                pred = self.predict(line)
                if (pred > 0) != line['buy_point']:
                    for i in self.features:
                        self.weights[i] += self.eta * (float(line['buy_point']) - pred)  # eta(y-f(x))
                        self.theta[i] += self.eta * (pred - float(line['buy_point']))
                    nUpdates += 1

            trainAcc = (len(self.train_data) - nUpdates) / len(self.train_data)
            print('updates=' + str(nUpdates),
                  'trainAcc=' + str(trainAcc), file=sys.stderr)
            self.evaluation()
            if nUpdates == 0:
                print('converged', file=sys.stderr)
                break

    def predict(self, line):
        return sum(
            self.weights[i] * float(line[i]) - self.theta[i] for i in self.features)  # sum(w[i] x[i]- theta[i])

    @staticmethod
    def load_data_for_stock_prediction(stock, short, mid, long, day):
        print('Load adl for %s' % stock)
        adl = load_adl_data(stock)
        adl_day = None
        lms_day = None
        vhf_day = None
        for line in adl:
            if line['date'] == day:
                adl_day = line['adl']
        print('Load vhf for %s' % stock)
        vhf = load_vhf_data(stock)
        for line in vhf:
            if line['date'] == day:
                vhf_day = line['vhf']
        lms = load_lms(stock)
        for line in lms:
            if line['date'] == day:
                lms_day = {'buy_large': line['buy_large'], 'sell_large': line['sell_large'],
                           'buy_mid': line['buy_mid'], 'sell_mid': line['sell_mid'],
                           'buy_small': line['buy_small'], 'sell_small': line['sell_small'],
                           'undirected_trade': line['undirected_trade']}
        m = ma_align(stock, short, mid, long)
        r, o = m.analysis_align_for_day(day)
        r.update(lms_day)
        r['adl'] = adl_day
        r['vhf'] = vhf_day
        r['stock'] = stock
        return r

    def evaluation(self):
        true_positive = 0
        false_negative = 0
        true_cnt = 1
        false_cnt = 1

        for line in self.dev_data:
            if line['buy_point'] == 'True':
                line['buy_point'] = 1
                true_cnt += 1
            elif line['buy_point'] == 'False':
                line['buy_point'] = -1
                false_cnt += 1
            if (self.predict(line) > 0) == line['buy_point']:
                if self.predict(line) > 0:
                    true_positive += 1
                else:
                    false_negative += 1

        print('Evaluation TP %d %d %.5f' % (true_positive, true_cnt, true_positive / float(true_cnt)))
        print('Evaluation FN %d %d %.5f' % (false_negative, false_cnt, false_negative / float(false_cnt)))

    def save_weights(self):
        params = [self.weights, self.theta]
        with open('../stock_data/quantitative_analysis/perceptron_params/params.pickle', 'wb') as f:
            pickle.dump(params, f)

    def load_weights(self):
        # noinspection PyBroadException
        try:
            with open('../stock_data/quantitative_analysis/perceptron_params/params.pickle', 'rb') as f:
                params = pickle.load(f)
                self.weights = params[0]
                self.theta = params[1]
        except:
            pass


if __name__ == '__main__':
    data_preparation()
    perceptron = Perceptron()
    perceptron.learn()
    perceptron.evaluation()
    perceptron.save_weights()
