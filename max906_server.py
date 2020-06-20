import socketserver
import time
from settings import ip_port, menu_mapping
from max906_log import log
from threading import Thread
from logging import DEBUG, ERROR
from settings import q, q_timeout, warn_pin, warm_pin
from queue import Empty
from to_ta import gpi_write


class MyServer(socketserver.BaseRequestHandler):
    def handle(self):
        t = Thread(target=self.handle_custom_cmd)
        t.setDaemon(True)  # 开启守护线程,主线程结束子线程也同时结束
        t.start()
        while True:
            try:
                time.sleep(1)
                try:
                    send_data = q.get(timeout=q_timeout)
                except Empty:
                    log(ERROR, "队列get超时,连接断开")
                    raise
                self.request.send(bytes(send_data, encoding="utf-8"))
            except Exception as e:
                gpi_write(warn_pin, 0)      # 异常退出将警报和恒温关闭
                gpi_write(warm_pin, 0)
                log(ERROR, str(e))
                break

    # 命令行处理子线程
    def handle_custom_cmd(self):
        while True:
            try:
                data = self.request.recv(1024).strip()
                if not data and data == b'max_906':
                    continue
                menu, kind, action = data.decode('utf-8').strip().split()
                if menu and kind and action:
                    func = menu_mapping[menu][kind][action]
                    func()
                log(DEBUG, "[INFO]%s" % data.decode("utf-8"))
            except Exception as e:
                log(ERROR, "[ERROR]%s" % str(e))
                break


# socket服务初始化
def init():
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(ip_port, MyServer)
    server.serve_forever()


if __name__ == "__main__":
    init()
