from setuptools import setup, find_packages
import codecs
import os
import stock
setup(
    name='stock',
    version='',
    url='',
    license='',
    author='zhangzhao',
    author_email='zhao.zhang.glacier@gmail.com',
    classifiers=['Development Status :: 4 - Beta',
                 'Programming Language :: Python :: 3.6'],
    packages=['stock', 'stock.gui', 'stock.common', 'stock.data', 'stock.gui', 'stock.quantitative_analysis',
              'stock.trade_api',
              'stock.visualization'],
    description=''
)
