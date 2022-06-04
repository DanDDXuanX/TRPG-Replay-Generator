#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.11.8'

# 绝对的全局变量
# 在开源发布的版本中，隐去了各个key

asterisk_line_columns=['asterisk_label','character','speech_text','category','filepath']

# 外部参数输入

import argparse
import sys
import os

ap = argparse.ArgumentParser(description="Speech synthesis and preprocessing from you logfile.")
ap.add_argument("-l", "--LogFile", help='The standerd input of this programme, which is mainly composed of TRPG log.',type=str)
ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
ap.add_argument("-t", "--CharacterTable", help='The correspondence between character and media elements, using tab separated text file or Excel table.',type=str)
ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the output audio files.',type=str,default='./output/')

ap.add_argument("-K", "--AccessKey", help='Your AccessKey.',type=str,default="Your_AccessKey")
ap.add_argument("-S", "--AccessKeySecret", help='Your AccessKeySecret.',type=str,default="Your_AccessKey_Secret")
ap.add_argument("-A", "--Appkey", help='Your Appkey.',type=str,default="Your_Appkey")
ap.add_argument("-U", "--Azurekey", help='Your Azure TTS key.',type=str,default="Your_Azurekey")
ap.add_argument("-R", "--ServRegion", help='Service region of Azure.', type=str, default="eastasia")

args = ap.parse_args()

char_tab = args.CharacterTable #角色和媒体对象的对应关系文件的路径
stdin_log = args.LogFile #log路径
output_path = args.OutputPath #保存的时间轴，断点文件的目录
media_obj = args.MediaObjDefine #媒体对象定义文件的路径

try:
    for path in [stdin_log,char_tab,media_obj]:
        if path == None:
            raise OSError("[31m[ArgumentError]:[0m Missing principal input argument!")
        if os.path.isfile(path) == False:
            raise OSError("[31m[ArgumentError]:[0m Cannot find file "+path)

    if output_path == None:
        raise OSError("[31m[ArgumentError]:[0m No output path is specified!")
    elif os.path.isdir(output_path) == False:
        try:
            os.makedirs(output_path)
        except Exception:
            raise OSError("[31m[SystemError]:[0m Cannot make directory "+output_path)
    else:
        pass
    output_path = output_path.replace('\\','/')
    
except Exception as E:
    print(E)
    sys.exit(1)

# 包导入

import pandas as pd
import numpy as np
from pygame import mixer
import re

# 类定义

#阿里云和Azure支持的所有voice名
voice_lib = pd.read_csv('./media/voice_volume.tsv',sep='\t').set_index('Voice')

# 阿里云的TTS引擎
class Aliyun_TTS_engine:
    # Keys
    AKID = args.AccessKey
    AKKEY = args.AccessKeySecret
    APPKEY = args.Appkey
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
        # 检查是否是空文件 通常是由于AppKey错误导致的
        if os.path.getsize(ofile) == 0:
            raise Exception('[33m[AliyunError]:[0m Synthesis failed, an empty wav file is created!')
            # os.remove(ofile) # 算了算了 0kb 也留着吧
        # 检查合成返回值是否成功
        elif success == False:
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
            print("[33m[AliyunError]:[0m Write data failed:", E)

# Azure 语音合成 alpha 1.10.3
class Azure_TTS_engine:
    # Key
    AZUKEY = args.Azurekey
    service_region = args.ServRegion
    # 音源表
    voice_list = voice_lib[voice_lib['service'] == 'Azure'].index
    # SSML模板
    SSML_tplt = open('./xml_templates/tplt_ssml.xml','r').read()
    def __init__(self,name='unnamed',voice = 'zh-CN-XiaomoNeural:general:1:Default',speech_rate=0,pitch_rate=0,aformat='wav'):
        if 'azure.cognitiveservices.speech' not in sys.modules:
            global speechsdk
            import azure.cognitiveservices.speech as speechsdk
        self.ID = name
        self.aformat = aformat
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
        audio_config = speechsdk.audio.AudioOutputConfig(filename=ofile)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        # 开始合成
        speech_synthesis_result = synthesizer.speak_ssml_async(self.ssml.format(text=clean_ts_azure(text))).get()
        # 检查结果
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
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
            # os.remove(ofile) # 算了算了 0kb 也留着吧
            raise Exception("[33m[AzureError]:[0m {}".format(cancellation_details.reason))


# 正则表达式定义

RE_dialogue = re.compile('^\[([\ \w\.\;\(\)\,]+)\](<[\w\=\d]+>)?:(.+?)(<[\w\=\d]+>)?({.+})?$')
RE_characor = re.compile('([\ \w]+)(\(\d*\))?(\.\w+)?')
RE_asterisk = re.compile('(\{([^\{\}]*?[;])?\*([\w\ \.\,，。：？！“”]*)?\})') # v 1.11.4 音频框分隔符只能用; *后指定可以有空格

media_list=[]

occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n')

# 函数定义

# 解析对话行 []
def get_dialogue_arg(text):
    cr,cre,ts,tse,se = RE_dialogue.findall(text)[0]
    this_charactor = RE_characor.findall(cr)
    # 语音和音效参数
    if se == '':
        asterisk_label = []
    else:
        asterisk_label = RE_asterisk.findall(se)

    return (this_charactor,ts,asterisk_label)

def isnumber(str):
    try:
        float(str)
        return True
    except Exception:
        return False
    
# 清理ts文本中的标记符号
def clean_ts(text):
    return text.replace('^','').replace('#','')

def clean_ts_azure(text): # SSML的转义字符
    return text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace("'",'&apos;')

# 解析函数
def parser(stdin_text):
    asterisk_line = pd.DataFrame(index=range(0,len(stdin_text)),columns=asterisk_line_columns)
    for i,text in enumerate(stdin_text):
        # 空白行
        if text == '':
            continue
        # 注释行 格式： # word
        elif text[0] == '#':
            continue
        # 对话行 格式： [角色1,角色2(30).happy]<replace=30>:巴拉#巴拉#巴拉<w2w=1>{*}
        elif text[0] == '[':
            try:
                # 读取角色、文本、音频信息
                this_charactor,ts,asterisk_label = get_dialogue_arg(text)
                if len(asterisk_label) == 0:
                    continue
                elif len(asterisk_label) == 1:
                    K0,K1,K2 = asterisk_label[0]
                    asterisk_line.loc[i,'asterisk_label'] = K0
                    #1.{*}
                    if K0 == '{*}':
                        asterisk_line.loc[i,'category'] = 1
                        asterisk_line.loc[i,'speech_text'] = clean_ts(ts) #need clean!
                        asterisk_line.loc[i,'filepath'] = 'None'
                    #2.{*生成这里面的文本，我在添加一点标点符号}
                    elif (K1=='')&(K2!=''):
                        asterisk_line.loc[i,'category'] = 2
                        asterisk_line.loc[i,'speech_text'] = K2
                        asterisk_line.loc[i,'filepath'] = 'None'
                    #3.{"./timeline.mp3",*}
                    elif (os.path.isfile(K1[1:-2])==True)&(K2==''):
                        asterisk_line.loc[i,'category'] = 3
                        asterisk_line.loc[i,'speech_text'] = 'None'
                        asterisk_line.loc[i,'filepath'] = K1[1:-2]
                    #4.{"./timeline.mp3",*30}|{NA,*30}
                    elif ((os.path.isfile(K1[1:-2])==True)|(K1[:-1]=='NA'))&(isnumber(K2)==True): # a 1.9.6
                        asterisk_line.loc[i,'category'] = 4
                        asterisk_line.loc[i,'speech_text'] = 'None'
                        asterisk_line.loc[i,'filepath'] = K1[1:-2]
                    #4.{SE1,*} 始终无视这种标记
                    elif K1[0:-1] in media_list:
                        asterisk_line.loc[i,'category'] = 4
                        asterisk_line.loc[i,'speech_text'] = 'None'
                        asterisk_line.loc[i,'filepath'] = K1[0:-1]
                        print('[33m[warning]:[0m A defined object',K1[0:-1],'is specified, which will not be processed.')
                    elif (os.path.isfile(K1[1:-2])==False): #3&4.指定了不存在的文件路径
                        raise OSError('[31m[ParserError]:[0m Asterisk SE file '+K1[0:-1]+' is not exist.')
                    else: # 其他的不合规的星标文本
                        raise ValueError('[31m[ParserError]:[0m Invalid asterisk lable appeared in dialogue line.')
                    
                else:
                    raise ValueError('[31m[ParserError]:[0m Too much asterisk time labels are set in dialogue line.')
                name,alpha,subtype= this_charactor[0]
                if subtype == '':
                    subtype = '.default'
                asterisk_line.loc[i,'character'] = name+subtype
            except Exception as E:
                print(E)
                raise ValueError('[31m[ParserError]:[0m Parse exception occurred in dialogue line ' + str(i+1)+'.')
        else:
            pass
    return asterisk_line.dropna()

# 音频合成函数
def synthesizer(key,asterisk):
    #读取Voice信息
    if asterisk['category'] > 2: #如果解析结果为3&4，不执行语音合成
        return 'Keep',False
    elif asterisk['character'] not in charactor_table.index: #指定了未定义的发言角色
        print('[33m[warning]:[0m Undefine charactor!')
        return 'None',False
    else:
        charactor_info = charactor_table.loc[asterisk['character']]
    if charactor_info['TTS'] == 'None': #如果这个角色本身就不带有发言
        print('[33m[warning]:[0m No voice is specified for ',asterisk['character'])
        return 'None',False
    else:
        ofile = output_path+'/'+'auto_AU_%d'%key+'.wav'
        try:
            charactor_info['TTS'].start(asterisk['speech_text'],ofile) #执行合成
            #print(asterisk['speech_text'],ofile)
        except Exception as E:
            print('[33m[warning]:[0m Synthesis failed in line '+'%d'%(key+1),'due to:',E)
            return 'None',False
        return ofile,True

# 获取语音长度
def get_audio_length(asterisk):
    if asterisk.category>3:
        return np.nan
    else:
        mixer.init()
        try:
            this_audio = mixer.Sound(asterisk.filepath)
        except Exception as E:
            print('[33m[warning]:[0m Unable to get audio length of '+str(asterisk.filepath)+', due to:',E)
            return np.nan
        return this_audio.get_length()

def main():
    global charactor_table
    global media_list

    print('[speech synthesizer]: Welcome to use speech_synthesizer for TRPG-replay-generator '+edtion)
    print('[speech synthesizer]: The processed Logfile and audio file will be saved at "'+output_path+'"')
    # 载入ct文件
    try:
        if char_tab.split('.')[-1] in ['xlsx','xls']:
            charactor_table = pd.read_excel(char_tab,dtype = str) # 支持excel格式的角色配置表
        else:
            charactor_table = pd.read_csv(char_tab,sep='\t',dtype = str)
        charactor_table.index = charactor_table['Name']+'.'+charactor_table['Subtype']
        if 'Voice' not in charactor_table.columns:
            print('[33m[warning]:[0m','Missing \'Voice\' columns.')
    except Exception as E:
        print('[31m[SyntaxError]:[0m Unable to load charactor table:',E)
        sys.exit(1)

    # 填补缺省值
    if 'Voice' not in charactor_table.columns:
        charactor_table['Voice'] = 'NA'
    else:
        charactor_table['Voice'] = charactor_table['Voice'].fillna('NA')
    if 'SpeechRate' not in charactor_table.columns:
        charactor_table['SpeechRate'] = 0
    else:
        charactor_table['SpeechRate'] = charactor_table['SpeechRate'].fillna(0).astype(int)
    if 'PitchRate' not in charactor_table.columns:
        charactor_table['PitchRate'] = 0
    else:
        charactor_table['PitchRate'] = charactor_table['PitchRate'].fillna(0).astype(int)

    # 建立TTS_engine的代码
    TTS = pd.Series(index=charactor_table.index,dtype='str')
    TTS_define_tplt = "Aliyun_TTS_engine(name='{0}',voice='{1}',speech_rate={2},pitch_rate={3})"
    AZU_define_tplt = "Azure_TTS_engine(name='{0}',voice='{1}',speech_rate={2},pitch_rate={3})"
    for key,value in charactor_table.iterrows():
        if (value.Voice != value.Voice)|(value.Voice=="NA"): # 如果音源是NA,就pass alpha1.6.3
            TTS[key] = '"None"'
        elif value.Voice in Aliyun_TTS_engine.voice_list: # 阿里云模式
            TTS[key] = TTS_define_tplt.format(key,value.Voice,value.SpeechRate,value.PitchRate)
        elif value.Voice[0:7] == 'Azure::': # Azure 模式 alpha 1.10.3
            TTS[key] = AZU_define_tplt.format(key,value.Voice[7:],value.SpeechRate,value.PitchRate)
        else:
            print('[33m[warning]:[0m Unsupported speaker name "{0}".'.format(value.Voice))
            TTS[key] = '"None"'
    # 应用并保存在charactor_table内
    try:
        charactor_table['TTS'] = TTS.map(lambda x:eval(x))
    except ModuleNotFoundError as E:
        print('[31m[ImportError]:[0m ',E,' .Execution terminated!')
        sys.exit(1)
    except ValueError as E: # 非法音源名
        print(E)
        sys.exit(1)

    # 载入od文件
    try:
        object_define_text = open(media_obj,'r',encoding='utf-8').read()#.split('\n')
    except UnicodeDecodeError as E:
        print('[31m[DecodeError]:[0m',E)
        sys.exit(1)
    if object_define_text[0] == '\ufeff': # UTF-8 BOM
        print('[33m[warning]:[0m','UTF8 BOM recognized in MediaDef, it will be drop from the begin of file!')
        object_define_text = object_define_text[1:]
    object_define_text = object_define_text.split('\n')
    
    for i,text in enumerate(object_define_text):
        if text == '':
            continue
        elif text[0] == '#':
            continue
        else:
            try:
                obj_name = text.split('=')[0]
                obj_name = obj_name.replace(' ','')
                if obj_name in occupied_variable_name:
                    raise SyntaxError('Obj name occupied')
                elif (len(re.findall('\w+',obj_name))==0)|(obj_name[0].isdigit()):
                    raise SyntaxError('Invalid Obj name')
                media_list.append(obj_name) #记录新增对象名称
            except Exception as E:
                print('[31m[SyntaxError]:[0m "'+text+'" appeared in media define file line ' + str(i+1)+':',E)
                sys.exit(1)

    # 载入log文件
    try:
        stdin_text = open(stdin_log,'r',encoding='utf8').read()#.split('\n')
    except UnicodeDecodeError as E:
        print('[31m[DecodeError]:[0m',E)
        sys.exit(1)
    if stdin_text[0] == '\ufeff': # 139 debug
        print('[33m[warning]:[0m','UTF8 BOM recognized in Logfile, it will be drop from the begin of file!')
        stdin_text = stdin_text[1:]
    stdin_text = stdin_text.split('\n')
    try:
        asterisk_line = parser(stdin_text)
    except Exception as E:
        print(E)
        sys.exit(1)

    asterisk_line['synth_status'] = False #v1.6.1 初始值，以免生成refresh的时候报错！

    # 开始合成
    print('[speech synthesizer]: Begin to speech synthesis!')
    for key,value in asterisk_line.iterrows():
        # 进行合成
        ofile_path,synth_status = synthesizer(key,value)
        if ofile_path == 'Keep':
            pass
        elif ofile_path == 'None':
            asterisk_line.loc[key,'filepath'] = synth_status
        elif os.path.isfile(ofile_path)==False:
            asterisk_line.loc[key,'filepath'] = 'None'
        else:
            asterisk_line.loc[key,'filepath'] = ofile_path
        asterisk_line.loc[key,'synth_status'] = synth_status

    # 仅category 3,或者成功合成的1，2去更新标记
    refresh = asterisk_line[(asterisk_line.category==3)|(asterisk_line.synth_status==True)].dropna().copy() #检定是否成功合成

    if len(refresh.index) == 0: #如果未合成任何语音
        print('[33m[warning]:[0m','No vaild asterisk label synthesised, execution terminated!')
        sys.exit(1) # alpha 1.11.7 未有合成也异常退出

    # 读取音频时长
    for key,value in refresh.iterrows():
        audio_lenth = get_audio_length(value)
        refresh.loc[key,'audio_lenth'] = audio_lenth

    # 生成新的标签
    new_asterisk_label = "{'"+refresh.filepath + "';*"+refresh.audio_lenth.map(lambda x:'%.3f'%x)+"}"
    refresh['new_asterisk_label'] = new_asterisk_label

    # 替换原来的标签
    for key,value in refresh.iterrows():
        stdin_text[key] = stdin_text[key].replace(value.asterisk_label,value.new_asterisk_label)

    # 输出新的目录
    out_Logfile = open(output_path+'/AsteriskMarkedLogFile.rgl','w',encoding='utf-8')
    out_Logfile.write('\n'.join(stdin_text))
    out_Logfile.close()

    print('[speech synthesizer]: Asterisk Marked Logfile path: '+output_path+'/AsteriskMarkedLogFile.rgl')
    print('[speech synthesizer]: Done!')

if __name__ == '__main__':
    main()
