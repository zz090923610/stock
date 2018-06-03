# -*- coding: utf-8 -*-
import time
import tushare as ts

# DEPENDENCY( tushare )
from tools.mkt_monitor.monitorAPI import MonitorAPI
from tools.date_util.market_calendar_cn import MktDateTime

m_api = MonitorAPI()
m_api.load_stock_features()


def fetch_real_time_quotes(symbol):
    """
    # TODO
    :param symbol:
    :return:
    """
    ds = ts.get_realtime_quotes(symbol).loc[0]
    price = ds['price']
    timestamp = "%s&%s" % (ds['date'], ds['time'])
    return {"var": "p", "val": price, "timestamp": timestamp}


def monitoring_cycle():
    """
    # TODO
    :return:
    """
    time_now = MktDateTime(m_api.cal.now('dt'), m_api.cal)
    if time_now.equiv_date:
        time.sleep(time_now.secs_to(time_now.datetime_r))
    for s in m_api.stock_feature_dict.keys():
        real_time_res = fetch_real_time_quotes(s)
        s_feature = m_api.stock_feature_dict[s]
        for r in s_feature.rules.values():
            r.check_val(real_time_res)


if __name__ == '__main__':
    while True:
        # noinspection PyBroadException
        try:
            monitoring_cycle()
            time.sleep(1)
        except Exception as e:
            pass

# TODO this daemon should always run, it should be able to handle incoming feature/rule modify requests.
# changes of feature/rule should be saved once made.
# more interesting messages should be prepared.
# trading actions currently disabled.
