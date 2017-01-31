#!/usr/bin/python3
import random

import sys

from qa_trend_continue import calc_average_trade_price_for_stock, calc_atpdr_for_stock, calc_atpd_for_all_stock
from qa_ma import ma_align
from qa_tick_lms import calc_lms_for_stocK_one_day_dict_wrap
from qa_adl import calculate_adl_for_stock
from qa_vhf import calculate_vhf
from qa_buy_point import get_buy_point_for_stock
from common_func import *
import multiprocessing as mp
import pandas as pd


def prepare_ma_lms_adl_for_stock(stock, short, mid, long, refresh=False, vhf_n=5):
    calc_average_trade_price_for_stock(stock, refresh)
    calc_atpdr_for_stock(stock)
    adl = calculate_adl_for_stock(stock)
    vhf = calculate_vhf(stock, vhf_n)
    buy_point_list = get_buy_point_for_stock(stock, 10, 30, 1.2)
    m = ma_align(stock, short, mid, long)
    date_valid_list = m.date_valid
    ma_list = []
    for d in date_valid_list:
        r, o = m.analysis_align_for_day(d)
        r.update(calc_lms_for_stocK_one_day_dict_wrap(stock, d))
        for l in adl:
            if l['date'] == d:
                r['adl'] = l['adl']
                break
        for l in vhf:
            if l['date'] == d:
                r['vhf'] = l['vhf']
                break
        if d in buy_point_list:
            r['buy_point'] = True
        else:
            r['buy_point'] = False
        r['stock'] = stock
        ma_list.append(r)
    return ma_list


def data_preparation():
    final_list = []
    calc_atpd_for_all_stock()
    pool = mp.Pool()
    for i in SYMBOL_LIST:
        pool.apply_async(prepare_ma_lms_adl_for_stock, args=(i, 10, 20, 40), callback=final_list.append)
    pool.close()
    pool.join()
    b = pd.DataFrame(final_list)
    b.to_csv('../stock_data/qa/perceptron.csv', index=False)
    return final_list


def load_preparation_data(train=7, dev=2, test=1):
    raw_data_list = []
    with open('../stock_data/qa/perceptron.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            raw_data_list.append(row)
    randomized_data_list = random.sample(raw_data_list, len(raw_data_list))
    train_data = randomized_data_list[0:int(train / (train + dev + test) * len(randomized_data_list))]
    dev_data = randomized_data_list[int(train / (train + dev + test) * len(randomized_data_list)):
    int((train + dev) / (train + dev + test) * len(randomized_data_list))]
    test_data = randomized_data_list[int((train + dev) / (train + dev + test) * len(randomized_data_list)):
    len(randomized_data_list)]
    features = [i for i in randomized_data_list[0].keys() if i not in ['stock', 'date', 'buy_point']]
    return train_data, dev_data, test_data, features


class Perceptron:
    def __init__(self, MAX_ITERATIONS=100):
        self.CLASSES = [True, False]
        self.MAX_ITERATIONS = MAX_ITERATIONS
        self.train_data, self.dev_data, self.test_data, self.features = load_preparation_data()
        self.weights = {i: 1 for i in self.features}
        self.theta = {i: 1 for i in self.features}
        self.eta = 0.5
        self.y = 'buy_point'

    def learn(self):
        for iteration in range(self.MAX_ITERATIONS):
            nUpdates = 0
            print('iteration:', iteration, end=' ', file=sys.stderr)
            for line in self.train_data:
                if line['buy_point'] =='True':
                    line['buy_point'] = True
                else:
                    line['buy_point'] = False
                pred = self.predict(line)
                if pred != line['buy_point']:
                    for i in self.features:
                        self.weights[i] += self.eta * (float(line['buy_point']) - float(pred))  # eta(y-f(x))
                        self.theta[i] += self.eta * (float(pred) - float(line['buy_point']))
                    nUpdates += 1

            trainAcc = (len(self.train_data) - nUpdates) / len(self.train_data)
            print('updates=' + str(nUpdates),
                  'trainAcc=' + str(trainAcc), file=sys.stderr)
            if nUpdates == 0:
                print('converged', file=sys.stderr)
                break

    def predict(self, line):
        return sum(self.weights[i] * float(line[i]) - self.theta[i] for i in self.features) > 0  # sum(w[i] x[i]- theta[i])

    def evaluation(self):
        correct_cnt = 0
        for line in self.dev_data:
            if line['buy_point'] == 'True':
                line['buy_point'] = True
            else:
                line['buy_point'] = False
            if self.predict(line) == line['buy_point']:
                correct_cnt += 1
        print('Evaliation %d of %d correct, rate %.24f' %(correct_cnt, len(self.dev_data), correct_cnt / len(self.dev_data)))

    def save_weights(self):
        params = [self.weights,self.theta]
        with open('../stock_data/qa/perceptron_params/.pickle', 'wb') as f:
            pickle.dump(params, f)

    def load_weights(self):
        try:
            with open('../stock_data/market_open_date_list.pickle', 'rb') as f:
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