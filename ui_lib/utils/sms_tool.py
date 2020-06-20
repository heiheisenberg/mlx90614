#!/usr/bin/env python
# coding=utf-8

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException


client = AcsClient('??', '??', 'cn-hangzhou')       # 具体参数参考阿里文档，参数为保密参数，勿泄露
request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dysmsapi.aliyuncs.com')
request.set_method('POST')
request.set_protocol_type('https')  # https | http
request.set_version('2017-05-25')
request.set_action_name('SendSms')

request.add_query_param('RegionId', "cn-hangzhou")
request.add_query_param('PhoneNumbers', "发送手机号")
request.add_query_param('SignName', "合法签名")
request.add_query_param('TemplateCode', "模板号")
request.add_query_param('TemplateParam', '模板信息')

# response = client.do_action(request)
response = client.do_action_with_exception(request)
print(str(response, encoding='utf-8'))