# -*- encoding=utf8 -*-
__author__ = "鸽男"

import os
import sys
import time
import gevent
import platform

from functools import wraps
from contextlib import suppress

from adb_commands import AdbCommands
from config import Config
from testinfo import TestInfo
from core.api import *

# 行为及其对应的中文
OPERATIONS = {
    "click": "查找并点击",
    "write": "在文本档内写入内容",
    "swipe": "滑动屏幕",
    "click_other": "查找前一张图并点击后一张图",
}


def write_cost_time(func):
    def wrapper(*args):
        start_time = time.time()
        log = func(*args)
        cost_time = "%.2f" % (time.time() - start_time)
        msg = "主线自动化结束, 角色进入待机状态, 此次测试共用时 %s s" % cost_time
        log.write_private_log(msg)
    return wrapper

def opera_when_failed(serialno, image, resolution):
    if TestInfo.RESULT["level"][serialno] >= 20:
        return
    # x, y = resolution
    # true_x = x - 20
    # true_y = y - 2
    # touch(serialno, (true_x, true_y))
    coord = exists(serialno, Template(image, resolution=resolution))
    if coord:
        touch(serialno, coord)


def opera(func):
    """打印每个行为的具体内容"""
    # @wraps
    def wrapper(self, *args, **kwargs):
        # 记录开始时间
        start_time = time.time()
        # 方法会返回对应的传参, 用于log记录传参是否有误
        self.set_state()
        ret = func(self, *args, **kwargs)
        count = 0
        operation = Config.OPERATIONS[func.__name__]
        state = ret["state"]
        retries = ret["retries"]
        serialno = ret["serialno"]
        info = ret["info"]
        log = ret["log"]
        action = ret["action"]
        resolution = ret["resolution"]
        result = True
        # 有可能会出现操作失败的情况, 重新执行直到成功或retries次
        while not state:
            opera_when_failed(serialno, "继续任务.png", resolution)
            if retries == 0:
                break
            if count - retries == 0:
                # 行为key为0, 表示此项为必须执行的项, 出错了便可提前中断
                if action == 0:
                    msg = "{}  <{}>  重新执行{}次后仍无法成功, 此次测试提前中断".format
                    result = False
                else:
                    msg = "{}  <{}>  重新执行{}次后仍无法成功, 直接进入后续步骤".format
                log.write_private_log(msg(operation, info, retries))
                snapshot(serialno, msg="操作失败")
                break
            # msg = "{}  <{}>  执行失败, 正在重新执行".format(operation, info)
            # log.write_private_log(msg)
            ret = func(self, *args, **kwargs)
            state = ret["state"]
            count += 1
        msg = "{}  <{}>, 用时 {} s".format(operation, info, "%.2f" % (time.time() - start_time))
        log.write_private_log(msg)
        return result
    return wrapper



 
class Operateions:

    adb = AdbCommands()

    def __init__(self, log, serialno, package, resolution):
        self.log = log
        self.serialno = serialno
        self.package = package
        self.resolution = resolution
        
    def set_state(self):
        self.result = {
            "info": None,
            "retries": 0,
            "log": self.log,
            "action": 1,
            "state": False,
            "serialno": self.serialno,
            "resolution": self.resolution
        }

    def find(self, image):
        """查找图片,最多检测5次"""
        for i in range(3):
            coord = exists(self.serialno, Template(image, resolution=self.resolution))
            if coord:
                self.log.write_private_log("查找图片  <%s>  成功" % image)
                return coord
        else:
            self.log.write_private_log("查找图片  <%s>  失败" % image)

    def wait(self, image):
        """等待出现图片"""
        self.log.write_private_log("开始等待图片  <%s> " % image)
        coord = wait(self.serialno, Template(image, resolution=self.resolution), timeout=240)
        if coord:
            self.log.write_private_log("等待图片  <%s>  成功" % image)
        else:
            self.log.write_private_log("等待图片  <%s>  失败" % image)
        return coord

    def check(self, source):
        """图片格式的检测"""
        # 检测图片是否以.png结尾, 不是则写入log
        if not source.endswith(".png"):
            msg = "图片  <%s>  非.png结尾, 请确认是否有误" % source
            self.log.write_private_log(msg)

    def wait_or_find(self, image, action):
        """根据传参来返回等待/查找的结果, 0等待1查找"""
        assert isinstance(action, int)
        return self.find(image) if action == 1 else self.wait(image)

    def touch(self, coord, times, image=None):
        """点击图片"""
        try:
            # 由于部分场景在点击后会退出该场景
            # 点击次数过多影响到下一个步骤
            # 因此点击仅可点仅1次
            # touch(self.serialno, Template(image, resolution=self.resolution))
            # 某些操作需要连点, 所以将times改为预设为1
            touch(self.serialno, coord, times=times)
            if image:
                self.log.write_private_log("点击图片  <%s %s>  成功" % (image, coord))
            else:
                self.log.write_private_log("点击坐标  <%s, %s>  成功" % coord)
            self.result["state"] = True
        except:
            import traceback
            traceback.print_exc()
            if image:
                self.log.write_private_log("点击图片  <%s>  失败" % image)
            else:
                self.log.write_private_log("点击坐标  <%s, %s>  失败" % coord)
    
    @opera
    def click(self, entry, action, retries, times=1):
        """查找图片后点击该图片"""
        self.result["info"] = entry
        self.result["retries"] = retries
        self.result["action"] = action
        # 根据传参来确定是否为等待还是简单查找
        if isinstance(entry, str):
            # 如果找到图片, 就尝试去点击图片
            self.check(entry)
            coord = self.wait_or_find(entry, action)
            if coord:
                self.touch(coord, times, entry)
        else:
            self.touch(entry, times)
        return self.result
    
    @opera
    def click_other(self, source, target, action, retries, times=1):
        """查找到A图片后点击B图片"""
        # 根据传参来确定是否为等待还是简单查找
        self.check(source)
        self.result["info"] = (source, target)
        self.result["retries"] = retries
        self.result["action"] = action
        # 如果找到图片, 就尝试去点击另一张图片
        source_coord = self.wait_or_find(source, action)
        if source_coord:
            if isinstance(target, str):
                self.check(target)
                target_coord = self.wait_or_find(target, action)
                self.touch(target_coord, times, target)
            else:
                target_coord = target
                gevent.sleep(1)
                self.touch(target_coord, times)
        return self.result

    def write(self, txt, retries=0):
        if not txt:
            txt = self.serialno.replace(".", "").replace(":", "")[-7:-4]
            txt += "a"
            txt += self.serialno.replace(".", "").replace(":", "")[-2:]
        self.result["info"] = txt
        self.result["retries"] = retries
        try:
            # 写入前延时下, 以确保输入框正常打开了
            gevent.sleep(2.5)
            self.adb.input(self.serialno, txt)
            gevent.sleep(0.5)
            self.adb.escape(self.serialno)
            gevent.sleep(2)
            self.log.write_private_log("写入内容  <%s>  成功" % txt)
            self.result["state"] = True
        except:
            self.log.write_private_log("写入内容  <%s>  失败" % txt)
        return self.result

    def sleep(self, s):
        gevent.sleep(s)

    def record(self, entry):
        if isinstance(entry, int):
            TestInfo.set_level(self.serialno, entry)
            self.log.write_private_log("玩家当前等级 %s 级" % entry)
        else:
            self.log.write_private_log(entry)
