from stock.common.common_func import BASIC_INFO
import tushare as ts


def calc_rt_tick(stock):
    outstanding = float(BASIC_INFO.outstanding_dict[stock]) * 100000000.
    large_threshold = outstanding / 3600000
    df = ts.get_today_ticks(stock)
    tick_buy = df[df['type'] == '买盘']
    tick_sell = df[df['type'] == '卖盘']
    tick_buy_large = tick_buy[tick_buy['volume'] >= large_threshold]
    tick_sell_large = tick_sell[tick_sell['volume'] >= large_threshold]
    tick_buy_small = tick_buy[tick_buy['volume'] < large_threshold]
    tick_sell_small = tick_sell[tick_sell['volume'] < large_threshold]
    v_buy_large = sum(tick_buy_large['volume'])
    v_sell_large = sum(tick_sell_large['volume'])
    v_buy_small = sum(tick_buy_small['volume'])
    v_sell_small = sum(tick_sell_small['volume'])
    v_large = v_buy_large - v_sell_large
    v_small = v_buy_small - v_sell_small
    try:
        vls_ratio = (v_buy_large + v_sell_large) / (v_buy_small + v_sell_small)
    except ZeroDivisionError:
        vls_ratio = 1
    return {'stock': stock, 'v_buy_large': v_buy_large, 'v_sell_large': v_sell_large, 'v_buy_small': v_buy_small,
            'v_sell_small': v_sell_small, 'v_large': v_large, 'v_small': v_small, 'vls_ratio': vls_ratio}
