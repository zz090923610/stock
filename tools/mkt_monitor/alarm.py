# -*- coding: utf-8 -*-
import os


class Alarm:
    """
    # TODO
    """
    def __init__(self, msg_type, payload):
        """
        # TODO
        :param msg_type:
        :param payload:
        """
        self.type = msg_type  # msg, order
        self.payload = payload

    def emit(self):
        """
        # TODO
        :return:
        """
        print(self.type, self.payload)
        if self.type == "msg":
            cmd = "wccmd -m '%s' ZZSELF" % self.payload
            os.system(cmd)
            cmd = "wccmd -m '%s' ZZY" % self.payload
            os.system(cmd)
