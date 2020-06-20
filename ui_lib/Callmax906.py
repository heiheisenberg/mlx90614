import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal
from threading import Thread
from max906 import Ui_Form
from utils import AutoScan
from PyQt5 import QtCore
from utils import WarnControl, WarmControl
import time
import socket


class MyMainWindow(QWidget, Ui_Form):
    append_str = pyqtSignal(str)
    Warn_Class = WarnControl  # 温度报警子线程类
    warn_obj = None

    Warm_Class = WarmControl  # 恒温监控系统
    warm_obj = None

    dynamic_t = None

    def append_api(self, text):
        self.append_str.emit(str(text))

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.sk = None  # socket对象
        self.player = None  # 音乐播放对象
        self.email_flag = False
        self.setup()

    def setup(self):
        self.setupUi(self)
        self.signal_init()

        # 初始化默认ip和端口
        self.ip_lineEdit.setText("192.168.43.93")
        self.port_lineEdit.setText("8080")

        # 新增音乐播放
        from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
        self.player = QMediaPlayer(self)
        url = QtCore.QUrl.fromLocalFile('8069.mp3')
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.setVolume(100)

    def signal_init(self):
        """
        信号初始化
        :return:
        """
        self.threading_spinBox.valueChanged.connect(self.threading_count)
        self.connect_pushButton.clicked.connect(self.socket_connect)
        self.close_pushButton.clicked.connect(self.socket_close)
        self.clear_pushButton.clicked.connect(self.clear_output)
        self.save_pushButton.clicked.connect(self.save_log)
        self.auto_ip_pushButton.clicked.connect(self.auto_map)
        self.send_pushButton.clicked.connect(self.send_cmd)

        # 2020/01/11新增
        self.warn_checkBox.clicked[bool].connect(self.warn_checkbox_slot)
        self.warm_checkBox.clicked[bool].connect(self.warm_checkbox_slot)

        # 2020/01/12 QTextEdit bug修复
        self.append_str.connect(self.append_to_output)

        # 2020/01/13 数据分析动态绘图
        self.plot_dynamic_pushButton.clicked.connect(self.dynamic_start)
        self.plot_stop_pushButton.clicked.connect(self.dynamic_stop)

        # 2020/01/14 新增邮件报警信息通知
        self.email_checkBox.clicked[bool].connect(self.email_notify_slot)

    def warn_warm_sys_init(self):
        warn_status = self.warn_checkBox.isChecked()
        warn_pre = float(self.warn_pre_doubleSpinBox.text())
        warn_dis = float(self.warn_dis_doubleSpinBox.text())
        warm_status = self.warm_checkBox.isChecked()
        warm_pre = float(self.warm_pre_doubleSpinBox.text())
        warm_dis = float(self.warn_dis_doubleSpinBox.text())
        self.append_api("[INFO]温度报警系统初始化: {} {} {}".format(warn_status, warn_pre, warn_dis))
        self.append_api("[INFO]恒温控制系统初始化: {} {} {}".format(warm_status, warm_pre, warm_dis))

        self.warn_checkbox_slot(warn_status)
        self.warm_checkbox_slot(warm_status)

    # 获取socket套接字
    def socket_activate(self):
        self.sk = socket.socket()  # tcp连接

    # 尝试连接远程服务器
    def socket_connect(self):
        self.socket_activate()
        ip = self.ip_lineEdit.text()
        port = self.port_lineEdit.text()

        self.ip_lineEdit.setDisabled(True)
        self.port_lineEdit.setDisabled(True)
        self.connect_pushButton.setDisabled(True)
        self.send_pushButton.setDisabled(True)
        self.append_api("[INFO]正在连接:ip, port= %s %s" % (ip, port))
        print("正在连接==>ip, port= %s %s" % (ip, port), type(ip), type(port))
        t_c = Thread(target=self._socket_connect, args=(ip, int(port)))
        t_c.start()

    # 子线程
    def _socket_connect(self, ip, port):
        try:
            self.sk.connect((ip, int(port)))
            self.append_api("[INFO]服务器连接成功!")

            # 初始化温控系统, 在连接成功后
            self.warn_warm_sys_init()
        except Exception as e:
            self.append_api("[ERROR]远程服务器连接失败!")
            self.append_api("[ERROR]%s" % str(e))
            self.socket_close()
        else:
            # 连接成功后放开命令行按钮
            self.status_label.setText("连接成功:%s" % ip)
            self.send_pushButton.setEnabled(True)
            t_r = Thread(target=self._socket_recv)
            t_r.start()
            t_r.join()

    # 子线程监听服务端消息
    def _socket_recv(self):
        from utils import Sqlite3Class
        from datetime import datetime
        db = Sqlite3Class(self)
        db.activate()
        sql = 'insert into ta_to ("ta", "to", "time") values (?, ?, ?)'
        while True:
            time.sleep(0.8)
            try:
                data = self.sk.recv(1024)
                if not data:
                    # 主机存活状态检查
                    self.sk.send(b"max_906")
                    continue
                self.append_api("[INFO]%s" % data.decode("utf-8"))

                # 将数据插入数据库
                ta, to = self.handle_data(data.decode("utf-8"))
                db.insert_one(sql, (ta, to, datetime.now().strftime("%Y-%m-%d %X")))
            except Exception as e:
                self.append_api("[ERROR]%s" % str(e))
                self.socket_close()
                db.close()
                break

    @staticmethod
    def handle_data(data):
        # TA: 9.39 TO: 10.03
        data_list = data.split()
        return data_list[1], data_list[3]

    # 断开连接
    def socket_close(self):
        self.ip_lineEdit.setEnabled(True)
        self.port_lineEdit.setEnabled(True)
        self.connect_pushButton.setEnabled(True)
        self.status_label.setText("未连接")
        try:
            self.sk.close()
        except Exception as e:
            print("[ERROR]sk.close()关闭失败:%s" % str(e))
        self.warn_checkbox_slot(False)  # 温控系统下线
        self.warm_checkbox_slot(False)  # 恒温系统下线

        # 发送停止数据动态分析指令
        self.dynamic_stop()

    # 清空输出
    def clear_output(self):
        self.output_textEdit.clear()

    # 监控输出槽函数
    def append_to_output(self, text):
        self.output_textEdit.append(text)

    # 保存日志
    def save_log(self):
        context = self.output_textEdit.toPlainText()
        with open('max906_sentry.log', 'a', encoding='utf-8') as fp:
            fp.write(context)
            fp.write('\n--------' + time.asctime() + '----end of-----\n')
            self.append_api("[INFO]日志保存成功")

    # 尝试自动获取树莓派ip
    def auto_map(self):
        ip_mask = self.ip_lineEdit.text()
        self.threading_spinBox.setDisabled(True)
        self.append_api("[INFO]正在获取树莓派ip==> %s" % ip_mask)
        self.auto_ip_pushButton.setDisabled(True)
        scan = AutoScan(ip_mask, self)
        t = Thread(target=scan.run_scan)
        t.start()

    # 发送指令到服务器
    def send_cmd(self, custom=None):
        if custom:
            cmd_str = custom
        else:
            cmd_str = self.cmd_lineEdit.text()
        try:
            self.sk.send(bytes(cmd_str, encoding="utf-8"))
        except Exception as e:
            # 如果连接中断, 监听线程会关闭连接
            self.append_api("[Error]%s" % str(e))
        finally:
            self.cmd_lineEdit.setText("")

    # 扫描线程
    def threading_count(self):
        count = self.threading_spinBox.text()
        print("[INFO]当前工作线程: {}".format(count), type(count))
        self.append_api("[INFO]当前工作线程: {}".format(count))

    def warn_checkbox_slot(self, status):
        """
        温度报警槽函数
        :param status: True, 开启温度报警
        :return:
        """
        print("温度报警状态==>{}".format(status), type(status))
        self.append_api("[INFO]温度报警状态: {}".format(status))
        if status:
            self.warn_obj = self.Warn_Class(self)
            self.warn_obj.start()
        elif self.warn_obj:
            self.warn_obj.stop()  # 发送停止信号, 线程会执行完清理工作后退出

    def warm_checkbox_slot(self, status):
        """
        恒温控制
        :param status:
        :return:
        """
        print("恒温系统状态==>{}".format(status), type(status))
        self.append_api("[INFO]恒温系统状态: {}".format(status))
        if status:
            self.warm_obj = self.Warm_Class(self)
            self.warm_obj.start()
        elif self.warm_obj:
            self.warm_obj.stop()

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现窗体关闭时执行清理工作
        :param event: close()触发的事件
        :return: None
        """
        reply = QMessageBox.warning(self,
                                    'MLX90614',
                                    "程序退出后温度报警和恒温系统将会下线!!!",
                                    QMessageBox.Yes | QMessageBox.No,
                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.socket_close()
            event.accept()
        else:
            event.ignore()

    # 开启数据动态分析
    def dynamic_start(self):
        self.dynamic_t = self.matplotlibwidget_dynamic.mpl.compute_initial_figure(self)

    # 关闭数据动态分析,忽略错误
    def dynamic_stop(self):
        try:
            self.dynamic_t.stop()
        except Exception as e:
            self.append_api("[ERROR]关闭数据动态分析错误: %s" % str(e))

    def email_notify_slot(self, status):
        self.append_api("[INFO]当前邮件通知状态:{}".format(status))
        self.email_flag = status


def run_window():
    app = QApplication(sys.argv)
    my_win = MyMainWindow()
    my_win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run_window()
