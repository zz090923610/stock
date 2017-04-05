import asyncio
import os
import random
import string
import threading
# 用于模拟登陆新浪微博
import time

import requests
import websockets

from stock.common.common_func import BASIC_INFO
from stock.common.communction import simple_publish
from stock.real_time.sina_lv2.sina_login import SinaLoginHdl


# noinspection PyBroadException,PyUnusedLocal
class WSHdl:
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
        self.load_cookie()
        is_login = self.is_login()
        if is_login:
            print('sina quote already login')
            return
        a = SinaLoginHdl(self.username, self.password, self.cookie_path)
        a.login()
        self.load_cookie()

    @staticmethod
    def timestamp_mills():
        return int(time.time() * 1000)

    def get_auth_token(self, kick=False):
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

    async def refresh_auth_token(self, loop):
        cnt = 0
        while self.running:
            await asyncio.sleep(59)
            cnt += 1
            if cnt != 2:
                print('sent heartbeat')
                self.ws.send('')
            else:
                self.get_auth_token()
                if self.ws is not None:
                    print('[refresh token] %s' % self.auth_token)
                    self.ws.send(self.auth_token)
                cnt = 0

    async def web_socket_async_hdl(self, loop):
        if self.first_time:
            self.get_auth_token(kick=True)
            self.first_time = False
        url = 'wss://ff.sinajs.cn/wskt?' \
              'token=%s' \
              '&list=%s' \
              % (self.auth_token, self.query_str_list)
        print(url)
        self.ws = await websockets.connect(url)
        while self.running:
            if self.ws.state == 1:
               data = await self.ws.recv()
               simple_publish('sina-lv2-update_%s' % self.stock_list, "{}".format(data))
               print("{}".format(data))
            else:
                self.ws = await websockets.connect(url)
        #async with websockets.connect(url) as websocket:
        #    self.ws = websocket
        #    data = await websocket.recv()
        #    simple_publish('sina-lv2-update_%s' % self.stock_list, "{}".format(data))
        #    print("{}".format(data))

    def _start_ws(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        asyncio.ensure_future(self.web_socket_async_hdl(self.event_loop))
        asyncio.ensure_future(self.refresh_auth_token(self.event_loop))
        self.event_loop.run_forever()

    def start_ws(self):
        self.login()
        threading.Thread(target=self._start_ws).start()

    def stop(self):
        self.running = False
        next(self.ws.close())
        self.event_loop.stop()
        self.token_var = 'var%%20KKE_auth_%s' % self.id_generator()
        self.auth_token = ''
        self.event_loop = None
        self.first_time = True
        self.ws = None
