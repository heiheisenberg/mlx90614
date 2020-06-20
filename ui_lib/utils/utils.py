import subprocess
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from threading import Event
import IPy
import sys
import queue
import sqlite3
import time
import numpy as np
from .email_tool import email_api

if sys.platform.startswith("win"):
    cmd_ping = 'ping %s -n 1 -w 1'
else:
    cmd_ping = 'ping %s -c 1 -W 1'


class AutoScan(object):

    def __init__(self, ip_mask, wp):
        self.wp = wp
        max_workers = self.wp.threading_spinBox.text()
        self.max_workers = int(max_workers) if int(max_workers) else 4
        ip = IPy.IP(ip_mask)
        self.ip_len = ip.len()
        self.result = []        # 保存ping 获取到的存活主机
        
        self.pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.q = queue.Queue()
        for i in ip:
            self.q.put(str(i))

    def scan_task(self):
        try:
            ip = self.q.get(block=False)
        except queue.Empty as e:
            print("[ERROR]%s" % str(e))
            return
        print("[INFO]ping: %s" % str(ip))
        try:
            self.wp.append_api("[INFO]ping: %s" % str(ip))
            ret = subprocess.getstatusoutput(cmd_ping % str(ip))
            if ret[0] == 0:
                print("[INFO]ping: %s success!" % str(ip))
                self.wp.append_api("[INFO]ping: %s success!" % str(ip))
                self.result.append(str(ip))
        except Exception as e:
            print("[ERROR]%s" % str(e))
            return None

    def run_scan(self):
        print("[INFO]ip扫描线程启动==>")
        self.wp.append_api("[INFO]ip扫描线程启动==> {}".format(self.max_workers))
        for i in range(self.ip_len):
            self.pool.submit(self.scan_task)
        self.pool.shutdown()

        # 扫描结束打印输出
        if not self.result:
            self.wp.append_api("[INFO]没有找到存活主机")
        else:
            for item in self.result:
                print("[INFO]找到一个存活主机: %s" % item)
                self.wp.append_api("[INFO]找到一个存活主机: %s" % item)

        # 结束后负责释放控件
        self.wp.auto_ip_pushButton.setEnabled(True)
        self.wp.threading_spinBox.setEnabled(True)
        

class GeneralThread(Thread):
    """
    通用线程控制类
    """
    def __init__(self, *args, **kwargs):
        """
        之类如果实现了自己的构造方法,应该调用父类的实现
        """
        super(GeneralThread, self).__init__(*args, **kwargs)
        self._stop_event = Event()
        
    def stop(self):
        self._stop_event.set()
        
    def should_stop(self):
        return self._stop_event.is_set()


class WarnControl(GeneralThread):

    def __init__(self, wp):
        super(WarnControl, self).__init__()
        self.wp = wp

    def run(self) -> None:
        db = Sqlite3Class(self.wp)
        db.activate()
        try_max = 5
        while True:
            try:
                time.sleep(1)
                # 动态获取预设温度和温差
                warn_pre = float(self.wp.warn_pre_doubleSpinBox.text())
                warn_dis = float(self.wp.warn_dis_doubleSpinBox.text())
                current_tmp = db.get_last()  # 当前温度
                if current_tmp:
                    current_tmp = current_tmp[2]
                    try_max = 5
                    if warn_pre + warn_dis <= current_tmp:
                        self.wp.append_api("[WARNING]高温预警")
                        self.wp.warn_status_label.setStyleSheet("background-color: red;")
                        # 添加温度报警声
                        self.wp.player.play()
                        # 添加邮件通知
                        if self.wp.email_flag:
                            email_api.send(pre_warm=warn_pre, dis_warm=current_tmp)
                        self.wp.send_cmd('set warn on')
                    else:
                        self.wp.player.stop()
                        self.wp.warn_status_label.setStyleSheet("background-color: green;")
                        self.wp.send_cmd('set warn off')
                else:
                    try_max -= 1
                    self.wp.append_api("[ERROR]获取当前温度失败,正在尝试==>")
                if not try_max:
                    db.close()
                    self.wp.append_api("[ERROR]获取当前温度失败,温度警告系统下线==>")
                    break

                if self.should_stop():
                    db.close()
                    self.wp.append_api("[WARNING]温度监控系统正在下线")
                    self.wp.send_cmd('set warn off')
                    break
            except Exception as e:
                self.wp.append_api("[ERROR]温度报警系统出错:%s" % str(e))
                db.close()
                break   
        self.wp.append_api("[WARNING]温度报警系统已下线")
        self.wp.warn_status_label.setStyleSheet("background-color: gray;")


class WarmControl(GeneralThread):
    def __init__(self, wp):
        super(WarmControl, self).__init__()
        self.wp = wp

    def run(self) -> None:
        db = Sqlite3Class(self.wp)
        db.activate()
        try_max = 5
        while True:
            try:
                time.sleep(2)
                # 动态获取预设温度和温差
                warm_pre = float(self.wp.warm_pre_doubleSpinBox.text())
                warm_dis = float(self.wp.warm_dis_doubleSpinBox.text())
                current_tmp = db.get_last()  # 当前温度
                if current_tmp:
                    current_tmp = current_tmp[2]
                    try_max = 5
                    if current_tmp <= warm_pre - warm_dis:
                        self.wp.append_api("[INFO]正在加热==>")
                        self.wp.warm_status_label.setStyleSheet("background-color: red;")
                        self.wp.send_cmd('set warm on')
                    else:
                        self.wp.append_api("[INFO]保温模式==>")
                        self.wp.warm_status_label.setStyleSheet("background-color: green;")
                        self.wp.send_cmd('set warm off')
                else:
                    try_max -= 1
                    self.wp.append_api("[ERROR]获取当前温度失败,正在尝试==>")
                if not try_max:
                    db.close()
                    self.wp.append_api("[ERROR]获取当前温度失败,恒温系统即将下线==>")
                    break

                if self.should_stop():
                    db.close()
                    self.wp.append_api("[WARNING]恒温系统正在下线")
                    self.wp.send_cmd('set warm off')
                    break
            except Exception as e:
                self.wp.append_api("[ERROR]恒温系统出错:%s" % str(e))
                self.wp.append_api("[WARNING]恒温系统正在下线")
                db.close()
                break
        self.wp.append_api("[WARNING]恒温系统已下线")
        self.wp.warm_status_label.setStyleSheet("background-color: gray;")


class DynamicMatThreading(GeneralThread):

    def __init__(self, canvas_obj=None):
        super(DynamicMatThreading, self).__init__()
        self.canvas_obj = canvas_obj        # 画布对象

    def run(self) -> None:
        db = Sqlite3Class(self.canvas_obj.wp)
        db.activate()
        self.canvas_obj.fig.suptitle("温度报表动态分析")
        self.canvas_obj.wp.append_api("[INFO]数据动态分析开启成功")
        print("[INFO]数据动态分析开启成功")
        while True:
            try:
                time.sleep(1)
                # 从数据库读取最后60条数据
                self.handler_plot(db)
                if self.should_stop():
                    self.canvas_obj.wp.append_api('[INFO]停止动态分析==>')
                    db.close()
                    break
            except Exception as e:
                print("[ERROR]动态分析出错:%s" % str(e))
                self.canvas_obj.wp.append_api('[ERROR]动态分析出错:%s' % str(e))
                db.close()
                break
        self.canvas_obj.wp.append_api('[INFO]数据动态分析已停止工作==>')
        print('[INFO]数据动态分析已停止工作==>')

    def handler_plot(self, db):
        ret = db.get_last(60)[-1::-1]  # reverse
        t = np.arange(len(ret))
        ta = [i[1] for i in ret]
        to = [i[2] for i in ret]
        ta = np.array(ta)
        to = np.array(to)
        self.canvas_obj.axes.cla()
        self.canvas_obj.axes.plot(t, ta, label="ta")
        self.canvas_obj.axes.plot(t, to, label='to')
        self.canvas_obj.axes.legend()
        self.canvas_obj.draw()


class Sqlite3Class(object):
    def __init__(self, wp):
        self.db_name = 'max906.db'
        self.conn = None
        self.cursor = None
        self.wp = wp

    def activate(self):
        """
        激活sqlite数据库
        :return:
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
        except Exception as e:
            self.wp.append_api("[ERROR]数据库连接失败:%s" % str(e))
            return None
        else:
            self.cursor = self.conn.cursor()
            return self.cursor

    def close(self):
        self.cursor.close()
        self.conn.close()

    def get_last(self, count=1):
        try:
            sql = 'select * from ta_to order by id desc limit %d' % count
            self.cursor.execute(sql)
        except sqlite3.OperationalError as e:
            self.wp.append_api("[ERROR]%s" % str(e))
            return None
        except Exception as e:
            self.wp.append_api("[ERROR]%s" % str(e))
            return None
        else:
            ret = self.cursor.fetchall()
            if count == 1 and ret:
                ret = ret[0]
            return ret

    def insert_one(self, sql, *args, **kwargs):
        try:
            self.cursor.execute(sql, *args, **kwargs)
            self.conn.commit()
        except sqlite3.OperationalError as e:       # database is locked
            self.wp.append_api("[ERROR]数据库插入失败:{}-[{}]".format(str(e), sql))
            pass
        except Exception as e:
            self.wp.append_api("[ERROR]数据库插入失败:{}-[{}]".format(str(e), sql))
            self.close()
            raise
