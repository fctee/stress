import os
import sys

from contextlib import suppress
from argparse import ArgumentParser
from importlib import import_module

from database import DataBaseManage


LIST_FILES = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__))))


class CommandError(Exception):
    pass


def load_command_module(module, method):
    """方法引用"""
    try:
        module = import_module(module)
    except ImportError:
        raise ImportError("Get a wrong module '%s' to import." % module)
    if hasattr(module, method):
        return getattr(module, method)
    else:
        raise CommandError("Get a wrong method '%s' to import." % method)


class CommandManagement:

    """
    指令解析, 用以解析docker启动时携带的cmd指令
    """

    def __init__(self, argv):
        self.argv = argv
        self.prog_name = os.path.basename(argv[0])
        # 先检查python3后面接的文件(如stress.py)是否存在
        if self.prog_name not in LIST_FILES:
            raise CommandError("Can't get the executable file.")
        # 文件存在就把.py给去掉以方便import
        if self.prog_name.endswith(".py"):
            self.prog_name = self.prog_name[:-3]

    def execute(self):
        """
        解析argv并调用对应的module去执行
        """
        # 提取method
        try:
            subcommand = self.argv[1]
        except IndexError:
            raise
        # 提取method所需要用到的参数
        parser = ArgumentParser()
        options, args = parser.parse_known_args(self.argv[2:])
        # args一定要包括user, ip, ports
        if len(args) != 3:
            raise CommandError("Can't parse args from 'python3%s'" % " ".join(self.argv))
        # 如果method为run, 则正式调用对应的module, method去执行; 反之则raise
        if subcommand == "run":
            load_command_module(self.prog_name, subcommand)(*args)
        else:
            raise CommandError("Get a wrong method '%s' to import." % subcommand)


def execute_from_command_line(argv):
    management = CommandManagement(argv)
    management.execute()