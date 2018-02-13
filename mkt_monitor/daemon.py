import time
import tushare as ts

# DEPENDENCY( tushare )
from mkt_monitor.monitorAPI import MonitorAPI

m_api = MonitorAPI()
m_api.load_stock_features()


def fetch_real_time_quotes(symbol):
    ds = ts.get_realtime_quotes("000155").loc[0]
    price = ds['price']
    timestamp = "%s&%s" % (ds['date'], ds['time'])
    return {"var": "p", "val": price, "timestamp": timestamp}


def monitoring_cycle():
    for s in m_api.stock_feature_dict.keys():
        print(s)
        real_time_res = fetch_real_time_quotes(s)
        s_feature = m_api.stock_feature_dict[s]
        for r in s_feature.rules.values():
            r.check_val(real_time_res)


if __name__ == '__main__':
    while True:
        monitoring_cycle()
        time.sleep(1)

# TODO this daemon should always run, it should also be able to handle incoming feature/rule modify requests.
# TODO changes of feature/rule should be saved once made.
# TODO proper messages should be prepared.
# TODO trading actions should be implemented
