#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# @Author: luzhiqi
# @Email: luzhiqi@ijunhai.com
# @Date: 2020-02-09 22:43:54
# @LastEditor: luzhiqi
# @LastEditTime: 2020-02-09 22:43:54

import json

class TestInfo:
    """
    于此处测试人员执行脚本时的数据
    INFO:
        测试人员开始执行脚本时传入的数据
        如 人员, 游戏, 应用包名, 步骤等
    RESULT:
        执行自动化脚本时写入的数据
        如 人员, 游戏, 安装, 等级等
    """
    RESULT = dict.fromkeys((
        "INSTALL", "START",
        "LEVEL", "STATE"
    ))
    TESTINFO = dict.fromkeys((
        "resolution", "image",
        "package", "level", "time"
    ))


    @classmethod
    def initialize_testinfo(cls, entry):
        """
        初始化测试信息
        entry的内容应当为list, 其内容如下
            [
                id, 
                执行人员,
                项目,
                分辨率,
                重试图片,
                包名,
                等级,
                时长
            ]
        """
        if not isinstance(entry, list):
            raise ValueError("Got wrong value from database.")
        try:
            cls.TESTINFO["resolution"] = json.loads(entry[3])
            cls.TESTINFO["image"] = json.loads(entry[4])
            cls.TESTINFO["package"] = entry[5]   # package在django端并未json化
            cls.TESTINFO["level"] = json.loads(entry[6])
            cls.TESTINFO["time"] = json.loads(entry[7])
        except:
            raise ValueError("Wrong values:\n %s" % json.dumps(entry, indent=4))

    @classmethod
    def initialize_result(cls, serialno):
        """预设INFO RESULT和STATE的初始值"""
        cls.RESULT["INSTALL"][serialno] = False
        cls.RESULT["START"][serialno] = False
        cls.RESULT["LEVEL"][serialno] = 0
        cls.RESULT["STATE"][serialno] = False

    @classmethod
    def set_INSTALL(cls, serialno, data):
        cls.RESULT["INSTALL"][serialno] = data

    @classmethod
    def set_START(cls, serialno, data):
        cls.RESULT["START"][serialno] = data

    @classmethod
    def set_LEVEL(cls, serialno, data):
        cls.RESULT["LEVEL"][serialno] = data

    @classmethod
    def set_STATE(cls, serialno, data):
        cls.RESULT["STATE"][serialno] = data
