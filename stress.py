from gevent import monkey
monkey.patch_all()

import re
import os
import sys
import time
import gevent
import platform
import threading

from contextlib import suppress
from difflib import get_close_matches

# from cli.runner import run_script
from core.api import auto_setup
from report.report import LogToHtml

from adb_commands import AdbCommands
from adb_connection import *
from log_manage import LogManage
from fight2.fight2 import run_test
from config import Config
from testinfo import TestInfo
from finish import Finish






class AutoTest:
    """
    游戏自动化测试的行为流程
    行为流程在sernial_begin内添加
    """

    adb = AdbCommands()

    def __init__(self, game, package, apk, number):
        self.game = game
        self.filepath = os.getcwd()
        self.gamepath = os.path.join(self.filepath, game)
        self.package = package
        self.apk = os.path.join(self.gamepath, apk)
        self.number = number

    def thread_begin(self, devices):
        spl = 3
        length = int(len(devices) / spl)
        for i in range(spl):
            _devices = devices[(length * i): (length * (i + 1))]
            thread = threading.Thread(target=self.gevent_begin, args=(_devices, ))
            thread.setDaemon(False)
            thread.start()

    def gevent_begin(self, devices):
        """使用gevent运行脚本"""
        # 遍历所有设备并安装包
        sys.stdout.write("How many devices have the gevent got? %s\n" % len(devices))
        gevent.joinall([
            gevent.spawn(self.serial_begin, serialno) 
            for serialno in devices
        ])

    def serial_begin(self, serialno):
        """开始测试"""
        log = self.generate_log(serialno)
        TestInfo.initialize_result(serialno)
        # 每次开始时先返回下桌面
        # self.adb.home(serialno)
        self.restart_game(serialno)
        gevent.sleep(45)
        try:
            self.run_airtest(log, serialno)
        except:
            import traceback
            traceback.print_exc()
        state = True if self.package in self.adb.activity(serialno) else False
        TestInfo.set_state(serialno, state)

    def generate_log(self, serialno):
        """创建每台设备的log"""
        log = LogManage(self.number)
        log.set_private_log(os.path.join(self.filepath, "log"), serialno)
        log.delete_private_log()
        log.write_private_log(self.game)
        log.write_private_log(self.package)
        log.write_private_log(self.apk)
        return log

    def restart_game(self, serialno):
        """某些情况下会初始化失败, 因此直接关闭再启动"""
        gevent.sleep(10)
        self.adb.end(serialno, self.package)
        gevent.sleep(3)
        self.adb.start(serialno, self.package)

    def delete_files(self, path):
        for file in os.listdir(path):
            if os.path.isfile(file):
                os.remove(os.path.join(path, file))

    def run_airtest(self, log, serialno):
        log_path = os.path.join(self.filepath, "log", serialno.replace(".", "").replace(":", ""))
        logdir = os.path.join(log_path, "screenshots")
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        [self.delete_files(path) for path in [log_path, logdir]]
        # airtest的 autot_setup 设置好后, 可直接调用写好的脚本方法执行脚本
        auto_setup(basedir=self.gamepath, devices=["Android:///%s" % serialno], logdir=logdir)
        run_test(log, serialno, self.package)

    def generate_report_html(self, serialno):
        log_path = os.path.join(self.filepath, "log", serialno.replace(".", "").replace(":", ""))
        logdir = os.path.join(log_path, "screenshots")
        outputfilepath = os.path.join(self.filepath, "log")
        outputfile = os.path.join(outputfilepath, "%s_REPORT.html" % serialno.replace(".", "").replace(":", ""))
        script_name = os.path.join(self.game, self.game + ".py")
        # airtest实际生成报告的函数
        report = LogToHtml(serialno, self.filepath, logdir, export_dir=None, \
                                script_name=script_name, lang="zh", plugins=None)
        report.report(serialno, Config.HTML_TPL, output_file=outputfile, record_list=[])






def run(user, ip, ports):
    """执行自动化测试"""
    # 确认是否传入了正确的user
    if user:
        from database import DataBaseManage
    else:
        raise ValueError("Can't start test without user.")
    ip = Config.IPS[int(ip)]
    db = DataBaseManage()
   # 先更新各每个测试人员其在autotest_stress_state表中的状态, 该状态用于更新操作是处于正在进行还是已完成
    state_table = "autotest_stress_state"
    out = db.select(state_table, "TESTER='%s' and IP='%s'" % (user, ip))
    if out:
        db.update(state_table, "STATE='underway'", "TESTER='%s' and IP='%s'" % (user, ip))
    elif out is False:
        raise ConnectionError("Can't connect to MySql server.")
    else:
        db.insert(state_table, "TESTER='%s', IP='%s', RESULT='underway" % (user, ip))
    # 检查数据库的内容是否正确
    run_table = "autotest_stress"
    out = db.select(run_table, keywords="TESTER=%s" % user)
    if out:
        TestInfo.initialize_testinfo(out)
    else:
        raise ValueError("Get unexpected values from table `autotest_stress`.")
    game = db.select(run_table, want="game", keywords="TESTER=%s" % user)
    if out:
        game = game[0][0]
    else:
        raise ValueError("Can't get game from table `%s`." % run_table)
    # 检查是否有对应的文件夹
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    for path in os.listdir(filepath):
        if path == game:
            break
    else:
        raise ValueError("Can't start test with a wrong game.")

    package = TestInfo.TESTINFO["package"]

    devices = list_devices(ip, int(ports))
    start = time.time()
    auto = AutoTest(game, package, number)
    auto.gevent_begin(devices)

    for serialno in devices:
        time.sleep(10)
        auto.generate_report_html(serialno)
    # 总时长统计
    end = time.time()
    cost = int((end - start) / 60)
    # finish暂未实现
    # f = Finish(devices, package, number)
    # f.record(cost)
    # 将状态更新为已完成
    db.update(state_table, "STATE='finished'", "TESTER='%s' and IP='%s'" % (user, ip))


if __name__ == '__main__':
    from exec_command import execute_from_command_line
    try:
        execute_from_command_line(sys.argv)
    except:
        sys.stderr.write("Can't start stress test.")
        import traceback
        traceback.print_exc()