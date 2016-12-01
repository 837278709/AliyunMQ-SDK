#encoding:utf-8

'''
Created on Dec 1, 2016

@author: jack
'''

import socket
import hmac
from hashlib import sha1
"""
解析url
"""
def parseURL(url):
    iplist = socket.gethostbyname_ex(url)
    if len(iplist) == 0:
        return None
    ips = iplist[2]
    if len(ips) == 0:
        return None
    return ips[0]
"""
认证签名
"""
def calSignature(signString, sk):
    mac = hmac.new(sk, signString, sha1)
    return mac.digest().encode('base64').rstrip()

class MyClass(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        