#!/usr/bin/env python
# coding: utf-8

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import base64
import os
import re

from .TTSengines import Aliyun_TTS_engine, Azure_TTS_engine, Tencent_TTS_engine

# 从Key服务器请求语音合成key

class KeyRequest:
    service_ip_path = './assets/security/service_ip'
    private_key_path = './assets/security/private_key.pem'
    def __init__(self,cdkey:str):
        # 校验CDKey
        self.status = self.checkup_cdkey(cdkey)
        if self.status:
            return
        # 载入key和ip
        self.status = self.load_private_key()
        if self.status:
            return
        # 发送请求
        self.status = self.request_key()
        if self.status:
            return
        # 解密反馈
        self.status = self.bulid_key_struct()
        if self.status:
            return
        # 将获取的key应用到TTSengine
        self.status = self.execute()
    # 检查CDKEY
    def checkup_cdkey(self,cdkey:str):
        if cdkey == '':
            return 8
        self.cdkey:str = str(cdkey).upper()
        RE_CDKey = re.compile('([A-Z0-9]{4}-){3}[A-Z0-9]{4}')
        if RE_CDKey.fullmatch(self.cdkey):
            return 0
        else:
            return 7
    # 载入私钥
    def load_private_key(self):
        if os.path.isfile(self.private_key_path):
            with open(self.private_key_path, 'rb') as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
        else:
            return 6 # Key
        if os.path.isfile(self.service_ip_path):
            with open(self.service_ip_path,'r') as ip_file:
                self.service_ip = ip_file.read()
        else:
            return 5 # IP
        return 0
    # 解密
    def decrypt_key(self,encrypted_base64:str)->str:
        '输入一个base64，解密并输出key原文'
        encrypted_key = base64.b64decode(encrypted_base64)
        decrypted_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted_key.decode('utf-8')
    # 解密key结构
    def bulid_key_struct(self)->dict:
        try:
            self.keys = {key:self.decrypt_key(value) for key,value in self.result['keys'].items()}
            return 0
        except Exception as E:
            return 2 # decrypt_key
    # 请求
    def request_key(self):
        # 构造请求的数据 # TODO：请求内容
        request_message = {
            'cdkey': self.cdkey
        }
        # 发送 POST 请求
        try:
            response = requests.post(self.service_ip, data=request_message)
            self.result = response.json()
        except Exception as E:
            # print(E)
            return 4 # network
        # 查看请求
        if self.result['status'] == 200:
            return 0
        elif self.result['status'] == 401:
            return 3 # 无权限
        else:
            return 9 # 其他
    def execute(self):
        try:
            # 阿里云语音合成key
            Aliyun_TTS_engine.AKID = self.keys['Aliyun.accesskey']
            Aliyun_TTS_engine.AKKEY = self.keys['Aliyun.accesskey_secret']
            Aliyun_TTS_engine.APPKEY = self.keys['Aliyun.appkey']
            # Azure语音合成key
            Azure_TTS_engine.AZUKEY = self.keys['Azure.azurekey']
            Azure_TTS_engine.service_region = self.keys['Azure.service_region']
            # 腾讯的语音合成key
            Tencent_TTS_engine.APPID = int(self.keys['Tencent.appid'])
            Tencent_TTS_engine.SecretId = self.keys['Tencent.secretid']
            Tencent_TTS_engine.SecretKey = self.keys['Tencent.secretkey']
            # 返回值
            return 0
        except Exception:
            return 1
