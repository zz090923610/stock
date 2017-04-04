import pickle
import random
import string
import threading
import urllib.error
import urllib.request
import re

import requests
import rsa
import http.cookiejar  # 从前的cookielib
import base64
import json
import urllib
import urllib.parse
import binascii
import websockets
import asyncio
# 用于模拟登陆新浪微博
import time

from stock.common.common_func import BASIC_INFO
from stock.common.communction import simple_publish
cookie_path='/tmp/cookie1'

class launcher:
    def __init__(self, username, password):
        self.cookie_container = http.cookiejar.CookieJar()
        self.password = password
        self.username = username

    def get_prelogin_args(self):

        """
        该函数用于模拟预登录过程,并获取服务器返回的 nonce , servertime , pub_key 等信息
        """
        json_pattern = re.compile('\((.*)\)')
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&' \
              + self.get_encrypted_name() + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)'
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            raw_data = response.read().decode('utf-8')
            json_data = json_pattern.search(raw_data).group(1)
            data = json.loads(json_data)
            return data
        except urllib.error as e:
            print("%d" % e.code)
            return None

    def get_encrypted_pw(self, data):
        rsa_e = 65537  # 0x10001
        pw_string = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' + str(self.password)
        key = rsa.PublicKey(int(data['pubkey'], 16), rsa_e)
        pw_encypted = rsa.encrypt(pw_string.encode('utf-8'), key)
        self.password = ''  # 清空password
        passwd = binascii.b2a_hex(pw_encypted)
        print(passwd)
        return passwd

    def get_encrypted_name(self):
        username_urllike = urllib.request.quote(self.username)
        username_encrypted = base64.b64encode(bytes(username_urllike, encoding='utf-8'))
        return username_encrypted.decode('utf-8')

    def enableCookies(self):
        # 建立一个cookies 容器
        # 将一个cookies容器和一个HTTP的cookie的处理器绑定
        cookie_support = urllib.request.HTTPCookieProcessor(self.cookie_container)
        # 创建一个opener,设置一个handler用于处理http的url打开
        opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
        # 安装opener，此后调用urlopen()时会使用安装过的opener对象
        urllib.request.install_opener(opener)

    def build_post_data(self, raw):
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "useticket": "1",
            "pagerefer": "http://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com"
                         "%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.14",
            "vsnf": "1",
            "su": self.get_encrypted_name(),
            "service": "miniblog",
            "servertime": raw['servertime'],
            "nonce": raw['nonce'],
            "pwencode": "rsa2",
            "rsakv": raw['rsakv'],
            "sp": self.get_encrypted_pw(raw),
            "sr": "1280*800",
            "encoding": "UTF-8",
            "prelt": "77",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        data = urllib.parse.urlencode(post_data).encode('utf-8')
        return data

    def login(self):
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        self.enableCookies()
        data = self.get_prelogin_args()
        post_data = self.build_post_data(data)
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36"
        }
        try:
            request = urllib.request.Request(url=url, data=post_data, headers=headers)
            response = urllib.request.urlopen(request)
            # for cookie in response.cookies:
            #    print(cookie)
            html = response.read().decode('GBK')
            # print(html)
        except urllib.error as e:
            print(e.code)

        p = re.compile('location\.replace\(\'(.*?)\'\)')
        p2 = re.compile(r'"userdomain":"(.*?)"')

        # noinspection PyBroadException
        try:
            # noinspection PyUnboundLocalVariable
            login_url = p.search(html).group(1)
            print(login_url)
            request = urllib.request.Request(login_url)
            response = urllib.request.urlopen(request)
            page = response.read().decode('utf-8')
            print(page)
            login_url = 'http://weibo.com/' + p2.search(page).group(1)
            request = urllib.request.Request(login_url)
            response = urllib.request.urlopen(request)
            # noinspection PyUnusedLocal
            final = response.read().decode('utf-8')

            print("Login success!")
        except:
            print('Login error!')
            return 0

    def save_cookie(self):
        with open(cookie_path, 'wb') as f:
            pickle.dump(self.cookie_container, f)


class WSHdl:
    def __init__(self, stock):
        self.stock = stock
        self.mkt_stock = BASIC_INFO.market_code_of_stock(stock)
        self.token = ''
        self.query_str_list = '2cn_%s,' \
                              '2cn_%s_orders,' \
                              '2cn_%s_0,' \
                              '2cn_%s_1,' \
                              '%s_i,' \
                              '%s' % (
                                  self.mkt_stock, self.mkt_stock, self.mkt_stock, self.mkt_stock, self.mkt_stock,
                                  self.mkt_stock)
        self.client_ip = ''
        self.s = requests.session()
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
        with open(cookie_path, 'rb') as f:
            self.s.cookies = pickle.load(f)

    def save_cookie(self):
        with open(cookie_path, 'wb') as f:
            pickle.dump(self.s.cookies, f)


    def get_ip(self):
        url = 'https://ff.sinajs.cn'
        param_list = {
            '_': self.timestamp_mills(),
            'list': 'sys_clientip'
        }
        a = self.s.get(url, params=param_list)
        return a.text.split('"')[1]

    @staticmethod
    def timestamp_mills():
        return int(time.time() * 1000)

    def get_auth_token(self, kick=False):
        url = 'https://current.sina.com.cn/auth/api/jsonp.php/' \
              '%s=/' \
              'AuthSign_Service.getSignCode' % self.token_var

        param_list = {
            'query': 'A_hq',
            'ip': self.ip,
            '_': random.random(),
            'list': self.query_str_list
        }
        if kick:
            param_list['kick'] = 1

        ret = self.s.get(url, params=param_list)
        print(ret.headers['Set-Cookie'])
        print(ret.text)
        self.auth_token = ret.text.split('"')[1]
        self.save_cookie()

    async def refresh_auth_token(self, loop):
        while self.running:
            await asyncio.sleep(180)
            self.get_auth_token()
            if self.ws is not None:
                print('[refresh token] %s' % self.auth_token)
                self.ws.send(self.auth_token)

    async def web_socket_async_hdl(self, loop):
        if self.first_time:
            self.get_auth_token(kick=True)
            self.first_time = False
            # await asyncio.sleep(3)
        url = 'wss://ff.sinajs.cn/wskt?' \
              'token=%s' \
              '&list=%s' \
              % (self.auth_token, self.query_str_list)
        print(url)
        async with websockets.connect(url) as websocket:
            self.ws = websocket
            data = await websocket.recv()
            simple_publish('sina-lv2-update_%s' % self.stock, "{}".format(data))
            print("{}".format(data))

    def _start_ws(self):
        self.event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event_loop)
        asyncio.ensure_future(self.web_socket_async_hdl(self.event_loop))
        asyncio.ensure_future(self.refresh_auth_token(self.event_loop))
        self.event_loop.run_forever()

    def start_ws(self):
        self.load_cookie()
        threading.Thread(target=self._start_ws).start()

    def stop_ws(self):
        self.running = False
        self.event_loop.stop()

        self.token_var = 'var%%20KKE_auth_%s' % self.id_generator()
        self.auth_token = ''
        self.event_loop = None
        self.first_time = True
        self.ws = None
