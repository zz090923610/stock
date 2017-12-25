
class TranslateHdl:
    def __init__(self):
        self.dict = {}

    def add_translation(self, line):
        # parse line, two conditions
            if ':' in line:
                trans_list = line.split(" ")[1:] #FIXME future implementation
                for i in trans_list:
                    (k, v) = i.split(":")
                    if k not in self.dict.keys():
                        self.dict[k] = v
            else:
                trans_list = line.split(" ")
                if len(trans_list) == 3:
                    if trans_list[1] not in self.dict.keys():
                        self.dict[trans_list[1]] = trans_list[2]

    def clear(self):
        self.dict.clear()

    def load(self, path):
        pass
