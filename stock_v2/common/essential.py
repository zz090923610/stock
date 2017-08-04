from urllib.error import URLError
from urllib.request import urlopen


def internet_on(url='http://www.baidu.com'):
    try:
        urlopen(url, timeout=1)
        return True
    except URLError as err:
        return False


