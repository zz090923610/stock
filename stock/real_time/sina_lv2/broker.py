import _thread
import json
import os
import random
import string
import sys
# 用于模拟登陆新浪微博
import time

import requests
# noinspection PyPackageRequirements
import websocket

from stock.common.common_func import BASIC_INFO
from stock.common.communction import simple_publish
from stock.common.time_util import TimeUtil
from stock.real_time.sina_lv2.sina_login import SinaLoginHdl


# mqtt control:
# res_topic: real_tick_update, real_tick_ctrl
# real_tick_ctrl: auth_failed, closed, started_$PID

# noinspection PyBroadException,PyUnusedLocal
class WebSocketAuthTokenHdl:
    def __init__(self, stock_list, username, password, cookie_path):
        self.stock_list = stock_list
        self.username = username
        self.password = password
        self.cookie_path = cookie_path
        self.mkt_stock_list = [BASIC_INFO.market_code_of_stock(s) for s in self.stock_list]
        self.query_str_list = ''
        for s in self.mkt_stock_list:
            self.query_str_list += '2cn_%s_0,' \
                                   '2cn_%s_1,' \
                                   % (s, s)
        self.query_str_list = self.query_str_list[:len(self.query_str_list) - 1]
        self.client_ip = ''
        self.s = requests.session()
        self.s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 ' \
                                       '(KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
        self.ws = None
        self.load_cookie()
        self.ip = self.get_ip()
        self.token_var = 'var%%20KKE_auth_%s' % self.id_generator()
        self.auth_token = ''
        self.event_loop = None
        self.first_time = True
        self.running = True

    @staticmethod
    def id_generator(size=9, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def load_cookie(self):
        self.s.cookies.clear()
        try:
            if os.path.isfile(self.cookie_path):
                with open(self.cookie_path) as f:
                    for line in f.read().splitlines():
                        sp = line.split(',')
                        if len(sp) == 4:
                            self.s.cookies.set(sp[0], sp[1], domain=sp[2], path=sp[3])
        except:
            pass

    def save_cookie(self):
        try:
            with open(self.cookie_path, 'w') as f:
                for c in self.s.cookies:
                    f.write('%s,%s,%s,%s\n' % (c.name, c.value, c.domain, c.path))
        except:
            print('save cookie error')

    def get_ip(self):
        url = 'https://ff.sinajs.cn'
        param_list = {
            '_': self.timestamp_mills(),
            'list': 'sys_clientip'
        }
        a = self.s.get(url, params=param_list)
        return a.text.split('"')[1]

    def is_login(self):
        if os.path.isfile(self.cookie_path):
            return True
        else:
            return False

    def login(self):
        is_login = self.is_login()
        if is_login:
            self.load_cookie()
            print('sina quote already login')
            return
        a = SinaLoginHdl(self.username, self.password, self.cookie_path)
        a.login()
        self.load_cookie()

    @staticmethod
    def timestamp_mills():
        return int(time.time() * 1000)

    def get_auth_token(self, kick=False):
        self.token_var = 'var%%20KKE_auth_%s' % self.id_generator()
        url = 'https://current.sina.com.cn/auth/api/jsonp.php/' \
              '%s=/' \
              'AuthSign_Service.getSignCode' % self.token_var
        #  url = 'https://current.sina.com.cn/auth/api/jsonp.php/varxxxl/AuthSign_Service.getSignCode'
        param_list = {
            'query': 'A_hq',
            'ip': self.ip,
            '_': random.random(),
            'list': self.query_str_list
        }
        if kick:
            param_list['kick'] = 1

        ret = self.s.get(url, params=param_list)
        print(ret.text)
        self.auth_token = ret.text.split('"')[1]
        return 'wss://ff.sinajs.cn/wskt?token=%s&list=%s' % (self.auth_token, self.query_str_list)

    def stop(self):
        self.running = False
        self.token_var = 'var%%20KKE_auth_%s' % self.id_generator()
        self.auth_token = ''


type_dict = {'0': 'S', '1': 'M', '2': 'B'}


# noinspection PyUnusedLocal
class WebSHdl:
    def __init__(self, stock_list, username, password, cookie_path, url=''):
        self.url = url
        self.auth_hdl = WebSocketAuthTokenHdl(stock_list, username, password, cookie_path)

    def on_message(self, ws, message):
        if message == 'sys_auth=FAILED':
            simple_publish('real_tick_ctrl', 'auth_failed')
            print(message)
            ws.close()
        self.parse_payload(message)

    @staticmethod
    def on_error(ws, error):
        print(error)

    @staticmethod
    def on_close(ws):
        simple_publish('real_tick_ctrl', 'closed')
        print("### closed ###")

    @staticmethod
    def parse_payload(payload):
        """
        sortid  |date        |price|num |money    |*       |*      |type|*
        10061883|15:00:00.000|3.680|4300|15824.000|10033886|9995765|2   |2012,
        type:
        0: S 
        1: M 
        2: B
        :publish: 'real_tick_update', json.dumps({'stock': stock, 'tick': final_list})
        """
        [title, raw_lines] = payload.split('=')
        lines = raw_lines.split(',')
        final_list = []
        for line in lines:
            cells = line.split('|')
            final_list.append(
                {'sort_id': cells[0], 'time': cells[1], 'price': float(cells[2]), 'hands': int(cells[3]) / 100,
                 'type': type_dict[cells[7]]})
        stock = title.split('_')[1][2:]
        simple_publish('real_tick_update', json.dumps({'stock': stock, 'tick': final_list}))

    def on_open(self, ws):
        def refresh_token(*args):
            print('refresh thread run')
            while True:
                time.sleep(170)
                self.auth_hdl.get_auth_token()
                print('Refresh Token', TimeUtil().get_time_of_a_day(), self.auth_hdl.auth_token)
                ws.send('*%s' % self.auth_hdl.auth_token)

        def heartbeat(*args):
            print('heartbeat thread run')
            while True:
                time.sleep(60)
                print('[Heart Beat]', TimeUtil().get_time_of_a_day())
                ws.send('')

        _thread.start_new_thread(refresh_token, ())
        _thread.start_new_thread(heartbeat, ())

    def main(self):
        if self.url == '':
            self.auth_hdl.login()
            self.url = self.auth_hdl.get_auth_token(kick=True)
        websocket.enableTrace(True)
        ws = websocket.WebSocketApp(self.url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        ws.run_forever()


if __name__ == '__main__':
    s_list = []
    if len(sys.argv) > 1:
        s_list = [i for i in sys.argv[1:]]
    simple_publish('real_tick_ctrl', 'started_%d' % os.getpid())
    b = WebSHdl(s_list, '610153443@qq.com',
                'f9c6c2827d3e5647',
                '/tmp/cookie')
    b.main()
