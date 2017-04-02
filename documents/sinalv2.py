from stock.real_time.sina_lv2.broker import *

a=launcher('610153443@qq.com','f9c6c2827d3e5647')
a.login()

b=WSHdl('','', a.cookie_container)
c=b.update_auto_token()

