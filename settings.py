# 配置信息
from multiprocessing import Queue
from to_ta import gpi_write
from functools import partial

q = Queue(5)        # 用于主进程和socket服务端子进程通信
q_timeout = 20      # 队列等待超时时间

SMBus = 0x5A        # 出厂设置默认地址
TA = 0x006          # 环境温度寄存器地址
TOBJ1 = 0x007       # 物体温度寄存器地址
TOBJ2 = 0x008

ip_port = ("0.0.0.0", 8080)    # 服务器ip和端口

LCDAddr = 0x3F      # 1602地址

warn_pin = 0        # 温度控制pin引脚号
warm_pin = 2        # 恒温控制pin 码


# 指令映射
menu_mapping = {
    'set': {
        'warn': {
            'on': partial(gpi_write, warn_pin, 1),
            'off': partial(gpi_write, warn_pin, 0)
        },
        'warm': {
            'on': partial(gpi_write, warm_pin, 1),
            'off': partial(gpi_write, warm_pin, 0)
        },
    },
    'get': {},
}
