import sys
import time
import gevent

sys.path.append("..")
from control import Operateions, write_cost_time
from testinfo import TestInfo

resolution = (1280, 720)

steps = [
    # (操作, png文件, 是否需要一直等待(0是1否), 失败重试次数)
    # ("click", "一键注册.png", 0, 3),
    # ("click", "确定注册.png", 0, 3),
    ("click", "战玲珑2图标.png", 0, 3),
    ("record", "进入游戏成功"),
    ("click", "战玲珑2图标.png", 0, 0),
    ("click", "输入帐号.png", 0, 3),
    ("write", "", 0),
    ("click", "登录游戏.png", 0, 3),
    ("sleep", 2),
    ("click", "公告确定.png", 1, 1),
    ("click", "登录游戏.png", 0, 3),
    ("click", "女性角色.png", 0, 3),
    ("click", "职业图标.png", 0, 3),
    ("click", "修改名字.png", 1, 0),
    ("write", "", 0),
    ("click", "创建角色.png", 0, 3),
    ("click", "创建角色.png", 1, 0),
    ("click", "继续任务.png", 0, 1),
    ("record", 4),
    ("sleep", 180),
    # (操作, png文件A, png文件B, 是否需要一直等待, 失败重试次数, 点击次数)
    # 第一个强制引导
    # ("click_other", "新手引导NPC.png", "继续任务.png", 0, 3, 20),
    # ("click_other", "新手引导NPC.png", (450, 200), 0, 3, 3),
    ("click", "学习按钮.png", 0, 3),
    ("record", 10),
    ("sleep", 30),
    ("click", "立即穿戴.png", 0, 1),
    ("click", "立即穿戴.png", 1, 0),
    ("click", "立即穿戴.png", 1, 0),
    ("sleep", 60),
    # ("click_other", "新手引导NPC.png", "继续任务.png", 0, 3, 30),
    # ("click_other", "新手引导NPC.png", (630, 200), 0, 3, 3),
    ("click", "学习按钮.png", 0, 3),
    ("record", 15),

    # 第二个强制引导
    ("click_other", "新手引导NPC.png", "首领图标.png", 0, 3),
    ("click_other", "首领图标.png", (1070, 100), 1, 0),
    ("click_other", "新手引导NPC.png", "挑战按钮.png", 0, 3),
    
    ("sleep", 60),

    ("click", "立即穿戴.png", 1, 0),
    
    ("click", "查看按钮.png", 0, 2),
    ("click", "穿戴按钮2.png", 0, 2),
    ("click", "退出背包.png", 0, 2),

    ("click", "立即穿戴.png", 1, 0),
    
    ("sleep", 45),
    
    ("click", "立即穿戴.png", 1, 0),

    ("sleep", 210),

    ("click", "立即穿戴.png", 1, 1),

    ("click", "查看按钮.png", 0, 2),
    ("click", "穿戴按钮2.png", 0, 2),
    ("click", "退出背包.png", 0, 2),
    
    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),

    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),

    ("record", 20),

    # 第三个强制引导
    ("click_other", "锻造图标.png", (220, 280), 0, 3, 20),
    ("click", "武器强化.png", 0, 3),
    ("click", "强化按钮.png", 0, 3),
    ("click", "退出强化.png", 0, 3),
    ("record", 20),

    ("click_other", "新手引导NPC.png", "背包图标.png", 0, 3),
    ("click_other", "新手引导NPC.png", (1070, 650), 0, 3),
    ("click_other", "兑换按钮.png", (880, 220), 0, 3),
    ("click", "兑换按钮.png", 0, 3),
    ("click", "退出仙贝兑换.png", 0, 3),
    ("click", "退出背包.png", 0, 3),

    ("click_other", "新手引导NPC.png", "商城图标.png", 0, 3),
    ("click_other", "购买按钮.png", (440, 390), 0, 3),
    ("click_other", "购买弹窗.png", (850, 310), 0, 3),
    ("click", "退出商城.png", 0, 3),

    ("click_other", "新手引导NPC.png", (150, 280), 0, 3, 30),
    ("click_other", "新手引导NPC.png", (800, 200), 0, 3),
    ("click", "学习按钮.png", 0, 3),

    ("click_other", "新手引导NPC.png", "首领图标.png", 0, 3),
    ("click_other", "首领图标.png", (1070, 100), 1, 0),
    ("click_other", "新手引导NPC.png", "挑战按钮.png", 0, 3),

    ("record", 24),

    ("sleep", 120),

    ("click_other", "领取豪礼.png", (1150, 105), 0, 3),
    ("record", 28),

    ("sleep", 180),

    ("click", "立即穿戴.png", 1, 3),

    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),

    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),

    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),

    ("click", "查看按钮.png", 1, 0),
    ("click", "穿戴按钮2.png", 1, 0),
    ("click", "退出背包.png", 1, 0),

    ("sleep", 30),

    # 第四个强制引导
    ("click_other", "新手引导NPC.png", "首领图标.png", 0, 3),
    ("click_other", "首领图标.png", (1070, 100), 1, 0),
    ("click_other", "新手引导NPC.png", "挑战按钮.png", 0, 3),
    ("record", 31),
]





@write_cost_time
def run_test(log, serialno, package):
    import time
    op = Operateions(log, serialno, package, resolution)
    gevent.sleep(10)
    start = time.time()
    count = 0
    for method, *args in steps:
        out = getattr(op, method)(*args)
        # 有一次必要的操作失败了, 就直接break
        if out is False:
            break
        # 每次行为结束后都让位给别的协程
        # 以确保不会被这一个协程一直占用着线程
        gevent.sleep(0.01)
        now = time.time()
        # 时长超过35分钟, 也直接break, 以免总测试时间过长
        if (now - start) >= (35 * 60):
            break
        count += 1
        if count >= 2:
            # 行动次数到第2次时
            TestInfo.set_start(serialno, True)
    return log
