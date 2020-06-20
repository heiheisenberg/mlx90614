import matplotlib
from PyQt5.QtWidgets import QSizePolicy, QWidget, QVBoxLayout
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from utils import DynamicMatThreading

matplotlib.use("Qt5Agg")


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        # 定义FigureCanvas的尺寸策略
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self, *args, **kwargs):
        """
        子类实现此方法, 绘图函数
        :return:
        """
        pass


class SimpleMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""

    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.fig.suptitle("温度报表静态分析")
        self.axes.plot(t, s)


class DynamicMplCanvas(MyMplCanvas):
    wp = None
    dynamic_t = None

    # 动态分析
    def compute_initial_figure(self, wp):
        self.wp = wp
        self.dynamic_t = DynamicMatThreading(self)
        self.dynamic_t.start()                  # 开启分析线程, 执行run方法
        return self.dynamic_t


class MatWidgetBase(object):
    mpl_layout = None
    mpl = None
    mpl_ntb = None
    canvas_class = MyMplCanvas

    def init_ui(self):
        self.mpl_layout = QVBoxLayout(self)
        self.mpl = self.canvas_class(self, width=5, height=4, dpi=100)
        self.mpl_ntb = NavigationToolbar(self.mpl, self)  # 添加完整的 toolbar

        self.mpl_layout.addWidget(self.mpl)
        self.mpl_layout.addWidget(self.mpl_ntb)


# 静态分析组件
class MatStaticWidget(QWidget, MatWidgetBase):
    canvas_class = SimpleMplCanvas

    def __init__(self, parent=None):
        super(MatStaticWidget, self).__init__(parent)
        self.init_ui()


# 动态分析组件
class MatDynamicWidget(QWidget, MatWidgetBase):
    canvas_class = DynamicMplCanvas     # self.mpl = canvas_class()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.init_ui()
