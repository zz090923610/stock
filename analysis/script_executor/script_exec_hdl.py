import math
import os
import re
import sys

import pandas as pd
import multiprocessing as mp
from analysis.script_executor.TranslateHdl import TranslateHdl
from tools.data.file_hdl import load_text
from tools.data.path_hdl import path_expand, directory_ensure
from tools.io import logging


# noinspection PyMethodMayBeStatic
class ScriptHdl:
    """
    maintain a script content, header, col info.
    """
    def __init__(self, path):
        """
        :param path: script path, string
        """
        self.col_desc = {}
        self.content = self.load_script(path)
        self.header = self.parse_script_head()
        self.name = os.path.split(path)[-1]

    def parse_script_head(self):
        """
        generate script header dict, add variable translations to system.
        """
        script = self.content
        parallel_level = ''  # FOLDER/SINGLE
        input_dir_file = ''
        output_dir_file = ''
        output_cols = []
        t = TranslateHdl()
        t.load()
        for line in script:
            if line[0] == 'PLEV':
                parallel_level = line[1]
            elif line[0] == 'FIN':
                input_dir_file = path_expand(line[1])
            elif line[0] == 'PLFDOUT':
                directory_ensure(path_expand(line[1]))
                output_dir_file = path_expand(line[1])
            elif line[0] == 'OUTCOLS':
                output_cols += re.split(r',', line[1])
            elif line[0] == 'TRANSLATE':
                t.add_translation(' '.join(line[1:]))
            elif line[0] == 'COLDESC':
                cols = line[1].split(',')
                precision = line[2]
                for c in cols:
                    self.col_desc[c] = precision
        t.save()
        return {"parallel_level": parallel_level, "input_dir_file": input_dir_file,
                "output_dir_file": output_dir_file, "output_cols": output_cols}

    def load_script(self, path):
        """
        :param path: string
        :return:    list of tokens, which is list of list of strings.
        """
        script_path = self._validate_script_path(path)
        raw_script = load_text(script_path)
        script = []
        for line in raw_script:
            if len(line.lstrip().rstrip()) > 0:
                split_line = re.split(r'[ \t]+', line.split('#')[0].lstrip().rstrip())
                if (split_line[0] != '') & (split_line[0] != '#'):
                    script.append(split_line)
        # for line in script:
        #    print(line)
        return script

    def _validate_script_path(self, script_path):
        """
        properly check whether script exists, and search for program's script space, return a valid path
        :param script_path: string
        :return:            path
        """
        if os.path.isfile(script_path):
            return script_path

        elif os.path.split(script_path)[-1].split(".")[0] + ".txt" in os.listdir(os.path.join(os.getcwd(), "scripts")):
            return os.path.join(os.getcwd(), "scripts", script_path.split("/")[-1].split(".")[0] + ".txt")
        else:
            logging("ScriptHdl", "[ ERROR ] invalid script path %s" % script_path)
            return "/tmp"


# noinspection PyMethodMayBeStatic
class WorkSheetHdl:
    """
    maintain a pd.DataFrame.
    """
    def __init__(self, input_data, out_path, output_cols, col_desc):
        self.name = 'data'
        self.out_path = out_path
        self.out_cols = output_cols
        self.data = self.load_data_as_pd(input_data)
        self.col_desc = col_desc if self.data is not None else None

    def load_data_as_pd(self, input_data):
        """
        :param input_data: can be a DataFrame or string represents a path
        :return:
        """
        if type(input_data) == pd.DataFrame:
            data = input_data
        elif type(input_data) == str:
            try:
                data = pd.read_csv(path_expand(input_data))
            except FileNotFoundError:
                logging("WorkSheetHdl", "[ ERROR ] csv load failed %s" % path_expand(input_data))
                data = None
        else:
            data = None
        return data

    def save_data(self, index=False):
        """
        :param index:  boolean, whether to save DataFrame index.
        :return:        if self.out_path is "STD", will return DataFrame instead of save to file.
        """
        # round data_frame
        if (self.col_desc is not None) & (type(self.col_desc) == dict):
            col_list = self.data.columns.tolist() if self.data is not None else None
            round_dict = {}
            for k in self.col_desc.keys():
                if k in col_list:
                    round_dict[k] = int(self.col_desc[k].split(".")[-1])
            self.data = self.data.round(round_dict)
        if self.out_path != 'STD':
            self.data[self.out_cols].to_csv(self.out_path, index=index)
        else:
            return self.data[self.out_cols]


class ScriptExecHdl:
    """
    Hdl to execuate script
    """
    def __init__(self, script_path):
        """
        :param script_path: string
        """
        self.script_hdl = ScriptHdl(script_path)

    def exec_script(self):
        """
        execuate script, whether do it parallel or not is specified in header.
        """
        if self.script_hdl.header['parallel_level'] == 'FOLDER':
            data_file_list = os.listdir(self.script_hdl.header['input_dir_file'])
            input_dir = self.script_hdl.header['input_dir_file'].rstrip('/')
            output_dir = self.script_hdl.header['output_dir_file'].rstrip('/')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            pool = mp.Pool()
            logging("ScriptExecHdl", '[ INFO ] parallel_start_%s_%d' % (self.script_hdl.name, len(data_file_list)),
                    method='all')
            for i in data_file_list:
                pool.apply_async(execute_script_on_single_input,
                                 args=(os.path.join(input_dir, i), os.path.join(output_dir, i), self.script_hdl))
                # execute_script_on_single_input(os.path.join(input_dir, i), os.path.join(output_dir, i), self.script_hdl)
            pool.close()
            pool.join()
            logging("ScriptExecHdl", "[ INFO ] parallel_finish_%s" % self.script_hdl.name, method='all')
        elif self.script_hdl.header['parallel_level'] == 'SINGLE':
            execute_script_on_single_input(self.script_hdl.header['input_dir_file'],
                                           self.script_hdl.header['output_dir_file'],
                                           self.script_hdl)


def execute_script_on_single_input(input_data, out_path, script_hdl):
    """
    execuate a script on single data sheet.
    :param input_data:  can be path, string, or DataFrame
    :param out_path:    string
    :param script_hdl:  instance of ScriptHdl
    """
    work_sheet = WorkSheetHdl(input_data, out_path, script_hdl.header['output_cols'], script_hdl.col_desc)
    try:
        for (idx, line) in enumerate(script_hdl.content):
            if line[0] == 'ADDC':
                opts_cols = []
                for op_source in line[2:]:
                    opts_cols.append(op_source)
                result_col_name = line[1]
                work_sheet.data[result_col_name] = 0
                for col in opts_cols:
                    if is_num(col):
                        work_sheet.data[result_col_name] += float(col)
                    else:
                        work_sheet.data[result_col_name] += work_sheet.data[col]
            elif line[0] == 'SUBC':
                opts_cols = []
                for op_source in line[2:]:
                    opts_cols.append(op_source)
                result_col_name = line[1]
                work_sheet.data[result_col_name] = work_sheet.data[opts_cols[0]]
                for col in opts_cols[1:]:

                    if is_num(col):
                        work_sheet.data[result_col_name] -= float(col)
                    else:
                        work_sheet.data[result_col_name] -= work_sheet.data[col]
            elif line[0] == 'MULC':
                opts_cols = []
                for op_source in line[2:]:
                    opts_cols.append(op_source)
                result_col_name = line[1]
                work_sheet.data[result_col_name] = work_sheet.data[opts_cols[0]]
                for col in opts_cols[1:]:
                    if is_num(col):
                        work_sheet.data[result_col_name] *= float(col)
                    else:
                        work_sheet.data[result_col_name] *= work_sheet.data[col]
            elif line[0] == 'DIVC':
                opts_cols = []
                for op_source in line[2:]:
                    opts_cols.append(op_source)
                result_col_name = line[1]
                work_sheet.data[result_col_name] = work_sheet.data[opts_cols[0]]
                for col in opts_cols[1:]:
                    if is_num(col):
                        work_sheet.data[result_col_name] /= float(col)
                    else:
                        work_sheet.data[result_col_name] /= work_sheet.data[col]
            elif line[0] == 'MODC':
                opts_cols = []
                for op_source in line[2:]:
                    opts_cols.append(op_source)
                result_col_name = line[1]
                work_sheet.data[result_col_name] = work_sheet.data[opts_cols[0]]
                for col in opts_cols[1:]:
                    if is_num(col):
                        work_sheet.data[result_col_name] %= col
                    else:
                        work_sheet.data[result_col_name] %= work_sheet.data[col]
            elif line[0] == 'SQRTC':
                result_col_name = line[1]
                work_sheet.data[result_col_name] = work_sheet.data[line[2]]
                work_sheet.data[result_col_name] = work_sheet.data[result_col_name].apply(math.sqrt)
            elif line[0] == 'EXPC':
                result_col_name = line[1]
                work_sheet.data[result_col_name] = work_sheet.data[line[2]]
                work_sheet.data[result_col_name] = work_sheet.data[result_col_name].apply(math.exp)
            elif line[0] == 'SHIFT':
                result_col_name = line[1]
                if len(line) == 4:
                    work_sheet.data[result_col_name] = work_sheet.data[line[2]].shift(int(line[3]))
            elif line[0] == 'JUDGE':
                result_col_name = line[1]
                conds = line[2]
                half_way = re.sub(r'([a-zA-Z][_a-zA-Z0-9]*)', r'work_sheet.data["\1"]', conds)
                full_way = 'work_sheet.data["%s"] = %s' % (result_col_name, half_way)
                exec(full_way)
            elif line[0] == 'APPLYH':
                result_col_name = line[1]
                func = line[2]
                cols = 'work_sheet.data[[' + \
                       ', '.join(list(map(lambda i: '"%s"' % i, line[3:]))) + \
                       ']]'
                func = parse_lambda(script_hdl.content[idx + 1]) if func.upper() == 'LAMBDA' else func
                full_cmd = 'work_sheet.data[\'%s\'] = %s.apply(%s,axis=1)' % (result_col_name, cols, func)
                exec(full_cmd)
        work_sheet.save_data()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging('ScriptExecHdl',
                '[ ERROR ] %s_on_%s_%r, (%r, %r, %d)' % (script_hdl.name, os.path.split(out_path)[-1], e,
                                                         exc_type, fname, exc_tb.tb_lineno), method='all')
        return
    logging('ScriptExecHdl', '[ INFO ] %s_on_%s_applied' % (script_hdl.name, os.path.split(out_path)[-1]))


def parse_lambda(line):
    """
    generate a pandas lambda function string like:
        lambda x: x**2
    :param line:    tokens, [] of string
    :return:        lambda function, string
    """
    line = ['lambda'] + line[1:]
    return ' '.join(line)


# CMDEXPORT ( SCRIPT {script_path}) exec_script
def exec_script(script_path):
    """
    Export this function to Control Framework, a control command like:
        SCRIPT ma
    can be added to .ctrl batch file to save some work.
    Execuate a script. ".txt" extension name should not be specified.
    :param script_path: path to script without ".txt"
    """
    s_hdl = ScriptExecHdl(script_path)
    s_hdl.exec_script()


# noinspection PyBroadException
def is_num(target):
    """
    check whether a string can be convert to a number.
    :param target:  string
    :return:        boolean
    """
    try:
        float(target)
        return True
    except Exception:
        return False
