import os
import sys
import unittest
from .parser import *
import pandas as pd


class TestParserDataInput(unittest.TestCase):
    def test_load_data(self):
        assert type(load_data('./stock/ScriptExecutor/test_data.csv')) == pd.core.frame.DataFrame
        assert load_data('./test.csv') is None
        a=load_data('./stock/ScriptExecutor/test_data.csv')
        assert type(load_data(a)) == pd.core.frame.DataFrame

    def test_load_script(self):
        assert load_script('./stock/ScriptExecutor/test_script.txt') == \
               [['ADD', 'COL3', 'COL1', 'COL2/VAR/IMM'], ['SUB', 'COL3', 'COL1', 'COL2/VAR/IMM'],
                ['MUL', 'COL3', 'COL1', 'COL2/VAR/IMM'], ['DIV', 'COL3', 'COL1', 'COL2/VAR/IMM'],
                ['MOD', 'COL3', 'COL1', 'COL2/VAR/IMM'], ['EXP', 'COL2', 'COL1', 'VAR/IMM'], ['SQRT', 'COL2', 'COL1'],
                ['SHIFT', 'COL2', 'COL1', 'OFFSET', 'RANG/SING'], ['SORT', 'TABLE', 'COL1', 'ASC/DEC'],
                ['FLT', 'TABLE', 'COND']]


if __name__ == '__main__':
    unittest.main()