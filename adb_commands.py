# -*- encoding=utf8 -*-
__author__ = "鸽男"


import sys
import platform
import traceback
import subprocess

if platform.system() == "Linux":
    adb_path = "/opt/adb/platform-tools/adb"
else:
    adb_path = "adb"



def monitor(func):
    def wrapper(self, *args):
        # 这种简单的重连效果并不是很理想,
        # 目前暂时不处理断开重连, 
        # 单docker30台云手机adb已经可以稳定不断开
        # serialno = args[0]
        # if serialno not in self.devices():
        #     self.disconnect(serialno)
        #     self.connect(serialno)
        try:
            out = func(self, *args)
        except:
            traceback.print_exc()
            out = None
        return out
    return wrapper




class SubPopen:

    def __init__(self):
        pass

    def split_cmd(self, cmd):
        """
        为防止出现不以传入list形式的指令
        """
        return cmd.split(" ") if isinstance(cmd, str) else cmd

    def call_shell(self, cmd, device):
        """执行cmd"""
        # 传入device为Flase则表示未有多个device
        # 此时直接用cmd
        if not device:
            cmds = [adb_path] + self.split_cmd(cmd)
        else:
            cmds = [adb_path, "-s"] + self.split_cmd(cmd)
        # sys.stdout.write("%s\n" % cmds)
        proc = subprocess.Popen(
            cmds,
            stdout=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
        )
        return proc

    def run_cmd(self, cmd, device=True):
        """执行cmd并解析返回内容"""
        proc = self.call_shell(cmd, device)
        stdout, stderr = proc.communicate()
        if isinstance(stdout, bytes):
            stdout = stdout.decode(sys.getfilesystemencoding())
        proc.kill()
        return stdout



class AdbCommands(SubPopen):

    """
    所有adb指令均在此处增加
    """

    def __init__(self):
        super(AdbCommands, self).__init__()

    def run(self):
        return self.run_cmd(["start-server"], device=False)

    def kill(self):
        return self.run_cmd(["kill-server"], device=False)

    def devices(self):
        """adb 获取当前所有连接的设备"""
        return self.run_cmd(["devices"], device=False)

    def connect(self, serialno):
        """adb 连接设备"""
        return self.run_cmd(["connect", serialno], device=False)

    def disconnect(self, serialno):
        return self.run_cmd(["disconnect", serialno], device=False)

    def keyevent(self, serialno, event):
        return self.run_cmd([serialno, "shell", "input", "keyevent", event])

    @monitor
    def customize(self, serialno, entry):
        """adb 自定义指令"""
        if isinstance(entry, list):
            cmd = [serialno] + entry

        elif isinstance(entry, str):
            if not entry.startswith(" "):
                entry = " " + entry
            cmd = serialno + entry

        else:
            backmsg = "Unknow command %s" % entry
            sys.stdout.write(backmsg)
            return backmsg
        return self.run_cmd(cmd)
    
    @monitor
    def root(self, serialno):
        return self.run_cmd([serialno, "root"])

    @monitor
    def brand(self, serialno):
        return self.run_cmd([serialno, "shell", "getprop", "ro.product.brand"])

    @monitor
    def model(self, serialno):
        return self.run_cmd([serialno, "shell", "getprop", "ro.product.model"])

    @monitor
    def version(self, serialno):
        return self.run_cmd([serialno, "shell", "getprop", "ro.build.version.release"])

    @monitor
    def home(self, serialno):
        """adb 返回桌面"""
        return self.keyevent(serialno, "HOME")
    @monitor
    def enter(self, serialno):
        """adb 点击确定"""
        return self.keyevent(serialno, "ENTER")

    @monitor
    def escape(self, serialno):
        return self.keyevent(serialno, "ESCAPE")

    @monitor
    def input(self, serialno, text):
        return self.run_cmd([serialno, "shell", "input","text", "'%s'" % text])

    @monitor
    def packagefrom3(self, serialno):
        """adb 第3方app"""
        return self.run_cmd([serialno, "shell", "pm", "list", "package", "-3"])

    @monitor
    def install(self, serialno, apk):
        """adb 安装app"""
        return self.run_cmd([serialno, "install", apk])

    @monitor
    def uninstall(self, serialno, package):
        """adb 卸载app"""
        return self.run_cmd([serialno, "uninstall", package])

    @monitor
    def start(self, serialno, package):
        """adb monkey启动app"""
        cmd = [serialno, "shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"]
        return self.run_cmd(cmd)

    @monitor
    def end(self, serialno, package):
        """adb 退出app"""
        return self.run_cmd([serialno, "shell", "am", "force-stop", package])

    @monitor
    def touch(self, serialno, coord):
        """adb 根据坐标点击手机屏幕"""
        try:
            x, y = coord
        except:
            backmsg ="Wrong coordinate %s" % list(coord)
            sys.stdout.write(backmsg)
            return backmsg
        return self.run_cmd([serialno, "shell", "input", "tap", str(x), str(y)])

    @monitor
    def activity(self, serialno):
        """adb 获取当前处于活跃状态的app"""
        return self.run_cmd([serialno, "shell", "dumpsys", "activity"])

    @monitor
    def uiautomator(self, serialno, path):
        """adb 获取screen当前的元素文件"""
        return self.run_cmd([serialno, "shell", "uiautomator", "dump", "--compressed", path])

    @monitor
    def pull(self, serialno, source, target):
        """adb 将手机中的文件推到其所连接的机器上"""
        return self.run_cmd([serialno, "pull", source, target])

    @monitor
    def clear(self, serialno, package):
        """adb 清除app数据"""
        return self.run_cmd([serialno, "shell", "pm", "clear", package])

