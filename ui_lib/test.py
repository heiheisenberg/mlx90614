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

from multiprocessing import Process
import time


def func():
    a = 0
    while True:
        time.sleep(1)
        a += 1
        print("hello world %d" % a)


if __name__ == "__main__":
    t = Process(target=func)
    t.daemon = True
    t.start()

    for i in range(20):
        time.sleep(1)
        print("主进程ing==>")
