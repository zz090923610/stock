# -*- coding: utf-8 -*-
import re

from tools.mkt_monitor.alarm import Alarm
from tools.date_util.market_calendar_cn import MktDateTime, MktCalendar


class Rule:
    """
    # TODO
    """
    def __init__(self, cal: MktCalendar):
        """
        # TODO
        :param cal:
        """
        self.symbol = ''
        self.cal = cal
        self.name = ''
        self.function = ''
        self.t0 = None
        self.unit = ''
        self.trigger = ''
        self.action = []
        self.status = ''
        self.valid = ''
        self.valid_until = ''
        self.callback = []
        self.create_date = ''

    def reset(self):
        """
        # TODO
        :return:
        """
        self.__init__(self.cal)

    def parse_line(self, line):
        """
        # TODO
        :param line:
        :return:
        """
        if len(line) <= 1:
            return
        self.reset()
        # a line like this:
        # symbol:000001 name:pressure unit:d func:p=11-0.1(t-t0) t0:2018-02-01&09:30:00 status:pending valid:1d action:sendmsg action:sell callback:activate_support callback:sleep_self
        # name:support unit:d func:p=9-0.1t status:pending valid:1d action:sendmsg action:buy
        items = line.strip().split(" ")
        for i in items:
            try:
                (k, v) = i.split(":", 1)
                if k == "symbol":
                    self.symbol = v
                elif k == "name":
                    self.name = v
                elif k == "func":
                    self.function = v
                elif k == "t0":
                    self.t0 = MktDateTime(v, self.cal)
                elif k == "unit":
                    self.unit = v
                elif k == "trigger":
                    self.trigger = v
                elif k == "status":
                    self.status = v
                elif k == "valid":
                    self.valid = v
                elif k == "action":
                    self.action.append(v)
                elif k == "callback":
                    self.callback.append(v)
            except Exception as e:
                print("ERR when parsing %s" % i)
                print(e)
        self.create_date = self.cal.now('d')
        self.calc_valid_until()

    def generate_line(self):
        """
        # TODO
        :return:
        """
        action_str = " ".join(["action:%s" % i for i in self.action])
        callback_str = " ".join(["callback:%s" % i for i in self.callback])
        line = " ".join(
            ["symbol:" + self.symbol, "name:" + self.name, "func:" + self.function, "t0:" + self.t0.datetime_specified,
             "unit:" + self.unit, "trigger:" + self.trigger, "status:" + self.status,
             "valid:" + self.valid, action_str, callback_str])
        return line

    def calc_delta_t(self, t0, t):
        """
        # TODO
        :param t0:
        :param t:
        :return:
        """
        dt = t - t0
        if self.unit == "s":
            dt /= 1
        elif self.unit == "1m":
            dt /= 60
        elif self.unit == "3m":
            dt /= 180
        elif self.unit == "5m":
            dt /= 300
        elif self.unit == "10m":
            dt /= 600
        elif self.unit == "15m":
            dt /= 900
        elif self.unit == "30m":
            dt /= 1800
        elif (self.unit == "60m") | (self.unit == "h"):
            dt /= 3600
        elif self.unit == "d":
            dt /= 14400
        elif self.unit == "m":
            dt /= 288000
        return dt

    # noinspection PyUnusedLocal
    def calc_value_of_func_now(self):
        """
        # TODO
        :return:
        """
        t0 = self.t0
        t = MktDateTime(self.cal.now('dt'), self.cal)
        dt = self.calc_delta_t(t0, t)
        # above var would be called when eval-ing func
        func = self.function.split("=")[1]
        res_var = self.function.split("=")[0].strip()

        res_val = eval(func)
        return {"var": res_var, "val": res_val, "timestamp": t}

    def calc_valid_until(self):
        """
        # TODO
        :return:
        """
        m = re.search('[0-9]+', self.valid)
        try:
            num = int(m.group())
        except AttributeError:
            num = 1
        m = re.search('[a-zA-Z]+', self.valid)
        try:
            unit = m.group()
        except AttributeError:
            unit = 'd'
        if unit == 'd':
            num *= 1
        elif unit == 'w':
            num *= 5
        elif unit == 'm':
            num *= 20
        valid_until_date = self.cal.calc_t(self.create_date, "+", num)
        self.valid_until = "%s&15:00:00" % valid_until_date

    def check_val(self, val_now):
        """
        # TODO
        :param val_now:
        :return:
        """
        # val_now should be in {"var":"",  "val":'', "timestamp": t} format
        t_now = self.cal.now('dt')
        if (self.status == "finished") | (self.status == 'pending'):
            return []
        if t_now >= self.valid_until:
            self.status = "finished"
            return []
        val_calc = self.calc_value_of_func_now()
        print("[%s:%s] calc/now: %s/%s" % (self.symbol, self.name, val_calc['val'], val_now['val']))
        m = re.search('[<>=]+', self.trigger)
        try:
            trigger_direction = m.group()
        except AttributeError:
            trigger_direction = "=="

        print("eval: ", "%s %s %s" % (val_calc['val'], trigger_direction, val_now['val']))
        result = eval("%s %s %s" % (val_calc['val'], trigger_direction, val_now['val']))

        if result:
            for a in self.action:
                if 'sendmsg' in a:
                    msg = "[ %s ] rule %s triggered, %s(calc) %s %s(now)" % (
                        self.symbol, self.name, val_calc['val'], self.trigger, val_now['val'])
                    Alarm('msg', msg).emit()
                elif 'trade' in a:
                    Alarm('order', a).emit()
            cb_list = []
            for c in self.callback:
                (cb_action, cb_obj) = c.split("_")
                if cb_obj == "self":
                    self.status = {"pend": "pending", "finish": "finished", "activate": "active"}[cb_action]
                else:
                    cb_list.append(c)
            return cb_list
        else:
            return []
