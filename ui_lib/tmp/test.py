# import socket
# from threading import Thread
#
# sk = socket.socket()
# ip_port = ('0.0.0.0', 8080)
# sk.bind(ip_port)
# sk.listen(4)
#
#
# conn, addr = sk.accept()        # 值接受一个客户端请求
# while True:
#     if conn:
#         print("客户端地址==> %s" % addr[0])
#         data = input(">>>")
#         conn.send(bytes(data, encoding="utf-8"))

# from threading import Thread
# import time
# a = 0
#
#
# def func():
#     while True:
#         time.sleep(1)
#         global a
#         a += 1
#         print("hello world. %d" % a)
#
#
# if __name__ == "__main__":
#     t = Thread(target=func)
#     t.start()
#
#     print("主线程执行完毕")

# from multiprocessing import Process
# import time


# def func():
#     a = 0
#     while True:
#         time.sleep(1)
#         a += 1
#         print("hello world %d" % a)
#
#
# if __name__ == "__main__":
#     t = Process(target=func)
#     t.daemon = True
#     t.start()
#
#     for i in range(20):
#         time.sleep(1)
#         print("主进程ing==>")

# import sqlite3
#
# connect = sqlite3.connect("max906.db")
# cursor = connect.cursor()

import sys
import random
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QWidget
from numpy import arange, sin, pi
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")


class MyMplCanvas(FigureCanvas):
    """FigureCanvas的最终的父类其实是QWidget。"""

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        self.axes = self.fig.add_subplot(111)  # 建立一个子图，如果要建立复合图，可以在这里修改

        self.axes.hold(False)  # 每次绘图的时候不保留上一次绘图的结果

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    '''绘制静态图，可以在这里定义自己的绘图逻辑'''

    def start_static_plot(self):
        self.fig.suptitle('测试静态图')
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)
        self.axes.set_ylabel('静态图：Y轴')
        self.axes.set_xlabel('静态图：X轴')
        self.axes.grid(True)

    '''启动绘制动态图'''

    def start_dynamic_plot(self, *args, **kwargs):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)  # 每隔一段时间就会触发一次update_figure函数。
        timer.start(1000)  # 触发的时间间隔为1秒。

    '''动态图的绘图逻辑可以在这里修改'''

    def update_figure(self):
        self.fig.suptitle('测试动态图')
        l = [random.randint(0, 10) for i in range(4)]
        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.axes.set_ylabel('动态图：Y轴')
        self.axes.set_xlabel('动态图：X轴')
        self.axes.grid(True)
        self.draw()
