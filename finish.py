#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-16 20:20:00
# @LastEditor: luzhiqi
# @LastEditTime: 2020-02-16 20:20:00

import os

from copy import deepcopy

from database import DataBaseManage
from adb_commands import AdbCommands
from testinfo import TestInfo



GAMES = {
    "所有游戏": "",
    "战玲珑2": "fight2",
}


class Finish:

    adb = AdbCommands()

    def __init__(self, user, game, devices, package):
        self.user = user
        self.game = game
        self.devices = devices
        self.package = package

    def record(self):
        """所有测试结束后将数据写入数据库"""
        data = self.get_final_result()
        db = DataBaseManage()
        table = "autotest_stress_result"
        # 在写入新数据之前，需要将该测试人员关于此游戏的旧数据全部清除
        keys = "GAME='{}' AND EXECUTOR='{}'".format
        out = db.select(table, "id", keys(self.game, self.user))
        if out:
            # out的格式为[(1,), (2,)]
            [db.delete(table, id[0]) for id in out]

        for d in data:
            # 组合成mysql的部分语句
            start = "(null"
            for value in d.values():
                if isinstance(value, str):
                    start += ", '{}'"
                elif isinstance(value, int):
                    start += ", {}"
            content = "{});".format(start)
            values = content.format(d["SERIALNUMBER"], d["GAME"], d["INSTALL"],
                                        d["ACTIVITY"], d["LEVEL"], d["RESULT"],
                                        d["LOG"], d["REPORT"], d["EXECUTOR"])
            db.insert(table, values)

    def check_activity(self, serialno):
        """adb 检测游戏是否仍在运行"""
        return True if self.package in self.adb.activity(serialno) else False

    def get_final_result(self):
        """
        结果的汇总, 
        返回列表, 内容为:
        [
            {
                设备型号,
                游戏代号,
                安装成功与否,
                游戏是否仍处于运行状态,
                执行结果,
                玩家等级, 
                log文件名,
                html文件名,
                执行人员名,
            },
            ...
        ]
        """
        result = list()
        for serialno in self.devices:
            log = "{}_LOG".format(serialno.replace(".", "").replace(":", ""))
            report = "{}_REPORT".format(serialno.replace(".", "").replace(":", ""))
            for k, v in GAMES.items():
                if self.game == v:
                    game = k
                    break
                else:
                    game = None
            # 默认每部手机的都为执行失败, 安装失败, 无等级, 游戏已退出
            data = {
                "SERIALNUMBER": serialno,
                "GAME": game,
                "INSTALL": "失败", 
                "ACTIVITY": "已退出",
                "LEVEL": None,
                "RESULT": "失败",
                "LOG": log,
                "REPORT": report,
                "EXECUTOR": self.user,
            }
            
            _data = deepcopy(data)
            # 开始写入最终结果数据
            data["INSTALL"] = TestInfo.RESULT[self.user][self.game][serialno]["INSTALL"]
            data["LEVEL"] = TestInfo.RESULT[self.user][self.game][serialno]["LEVEL"]

            if self.check_activity(serialno) is True:
                data["ACTIVITY"] = "游戏中"

            pattern = TestInfo.INFO[self.user][self.game]["level"]
            if not pattern:
                check_list = ["INSTALL", "ACTIVITY"]
            else:
                check_list = ["INSTALL", "LEVEL", "ACTIVITY"]
            # 待定项中, 若有一项与初始值一致, 即表明执行失败
            for ident in check_list:
                if _data[ident] == data[ident]:
                        break
            else:
                if pattern:
                    # 仅当等级与预期等级一致时, 才判定为执行成功
                    if data["LEVEL"] == pattern:
                        data["RESULT"] = "成功"
                else:
                    data["RESULT"] = "成功"

            result.append(data)

        return result
