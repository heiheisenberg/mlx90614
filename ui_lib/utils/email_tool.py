from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from .settings import email, email_time
from threading import Thread
import time


class EmailNotify(object):
    msg = 'MLX90614温度系统报警：高温警报！预设温度：{pre_warm}，当前温度：{dis_warm}'
    last_send = 0

    def __init__(self,):
        self.request = CommonRequest()
        self.client = AcsClient('xx', 'xx', 'cn-hangzhou')
        self.init()                     # 只初始化一次

    def init(self):
        self.request.set_accept_format('json')
        self.request.set_domain('dm.aliyuncs.com')
        self.request.set_method('POST')
        self.request.set_protocol_type('https')  # https | http
        self.request.set_version('2015-11-23')
        self.request.set_action_name('SingleSendMail')

        self.request.add_query_param('RegionId', "cn-hangzhou")
        self.request.add_query_param('AccountName', "??")
        self.request.add_query_param('AddressType', "1")
        self.request.add_query_param('ReplyToAddress', "true")
        self.request.add_query_param('ToAddress', email)
        self.request.add_query_param('Subject', "温度报警系统通知")
        self.request.add_query_param('TagName', "温度报警系统通知")

    def send(self, pre_warm, dis_warm):
        send_now = int(time.time())
        send_to_last = send_now - self.last_send
        if send_to_last >= email_time:      # 邮件发送间隔,不能无限制发送
            self.last_send = send_now
            self.request.add_query_param('TextBody', self.msg.format(pre_warm=pre_warm, dis_warm=dis_warm))
            t = Thread(target=self.client.do_action_with_exception, args=(self.request, ))
            t.start()


email_api = EmailNotify()


# if __name__ == '__main__':
#     ret = email_api.send(50.0, 52.0)
#     print(ret)
