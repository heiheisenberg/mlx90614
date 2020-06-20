from max906_server import init                # socket服务端初始化
from to_ta import mlx_init, gpi_init          # 主设备初始化
from to_ta import get_ta_to                   # 数据采集函数
from to_ta import WiringPiSetupError
from settings import q, warn_pin, warm_pin
from multiprocessing import Process
import sys
import time
from max906_log import log          # 日志模块
from logging import DEBUG, ERROR
from queue import Full


def run():
    try:
        bus_fd = mlx_init()                  # init mlx_90614
        gpi_init(warn_pin)                   # 初始化温度控制系统
        gpi_init(warm_pin)                   # 初始化恒温控制系统
    except WiringPiSetupError as e:
        log(ERROR, str(e))
        sys.exit(1)
    server_t = Process(target=init)          # 开启socket服务端子进程
    server_t.daemon = True                   # 设置为守护进程
    server_t.start()

    # 主进程处理数据
    while True:
        try:
            time.sleep(1)                   # 采样时间间隔
            _handle_data(bus_fd)
        except Exception as e:
            log(ERROR, str(e))
            sys.exit(1)


def _handle_data(bus_fd):
    """
    数据处理, 并负责吧数据放入队列中
    :param bus_fd: 从设备句柄
    :return:
    """
    ret = get_ta_to(bus_fd)
    if ret[2] == 0:
        to = ret[1]*0.02 - 273.15
    to = ret[1] * 0.02 - 273.15
    msg = "TA: {:.2f} TO: {:.2f} ".format(ret[0], to)
    log(DEBUG, msg)             # 本地保存数据
    try:
        q.put(msg, block=False)     # 这样做的目的是为了客户端在连接时看到的是实时数据
    except Full:
        log(DEBUG, "队列已满")


if __name__ == '__main__':
    run()
