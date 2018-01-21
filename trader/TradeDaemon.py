#!/usr/bin/env python
# -*- coding:utf-8 -*-
import threading
import time

from tools.daemon_class import DaemonClass
from trader.account_info import AUTH
from trader.api_driver import TradeAPI


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class TradeDaemon(DaemonClass):
    def __init__(self, topic_sub='trade_req', topic_pub='trade_res/str', auth=None):
        super().__init__(topic_sub=topic_sub, topic_pub=topic_pub, auth=auth)
        self.trade_api = TradeAPI(headless=True, auth=AUTH)
        self.captcha_db = {}
        self.heart_thread = StoppableThread(target=self.heart_beat, daemon=True)

    def heart_beat(self):
        self.trade_api.respond('TradeDaemon/heartbeat started')
        while not self.cancel_daemon:
            time.sleep(120)
            self.trade_api.send_heartbeat()
            if self.trade_api.status != 'active':
                return

    def mqtt_on_message(self, mqttc, obj, msg):
        payload = msg.payload.decode('utf8')
        if payload == 'prelogin':
            try:
                self.heart_thread.stop()
                self.heart_thread.join()
                self.heart_thread = StoppableThread(target=self.heart_beat, daemon=True)
            except Exception as e:
                pass
            self.trade_api.pre_login()
        elif payload == 'cash':
            self.trade_api.get_available_cash()
        elif payload == 'status':
            self.trade_api.respond('TradeDaemon/status_%s' % self.trade_api.status)
        elif payload.split("_")[0] == "login":
            self.trade_api.login_with_verify_code(payload.split("_")[1])
            if self.trade_api.status == 'active':
                self.heart_thread.start()
        elif payload.split("_")[0] == "buy":
            (b, symbol, price, quant) = payload.split("_")
            threading.Thread(target=self.trade_api.buy, args=(symbol, price, quant)).start()
        elif payload.split("_")[0] == "sell":
            (s, symbol, price, quant) = payload.split("_")
            threading.Thread(target=self.trade_api.sell, args=(symbol, price, quant)).start()


if __name__ == '__main__':
    a = TradeDaemon(auth=AUTH)
    a.daemon_main()
