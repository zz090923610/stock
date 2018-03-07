from tools.communication.mqtt import simple_publish


# DEP_APT( mosquitto mosquitto-clients )


def logging(source, msg, method='mqtt'):
    if method == 'mqtt':
        simple_publish('logging', '[ %s ] %s' % (source, msg))
    elif method == "stdout":
        print('[ %s ] %s' % (source, msg))


def out(source, msg, method='mqtt'):
    if method == 'mqtt':
        simple_publish(source, msg)

