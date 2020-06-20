import wiringpi as wpi
from settings import LCDAddr

fd_1602 = wpi.wiringPiI2CSetup(LCDAddr)  # I2C初始化


def send_bit(comm, rs=1):
    # 先送最高4位
    buf = comm & 0xF0
    buf = buf | 0x04 | rs       # rs=1是写数据, rs=0是写指令
    wpi.wiringPiI2CWrite(fd_1602, buf)
    wpi.delay(2)
    buf &= 0xFB                 # EN 1 -> 0
    wpi.wiringPiI2CWrite(fd_1602, buf)

    # 后送低4位
    buf = (comm & 0x0F) << 4
    buf = buf | 0x04 | rs
    wpi.wiringPiI2CWrite(fd_1602, buf)
    wpi.delay(2)
    buf &= 0xFB
    wpi.wiringPiI2CWrite(fd_1602, buf)


def init_1602():
    send_bit(0x33, 0)       # 先初始化为8位数据线
    wpi.delay(5)
    send_bit(0x32, 0)       # 然后初始化为4位数据线
    wpi.delay(5)
    send_bit(0x28, 0)       # 2 Lines & 5*7 dots
    wpi.delay(5)
    send_bit(0x0C, 0)       # Enable display without cursor
    wpi.delay(5)
    send_bit(0x01, 0)       # Clear Screen


def clear():                # 清屏
    send_bit(0x01, 0)
