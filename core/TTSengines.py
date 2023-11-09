#!/usr/bin/env python
# coding: utf-8
# 语音服务类定义

import uuid
import time
import hmac
import wave
import urllib
import hashlib
import base64
import json
import numpy as np
import pandas as pd
import os
import pydub
import nls
import azure.cognitiveservices.speech as speechsdk
import pyttsx3
from websocket import ABNF, WebSocketApp
from .Exceptions import SynthesisError, WarningPrint

voice_lib = pd.read_csv('./assets/voice_volume.tsv',sep='\t').set_index('Voice')

# 没用的基类
class TTS_engine:
    # 调用计数器
    counter = 0
    def __init__(self,name='unnamed',voice = 'ailun',speech_rate=0,pitch_rate=0,aformat='wav'):
        pass
    def start(self,text,ofile):
        pass
    def linear_mapping(self,value):
        if value == 0:
            return 1
        elif value > 0:
            return 1 + value/500
        else:
            return 1 + value/1000
    def print_success(self,text,ofile):
        # 计数器+1
        self.__class__.counter += 1
        if len(text) >= 5:
            print_text = text[0:5]+'...'
        else:
            print_text = text
        print("[{0}({1})]: {2} -> '{3}'".format(self.ID,self.voice,print_text,ofile))

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
        # 检查key状态
        if (
            Aliyun_TTS_engine.AKID == 'Your_AccessKey' or 
            Aliyun_TTS_engine.AKKEY == 'Your_AccessKey_Secret' or 
            Aliyun_TTS_engine.APPKEY == 'Your_Appkey'
        ):
            raise SynthesisError('AliyunKey')
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
            self.print_success(text=text,ofile=ofile)
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
    SSML_tplt = open('./assets/xml_templates/tplt_ssml.xml','r').read()
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
        # 检查key状态
        if Azure_TTS_engine.AZUKEY == 'Your_Azurekey':
            raise SynthesisError('AzureKey')
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
            # 输出成功
            self.print_success(text=text,ofile=ofile)
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
        'dadada': './assets/beats/da.wav',
        'dududu': './assets/beats/dang.wav',
        'kakaka': './assets/beats/ka.wav',
        'zizizi': './assets/beats/zi.wav',
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
        if tx_method['method'] != 'w2w' or tx_method['method_dur'] == 0:
            self.time_unit = 0
        else:
            self.time_unit:float = tx_method['method_dur']/self.frame_rate
    # 开始语音合成
    def start(self,text:str, ofile:str):
        self.ofile = ofile
        # 逐个字遍历text：
        this_Track = pydub.AudioSegment.silent(
            duration=int(len(text)*self.time_unit*1000 + 1), # 持续时间=文本时间+1
            frame_rate=48000
            )
        if self.time_unit != 0:
            for idx,word in enumerate(text):
                # 如果是中文、数字、英文，则附加一次单位音频
                if word.isalnum():
                    this_Track = this_Track.overlay(
                        seg = self.unit,
                        position = int(idx*self.time_unit*1000)
                    )
        # 保存为文件
        self.print_success(text=text,ofile=ofile)
        this_Track.export(ofile,format='wav')

# 腾讯云的TTS
class Tencent_TTS_engine(TTS_engine):
    APPID = 0
    SecretId = 'Your_SecretID'
    SecretKey = 'Your_SecretKey'

    _PROTOCOL = "wss://"
    _HOST = "tts.cloud.tencent.com"
    _PATH = "/stream_ws"
    _ACTION = "TextToStreamAudioWS"

    Status = {
        'NOTOPEN'   : 0,
        'STARTED'   : 1,
        'OPENED'    : 2,
        'FINAL'     : 3,
        'ERROR'     : 4,
        'CLOSED'    : 5,
    }
    voice_list = voice_lib[voice_lib['service'] == 'Tencent'].index
    def __init__(self, name='unnamed', voice='101001', speech_rate=0, pitch_rate=0, aformat='wav'):
        self.ID = name
        self.status = self.Status["NOTOPEN"]
        self.ws = None
        self.voice = voice
        self.aformat = aformat
        self.speed = self.speechrate_formula(speech_rate)
        # 处理
        if self.voice in self.voice_list:
            self.voice_type = int(self.voice)
            self.volume = int(voice_lib.loc[self.voice,'avaliable_volume'])
        else:
            raise SynthesisError('TctInvArg', str(self.voice))
        # self.voice = 101001
        if self.aformat == 'wav':
            self.codec = 'pcm'
        else:
            self.codec = 'mp3'
        # 暂时不兼容情感
        # self.emotion_category = ""
        # self.emotion_intensity = 0
        # 初始化的会话ID
        self.session_id = ""
        # 检查key状态
        if (
            Tencent_TTS_engine.APPID == 0 or 
            Tencent_TTS_engine.SecretId == 'Your_SecretID' or 
            Tencent_TTS_engine.SecretKey == 'Your_SecretKey'
        ):
            raise SynthesisError('TencentKey')
    def speechrate_formula(self, speechrate):
        # value in [-2,4] = 0.25 * value + 1
        return (self.linear_mapping(speechrate) - 1)/0.25
    def __gen_signature(self, params):
        sort_dict = sorted(params.keys())
        sign_str = "GET" + self._HOST + self._PATH + "?"
        for key in sort_dict:
            sign_str = sign_str + key + "=" + str(params[key]) + '&'
        sign_str = sign_str[:-1]
        sign_str = sign_str.encode('utf-8')
        # secret_key = self.credential.secret_key.encode('utf-8')
        hmacstr = hmac.new(self.SecretKey.encode('utf-8'), sign_str, hashlib.sha1).digest()
        s = base64.b64encode(hmacstr)
        s = s.decode('utf-8')
        return s
    def __gen_params(self, text, session_id):
        # 随机生成UID
        self.session_id = session_id
        # 时间戳
        timestamp = int(time.time())

        params = dict()
        params['Action'] = self._ACTION
        params['AppId'] = int(self.APPID)
        params['SecretId'] = self.SecretId
        params['ModelType'] = 1
        params['VoiceType'] = self.voice_type
        params['Codec'] = self.codec
        params['SampleRate'] = 16000
        params['Speed'] = self.speed # [-2，6]
        params['Volume'] = self.volume/10 # [0,10]
        params['SessionId'] = self.session_id
        params['Text'] = text
        params['EnableSubtitle'] = False
        params['Timestamp'] = timestamp
        params['Expired'] = timestamp + 24 * 60 * 60
        # if self.emotion_category != "":
        #     params['EmotionCategory'] = self.emotion_category
        #     if self.emotion_intensity != 0:
        #         params['EmotionIntensity'] = self.emotion_intensity
        return params
    def __create_query_string(self, param):
        param['Text'] = urllib.parse.quote(param['Text'])
        param = sorted(param.items(), key=lambda d: d[0])

        url = self._PROTOCOL + self._HOST + self._PATH
        signstr = url + "?"
        for x in param:
            tmp = x
            for t in tmp:
                signstr += str(t)
                signstr += "="
            signstr = signstr[:-1]
            signstr += "&"
        signstr = signstr[:-1]
        return signstr
    def start(self, text, ofile):
        # 结果对象
        self.audio_data = bytes()
        self.message = []
        # Websockets 的回调函数
        def _close_conn(reason):
            self.ws.close()
        def _on_data(ws, data, opcode, flag):
            # logger.info("data={} opcode={} flag={}".format(data, opcode, flag))
            # 接收到音频
            if opcode == ABNF.OPCODE_BINARY:
                self.audio_data += data
            # 接收到文字
            elif opcode == ABNF.OPCODE_TEXT:
                resp = json.loads(data) # WSResponseMessage
                # 错误
                if resp['code'] != 0:
                    self.status = self.Status['ERROR']
                    self.message.append(
                        "[E{}]:{}".format(resp['code'], resp['message'])
                        )
                # 终结
                if "final" in resp and resp['final'] == 1:
                    # logger.info("recv FINAL frame")
                    _close_conn("after recv final")
                    # 保存文件
                    if self.aformat == "wav":
                        wav_fp = wave.open(ofile, "wb")
                        wav_fp.setnchannels(1)
                        wav_fp.setsampwidth(2)
                        wav_fp.setframerate(16000)
                        wav_fp.writeframes(self.audio_data)
                        wav_fp.close()
                    elif self.aformat == "mp3":
                        fp = open(ofile, "wb")
                        fp.write(self.audio_data)
                        fp.close()
                    # 更新状态
                    self.status = self.Status['FINAL']
                    return
                # 字幕
                if "result" in resp:
                    if "subtitles" in resp["result"] and resp["result"]["subtitles"] is not None:
                        # self.listener.on_text_result(resp) # 如果有字幕，暂时不处理这个情况
                        pass
                    return
            # 异常的情况，略过
            else:
                pass
        def _on_error(ws, error):
            if self.status == self.Status['FINAL'] or self.status == self.Status['CLOSED']:
                return
            self.status = self.Status['ERROR']
            self.message.append("[ERROR]:{}".format(error))
            _close_conn("after recv error")
        def _on_close(ws, close_status_code, close_msg):
            self.status = self.Status['CLOSED']
        def _on_open(ws):
            self.status = self.Status['OPENED']
        # 主要逻辑
        session_id = str(uuid.uuid1())
        params = self.__gen_params(text=text, session_id=session_id)
        signature = self.__gen_signature(params)
        requrl = self.__create_query_string(params)

        autho = urllib.parse.quote(signature)
        requrl += "&Signature=%s" % autho
        # WebSocket
        self.ws = WebSocketApp(
            url = requrl, 
            header = None,
            on_error=_on_error, 
            on_close=_on_close,
            on_data=_on_data
        )
        self.ws.on_open = _on_open
        # 开始执行（不采用多线程）
        self.status = self.Status['STARTED']
        self.ws.run_forever()
        # 根据Status，获取返回值
        if self.status == 3: # FINAL
            self.print_success(text=text,ofile=ofile)
        elif self.status == 5: # ERROR
            raise SynthesisError('TctErrRetu', '; '.join(self.message))
        else:
            raise SynthesisError('TctUknErr', self.status)

# 百度的TTS

# 讯飞的TTS

# 系统的TTS
class System_TTS_engine(TTS_engine):
    # 初始化的参数
    def __init__(self, name='unnamed', voice=None, speech_rate=0, pitch_rate=0, aformat='wav'):
        self.ID = name
        self.voice = voice
        self.aformat = aformat
        self.speech_rate = speech_rate
        try:
            # 合成器
            self.synthesizer = pyttsx3.init()
            # 获取可用音源名
            self.get_available()
            # 应用参数
            try:
                if voice:
                    self.synthesizer.setProperty('voice', self.voice_list[self.voice])
                self.synthesizer.setProperty('rate', int(self.linear_mapping(self.speech_rate)*200))
            except KeyError:
                raise SynthesisError('SysInvArg',self.voice)
        except ValueError:
            self.synthesizer = None
    # 获取可用语音列表
    def get_available(self):
        self.voice_list = {}
        if self.synthesizer:
            for voice in self.synthesizer.getProperty('voices'):
                self.voice_list[voice.name] = voice.id
        return self.voice_list
    # 开始
    def start(self, text, ofile):
        if self.synthesizer:
            self.synthesizer.save_to_file(text, ofile)
            try:
                self.synthesizer.runAndWait()
            except Exception as E:
                SynthesisError('SysFailed',E)
            if not os.path.isfile(ofile):
                SynthesisError('SysFailed','No file saved!')
            # 输出显示
            self.print_success(text=text,ofile=ofile)
        else:
            raise SynthesisError('SysUnaval')