import os
import re

import sys

from tools.internal_func_entry import init_data_root, update_symbol_list


class OverviewHdl:
    def __init__(self):
        self.pwd = os.getcwd()
        self.dep_list = []
        self.file_to_check = []
        self.todo_list = []

    def search_down_sub_path(self, root):
        files = os.listdir(root)
        for f in files:
            if os.path.isdir(root + '/' + f):
                self.search_down_sub_path(root + '/' + f)
            elif len(f.split(".")) == 2:
                if f.split(".")[1] == "py":
                    self.file_to_check.append(root + '/' + f)

    def find_all_deps(self):
        self.search_down_sub_path(self.pwd)
        for f in self.file_to_check:
            self.find_dep_in_py_file(f)
        print(self.generate_pip_cmd())

    def find_dep_in_py_file(self, path):
        with open(path) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        for l in content:
            try:
                res = re.search(r"DEPENDENCY\(([-a-zA-Z0-0 ]+)\)", l).group(1).lstrip().rstrip().split(" ")
                for r in res:
                    if r not in self.dep_list:
                        self.dep_list.append(r)
            except AttributeError:
                continue

    def find_todo_in_py_file(self, path):
        with open(path) as f:
            content = f.readlines()
        content = [x.strip() for x in content]
        for l in content:
            try:
                res = re.search(r"#[ \t]*[tT][oO][dD][oO][:,.a-zA-Z0-9_\(\) ]*", l).group(0)
                if res not in self.todo_list:
                    self.todo_list.append(path +': ' +res)
            except AttributeError:
                continue

    def find_all_todos(self):
        self.search_down_sub_path(self.pwd)
        for f in self.file_to_check:
            self.find_todo_in_py_file(f)
        for i in self.todo_list:
            print(i)

    def generate_pip_cmd(self):
        return "sudo pip3 install " + " ".join(self.dep_list)

    def init_path(self):
        init_data_root()

    def update(self):
        update_symbol_list()


if __name__ == '__main__':

    a = OverviewHdl()
    if '-d' in sys.argv:
        a.find_all_deps()
    if '-t' in sys.argv:
        a.find_all_todos()
    if '-i' in sys.argv:
        a.init_path()
    if '-u' in sys.argv:
        a.update()
