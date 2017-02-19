#!/usr/bin/python3
from common_func import *


def load_stock_tick_data(stock, target_date):
    df = pd.read_csv('../stock_data/tick_data/%s/%s_%s.csv' % (stock, stock, target_date))
    df = df.sort_values(by='time', ascending=True)
    df = df.reset_index()
    df = df.drop('index', 1)
    # noinspection PyBroadException
    try:
        df = df.drop('Unnamed: 0', 1)
    except:
        pass
    return df


def calc_tvi_stock_day(stock, target_date):
    df = load_stock_tick_data(stock, target_date)
    tvi = 0
    direction = 'a'
    df['tvi'] = 0
    for x in range(len(df)):
        if df.iloc[x]['type'] == u'买盘':
            direction = 'a'
        elif df.iloc[x]['type'] == u'卖盘':
            direction = 'd'
        if direction == 'a':
            tvi += df.iloc[x]['volume']
        elif direction == 'd':
            tvi -= df.iloc[x]['volume']
        df.set_value(x, 'tvi', tvi)
    save_tvi_stock_day(stock, target_date, (df, {'date': target_date, 'tvi': tvi}))
    return df, {'date': target_date, 'tvi': tvi}


def load_tvi_stock_day(stock, target_date):
    try:
        with open('../stock_data/qa/tvi/%s_%s.pickle' % (stock, target_date), 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None, None


def save_tvi_stock_day(stock, target_date, dic):
    if not os.path.exists('../stock_data/qa/tvi/'):
        subprocess.call('mkdir -p ../stock_data/qa/tvi/', shell=True)
    with open('../stock_data/qa/tvi/%s_%s.pickle' % (stock, target_date), 'wb') as f:
        pickle.dump(dic, f, -1)



