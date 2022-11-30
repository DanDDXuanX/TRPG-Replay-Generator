#!/usr/bin/env python
# coding: utf-8

# 语音合成模块的退出代码：
# 0. 有覆盖原log，合成正常，可以继续执行主程序
# 1. 无覆盖原log，无需合成，可以继续执行主程序
# 2. 无覆盖原log，合成未完成，不能继续执行主程序
# 3. 有覆盖原log，合成未完成，不能继续执行主程序

# 版本
from core.Utils import EDITION
# 日志和报错
from core.Exceptions import RplGenError, Print
from core.Exceptions import DecodeError, IgnoreInput, MediaError, ArgumentError, ParserError, SyntaxsError, SynthesisError
from core.Exceptions import SynthPrint, WarningPrint
# 包导入
import sys
import os
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
from core.TTSengines import Aliyun_TTS_engine,Azure_TTS_engine,voice_lib
# 从主程序借来的Audio类
from core.Medias import Audio
# 正则表达式定义
from core.Regexs import RE_dialogue,RE_characor,RE_asterisk,RE_mediadef
# 工具函数
from core.Utils import clean_ts,isnumber,mod62_timestamp

class SpeechSynthesizer:
    # 初始化模块功能，载入外部参数
    def __init__(self,args) -> None:
        # 输入文件
        self.stdin_log = args.LogFile
        self.media_obj = args.MediaObjDefine
        self.char_tab = args.CharacterTable
        self.output_path = args.OutputPath
        # Keys
        Aliyun_TTS_engine.AKID = args.AccessKey
        Aliyun_TTS_engine.AKKEY = args.AccessKeySecret
        Aliyun_TTS_engine.APPKEY = args.Appkey
        Azure_TTS_engine.AZUKEY = args.Azurekey
        Azure_TTS_engine.service_region = args.ServRegion
        # 初始化日志打印
        if args.Language == 'zh':
            # 中文
            Print.lang = 1 
            RplGenError.lang = 1
        else:
            # 英文
            Print.lang == 0
            RplGenError.lang = 0
        # 检查外部参数合法性
        try:
            for path in [self.stdin_log,self.media_obj,self.char_tab]:
                if path is None:
                    raise ArgumentError('MissInput')
                if os.path.isfile(path) == False:
                    raise ArgumentError('FileNotFound',path)

            if self.output_path is None:
                raise ArgumentError('MustOutput')
            elif os.path.isdir(self.output_path) == False:
                try:
                    os.makedirs(self.output_path)
                except Exception:
                    raise ArgumentError('MkdirErr',self.output_path)
            else:
                pass
            self.output_path = self.output_path.replace('\\','/')
        except Exception as E:
            print(E)
            sys.exit(2) # 缺少必要文件路径，异常退出
        # 全局变量
        self.occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n')
        # 开始执行主流程
        self.main()
    # 解析发言行
    def get_dialogue_arg(self,text) -> tuple:
        cr,cre,ts,tse,se = RE_dialogue.findall(text)[0]
        this_charactor = RE_characor.findall(cr)
        # 语音和音效参数
        if se == '':
            asterisk_label = []
        else:
            asterisk_label = RE_asterisk.findall(se)
        return (this_charactor,ts,asterisk_label)
    # 解析log文件函数
    def parser(self,stdin_text) -> pd.DataFrame:
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
                    this_charactor,ts,asterisk_label = self.get_dialogue_arg(text)
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
                        elif K1[0:-1] in self.media_list:
                            asterisk_line.loc[i,'category'] = 4
                            asterisk_line.loc[i,'speech_text'] = 'None'
                            asterisk_line.loc[i,'filepath'] = K1[0:-1]
                            print(WarningPrint('DefAsterSE',K1[0:-1]))
                        elif (os.path.isfile(K1[1:-2])==False): #3&4.指定了不存在的文件路径
                            raise ParserError('BadAsterSE',K1[0:-1])
                        else: # 其他的不合规的星标文本
                            raise ParserError('InvAster')
                        
                    else:
                        raise ParserError('2muchAster',str(i+1))
                    name,alpha,subtype= this_charactor[0]
                    if subtype == '':
                        subtype = '.default'
                    asterisk_line.loc[i,'character'] = name+subtype
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrDial', str(i+1))
            else:
                pass
        return asterisk_line.dropna()
    # 音频合成函数
    def synthesizer(self,key,asterisk) -> tuple:
        #读取Voice信息
        if asterisk['category'] > 2: #如果解析结果为3&4，不执行语音合成
            return 'Keep',False
        elif asterisk['character'] not in self.charactor_table.index: #指定了未定义的发言角色
            print(WarningPrint('UndefChar',asterisk['character']))
            return 'None',False
        else:
            charactor_info = self.charactor_table.loc[asterisk['character']]
        #如果这个角色本身就不带有发言
        if charactor_info['TTS'] == 'None':
            print(WarningPrint('CharNoVoice',asterisk['character']))
            return 'None',False
        else:
            # alpha 1.12.4 在输出路径里加上timestamp，和序号和行号统一
            ofile = self.output_path +'/'+'auto_AU_%d'%(key+1)+'_'+mod62_timestamp()+'.wav'
            # alpha 1.12.4 如果合成出现异常，重试
            for time_retry in range(1,6):
                # 最多重试5次
                try:
                    charactor_info['TTS'].start(asterisk['speech_text'],ofile) #执行合成
                    return ofile,True  # 如果能不出异常的结束，则退出循环
                except Exception as E:
                    # 如果出现了异常
                    print(WarningPrint('SynthFail', str(key+1), str(time_retry), E))
            # 如果超出了5次尝试，返回Fatal
            return 'Fatal',False
    # 建立语音合成对象
    def bulid_tts_engine(self,charactor_table) -> pd.Series:
        # TTS engines 对象的容器
        TTS = pd.Series(index=charactor_table.index,dtype='str')
        # 逐个遍历角色
        for key,value in charactor_table.iterrows():
            try:
                # 如果音源是NA，那么TTS 是 "None"
                if (value.Voice != value.Voice)|(value.Voice=="NA"): 
                    TTS[key] = '"None"'
                # 阿里云模式：如果音源名在音源表内
                elif value.Voice in Aliyun_TTS_engine.voice_list:
                    TTS[key] = Aliyun_TTS_engine(name=key, voice=value.Voice, speech_rate=int(value.SpeechRate), pitch_rate=int(value.PitchRate))
                # Azure 模式：如果音源名以 'Azure::' 作为开头
                elif value.Voice[0:7] == 'Azure::':
                    TTS[key] = Azure_TTS_engine(name=key, voice=value.Voice[7:], speech_rate=int(value.SpeechRate), pitch_rate=int(value.PitchRate))
                # 否则，是非法的音源名
                else:
                    print(WarningPrint('BadSpeaker',value.Voice))
                    TTS[key] = '"None"'
            except ModuleNotFoundError as E:
                # 缺乏依赖包，异常退出
                print(RplGenError('ImportErr',E))
                sys.exit(2) 
            except ValueError as E:
                # 包含非法音源名，异常退出
                print(E)
                sys.exit(2)
        # 返回 TTS engine
        return TTS
    # 载入输入文件
    def load_medias(self) -> None:
        # 载入角色配置表
        try:
            if self.char_tab.split('.')[-1] in ['xlsx','xls']:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore') # 禁用读取excel时报出的：UserWarning: Data Validation extension is not supported and will be removed
                    charactor_table = pd.read_excel(self.char_tab,dtype = str,sheet_name='角色配置') # 支持excel格式的角色配置表
            else:
                charactor_table = pd.read_csv(self.char_tab,sep='\t',dtype = str)
            charactor_table.index = charactor_table['Name']+'.'+charactor_table['Subtype']
            if 'Voice' not in charactor_table.columns:
                print(WarningPrint('MissVoice'))
        except Exception as E:
            print(SyntaxsError('CharTab',E))
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
        # 填补剩余空缺值
        charactor_table = charactor_table.fillna('NA')
        # 保存 TTS engine 在 charactor_table 内
        charactor_table['TTS'] = self.bulid_tts_engine(charactor_table)
        # 角色表
        self.charactor_table = charactor_table
        # 载入媒体定义文件
        self.media_list=[]
        try:
            object_define_text = open(self.media_obj,'r',encoding='utf-8').read()#.split('\n')
        except UnicodeDecodeError as E:
            print(DecodeError('DecodeErr',E))
            sys.exit(2) # 解码角色配置表错误，异常退出
        if object_define_text[0] == '\ufeff': # UTF-8 BOM
            print(WarningPrint('UFT8BOM'))
            object_define_text = object_define_text[1:]
        object_define_text = object_define_text.split('\n')
        # 逐行载入媒体
        for i,text in enumerate(object_define_text):
            if text == '':
                continue
            elif text[0] == '#':
                continue
            try:
                # 尝试解析媒体定义文件
                obj_name,obj_type,obj_args = RE_mediadef.findall(text)[0]
            except:
                # 格式不合格的行直接略过
                continue
            else:
                # 格式合格的行开始解析
                try:
                    if obj_name in self.occupied_variable_name:
                        raise SyntaxsError('OccName')
                    elif (len(re.findall('\w+',obj_name))==0)|(obj_name[0].isdigit()):
                        raise SyntaxsError('InvaName')
                    else:
                        #记录新增对象名称
                        self.media_list.append(obj_name) 
                except Exception as E:
                    print(E)
                    print(SyntaxsError('MediaDef',text,str(i+1)))
                    sys.exit(2) # 媒体定义文件格式错误，异常退出
        # 载入log文件
        try:
            self.stdin_text = open(self.stdin_log,'r',encoding='utf-8').read()#.split('\n')
        except UnicodeDecodeError as E:
            print(DecodeError('DecodeErr',E))
            sys.exit(2) # 解码log文件错误，异常退出！
        if self.stdin_text[0] == '\ufeff': # 139 debug
            print(WarningPrint('UFT8BOM'))
            self.stdin_text = self.stdin_text[1:]
        self.stdin_text = self.stdin_text.split('\n')
        # 解析log文件
        try:
            self.asterisk_line = self.parser(self.stdin_text)
        except Exception as E:
            print(E)
            sys.exit(2) # 解析log错误，异常退出！
        # 初始值，以免生成refresh的时候报错！
        self.asterisk_line['synth_status'] = False
        # 是否发生中断？
        self.fatal_break = False 
    # 执行语音合成
    def exec_synth(self) -> None:
        for key,value in self.asterisk_line.iterrows():
            # 进行合成：返回值是输入路径(str) 和 成功状态(bool)
            ofile_path,synth_status = self.synthesizer(key,value)
            # 如果不需要执行语音合成
            if ofile_path == 'Keep':
                pass
            # 如果角色本身不带有语音
            elif ofile_path == 'None':
                self.asterisk_line.loc[key,'filepath'] = synth_status
            # 如果合成发生重大错误
            elif ofile_path == 'Fatal':
                self.asterisk_line.loc[key,'filepath'] = synth_status
                self.fatal_break = True
                print(SynthesisError('FatalError'))
                break
            # 合成的文件被人删了？
            elif os.path.isfile(ofile_path)==False:
                self.asterisk_line.loc[key,'filepath'] = 'None'
            # 成功了！！
            else:
                self.asterisk_line.loc[key,'filepath'] = ofile_path
            self.asterisk_line.loc[key,'synth_status'] = synth_status
    # 更新log文件
    def update_logfile(self) -> None:
        # 需要更新的log文件：category==3 需要同步星标时间；synth_status==True 语音合成成功
        refresh = self.asterisk_line[(self.asterisk_line.category==3)|(self.asterisk_line.synth_status==True)].dropna().copy() #检定是否成功合成
        if len(refresh.index) == 0: #如果未合成任何语音
            if self.fatal_break == True:
                print(WarningPrint('SynthNBegin'))
                sys.exit(2) # 在第一行就终止
            else:
                print(WarningPrint('No2Synth'))
                sys.exit(1) # 未有合成，警告退出
        # 原始log文件备份到输出路径
        backup_log = self.output_path+'/OriginalLogfileBackup_'+mod62_timestamp()+'.rgl'
        backup_logfile = open(backup_log,'w',encoding='utf-8')
        backup_logfile.write('\n'.join(self.stdin_text))
        backup_logfile.close()
        print(SynthPrint('OriBack',backup_log))
        # 读取音频时长
        for key,value in refresh.iterrows():
            try:
                refresh.loc[key,'audio_lenth'] = Audio(value.filepath).get_length()
            except MediaError as E:
                print(WarningPrint('BadAuLen', str(value.filepath), E))
                refresh.loc[key,'audio_lenth'] = np.nan
        # 生成新的标签
        new_asterisk_label = "{'"+ refresh.filepath + "';*"+ refresh.audio_lenth.map(lambda x:'%.3f'%x)+"}"
        refresh['new_asterisk_label'] = new_asterisk_label
        # 替换原来的标签
        for key,value in refresh.iterrows():
            self.stdin_text[key] = self.stdin_text[key].replace(value.asterisk_label,value.new_asterisk_label)
        # 覆盖原始log文件
        stdout_logfile = open(self.stdin_log,'w',encoding='utf-8')
        stdout_logfile.write('\n'.join(self.stdin_text))
        stdout_logfile.close()
    # 主流程
    def main(self) -> None:
        # 欢迎
        print(SynthPrint('Welcome',EDITION))
        print(SynthPrint('SaveAt',self.output_path))
        # 载入输入文件
        self.load_medias()
        # 开始合成
        print(SynthPrint('SthBegin'))
        self.exec_synth()
        # 更新log文件
        self.update_logfile()
        print(SynthPrint('Refresh'))
        # 结尾检查是错误退出还是正常退出
        if self.fatal_break == True:
            print(SynthPrint('Breaked'))
            sys.exit(3)
        else:
            print(SynthPrint('Done'))

class SpeechStudio:
    # 初始化模块功能，载入外部参数
    def __init__(self,args):
        # Keys
        Aliyun_TTS_engine.AKID = args.AccessKey
        Aliyun_TTS_engine.AKKEY = args.AccessKeySecret
        Aliyun_TTS_engine.APPKEY = args.Appkey
        Azure_TTS_engine.AZUKEY = args.Azurekey
        Azure_TTS_engine.service_region = args.ServRegion
        # 初始化日志打印
        if args.Language == 'zh':
            # 中文
            Print.lang = 1 
            RplGenError.lang = 1
        else:
            # 英文
            Print.lang == 0
            RplGenError.lang = 0
        # 进入状态
        self.init_type = args.Init
        # 如果选择仅预览，则忽略输入文件！
        try:
            if self.init_type in ['Aliyun','Azure']:
                raise IgnoreInput()
            else:
                raise ArgumentError('BadInit',self.init_type)
        except IgnoreInput as E:
            print(E)
        except Exception as E:
            print(E)
            sys.exit(2) # 缺少必要文件路径，异常退出
        # 声音轨道
        self.preview_channel = mixer.Channel(1)
        # 开始执行主流程
        self.main()
    # 根据选中的语音服务，切换frame
    def show_selected_options(self,event):
        self.servframe_display.place_forget()
        try:
            select = self.Servicetype[self.tts_service.get()]
        except:
            messagebox.showerror(title='错误',message='服务名错误！')
            select = self.Servicetype['阿里云']
        select.place(x=10,y=40,width=360,height=190)
        self.servframe_display = select
    # 选中的阿里云音源
    def update_selected_voice_aliyun(self,event):
        aliyun_voice_selected  = self.aliyun_voice.get()
        # 更新描述
        self.aliyun_voice_description.config(text='('+voice_lib.loc[aliyun_voice_selected,'description']+')')
    # 选中的Azure音源
    def update_selected_voice_azure(self,event):
        azure_voice_selected = self.azure_voice.get()
        azure_style_available = voice_lib.loc[azure_voice_selected,'style'].split(',')
        azure_role_available = voice_lib.loc[azure_voice_selected,'role'].split(',')
        # 更新描述
        self.azure_voice_description.config(text='('+voice_lib.loc[azure_voice_selected,'description']+')')
        # 更新可用的role和style
        self.azure_style_combobox.config(values=azure_style_available)
        self.azure_role_combobox.config(values=azure_role_available)
        self.azure_style.set('general')
        self.azure_role.set('Default')
        self.azure_degree.set(1.0)
    # 复制到剪贴板
    def copy_args_clipboard(self):
        if self.tts_service.get() == '阿里云':
            voice_this = self.aliyun_voice.get()
        elif self.tts_service.get() == '微软Azure':
            voice_this = 'Azure::'+self.azure_voice.get()+':'+self.azure_style.get()+':'+str(self.azure_degree.get())+':'+self.azure_role.get()
        copy_to_clipboard = '\t'.join([voice_this,str(self.speech_rate.get()),str(self.pitch_rate.get())])
        #messagebox.showinfo(title='复制到剪贴板',message='已成功将\n'+copy_to_clipboard+'\n复制到剪贴板')
        self.main_window.clipboard_clear()
        self.main_window.clipboard_append(copy_to_clipboard)
    # 将选择条的数值强行转换为整型
    def get_scale_to_intvar(self,variable):
        variable.set(int(variable.get()))
    # 执行语音合成
    def exec_synthesis(self,command='play'):
        # 音源不同，语音合成的服务不同
        if self.tts_service.get() == '阿里云':
            voice_this = self.aliyun_voice.get()
            TTS_engine = Aliyun_TTS_engine
        elif self.tts_service.get() == '微软Azure':
            voice_this = self.azure_voice.get()+':'+self.azure_style.get()+':'+str(self.azure_degree.get())+':'+self.azure_role.get()
            TTS_engine = Azure_TTS_engine
        # 如果没有指定voice
        if voice_this.split(':')[0]=='':
            messagebox.showerror(title='错误',message='缺少音源名!')
            return 0
        try:
            this_tts_engine = TTS_engine(name='preview',
                                        voice = voice_this,
                                        speech_rate=self.speech_rate.get(),
                                        pitch_rate=self.pitch_rate.get(),
                                        aformat='wav')
        except KeyError as E: # 非法的音源名
            print(WarningPrint('BadSpeaker',E))
            messagebox.showerror(title='合成失败',message="[错误]：不支持的音源名！")
            return 0
        # 执行合成
        try:
            this_tts_engine.start(self.text_to_synth.get("0.0","end"),'./media/preview_tempfile.wav')
        except Exception as E:
            print(WarningPrint('PrevFail',E))
            messagebox.showerror(title='合成失败',message="[错误]：语音合成失败！")
            return 0
        if command == 'play':
            # 播放合成结果
            try:
                Audio('./media/preview_tempfile.wav').display(self.preview_channel)
                return 1
            except Exception as E:
                print(WarningPrint('AuPlayFail',E))
                messagebox.showerror(title='播放失败',message="[错误]：无法播放语音！")
                return 0
        elif command == 'save':
            try:
                default_filename = voice_this.split(':')[0] + '_' + mod62_timestamp()+ '.wav'
                save_filepath = filedialog.asksaveasfilename(initialfile=default_filename,filetypes=[('音频文件','*.wav')])
                if save_filepath != '':
                    copy('./media/preview_tempfile.wav',save_filepath)
            except Exception as E:
                print(WarningPrint('SaveFail',E))
                messagebox.showerror(title='保存失败',message="[错误]：无法保存文件！")
                return 0
    # 建立窗口
    def window(self) -> tk.Tk:
        # 窗口
        self.main_window = tk.Tk()
        self.main_window.resizable(0,0)
        self.main_window.geometry("400x460")
        self.main_window.config(background ='#e0e0e0')
        self.main_window.title('语音合成试听')
        # 图标：仅在windows下有效
        try:
            self.main_window.iconbitmap('./media/icon.ico')
        except tk.TclError:
            pass
        # 主框
        self.tune_main_frame = tk.Frame(self.main_window)
        self.tune_main_frame.place(x=10,y=10,height=440,width=380)
        # 语音服务变量
        self.tts_service = tk.StringVar(self.tune_main_frame)
        self.tts_service.set({'Aliyun':'阿里云','Azure':'微软Azure'}[self.init_type])
        # 语速语调文本变量
        self.pitch_rate = tk.IntVar(self.tune_main_frame)
        self.pitch_rate.set(0)
        self.speech_rate = tk.IntVar(self.tune_main_frame)
        self.speech_rate.set(0)
        # 版本号
        tk.Label(self.tune_main_frame,text='Speech_synthesizer '+EDITION,fg='#d0d0d0').place(x=170,y=5,height=15)
        tk.Label(self.tune_main_frame,text='For TRPG-replay-generator.',fg='#d0d0d0').place(x=170,y=20,height=15)
        # 选中服务变量
        tk.Label(self.tune_main_frame,text='服务：').place(x=10,y=10,width=40,height=25)
        self.choose_type = ttk.Combobox(self.tune_main_frame,textvariable=self.tts_service,value=['阿里云','微软Azure'])
        self.choose_type.place(x=50,y=10,width=100,height=25)
        self.choose_type.bind("<<ComboboxSelected>>",self.show_selected_options)
        # 音源窗口
        self.Aliyun_frame = tk.LabelFrame(self.tune_main_frame,text='阿里-参数')
        self.Azure_frame = tk.LabelFrame(self.tune_main_frame,text='微软-参数')
        self.text_frame = tk.LabelFrame(self.tune_main_frame,text='文本')
        self.Servicetype = {'阿里云':self.Aliyun_frame,'微软Azure':self.Azure_frame}
        # 初始化显示的服务
        self.servframe_display = self.Servicetype[self.tts_service.get()]
        self.servframe_display.place(x=10,y=40,width=360,height=190)
        self.text_frame.place(x=10,y=240,width=360,height=150)
        # 复制到剪贴板按钮
        ttk.Button(self.Aliyun_frame,text='复制',command=self.copy_args_clipboard).place(x=310,y=-5,width=40,height=25)
        ttk.Button(self.Azure_frame,text='复制',command=self.copy_args_clipboard).place(x=310,y=-5,width=40,height=25)
        # 阿里云参数
        self.aliyun_voice = tk.StringVar(self.Aliyun_frame)
        ttk.Label(self.Aliyun_frame,text='音源名:').place(x=10,y=10,width=65,height=25)
        ttk.Label(self.Aliyun_frame,text='语速:').place(x=10,y=40,width=65,height=25)
        ttk.Label(self.Aliyun_frame,text='语调:').place(x=10,y=70,width=65,height=25)
        # 选择音源
        self.aliyun_voice_combobox = ttk.Combobox(self.Aliyun_frame,textvariable=self.aliyun_voice,values=list(voice_lib[voice_lib.service=='Aliyun'].index))
        self.aliyun_voice_combobox.place(x=75,y=10,width=100,height=25)
        self.aliyun_voice_combobox.bind("<<ComboboxSelected>>",self.update_selected_voice_aliyun)
        self.aliyun_voice_description = ttk.Label(self.Aliyun_frame,text='初始化',anchor='w')
        self.aliyun_voice_description.place(x=180,y=10,width=130,height=25)
        # 选择音源参数
        ttk.Spinbox(self.Aliyun_frame,from_=-500,to=500,textvariable=self.speech_rate,increment=10).place(x=75,y=40,width=50,height=25)
        ttk.Spinbox(self.Aliyun_frame,from_=-500,to=500,textvariable=self.pitch_rate,increment=10).place(x=75,y=70,width=50,height=25)
        ttk.Scale(self.Aliyun_frame,from_=-500,to=500,variable=self.speech_rate,command=lambda:self.get_scale_to_intvar(self.speech_rate)).place(x=135,y=40,width=200,height=25)
        ttk.Scale(self.Aliyun_frame,from_=-500,to=500,variable=self.pitch_rate,command=lambda:self.get_scale_to_intvar(self.pitch_rate)).place(x=135,y=70,width=200,height=25)
        # Azure参数
        self.azure_voice = tk.StringVar(self.Azure_frame)
        self.azure_style = tk.StringVar(self.Azure_frame)
        self.azure_degree = tk.DoubleVar(self.Azure_frame)
        self.azure_role = tk.StringVar(self.Azure_frame)
        self.azure_style.set('general')
        self.azure_degree.set(1.0)
        self.azure_role.set('Default')
        ttk.Label(self.Azure_frame,text='音源名:').place(x=10,y=10,width=65,height=25)
        ttk.Label(self.Azure_frame,text='风格:').place(x=10,y=40,width=65,height=25)
        ttk.Label(self.Azure_frame,text='风格强度:').place(x=215,y=40,width=65,height=25)
        ttk.Label(self.Azure_frame,text='扮演:').place(x=10,y=70,width=65,height=25)
        ttk.Label(self.Azure_frame,text='语速:').place(x=10,y=100,width=65,height=25)
        ttk.Label(self.Azure_frame,text='语调:').place(x=10,y=130,width=65,height=25)
        ## 选择音源名
        self.azure_voice_combobox = ttk.Combobox(self.Azure_frame,textvariable=self.azure_voice,values=list(voice_lib[voice_lib.service=='Azure'].index))
        self.azure_voice_combobox.place(x=75,y=10,width=170,height=25)
        self.azure_voice_combobox.bind("<<ComboboxSelected>>",self.update_selected_voice_azure)
        self.azure_voice_description = ttk.Label(self.Azure_frame,text='初始化',anchor='w')
        self.azure_voice_description.place(x=250,y=10,width=60,height=25)
        ## 选择style就role
        self.azure_style_combobox = ttk.Combobox(self.Azure_frame,textvariable=self.azure_style,values=['general'])
        self.azure_style_combobox.place(x=75,y=40,width=130,height=25)
        ttk.Spinbox(self.Azure_frame,textvariable=self.azure_degree,from_=0.01,to=2,increment=0.1).place(x=285,y=40,width=50,height=25)
        self.azure_role_combobox = ttk.Combobox(self.Azure_frame,textvariable=self.azure_role,values=['Default'])
        self.azure_role_combobox.place(x=75,y=70,width=260,height=25)
        ## 选择语速和语调
        ttk.Spinbox(self.Azure_frame,from_=-500,to=500,textvariable=self.speech_rate,increment=10).place(x=75,y=100,width=50,height=25)
        ttk.Spinbox(self.Azure_frame,from_=-500,to=500,textvariable=self.pitch_rate,increment=10).place(x=75,y=130,width=50,height=25)
        ttk.Scale(self.Azure_frame,from_=-500,to=500,variable=self.speech_rate,command=lambda:self.get_scale_to_intvar(self.speech_rate)).place(x=135,y=100,width=200,height=25)
        ttk.Scale(self.Azure_frame,from_=-500,to=500,variable=self.pitch_rate,command=lambda:self.get_scale_to_intvar(self.pitch_rate)).place(x=135,y=130,width=200,height=25)
        # 文本框体
        self.text_to_synth = tk.Text(self.text_frame,font=("黑体",11))
        self.text_to_synth.place(x=10,y=5,width=335,height=115)
        self.text_to_synth.insert(tk.END,'在这里输入你想要合成的文本！')
        # 确定合成按钮
        ttk.Button(self.tune_main_frame,text='播放',command=lambda:self.exec_synthesis('play')).place(x=120,y=395,height=40,width=60)
        ttk.Button(self.tune_main_frame,text='保存',command=lambda:self.exec_synthesis('save')).place(x=200,y=395,height=40,width=60)
        # 返回值
        return self.main_window
    # 主流程
    def main(self):
        self.window().mainloop()

if __name__ == '__main__':
    import argparse
    # 外部参数输入
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
    # 语言
    ap.add_argument("--Language",help='Choose the language of running log',default='en',type=str)
    args = ap.parse_args()
    # 主
    try:
        if args.PreviewOnly == True:
            SpeechStudio(args=args)
        else:
            SpeechSynthesizer(args=args)
    except:
        from traceback import print_exc
        print_exc()
