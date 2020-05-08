import os
import sys
from datetime import datetime



def time_covered_bracket():
    """返回带[]的时间,一般用在log的开头"""
    return datetime.now().strftime("[%y-%m-%d %X]")

PUBLICLOG = "public_log_{}.txt"
ERRORLOG = "error_log_{}.txt"


class LogManage:

    def __init__(self, number):
        self.public_log = os.path.join("log/", PUBLICLOG.format(number))
        self.error_log = os.path.join("log/", ERRORLOG.format(number))

    def set_private_log(self, game_path, serial_number):
        # 无线设备存在 . : 符号, 所以都尝试将这些符号删除
        self.serial_number = serial_number.replace(".", "").replace(":", "")
        self.log_path = os.path.join(game_path, self.serial_number)
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)
        self.private_log = os.path.join(self.log_path, "%s_LOG.txt" % self.serial_number)

    def delete_private_log(self):
        if os.path.exists(self.private_log):
            os.remove(self.private_log) 

    def delete_public_log(self):
        """首次执行时, 删除前一个log文件"""  
        if os.path.exists(self.public_log):
            os.remove(self.public_log)
        if os.path.exists(self.error_log):
            os.remove(self.error_log)

    def write_private_log(self, msg):
        """在log文件最后方写入msg"""
        msg = "{} {} {} ...\n".format(time_covered_bracket(), self.serial_number, msg)
        sys.stdout.write(msg)
        with open(self.private_log, "a+") as f:
            f.write(msg)

    def write_public_log(self, msg):
        """在public_log中写入msg"""
        with open(self.public_log, "a+") as f:
            f.write(msg)

    def write_error_log(self, msg):
        with open(self.error_log, "a+") as f:
            f.write(msg)

    def read_private_log(self):
        with open(self.private_log, "r+") as f:
            return f.readlines()
