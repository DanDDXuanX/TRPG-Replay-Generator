#!/usr/bin/env python
# coding: utf-8

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
import base64
import hashlib
import os
import uuid
import sys

from .TTSengines import Aliyun_TTS_engine, Azure_TTS_engine, Tencent_TTS_engine

# 从Key服务器请求语音合成key

class KeyRequest:
    service_ip_path = './assets/security/service_ip'
    private_key_path = './assets/security/keys_private_key.pem'
    public_key_path = './assets/security/messages_public_key.pem'
    def __init__(self):
        # 初始化
        self.mac_address:str = self.get_mac_address()
        self.client_tag:str  = self.get_client_tag()
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
    # 获取设备的Mac地址
    def get_mac_address(self):
        mac_address = uuid.getnode()
        mac_address_str = ':'.join(format(mac_address, '012x')[i:i+2] for i in range(0, 12, 2))
        return mac_address_str
    def get_client_tag(self):
        file_path = sys.executable
        with open(file_path, 'rb') as file:
            md5_hash = hashlib.md5()
            while chunk := file.read(4096):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    # 载入key
    def load_private_key(self):
        # 用于发送消息的公钥
        if os.path.isfile(self.public_key_path):
            with open(self.public_key_path, 'rb') as key_file:
                self.public_key = serialization.load_pem_public_key(
                    key_file.read()
                )
        else:
            return 6 # Key
        # 用于接受消息的私钥
        if os.path.isfile(self.private_key_path):
            with open(self.private_key_path, 'rb') as key_file:
                self.private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
        else:
            return 6 # Key
        # 服务端地址
        if os.path.isfile(self.service_ip_path):
            with open(self.service_ip_path,'r') as ip_file:
                self.service_ip = ip_file.read()
        else:
            return 5 # IP
        return 0
    # 加密发送的消息
    def encrypt_message(self,message:str)->str:
        encrypted_message = self.public_key.encrypt(
            message.encode('utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_message).decode()
    # 解密接受的Key
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
    # 鉴权消息
        request_message = {
            'message': 'key_request',
            'client': self.encrypt_message(self.client_tag),
            'mac': self.encrypt_message(self.mac_address)
        }
        # 发送 POST 请求
        try:
            response = requests.post(self.service_ip+'/authenticate', json=request_message)
            self.result = response.json()
        except Exception as E:
            # print(E)
            return 4 # network
        # 查看请求
        if self.result['status'] == 200:
            print('usage:', self.result['usage'])
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
    # 发送报文
    def post_usage(self):
        # 用量
        usage_counter = Aliyun_TTS_engine.counter + Azure_TTS_engine.counter + Tencent_TTS_engine.counter
        # 报文消息
        if usage_counter:
            post_message = {
                'message': 'usage_report',
                'client': self.encrypt_message(self.client_tag),
                'mac': self.encrypt_message(self.mac_address),
                'value': int(usage_counter)
            }
        # 发送 POST 请求
        try:
            response = requests.post(self.service_ip+'/messages', json=post_message)
            self.result = response.json()
        except Exception as E:
            return 4 # 网络和服务端
        # 查看请求
        if self.result['status'] == 200:
            # 重置用量
            Aliyun_TTS_engine.counter = 0
            Azure_TTS_engine.counter = 0
            Tencent_TTS_engine.counter = 0
            return 0 # 正常
        elif self.result['status'] == 400:
            return 1 # 报文错误
        else:
            return 9 # 其他