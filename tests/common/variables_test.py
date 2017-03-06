from nose.tools import *
from stock.common.variables import *


def test_common_vars():
    dft_root = '/tmp/stock_data'
    a = CommonVars(dft_root)
    assert_equal(a.stock_data_root, dft_root)
