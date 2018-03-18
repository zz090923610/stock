# -*- coding: utf-8 -*-
# DEP_APT( mosquitto mosquitto-clients )

from tools.communication.mqtt import simple_publish


def logging(source, msg, method='mqtt'):
    if method == 'mqtt':
        # TODO may be expensive since simple_publish create/destroy connection for every msg.
        # Implement logging class for operations generate tons of msgs.
        simple_publish('logging', '[ %s ] %s' % (source, msg))
    elif method == "stdout":
        print('[ %s ] %s' % (source, msg))
    elif method == 'all':
        simple_publish('logging', '[ %s ] %s' % (source, msg))
        print('[ %s ] %s' % (source, msg))
