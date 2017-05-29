import os
import sys
import unittest
from .parser import *
import pandas as pd


class TestParserDataInput(unittest.TestCase):
    def test_load_data(self):
        assert type(load_data('./stock/ScriptExecutor/test.csv')) == pd.core.frame.DataFrame
        assert load_data('./test.csv') is None
        a=load_data('./stock/ScriptExecutor/test.csv')
        assert type(load_data(a)) == pd.core.frame.DataFrame


if __name__ == '__main__':
    unittest.main()