# -*- coding: utf-8 -*-
import os


class Alarm:
    def __init__(self, msg_type, payload):
        self.type = msg_type  # msg, order
        self.payload = payload

    def emit(self):
        print(self.type, self.payload)
        if self.type == "msg":
            cmd = "wccmd -m '%s' ZZSELF" % self.payload
            os.system(cmd)
            cmd = "wccmd -m '%s' 张志远" % self.payload
            os.system(cmd)
