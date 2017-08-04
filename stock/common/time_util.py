import json
import os
import pickle
from datetime import datetime
from datetime import date
import time
from datetime import timedelta as td
import daemon
from stock.common.file_operation import save_pickle, load_pickle, logging
from stock.common.variables import *
import sys
import paho.mqtt.client as mqtt
import threading
import daemon.pidfile
import tushare as ts


def load_last_date(date_type='last_trade_day_cn'):
    if os.path.exists('/tmp/stock/daemon/pid/time_util.pid'):
        a = load_pickle('/tmp/stock/daemon/data/time_util/time_data.pickle')
        return a[date_type]
    else:
        return None  # FIXME


def load_stock_date_list_from_tick_files(stock):
    file_list = os.listdir('%s/tick_data/%s' % (COMMON_VARS_OBJ.stock_data_root, stock))
    if len(file_list) == 0:
        return []
    date_list = []
    for f in file_list:
        day = f.split('_')[1].split('.')[0]
        (y, m, d) = int(day.split('-')[0]), int(day.split('-')[1]), int(day.split('-')[2])
        date_list.append(datetime(y, m, d).strftime("%Y-%m-%d"))
    return date_list


def check_weekday(date_str):
    (y, m, d) = int(date_str.split('-')[0]), int(date_str.split('-')[1]), int(date_str.split('-')[2])
    if datetime(y, m, d).weekday() in range(0, 5):
        return True
    else:
        return False


def return_weekday(date_str):
    (y, m, d) = int(date_str.split('-')[0]), int(date_str.split('-')[1]), int(date_str.split('-')[2])
    return datetime(y, m, d).weekday()


def get_weekends_of_a_year(year):
    d1 = date(int(year), 1, 1)
    d2 = date(int(year), 12, 31)
    days = []
    delta = d2 - d1
    for i in range(delta.days + 1):
        if not check_weekday((d1 + td(days=i)).strftime('%Y-%m-%d')):
            days.append((d1 + td(days=i)).strftime('%Y-%m-%d'))
    return days


def create_market_close_days_for_year(year, other_close_dates_list):
    weekends_list = get_weekends_of_a_year(year)
    for d in other_close_dates_list:
        if d not in weekends_list:
            weekends_list.append(d)
    weekends_list.sort()
    with open('%s/dates/market_close_days_%s.pickle' % (COMMON_VARS_OBJ.stock_data_root, year), 'wb') as f:
        pickle.dump(weekends_list, f)


def update_market_open_date_list():
    print('Updating market dates list')
    b = ts.get_k_data('000001', index=True, start=COMMON_VARS_OBJ.START_DATE)
    days_cnt = len(b.index)
    days_list = b['date'].tolist()
    save_market_open_date_list(days_list)
    return days_list


def save_market_open_date_list(market_open_date_list):
    with open('%s/market_open_date_list.pickle' % COMMON_VARS_OBJ.stock_data_root, 'wb') as f:
        pickle.dump(market_open_date_list, f, -1)


def load_market_open_date_list_from(given_day=COMMON_VARS_OBJ.START_DATE):
    try:
        with open('%s/market_open_date_list.pickle' % COMMON_VARS_OBJ.stock_data_root, 'rb') as f:
            raw_date = pickle.load(f)
    except FileNotFoundError:
        raw_date = update_market_open_date_list()
    result_list = []
    for day in raw_date:
        if day >= given_day:
            result_list.append(day)
    return result_list


def str2date(str_date):
    (y, m, d) = int(str_date.split('-')[0]), int(str_date.split('-')[1]), int(str_date.split('-')[2])
    return date(y, m, d)


# noinspection PyMethodMayBeStatic
class TimeUtil:
    def __init__(self, as_daemon=False):
        self.dates = {'last_trade_day_cn': self.get_last_trade_day_cn(),
                      'last_day_cn': self.get_last_day_cn(),
                      'current_day_cn': self.get_real_day_cn()}
        if as_daemon:
            self.client = mqtt.Client()
            self.client.on_connect = self.mqtt_on_connect
            self.client.on_message = self.mqtt_on_message
            self.client.on_subscribe = self.mqtt_on_subscribe
            self.client.on_publish = self.mqtt_on_publish
            self.client.connect("localhost", 1883, 60)
            self.mqtt_topic_sub = "time_util_req"
            self.mqtt_topic_pub = "time_util_update"
            self.cancel_daemon = False

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        mqttc.subscribe(self.mqtt_topic_sub)

    def mqtt_on_message(self, mqttc, obj, msg):
        if IS_DEBUG:
            logging(msg.topic + " " + str(msg.qos) + " " + str(msg.payload), silence=True)
        payload = msg.payload.decode('utf8')
        if payload == 'is_alive':
            self.publish('alive')
        elif payload == 'date_req':
            self.publish('%s' % json.dumps(self.dates))

    def publish(self, msg, qos=1):
        (result, mid) = self.client.publish(self.mqtt_topic_pub, msg, qos)

    def mqtt_on_publish(self, mqttc, obj, mid):
        if IS_DEBUG:
            logging("Time Util Daemon mid: " + str(mid), silence=True)

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        if IS_DEBUG:
            logging("Time Util Daemon Subscribed: " + str(mid) + " " + str(granted_qos), silence=True)

    def mqtt_on_log(self, mqttc, obj, level, string):
        if IS_DEBUG:
            logging(string, silence=True)

    def MQTT_CANCEL(self):
        self.client.loop_stop(force=True)
        if IS_DEBUG:
            logging('Time Util Daemon MQTT Client Canceled', silence=True)

    def MQTT_START(self):
        threading.Thread(target=self.client.loop_start).start()
        if IS_DEBUG:
            logging('Time Util Daemon MQTT Client Started', silence=True)

    def daemon_main(self):
        self.MQTT_START()
        self.publish('alive')
        while not self.cancel_daemon:
            pid_dir = COMMON_VARS_OBJ.DAEMON['time_util']['pid_path']
            data_dir = COMMON_VARS_OBJ.DAEMON['time_util']['data_path']
            data_path = COMMON_VARS_OBJ.DAEMON['time_util']['data_path'] + '/time_data.pickle'
            if not os.path.isdir(pid_dir):
                os.makedirs(pid_dir)
            if not os.path.isdir(data_dir):
                os.makedirs(data_dir)
            new_dates = {'last_trade_day_cn': self.get_last_trade_day_cn(),
                         'last_day_cn': self.get_last_day_cn(),
                         'current_day_cn': self.get_real_day_cn()}
            data_file_exist = os.path.exists(data_path)
            if (self.dates != new_dates) | (data_file_exist is False):
                print('%r' % new_dates)
                self.dates = new_dates
                self.publish('%s' % json.dumps(self.dates))
                save_pickle(data_path, self.dates)
            time.sleep(2)
        self.MQTT_CANCEL()

    def get_last_trade_day_cn(self):
        current_time = time.time()
        utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
        local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(COMMON_VARS_OBJ.china_tz)
        year = local_now.strftime("%Y")
        local_now = local_now.strftime("%Y-%m-%d")

        history_market_open_list = self.load_historical_market_open_date_list()
        candidate_list = sorted(list(set(history_market_open_list).union(set(self.get_all_trade_days_of(year)))))
        candidate_list = [i for i in candidate_list if i <= local_now]
        time_of_the_day = self.get_time_of_a_day()

        if local_now in candidate_list:
            if time_of_the_day >= '17:30:00':
                result = local_now
            else:
                candidate_list.remove(local_now)
                result = max(candidate_list)
        else:
            result = max(candidate_list)
        return result

    def get_last_day_cn(self):
        current_time = time.time()
        utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
        local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(COMMON_VARS_OBJ.china_tz)
        year = local_now.strftime("%Y")
        local_now = local_now.strftime("%Y-%m-%d")
        last_year = str(int(year) - 1)
        candidate_list = sorted(self.get_all_days_of(last_year) + self.get_all_days_of(year))
        candidate_list = [i for i in candidate_list if i < local_now]
        return max(candidate_list)

    def sleep_until(self, when):
        h, m, s = int(when.split(':')[0]), int(when.split(':')[1]), int(when.split(':')[2])
        date_today = load_last_date()
        next_wake_up_time = datetime(int(date_today.split('-')[0]), int(date_today.split('-')[1]),
                                     int(date_today.split('-')[2]), h,
                                     m, s) + td(days=1)
        local_time = self.get_time_of_a_day()
        ln = datetime(int(date_today.split('-')[0]), int(date_today.split('-')[1]), int(date_today.split('-')[2]),
                      int(local_time.split(':')[0]), int(local_time.split(':')[1]), int(local_time.split(':')[2]))
        seconds = next_wake_up_time - ln
        print("now is " + self.get_time_of_a_day())
        print("sleeping %d" % seconds.seconds)
        time.sleep(seconds.seconds)

    @staticmethod
    def get_time():
        from datetime import datetime
        current_time = time.time()
        utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
        local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(COMMON_VARS_OBJ.china_tz)
        return local_now.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_real_day_cn():
        from datetime import datetime
        current_time = time.time()
        utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
        local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(COMMON_VARS_OBJ.china_tz)
        return local_now.strftime("%Y-%m-%d")

    @staticmethod
    def get_time_of_a_day():
        from datetime import datetime
        current_time = time.time()
        utc_now, now = datetime.utcfromtimestamp(current_time), datetime.fromtimestamp(current_time)
        local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(COMMON_VARS_OBJ.china_tz)
        return local_now.strftime("%H:%M:%S")

    def load_market_close_days_for_year(self, year):
        try:
            with open('%s/dates/market_close_days_%s.pickle' % (COMMON_VARS_OBJ.stock_data_root, year), 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return []

    @staticmethod
    def load_historical_market_open_date_list():
        try:
            with open('%s/market_open_date_list.pickle' % COMMON_VARS_OBJ.stock_data_root, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError as e:
            logging('load_market_open_date_list(): File not found')
            return []

    def get_all_sundays_of(self, year):
        if type(year) == str:
            year = int(year)
        d = date(year, 1, 1)  # January 1st
        d += td(days=6 - d.weekday())  # First Sunday
        ret_list = []
        while d.year == year:
            ret_list.append(d.strftime("%Y-%m-%d"))
            d += td(days=7)
        return ret_list

    def get_all_days_of(self, year):
        if type(year) == str:
            year = int(year)
        d = date(year, 1, 1)  # January 1st
        ret_list = []
        while d.year == year:
            ret_list.append(d.strftime("%Y-%m-%d"))
            d += td(days=1)
        return ret_list

    def get_all_saturdays_of(self, year):
        if type(year) == str:
            year = int(year)
        d = date(year, 1, 1)  # January 1st
        d += td(days=5 - d.weekday())  # First Saturday
        if d.year == year - 1:
            d += td(7)
        ret_list = []
        while d.year == year:
            ret_list.append(d.strftime("%Y-%m-%d"))
            d += td(days=7)
        return ret_list

    def get_all_weekends_of(self, year):
        if type(year) == str:
            year = int(year)
        sunday = self.get_all_sundays_of(year)
        saturday = self.get_all_saturdays_of(year)
        return sorted(sunday + saturday)

    def get_all_weekdays_of(self, year):
        if type(year) == str:
            year = int(year)
        weekends = self.get_all_weekends_of(year)
        days = self.get_all_days_of(year)
        weekdays = sorted(list(set(days) - set(weekends)))
        return weekdays

    def get_all_trade_days_of(self, year):
        if type(year) == str:
            year = int(year)
        all_days = self.get_all_days_of(year)
        weekends = self.get_all_weekends_of(year)
        close_days = self.load_market_close_days_for_year(year)
        return sorted(list(set(all_days) - set(weekends) - set(close_days)))


def main(args=None):
    if args is None:
        args = []
    pid_dir = COMMON_VARS_OBJ.DAEMON['time_util']['pid_path']
    data_dir = COMMON_VARS_OBJ.DAEMON['time_util']['data_path']
    if not os.path.isdir(pid_dir):
        os.makedirs(pid_dir)
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    with daemon.DaemonContext(
            pidfile=daemon.pidfile.PIDLockFile('%s/time_util.pid' % COMMON_VARS_OBJ.DAEMON['time_util']['pid_path'])):
        a = TimeUtil(as_daemon=True)
        a.daemon_main()


if __name__ == '__main__':
    main(sys.argv[1:])
