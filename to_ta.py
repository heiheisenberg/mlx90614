import wiringpi as wpi
from wiringpi import GPIO
import settings
from max906_log import log
import logging


class WiringPiSetupError(Exception):
    pass


# wpi初始化
def mlx_init():
    ret = wpi.wiringPiSetup()      # wPi
    if ret:
        log(logging.ERROR, "设备初始化失败")
        raise WiringPiSetupError("主设备初始化失败!")
    bus_fd = wpi.wiringPiI2CSetup(settings.SMBus)  # I2C初始化
    return bus_fd


def get_ta_to(bus_fd):
    # 数据采集函数
    ta = wpi.wiringPiI2CReadReg16(bus_fd, settings.TA)       # 读取环境温度
    ta = int(ta)*0.02 - 273.15
    log(logging.DEBUG, "环境温度==>%s", str(ta))

    to_1 = wpi.wiringPiI2CReadReg16(bus_fd, settings.TOBJ1)       # 读取物体温度to1
    to_2 = wpi.wiringPiI2CReadReg16(bus_fd, settings.TOBJ2)       # 这里到底是什么?好像读出来是0
    log(logging.DEBUG, "To1+To2==> %d %d", int(to_1), int(to_2))

    return ta, to_1, to_2


def gpi_init(pin, mode=GPIO.OUTPUT, pud=GPIO.PUD_DOWN):
    # 引脚初始化函数
    wpi.pinMode(pin, mode)
    if pud:
        wpi.pullUpDnControl(pin, pud)


def gpi_write(pin, status):
    # 写引脚状态
    wpi.digitalWrite(pin, status)


def gpi_read(pin):
    # 读取引脚状态
    return wpi.digitalRead(pin)

