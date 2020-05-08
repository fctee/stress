from gevent import monkey
monkey.patch_all()

import re
import os
import sys
import gevent

from difflib import get_close_matches

from adb_commands import AdbCommands
from adb_connection import *
from database import DataBaseManage
from config import Config



try:
    import xml.etree.cElementTree as xmltree
except ImportError:
    import xml.etree.ElementTree as xmltree



def parse_xml(xml):
    # 解析xml
    tree = xmltree.parse(xml)
    elements = tree.getroot()
    # 遍历xml查找所需要的 bounds 内容
    bounds = dict()
    for nodes in elements.findall("node"):
        for node in nodes:
            # 某些手机的ui.xml是令人恶心的3层结构
            for child_node in node:
                if not child_node.get("text"):
                    continue
                bounds.setdefault(child_node.get("text"), child_node.get("bounds"))
            # 空的text直接跳过
            if not node.get("text"):
                continue
            bounds.setdefault(node.get("text"), node.get("bounds"))
    return bounds


class PopupManage(AdbCommands):

    """
    app首次打开时会有2级授权弹窗需要处理
    """

    def __init__(self, serialno, word):
        self.serialno = serialno
        self.word = word
        self.filepath = os.getcwd()
        # 因为是一个行为流程, 所以直接在此处写上self.check_popup()
        self.check_popup()

    def check_popup(self):
        """检查是否存在2级弹窗"""
        while True:
            gevent.sleep(5)
            # 在获取到ui文件中进行判定
            # 如果未查找到权限相关的字眼
            # 便认定为不需要点击, break
            out = self.touch_popup()
            if not out:
                break

    def touch_popup(self):
        """adb 点击系统弹窗"""
        bounds = self.get_elements()
        if not bounds:
            return
        # 取出与允许最相似的key, 以防有些手机不是用始终允许
        key = get_close_matches(self.word, bounds.keys())
        if not key:
            return
        # 提取bounds对应value中的数字, 并以此为坐标范围
        left_x, left_y, right_x, right_y = tuple(re.findall(r"\d+", bounds[key[0]]))
        # 计算出点击坐标
        coord = ((int(left_x) + int(right_x)) / 2, (int(left_y) + int(right_y)) / 2)
        self.touch(self.serialno, coord)
        return coord

    def get_elements(self):
        """adb 获取当前app的元素经xml文件"""
        # 以serial number定义文件名
        xml = "%s_ui.xml" % self.serialno.replace(".", "").replace(":", "")
        # 所有手机均会有sdcard文件夹, 因此文件直接存放在sdcard下
        sdcard_filepath = os.path.join("/sdcard/", xml)
        self.uiautomator(self.serialno, sdcard_filepath)
        # 从手机拉取后放置在当前xmlfiles文件夹下
        target_filepath = os.path.join(self.filepath, "xmlfiles")
        # 进行文件夹检测, 不存在就创建
        if not os.path.exists(target_filepath):
            os.mkdir(target_filepath)
        self.pull(self.serialno, sdcard_filepath, target_filepath)
        return self.read_elements(target_filepath)

    def read_elements(self, path):
        """读取出xml中所有元素的text和坐标"""
        file = self.serialno.replace(".", "").replace(":", "")
        xml = os.path.join(path, "%s_ui.xml" % file)
        return parse_xml(xml) if os.path.exists(xml) else None




class ApkManage(AdbCommands):

    def __init__(self):
        super(ApkManage, self).__init__()


    def install(self, serialno, apk, package):
        """安装"""
        # self.install(serialno, apk)
        self.start(serialno, package)
        [PopupManage(serialno, word) for word in ["允许", "知道"]]
        self.end(serialno, package)

    def uninstall(self, serialno, apk, package):
        """精确卸载"""
        out = self.packagefrom3(serialno)
        if package not in out:
            return
        self.uninstall(serialno, package)

    def fuzzy_uninstall(self, serialno, apk, fuzzy_package):
        """模糊卸载"""
        out = self.packagefrom3(serialno)
        pattern = re.complie(r"\w+:")
        for line in out.readlines():
            if not line or not pattern.match(line):
                continue
            elif fuzzy_package in line:
                _, package = line.partition(":")
                self.uninstall(package)



def run(user, ip, ports):
    """
    应用管理的启动方法
    通过从数据库提取测试人员的操作, APK名或包名来判断具体执行哪个操作
    """
    if user:
        from database import DataBaseManage
    else:
        raise ValueError("Can't start apkmanage without user.")
    ip = Config.IPS[int(ip)]
    db = DataBaseManage()
    # 先更新各每个测试人员其在autotest_apkmanage_state表中的状态, 该状态用于更新操作是处于正在进行还是已完成
    state_table = "autotest_apkmanage_state"
    out = db.select(state_table, "TESTER='%s' and IP='%s'" % (user, ip))
    if out:
        db.update(state_table, "STATE='underway'", "TESTER='%s' and IP='%s'" % (user, ip))
    elif out is False:
        raise ConnectionError("Can't connect to MySql server.")
    else:
        db.insert(state_table, "TESTER='%s', IP='%s', RESULT='underway" % (user, ip))

    # 从数据库中提取数据
    run_table = "autotest_apkmanage"
    out = db.select(run_table, "TESTER='%s'" % user)
    if out:
        operation, apk, package = out[0]
    else:
        raise ValueError("Get unexpected values from table `%s`." % run_table)
    devices = list_devices(ip, int(ports))
    if hasattr(ApkManage, operation):
        gevent.joinall([
            gevent.spawn(getattr(ApkManage, operation), (serialno, apk, package))
            for serialno in devices
        ])
    # 将状态更新为已完成
    db.update(state_table, "STATE='finished'", "TESTER='%s' and IP='%s'" % (user, ip))




if __name__ == '__main__':
    from exec_command import execute_from_command_line
    try:
        execute_from_command_line(sys.argv)
    except:
        sys.stderr.write("Can't start apk management.")
        import traceback
        traceback.print_exc()