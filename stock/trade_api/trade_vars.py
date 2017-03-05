# -*- coding:utf-8 -*-
from stock.common.variables import stock_data_root

P_TYPE = {'http': 'http://', 'https': 'https://', 'gtja': 'https://'}
DOMAINS = {
    'gtja': 'trade.gtja.com'
}
ACTION_PORTAL = {
    'gtja': '/webtrade/trade/webTradeAction.do'
}
CAPTCHA_DB = {
    'gtja': '%s/trade_api/Captcha_gtja' % stock_data_root
}

AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'}

CAPTCHA = {'gtja': 'https://trade.gtja.com/webtrade/commons/verifyCodeImage.jsp'}