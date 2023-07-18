#!/usr/bin/env python
# coding: utf-8
# 语音服务类定义

import numpy as np
import pandas as pd
import sys
import os
import pydub
import base64
import wave
# import requests
import json
import time

from .Exceptions import SynthesisError, WarningPrint

voice_lib = pd.read_csv('./media/voice_volume.tsv',sep='\t').set_index('Voice')

# 没用的基类
class TTS_engine:
    def __init__(self,name='unnamed',voice = 'ailun',speech_rate=0,pitch_rate=0,aformat='wav'):
        pass
    def start(self,text,ofile):
        pass

# 阿里云的TTS引擎
class Aliyun_TTS_engine(TTS_engine):
    # Keys
    AKID = 'Your_AccessKey'
    AKKEY = 'Your_AccessKey_Secret'
    APPKEY = 'Your_Appkey'
    # 服务的URL
    URL="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1"
    # 音源表
    voice_list = voice_lib[voice_lib['service'] == 'Aliyun'].index
    def __init__(self,name='unnamed',voice = 'ailun',speech_rate=0,pitch_rate=0,aformat='wav'):
        if 'nls' not in sys.modules: # 兼容没有安装nls的使用 
            global nls
            import nls
        self.ID = name
        self.voice = voice
        self.aformat = aformat
        self.speech_rate = speech_rate
        self.pitch_rate = pitch_rate
        # 音量值如果是np.int64的话，无法导入json
        self.volume = int(voice_lib.loc[self.voice,'avaliable_volume'])
        self.synthesizer = nls.NlsSpeechSynthesizer(
                    url=Aliyun_TTS_engine.URL,
                    akid=Aliyun_TTS_engine.AKID, # BUG in aliyun nls SDK v1.0.0，ak和aks不再是这个类的初始化参数，将仅支持token
                    aksecret=Aliyun_TTS_engine.AKKEY,
                    appkey=Aliyun_TTS_engine.APPKEY,
                    on_data=self.on_data,
                    on_close=self.on_close,
                    callback_args=[self.ID,self.voice]
                )
    def start(self,text,ofile):
        self.ofile = open(ofile,'wb')
        success = self.synthesizer.start(text = text,
                                         voice=self.voice,aformat=self.aformat,
                                         speech_rate=self.speech_rate,
                                         pitch_rate=self.pitch_rate,
                                         volume=self.volume)
        # 检查是否是空文件 通常是由于AppKey错误导致的，或者输入为空
        # 若没有发言内容，阿里云也会生成一个44字节的空文件！
        if os.path.getsize(ofile) <= 128:
            # 删除文件
            # os.remove(ofile)
            raise SynthesisError('AliEmpty')
        # 检查合成返回值是否成功
        elif success == False:
            # os.remove(ofile)
            raise SynthesisError('AliOther')
        else:
            if len(text) >= 5:
                print_text = text[0:5]+'...'
            else:
                print_text = text
            print("[{0}({1})]: {2} -> '{3}'".format(self.ID,self.voice,print_text,ofile))            
    def on_close(self, *args):
        #print("on_close: args=>{}".format(args))
        try:
            self.ofile.close()
        except Exception as E:
            print(SynthesisError('AliClose',E))
    def on_data(self, data, *args):
        try:
            self.ofile.write(data)
        except Exception as E:
            # [AliyunError]: Write data failed: write to closed file 如果出现这个问题，会重复很多次，然后合成一个错误的文件
            print(SynthesisError('AliWrite',E))

# Azure 语音合成 alpha 1.10.3
class Azure_TTS_engine(TTS_engine):
    # Key
    AZUKEY = 'Your_Azurekey'
    service_region = 'eastasia'
    # 音源表
    voice_list = voice_lib[voice_lib['service'] == 'Azure'].index
    # SSML模板
    SSML_tplt = open('./xml_templates/tplt_ssml.xml','r').read()
    # 输出文件格式配置
    output_format = {'mp3':23,# SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3
                     'wav':21}# SpeechSynthesisOutputFormat.Riff48Khz16BitMonoPcm
    # 类方法：裁剪音频前后的空白
    def silence_slicer(ifile):
        input_au = pydub.AudioSegment.from_wav(ifile)
        # 将音频转化为array，并取绝对值
        input_au_array = np.abs(np.asarray(input_au.get_array_of_samples()))
        # 计算窗口大小，一个窗口是0.1s
        windows = input_au.frame_rate // 10
        n_windows = int(input_au.frame_count()//windows+1)
        # 是否是静音的
        is_silence = np.zeros(n_windows,dtype=bool)
        # 检定是否是静音的windows，阈值是20
        threshold = 20
        for i in range(0,n_windows):
            if input_au_array[i*windows:(i+1)*windows].mean() > threshold:
                is_silence[i] = True
        # 定位第一个和最后一个非静音windows
        first_true_index = 0
        last_true_index = 0
        for index,value in enumerate(is_silence):
            if value == True:
                last_true_index = index
                if first_true_index == 0:
                    first_true_index = index
        # 裁剪音频
        # |0|1|2|3|...|98|99|100|
        # |F|F|F|T|...|T |T |F  |
        #   first^    last^
        # 3*windows   (99+1)*windows
        sliced = input_au.get_sample_slice(start_sample=first_true_index*windows,end_sample=(last_true_index+1)*windows)
        # 覆盖文件
        if sliced.frame_count() < input_au.frame_count():
            try:
                sliced.export(ifile,format='wav')
                return sliced.frame_count()
            except Exception as E:
                print(WarningPrint('BadClip',ifile,E))
                return -1
    def clean_ts_azure(text): # SSML的转义字符
        return text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace("'",'&apos;')
    # 初始化
    def __init__(self,name='unnamed',voice = 'zh-CN-XiaomoNeural:general:1:Default',speech_rate=0,pitch_rate=0,aformat='wav'):
        if 'azure.cognitiveservices.speech' not in sys.modules:
            global speechsdk
            import azure.cognitiveservices.speech as speechsdk
        self.ID = name
        self.aformat = Azure_TTS_engine.output_format[aformat]
        # 500 - 2; -500 - 0.5
        self.speech_rate = str(speech_rate//5)+'%'
        # 500 - 12st; -500 - -12st
        self.pitch_rate = str(pitch_rate//10)+'%'
        # voice = speaker_style_degreee_role
        if ':' in voice:
            try:
                self.voice,self.style,self.degree,self.role = voice.split(':')
            except Exception:
                raise SynthesisError('AzuInvArg',voice)
        else:
            self.voice = voice
            self.style = 'general'
            self.degree = '1'
            self.role = 'Default'
        if self.voice in Azure_TTS_engine.voice_list: # 如果是表内提供的音源名
            self.volume = voice_lib.loc[self.voice,'avaliable_volume']
        else:
            self.volume = 100 # 音量的默认值
        self.ssml = Azure_TTS_engine.SSML_tplt.format(lang='zh-CN',voice_name=self.voice,
                                     style=self.style,degree=self.degree,role=self.role,
                                     pitch=self.pitch_rate,rate=self.speech_rate,volume=self.volume,
                                     speech_text="{text}")
    def start(self,text,ofile):
        # 准备配置
        speech_config = speechsdk.SpeechConfig(subscription=Azure_TTS_engine.AZUKEY, region=Azure_TTS_engine.service_region)
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat(self.aformat))
        audio_config = speechsdk.audio.AudioOutputConfig(filename=ofile)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        # 开始合成
        speech_synthesis_result = synthesizer.speak_ssml_async(self.ssml.format(text=Azure_TTS_engine.clean_ts_azure(text))).get()
        # 检查结果
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # 先裁剪掉前后的静音部分
            Azure_TTS_engine.silence_slicer(ofile)
            if len(text) >= 5:
                print_text = text[0:5]+'...'
            else:
                print_text = text
            print("[{0}({1})]: {2} -> '{3}'".format(self.ID,self.voice,print_text,ofile))
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print(SynthesisError('AzuErrRetu',cancellation_details.error_details))
            # 删除文件
            # os.remove(ofile)
            raise SynthesisError('AzuErrRetu',cancellation_details.reason)

# 节奏音 alpha 1.22
class Beats_engine(TTS_engine):
    voice_list = {
        'dadada': './media/beats/da.wav',
        'dududu': './media/beats/dang.wav',
        'kakaka': './media/beats/ka.wav',
        'zizizi': './media/beats/zi.wav',
    }
    def __init__(self,name='unnamed',voice='dadada',aformat='wav',frame_rate:int=30) -> None:
        # 初始化的参数
        self.ID = name
        self.voice = voice
        self.aformat = aformat
        # 项目画面的帧率
        self.frame_rate:int = frame_rate
        # 载入文件
        self.unit:pydub.AudioSegment = pydub.AudioSegment.from_file(self.voice_list[self.voice])
    # 指定一个文字显示效果，重设单位时间
    def tx_method_specify(self, tx_method:dict)->None:
        # 通过文字显示方法，获取单个字的时长
        if tx_method['method'] != 'w2w':
            print('warning')
        if tx_method['method_dur'] == 0:
            print('error')
        # 单位时间，单位为秒
        self.time_unit:float = tx_method['method_dur']/self.frame_rate
    # 开始语音合成
    def start(self,text:str, ofile:str):
        self.ofile = ofile
        # 逐个字遍历text：
        this_Track = pydub.AudioSegment.silent(
            duration=int(len(text)*self.time_unit*1000 + 1), # 持续时间=文本时间+1
            frame_rate=48000
            )
        for idx,word in enumerate(text):
            # 如果是中文、数字、英文，则附加一次单位音频
            if word.isalnum():
                this_Track = this_Track.overlay(
                    seg = self.unit,
                    position = int(idx*self.time_unit*1000)
                )
        # 保存为文件
        if len(text) >= 5:
            print_text = text[0:5]+'...'
        else:
            print_text = text
        print("[{0}({1})]: {2} -> '{3}'".format(self.ID,self.voice,print_text,ofile))            
        this_Track.export(ofile,format='wav')

# 腾讯云的TTS

# 百度的TTS

# 讯飞的TTS

# 标贝的TTS？