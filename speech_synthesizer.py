#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.7.3'

# 绝对的全局变量
# 在开源发布的版本中，隐去了各个key
URL="wss://nls-gateway.cn-shanghai.aliyuncs.com/ws/v1"

asterisk_line_columns=['asterisk_label','character','speech_text','category','filepath']

# 外部参数输入

import argparse
import sys
import os
import warnings

ap = argparse.ArgumentParser(description="Speech synthesis and preprocessing from you logfile.")
ap.add_argument("-l", "--LogFile", help='The standerd input of this programme, which is mainly composed of TRPG log.',type=str)
ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
ap.add_argument("-t", "--CharacterTable", help='The correspondence between character and media elements, using tab separated text file or Excel table.',type=str)
ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the output audio files.',type=str,default='./output/')

ap.add_argument("-K", "--AccessKey", help='Your AccessKey.',type=str,default="Your_AccessKey")
ap.add_argument("-S", "--AccessKeySecret", help='Your AccessKeySecret.',type=str,default="Your_AccessKey_Secret")
ap.add_argument("-A", "--Appkey", help='Your Appkey.',type=str,default="Your_Appkey")

args = ap.parse_args()

char_tab = args.CharacterTable #角色和媒体对象的对应关系文件的路径
stdin_log = args.LogFile #log路径
output_path = args.OutputPath #保存的时间轴，断点文件的目录
media_obj = args.MediaObjDefine #媒体对象定义文件的路径

# key 在这里输入了

AKID = args.AccessKey
AKKEY = args.AccessKeySecret
APPKEY = args.Appkey

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
        except:
            raise OSError("[31m[SystemError]:[0m Cannot make directory "+output_path)
    else:
        pass
    output_path = output_path.replace('\\','/')
    
except Exception as E:
    print(E)
    sys.exit()

# 包导入

import pandas as pd
import numpy as np
from pygame import mixer
import re

# 类定义

# 阿里云的TTS引擎
class TTS_engine:
    def __init__(self,name='unnamed',voice = 'ailun',speech_rate=0,pitch_rate=0,volume=50,aformat='wav'):
        if 'nls' not in sys.modules: # 兼容没有安装nls的使用 
            global nls
            import nls
        self.ID = name
        self.voice = voice
        self.aformat = aformat
        self.speech_rate = speech_rate
        self.pitch_rate = pitch_rate
        self.synthesizer = nls.NlsSpeechSynthesizer(
                    url=URL,
                    akid=AKID,
                    aksecret=AKKEY,
                    appkey=APPKEY,
                    on_data=self.on_data,
                    on_close=self.on_close,
                    callback_args=[self.ID,self.voice]
                )
    def start(self,text,ofile):
        self.ofile = open(ofile,'wb')
        self.synthesizer.start(text = text,
                               voice=self.voice,aformat=self.aformat,
                               speech_rate=self.speech_rate,
                               pitch_rate=self.pitch_rate)
        if len(text) >= 5:
            print_text = text[0:5]+'...'
        else:
            print_text = text
        print("[{0}({1})]:{2} -> '{3}'".format(self.ID,self.voice,print_text,ofile))
    def on_close(self, *args):
        #print("on_close: args=>{}".format(args))
        try:
            self.ofile.close()
        except Exception as E:
            print("[31m[TTSError]:[0m Close file failed since:", E)
    def on_data(self, data, *args):
        try:
            self.ofile.write(data)
        except Exception as E:
            print("[31m[TTSError]:[0m Write data failed:", E)

#阿里云支持的所有voice名

aliyun_voice_lib = [
    'xiaoyun','xiaogang','ruoxi','siqi','sijia','sicheng','aiqi','aijia','aicheng',
    'aida','ninger','ruilin','siyue','aiya','aixia','aimei','aiyu','aiyue','aijing',
    'xiaomei','aina','yina','sijing','sitong','xiaobei','aitong','aiwei','aibao',
    'harry','abby','andy','eric','emily','luna','luca','wendy','william','olivia',
    'shanshan','chuangirl','lydia','aishuo','qingqing','cuijie','xiaoze','tomoka',
    'tomoya','annie','jiajia','indah','taozi','guijie','stella','stanley','kenny',
    'rosa','farah','mashu','xiaoxian','yuer','maoxiaomei','aifei','yaqun','qiaowei',
    'dahu','ava','ailun','jielidou','laotie','laomei','aikan','tala','annie_saodubi',
    'zhitian','zhiqing']

# 正则表达式定义

RE_dialogue = re.compile('^\[([\w\.\;\(\)\,]+)\](<[\w\=\d]+>)?:(.+?)(<[\w\=\d]+>)?({.+})?$')
RE_characor = re.compile('(\w+)(\(\d*\))?(\.\w+)?')
RE_asterisk = re.compile('(\{([^\{\}]*?[,;])?\*([\w\.\,，]*)?\})')

media_list=[]

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
    except:
        return False
    
# 清理ts文本中的标记符号
def clean_ts(text):
    return text.replace('^','').replace('#','。')

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
                    #4.{"./timeline.mp3",*30}
                    elif (os.path.isfile(K1[1:-2])==True)&(isnumber(K2)==True):
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
    TTS_define_tplt = "TTS_engine(name='{0}',voice = '{1}',speech_rate={2},pitch_rate={3},volume=50)"
    for key,value in charactor_table.iterrows():
        if (value.Voice != value.Voice)|(value.Voice=="NA"): # 如果音源是NA,就pass alpha1.6.3
            TTS[key] = '"None"'
        elif value.Voice not in aliyun_voice_lib:
            print('[33m[warning]:[0m Unsupported speaker name "{0}".'.format(value.Voice))
            TTS[key] = '"None"'
        else:
            TTS[key] = TTS_define_tplt.format(key,value.Voice,value.SpeechRate,value.PitchRate)
    # 应用并保存在charactor_table内
    try:
        charactor_table['TTS'] = TTS.map(lambda x:eval(x))
    except ModuleNotFoundError as E:
        print('[31m[ImportError]:[0m ',E,'check https://help.aliyun.com/document_detail/374323.html. Execution terminated!')
        sys.exit()

    # 载入od文件
    object_define_text = open(media_obj,'r',encoding='utf-8').read().split('\n')
    
    for i,text in enumerate(object_define_text):
        if text == '':
            continue
        elif text[0] == '#':
            continue
        else:
            try:
                obj_name = text.split('=')[0]
                obj_name = obj_name.replace(' ','')
                media_list.append(obj_name) #记录新增对象名称
            except:
                print('[31m[SyntaxError]:[0m "'+text+'" appeared in media define file line ' + str(i+1)+'.')
                sys.exit()

    # 载入log文件
    stdin_text = open(stdin_log,'r',encoding='utf8').read().split('\n')
    try:
        asterisk_line = parser(stdin_text)
    except Exception as E:
        print(E)
        sys.exit()

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
        sys.exit()

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
    out_Logfile = open(output_path+'/AsteriskMarkedLogFile.txt','w',encoding='utf-8')
    out_Logfile.write('\n'.join(stdin_text))
    out_Logfile.close()

    print('[speech synthesizer]: Done!')

if __name__ == '__main__':
    main()
