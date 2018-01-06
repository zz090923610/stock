from tools.communication.mqtt import simple_publish

method = 'mqtt'


def logging(source, msg):
    if method == 'mqtt':
        simple_publish('logging', '[ %s ] %s' % (source, msg))


def out(source, msg):
    if method == 'mqtt':
        simple_publish(source, msg)


def test_internet(url='http://www.baidu.com'):
    from urllib.error import URLError
    from urllib.request import urlopen
    try:
        urlopen(url, timeout=1)
        return True
    except URLError as err:
        return False
