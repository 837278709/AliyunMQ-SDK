#encoding:utf-8

'''
Created on Dec 1, 2016

@author: jack
'''

import ConfigParser
import httplib
import json
import time
from urlparse import urlparse
from Util import parseURL, calSignature

"""
消费者类
"""
class HttpConsumer(object):
    
    def __init__(self):
        """签名字段"""
        self.signatue = "Signature"
        """消费者id"""
        self.consumerid = "ConsumerId"
        """消费主题"""
        self.topic = "topic"
        """访问码"""
        self.ak = "AccessKey"
        """配置文件解析器"""
        self.cf = ConfigParser.ConfigParser()
    """
    topic消费流程
    """
    def process(self):
        """开始读取配置文件"""
        self.cf.read("user.properties")
        """读取主题"""
        topic = self.cf.get("property", "topic")
        """存储消息的url路径"""
        url = self.cf.get("property", "url")
        """访问码"""
        ak = self.cf.get("property", "user_accesskey")
        """密钥"""
        sk = self.cf.get("property", "user_secretkey")
        """消费者组id"""
        cid = self.cf.get("property", "consumer_group")
        newline = "\n"
        """获取url主机域名地址"""
        urlname = urlparse(url).hostname
        """连接存储消息的服务器"""
        conn = httplib.HTTPConnection(parseURL(urlname))
        while True:
            try:
                """时间戳"""
                date = repr(int(time.time() * 1000))[0:13]
                """构造签名字符串"""
                signString = topic + newline + cid + newline + date
                """计算签名值"""
                sign = calSignature(signString,sk)
                """请求消息http头部"""
                headers = {
                    self.signatue : sign,
                    self.ak : ak,
                    self.consumerid : cid
                    }
                """开始发送获取消息的http请求"""
                conn.request(method="GET",url=url+"/message/?topic="+topic+"&time="+date+"&num=32",headers=headers)
                """获取http应答消息"""
                response = conn.getresponse()
                """验证应答消息状态值"""
                if response.status != 200:
                    continue
                """从应答消息中读取实际的消息内容"""
                msg = response.read()
                """将实际的消费消息进行解码"""
                messages = json.loads(msg)
                if len(messages) == 0:
                    time.sleep(2)
                    continue
                """依次获取每条消费消息"""
                for message in messages:
                    """计算时间戳"""
                    date = repr(int(time.time() * 1000))[0:13]
                    """构建删除消费消息url路径"""
                    delUrl = url + "/message/?msgHandle="+message['msgHandle'] + "&topic="+topic+"&time="+date
                    """构造签名字符串"""
                    signString = topic + newline + cid + newline + message['msgHandle'] + newline + date
                    """进行签名"""
                    sign = calSignature(signString,sk)
                    """构造删除消费消息http头部"""
                    delheaders = {
                           self.signatue : sign,
                        self.ak : ak,
                        self.consumerid : cid,
                }
                    """发送删除消息请求"""
                    conn.request(method="DELETE", url=delUrl, headers=delheaders)
                    """获取请求应答"""
                    response = conn.getresponse()
                    """读取应答内容"""
                    msg = response.read()
                    print "delete msg:"+msg
            except Exception,e:
                print e
        conn.close()
"""启动入口"""
if __name__ == '__main__':
    """构造消息消费者"""
    consumer = HttpConsumer()
    """开始进入消费流程"""
    consumer.process()
