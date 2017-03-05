#!/usr/bin/python3
from stock.common.common_func import *





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
        with open('%s/quantitative_analysis/tvi/%s_%s.pickle' % (stock_data_root, stock, target_date), 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None, None


def save_tvi_stock_day(stock, target_date, dic):
    if not os.path.exists('%s/quantitative_analysis/tvi/' % stock_data_root):
        subprocess.call('mkdir -p %s/quantitative_analysis/tvi/' % stock_data_root, shell=True)
    with open('%s/quantitative_analysis/tvi/%s_%s.pickle' % (stock_data_root, stock, target_date), 'wb') as f:
        pickle.dump(dic, f, -1)



