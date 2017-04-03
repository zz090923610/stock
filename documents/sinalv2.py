from stock.real_time.sina_lv2.broker import *

a=launcher('610153443@qq.com','f9c6c2827d3e5647')
a.login()
a.save_cookie()

from stock.real_time.sina_lv2.broker import *
b=WSHdl('','')
b.load_cookie()
b.get_auto_token()
b.start_ws()
b.auth_token='vxi_vTy_C7._v3LHiCmlA8IOntvHKA9fooO2VxmL'


a=launcher('610153443@qq.com','f9c6c2827d3e5647')
a.login()
a.save_cookie()