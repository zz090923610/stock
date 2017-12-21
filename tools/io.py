from tools.communication.mqtt import simple_publish

method = 'mqtt'


def logging(source, msg):
    if method == 'mqtt':
        simple_publish('logging', '[ %s ] %s' % (source, msg))


def out(source, msg):
    if method == 'mqtt':
        simple_publish(source, msg)
