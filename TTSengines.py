#!/usr/bin/env python
# coding: utf-8
# 语音服务类定义

import numpy as np
import pandas as pd
import sys
import os
import pydub

voice_lib = pd.read_csv('./media/voice_volume.tsv',sep='\t').set_index('Voice')

# 阿里云的TTS引擎
class Aliyun_TTS_engine:
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
                    akid=Aliyun_TTS_engine.AKID,
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
            raise Exception('[33m[AliyunError]:[0m Synthesis failed, an empty wav file is created!')
        # 检查合成返回值是否成功
        elif success == False:
            # os.remove(ofile)
            raise Exception('[33m[AliyunError]:[0m Other exception occurred!')
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
            print("[33m[AliyunError]:[0m Close file failed since:", E)
    def on_data(self, data, *args):
        try:
            self.ofile.write(data)
        except Exception as E:
            # [AliyunError]: Write data failed: write to closed file 如果出现这个问题，会重复很多次，然后合成一个错误的文件
            print("[33m[AliyunError]:[0m Write data failed:", E)

# Azure 语音合成 alpha 1.10.3
class Azure_TTS_engine:
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
                print('[33m[warning]:[0m Unable to clip the silence part from \"'+ ifile +'\", due to:',E)
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
                raise ValueError('[31m[AzureError]:[0m Invalid Voice argument: '+voice)
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
                    print("[33m[AzureError]:[0m {}".format(cancellation_details.error_details))
            # 删除文件
            # os.remove(ofile)
            raise Exception("[33m[AzureError]:[0m {}".format(cancellation_details.reason))
