import re
import time
import json
import platform

from adb_commands import AdbCommands
from config import Config
from database import DataBaseManage


__all__ = ("connect_devices", "list_devices")


adb = AdbCommands()
db = DataBaseManage()

def connect_devices(ip, ports):
    """云手机都需要先connect"""
    if platform.system() is "Windows":
        return
    adb.kill()
    adb.run()
    time.sleep(3)
    # 每次连接前需要先检查下地址是否处于连接中
    out = database.select("autotest_adbstatus", keywords="INUSE='true'")
    inuse = list()
    for args in out:
        _, addr, _ = args
        inuse.append(addr)
    count = 0
    for nsport in Config.PORTS:
        addr = ":".join([Config.IPS[ip], nsport])
        if addr not in inuse:
            adb.connect(addr)
        if count >= ports:
            break


def list_devices():
    """获取到devices列表"""
    pattern = re.compile(r"^[\w\d.:-]+\t[\w]+$")
    devices = list()
    for line in adb.devices().splitlines():
        if not line or not pattern.match(line):
            continue
        serialno, *args = line.partition("\t")
        devices.append(serialno)
    return devices