#!/usr/bin/env python
# coding: utf-8
from Utils import EDITION

# 在开源发布的版本中，隐去了各个key

# 语音合成模块的退出代码：
# 0. 有覆盖原log，合成正常，可以继续执行主程序
# 1. 无覆盖原log，无需合成，可以继续执行主程序
# 2. 无覆盖原log，合成未完成，不能继续执行主程序
# 3. 有覆盖原log，合成未完成，不能继续执行主程序

# 外部参数输入

import argparse
import sys
import os
from Exceptions import IgnoreInput, MediaError

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

ap.add_argument('--PreviewOnly',help='Ignore the input files, and open a speech preview gui windows.',action='store_true')
ap.add_argument('--Init',help='The initial speech service in preview.',type=str,default='Aliyun')
args = ap.parse_args()

try:
    if args.PreviewOnly == 1:
        # 如果选择仅预览，则忽略输入文件！
        if args.Init in ['Aliyun','Azure']:
            raise IgnoreInput('[speech synthesizer]: Preview Only!')
        else:
            raise ValueError("\x1B[31m[ArgumentError]:\x1B[0m Invalid initial status: "+args.Init)
    for path in [args.LogFile,args.CharacterTable,args.MediaObjDefine]:
        if path is None:
            raise OSError("\x1B[31m[ArgumentError]:\x1B[0m Missing principal input argument!")
        if os.path.isfile(path) == False:
            raise OSError("\x1B[31m[ArgumentError]:\x1B[0m Cannot find file "+path)

    if args.OutputPath is None:
        raise OSError("\x1B[31m[ArgumentError]:\x1B[0m No output path is specified!")
    elif os.path.isdir(args.OutputPath) == False:
        try:
            os.makedirs(args.OutputPath)
        except Exception:
            raise OSError("\x1B[31m[SystemError]:\x1B[0m Cannot make directory "+args.OutputPath)
    else:
        pass
    args.OutputPath = args.OutputPath.replace('\\','/')
except IgnoreInput as E:
    print(E)
except Exception as E:
    print(E)
    sys.exit(2) # 缺少必要文件路径，异常退出

# 包导入

import pandas as pd
import numpy as np
from pygame import mixer
import re
from shutil import copy
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

# 语音合成服务
from TTSengines import Aliyun_TTS_engine,Azure_TTS_engine,voice_lib

Aliyun_TTS_engine.AKID = args.AccessKey
Aliyun_TTS_engine.AKKEY = args.AccessKeySecret
Aliyun_TTS_engine.APPKEY = args.Appkey
Azure_TTS_engine.AZUKEY = args.Azurekey
Azure_TTS_engine.service_region = args.ServRegion

# 从主程序借来的Audio类
from Medias import Audio
# 正则表达式定义
from Regexs import RE_dialogue,RE_characor,RE_asterisk
# 函数定义
from Utils import clean_ts,isnumber,mod62_timestamp

# 全局变量
media_list=[]
occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n')

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

# 解析函数
def parser(stdin_text):
    # parsed log 列名
    asterisk_line_columns=['asterisk_label','character','speech_text','category','filepath']
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
                        print('\x1B[33m[warning]:\x1B[0m A defined object',K1[0:-1],'is specified, which will not be processed.')
                    elif (os.path.isfile(K1[1:-2])==False): #3&4.指定了不存在的文件路径
                        raise OSError('\x1B[31m[ParserError]:\x1B[0m Asterisk SE file '+K1[0:-1]+' is not exist.')
                    else: # 其他的不合规的星标文本
                        raise ValueError('\x1B[31m[ParserError]:\x1B[0m Invalid asterisk lable appeared in dialogue line.')
                    
                else:
                    raise ValueError('\x1B[31m[ParserError]:\x1B[0m Too much asterisk time labels are set in dialogue line.')
                name,alpha,subtype= this_charactor[0]
                if subtype == '':
                    subtype = '.default'
                asterisk_line.loc[i,'character'] = name+subtype
            except Exception as E:
                print(E)
                raise ValueError('\x1B[31m[ParserError]:\x1B[0m Parse exception occurred in dialogue line ' + str(i+1)+'.')
        else:
            pass
    return asterisk_line.dropna()

# 音频合成函数
def synthesizer(key,asterisk):
    #读取Voice信息
    if asterisk['category'] > 2: #如果解析结果为3&4，不执行语音合成
        return 'Keep',False
    elif asterisk['character'] not in charactor_table.index: #指定了未定义的发言角色
        print('\x1B[33m[warning]:\x1B[0m Undefine charactor!')
        return 'None',False
    else:
        charactor_info = charactor_table.loc[asterisk['character']]
    #如果这个角色本身就不带有发言
    if charactor_info['TTS'] == 'None':
        print('\x1B[33m[warning]:\x1B[0m No voice is specified for ',asterisk['character'])
        return 'None',False
    else:
        # alpha 1.12.4 在输出路径里加上timestamp，和序号和行号统一
        ofile = args.OutputPath+'/'+'auto_AU_%d'%(key+1)+'_'+mod62_timestamp()+'.wav'
        # alpha 1.12.4 如果合成出现异常，重试
        for time_retry in range(1,6):
            # 最多重试5次
            try:
                charactor_info['TTS'].start(asterisk['speech_text'],ofile) #执行合成
                return ofile,True  # 如果能不出异常的结束，则退出循环
            except Exception as E:
                # 如果出现了异常
                print('\x1B[33m[warning]:\x1B[0m Synthesis failed in line %d'%(key+1), '(%d),'%time_retry, 'due to:',E)
        # 如果超出了5次尝试，返回Fatal
        return 'Fatal',False

# 预览窗体
def open_Tuning_windows(init_type='Aliyun'):
    # 根据选中的语音服务，切换frame
    def show_selected_options(event):
        nonlocal servframe_display
        servframe_display.place_forget()
        try:
            select = Servicetype[tts_service.get()]
        except:
            messagebox.showerror(title='错误',message='服务名错误！')
            select = Servicetype['阿里云']
        select.place(x=10,y=40,width=360,height=190)
        servframe_display = select
    # 根据选中的Azure音源，更新可用的role和style
    def update_selected_voice(event):
        azure_voice_selected = azure_voice.get()
        azure_style_available = voice_lib.loc[azure_voice_selected,'style'].split(',')
        azure_role_available = voice_lib.loc[azure_voice_selected,'role'].split(',')
        azure_style_combobox.config(values=azure_style_available)
        azure_role_combobox.config(values=azure_role_available)
        azure_style.set('general')
        azure_role.set('Default')
        azure_degree.set(1.0)
    # 将选择条的数值强行转换为整型
    def get_scale_to_intvar(variable):
        variable.set(int(variable.get()))
    # 复制到剪贴板
    def copy_args_clipboard():
        if tts_service.get() == '阿里云':
            voice_this = aliyun_voice.get()
        elif tts_service.get() == '微软Azure':
            voice_this = 'Azure::'+azure_voice.get()+':'+azure_style.get()+':'+str(azure_degree.get())+':'+azure_role.get()
        copy_to_clipboard = '\t'.join([voice_this,str(speech_rate.get()),str(pitch_rate.get())])
        Tuning_windows.clipboard_clear()
        Tuning_windows.clipboard_append(copy_to_clipboard)
        #messagebox.showinfo(title='复制到剪贴板',message='已成功将\n'+copy_to_clipboard+'\n复制到剪贴板')
    # 执行合成
    def exec_synthesis(command='play'):
        # 音源不同，语音合成的服务不同
        if tts_service.get() == '阿里云':
            voice_this = aliyun_voice.get()
            TTS_engine = Aliyun_TTS_engine
        elif tts_service.get() == '微软Azure':
            voice_this = azure_voice.get()+':'+azure_style.get()+':'+str(azure_degree.get())+':'+azure_role.get()
            TTS_engine = Azure_TTS_engine
        # 如果没有指定voice
        if voice_this.split(':')[0]=='':
            messagebox.showerror(title='错误',message='缺少音源名!')
            return 0
        try:
            this_tts_engine = TTS_engine(name='preview',
                                         voice = voice_this,
                                         speech_rate=speech_rate.get(),
                                         pitch_rate=pitch_rate.get(),
                                         aformat='wav')
        except KeyError as E: # 非法的音源名
            print('\x1B[33m[warning]:\x1B[0m Unsupported speaker name',E)
            messagebox.showerror(title='合成失败',message="[错误]：不支持的音源名！")
            return 0
        # 执行合成
        try:
            this_tts_engine.start(text_to_synth.get("0.0","end"),'./media/preview_tempfile.wav')
        except Exception as E:
            print('\x1B[33m[warning]:\x1B[0m Synthesis failed in preview,','due to:',E)
            messagebox.showerror(title='合成失败',message="[错误]：语音合成失败！")
            return 0
        if command == 'play':
            # 播放合成结果
            try:
                Audio('./media/preview_tempfile.wav').display(preview_channel)
                return 1
            except Exception as E:
                print('\x1B[33m[warning]:\x1B[0m Failed to play the audio,','due to:',E)
                messagebox.showerror(title='播放失败',message="[错误]：无法播放语音！")
                return 0
        elif command == 'save':
            try:
                default_filename = voice_this.split(':')[0] + '_' + mod62_timestamp()+ '.wav'
                save_filepath = filedialog.asksaveasfilename(initialfile=default_filename,filetypes=[('音频文件','*.wav')])
                if save_filepath != '':
                    copy('./media/preview_tempfile.wav',save_filepath)
            except Exception as E:
                print('\x1B[33m[warning]:\x1B[0m Failed to save the file,','due to:',E)
                messagebox.showerror(title='保存失败',message="[错误]：无法保存文件！")
                return 0

    # 窗口
    Tuning_windows = tk.Tk()
    Tuning_windows.resizable(0,0)
    Tuning_windows.geometry("400x460")
    Tuning_windows.config(background ='#e0e0e0')
    Tuning_windows.title('语音合成试听')
    try:
        Tuning_windows.iconbitmap('./media/icon.ico')
    except tk.TclError:
        pass
    #Tuning_windows.transient(father)
    # 声音轨道
    preview_channel = mixer.Channel(1)
    # 主框
    tune_main_frame = tk.Frame(Tuning_windows)
    tune_main_frame.place(x=10,y=10,height=440,width=380)
    # 语音服务变量
    tts_service = tk.StringVar(tune_main_frame)
    tts_service.set({'Aliyun':'阿里云','Azure':'微软Azure'}[init_type])
    # 语速语调文本变量
    pitch_rate = tk.IntVar(tune_main_frame)
    pitch_rate.set(0)
    speech_rate = tk.IntVar(tune_main_frame)
    speech_rate.set(0)
    # 版本号
    tk.Label(tune_main_frame,text='Speech_synthesizer '+EDITION,fg='#d0d0d0').place(x=170,y=5,height=15)
    tk.Label(tune_main_frame,text='For TRPG-replay-generator.',fg='#d0d0d0').place(x=170,y=20,height=15)
    # 选中音源变量
    tk.Label(tune_main_frame,text='服务：').place(x=10,y=10,width=40,height=25)
    choose_type = ttk.Combobox(tune_main_frame,textvariable=tts_service,value=['阿里云','微软Azure'])
    choose_type.place(x=50,y=10,width=100,height=25)
    choose_type.bind("<<ComboboxSelected>>",show_selected_options)
    # 音源窗口
    Aliyun_frame = tk.LabelFrame(tune_main_frame,text='阿里-参数')
    Azure_frame = tk.LabelFrame(tune_main_frame,text='微软-参数')
    text_frame = tk.LabelFrame(tune_main_frame,text='文本')
    Servicetype = {'阿里云':Aliyun_frame,'微软Azure':Azure_frame}
    # 初始化显示的服务
    servframe_display = Servicetype[tts_service.get()]
    servframe_display.place(x=10,y=40,width=360,height=190)
    text_frame.place(x=10,y=240,width=360,height=150)
    # 复制到剪贴板按钮
    ttk.Button(Aliyun_frame,text='复制',command=copy_args_clipboard).place(x=310,y=-5,width=40,height=25)
    ttk.Button(Azure_frame,text='复制',command=copy_args_clipboard).place(x=310,y=-5,width=40,height=25)
    # 阿里云参数
    aliyun_voice = tk.StringVar(Aliyun_frame)
    ttk.Label(Aliyun_frame,text='音源名:').place(x=10,y=10,width=65,height=25)
    ttk.Label(Aliyun_frame,text='语速:').place(x=10,y=40,width=65,height=25)
    ttk.Label(Aliyun_frame,text='语调:').place(x=10,y=70,width=65,height=25)
    ttk.Combobox(Aliyun_frame,textvariable=aliyun_voice,values=list(voice_lib[voice_lib.service=='Aliyun'].index)).place(x=75,y=10,width=225,height=25)
    ttk.Spinbox(Aliyun_frame,from_=-500,to=500,textvariable=speech_rate,increment=10).place(x=75,y=40,width=50,height=25)
    ttk.Spinbox(Aliyun_frame,from_=-500,to=500,textvariable=pitch_rate,increment=10).place(x=75,y=70,width=50,height=25)
    ttk.Scale(Aliyun_frame,from_=-500,to=500,variable=speech_rate,command=lambda x:get_scale_to_intvar(speech_rate)).place(x=135,y=40,width=200,height=25)
    ttk.Scale(Aliyun_frame,from_=-500,to=500,variable=pitch_rate,command=lambda x:get_scale_to_intvar(pitch_rate)).place(x=135,y=70,width=200,height=25)
    # Azure参数
    azure_voice = tk.StringVar(Azure_frame)
    azure_style = tk.StringVar(Azure_frame)
    azure_degree = tk.DoubleVar(Azure_frame)
    azure_role = tk.StringVar(Azure_frame)
    azure_style.set('general')
    azure_degree.set(1.0)
    azure_role.set('Default')
    ttk.Label(Azure_frame,text='音源名:').place(x=10,y=10,width=65,height=25)
    ttk.Label(Azure_frame,text='风格:').place(x=10,y=40,width=65,height=25)
    ttk.Label(Azure_frame,text='风格强度:').place(x=215,y=40,width=65,height=25)
    ttk.Label(Azure_frame,text='扮演:').place(x=10,y=70,width=65,height=25)
    ttk.Label(Azure_frame,text='语速:').place(x=10,y=100,width=65,height=25)
    ttk.Label(Azure_frame,text='语调:').place(x=10,y=130,width=65,height=25)
    ## 选择音源名
    azure_voice_combobox = ttk.Combobox(Azure_frame,textvariable=azure_voice,values=list(voice_lib[voice_lib.service=='Azure'].index))
    azure_voice_combobox.place(x=75,y=10,width=225,height=25)
    azure_voice_combobox.bind("<<ComboboxSelected>>",update_selected_voice)
    ## 选择style就role
    azure_style_combobox = ttk.Combobox(Azure_frame,textvariable=azure_style,values=['general'])
    azure_style_combobox.place(x=75,y=40,width=130,height=25)
    ttk.Spinbox(Azure_frame,textvariable=azure_degree,from_=0.01,to=2,increment=0.1).place(x=285,y=40,width=50,height=25)
    azure_role_combobox = ttk.Combobox(Azure_frame,textvariable=azure_role,values=['Default'])
    azure_role_combobox.place(x=75,y=70,width=260,height=25)
    ## 选择语速和语调
    ttk.Spinbox(Azure_frame,from_=-500,to=500,textvariable=speech_rate,increment=10).place(x=75,y=100,width=50,height=25)
    ttk.Spinbox(Azure_frame,from_=-500,to=500,textvariable=pitch_rate,increment=10).place(x=75,y=130,width=50,height=25)
    ttk.Scale(Azure_frame,from_=-500,to=500,variable=speech_rate,command=lambda x:get_scale_to_intvar(speech_rate)).place(x=135,y=100,width=200,height=25)
    ttk.Scale(Azure_frame,from_=-500,to=500,variable=pitch_rate,command=lambda x:get_scale_to_intvar(pitch_rate)).place(x=135,y=130,width=200,height=25)
    # 文本框体
    text_to_synth = tk.Text(text_frame,font=("黑体",11))
    text_to_synth.place(x=10,y=5,width=335,height=115)
    text_to_synth.insert(tk.END,'在这里输入你想要合成的文本！')
    # 确定合成按钮
    ttk.Button(tune_main_frame,text='播放',command=lambda:exec_synthesis('play')).place(x=120,y=395,height=40,width=60)
    ttk.Button(tune_main_frame,text='保存',command=lambda:exec_synthesis('save')).place(x=200,y=395,height=40,width=60)
    # 主循环
    Tuning_windows.mainloop()

# 语音合成
def main():
    global charactor_table
    global media_list

    print('[speech synthesizer]: Welcome to use speech_synthesizer for TRPG-replay-generator '+EDITION)
    print('[speech synthesizer]: The processed Logfile and audio file will be saved at "'+args.OutputPath+'"')
    # 载入ct文件
    try:
        if args.CharacterTable.split('.')[-1] in ['xlsx','xls']:
            charactor_table = pd.read_excel(args.CharacterTable,dtype = str) # 支持excel格式的角色配置表
        else:
            charactor_table = pd.read_csv(args.CharacterTable,sep='\t',dtype = str)
        charactor_table.index = charactor_table['Name']+'.'+charactor_table['Subtype']
        if 'Voice' not in charactor_table.columns:
            print('\x1B[33m[warning]:\x1B[0m','Missing \'Voice\' columns.')
    except Exception as E:
        print('\x1B[31m[SyntaxError]:\x1B[0m Unable to load charactor table:',E)
        sys.exit(2) # 无法载入角色表，异常退出

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
            print('\x1B[33m[warning]:\x1B[0m Unsupported speaker name "{0}".'.format(value.Voice))
            TTS[key] = '"None"'
    # 应用并保存在charactor_table内
    try:
        charactor_table['TTS'] = TTS.map(lambda x:eval(x))
    except ModuleNotFoundError as E:
        print('\x1B[31m[ImportError]:\x1B[0m ',E,' .Execution terminated!')
        sys.exit(2) # 缺乏依赖包，异常退出
    except ValueError as E: # 非法音源名
        print(E)
        sys.exit(2) # 包含非法音源名，异常退出

    # 载入od文件
    try:
        object_define_text = open(args.MediaObjDefine,'r',encoding='utf-8').read()#.split('\n')
    except UnicodeDecodeError as E:
        print('\x1B[31m[DecodeError]:\x1B[0m',E)
        sys.exit(2) # 解码角色配置表错误，异常退出
    if object_define_text[0] == '\ufeff': # UTF-8 BOM
        print('\x1B[33m[warning]:\x1B[0m','UTF8 BOM recognized in MediaDef, it will be drop from the begin of file!')
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
                print('\x1B[31m[SyntaxError]:\x1B[0m "'+text+'" appeared in media define file line ' + str(i+1)+':',E)
                sys.exit(2) # 媒体定义文件格式错误，异常退出

    # 载入log文件
    try:
        stdin_text = open(args.LogFile,'r',encoding='utf-8').read()#.split('\n')
    except UnicodeDecodeError as E:
        print('\x1B[31m[DecodeError]:\x1B[0m',E)
        sys.exit(2) # 解码log文件错误，异常退出！
    if stdin_text[0] == '\ufeff': # 139 debug
        print('\x1B[33m[warning]:\x1B[0m','UTF8 BOM recognized in Logfile, it will be drop from the begin of file!')
        stdin_text = stdin_text[1:]
    stdin_text = stdin_text.split('\n')
    try:
        asterisk_line = parser(stdin_text)
    except Exception as E:
        print(E)
        sys.exit(2) # 解析log错误，异常退出！

    asterisk_line['synth_status'] = False # v1.6.1 初始值，以免生成refresh的时候报错！
    fatal_break = False # 是否发生中断？
    # 开始合成
    print('[speech synthesizer]: Begin to speech synthesis!')
    for key,value in asterisk_line.iterrows():
        # 进行合成
        ofile_path,synth_status = synthesizer(key,value)
        if ofile_path == 'Keep':
            pass
        elif ofile_path == 'None':
            asterisk_line.loc[key,'filepath'] = synth_status
        elif ofile_path == 'Fatal':
            asterisk_line.loc[key,'filepath'] = synth_status
            fatal_break = True
            print("\x1B[31m[FatalError]:\x1B[0m", "An unresolvable error occurred during speech synthesis!")
            break
        elif os.path.isfile(ofile_path)==False:
            asterisk_line.loc[key,'filepath'] = 'None'
        else:
            asterisk_line.loc[key,'filepath'] = ofile_path
        asterisk_line.loc[key,'synth_status'] = synth_status

    # 仅category 3,或者成功合成的1，2去更新标记
    refresh = asterisk_line[(asterisk_line.category==3)|(asterisk_line.synth_status==True)].dropna().copy() #检定是否成功合成

    if len(refresh.index) == 0: #如果未合成任何语音
        if fatal_break == True:
            print('\x1B[33m[warning]:\x1B[0m','Speech synthesis cannot begin, execution terminated!')
            sys.exit(2) # 在第一行就终止
        else:
            print('\x1B[33m[warning]:\x1B[0m','No valid asterisk label synthesised, execution terminated!')
            sys.exit(1) # 未有合成，警告退出

    # 原始log文件备份到输出路径
    backup_log = args.OutputPath+'/OriginalLogfileBackup_'+mod62_timestamp()+'.rgl'
    backup_logfile = open(backup_log,'w',encoding='utf-8')
    backup_logfile.write('\n'.join(stdin_text))
    backup_logfile.close()
    print('[speech synthesizer]: Original LogFile backup path: '+backup_log)

    # 读取音频时长
    for key,value in refresh.iterrows():
        try:
            refresh.loc[key,'audio_lenth'] = Audio(value.filepath).get_length()
        except MediaError as E:
            print('\x1B[33m[warning]:\x1B[0m Unable to get audio length of '+str(value.filepath)+', due to:',E)
            refresh.loc[key,'audio_lenth'] = np.nan

    # 生成新的标签
    new_asterisk_label = "{'"+refresh.filepath + "';*"+refresh.audio_lenth.map(lambda x:'%.3f'%x)+"}"
    refresh['new_asterisk_label'] = new_asterisk_label

    # 替换原来的标签
    for key,value in refresh.iterrows():
        stdin_text[key] = stdin_text[key].replace(value.asterisk_label,value.new_asterisk_label)

    # 覆盖原始log文件
    stdout_logfile = open(args.LogFile,'w',encoding='utf-8')
    stdout_logfile.write('\n'.join(stdin_text))
    stdout_logfile.close()
    print('[speech synthesizer]: Logfile refresh Done!')

    if fatal_break == True:
        print('[speech synthesizer]: Synthesis Breaked, due to FatalError!')
        sys.exit(3)
    else:
        print('[speech synthesizer]: Synthesis Done!')

if __name__ == '__main__':
    if args.PreviewOnly == True:
        open_Tuning_windows(init_type=args.Init)
    else:
        main()
