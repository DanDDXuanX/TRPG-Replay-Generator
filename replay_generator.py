#!/usr/bin/env python
# coding: utf-8

# 版本
from core.Utils import EDITION
# 异常与日志
from core.Exceptions import RplGenError, Print
from core.Exceptions import ParserError, RenderError, ArgumentError, MediaError, SyntaxsError, SynthesisError, DecodeError
from core.Exceptions import MainPrint, WarningPrint, CMDPrint
# 包导入
import sys
import os
import pandas as pd
import numpy as np
import pygame
import pygame.freetype
import re
import time #开发模式，显示渲染帧率
import pickle
# 文件路径
from core.FilePaths import Filepath
# 媒体类
from core.FreePos import Pos,FreePos,PosGrid
from core.Medias import MediaObj
from core.Medias import Text,StrokeText
from core.Medias import Bubble,Balloon,DynamicBubble,ChatWindow
from core.Medias import Background
from core.Medias import Animation,GroupedAnimation,BuiltInAnimation
from core.Medias import Audio,BGM
# 正则表达式
from core.Regexs import *
# 曲线函数
from core.Formulas import linear,quadratic,quadraticR,sigmoid,right,left,sincurve,normalized
from core.Formulas import formula_available
# 小工具们
from core.Utils import *

class ReplayGenerator:
    # 初始化参数
    def __init__(self,args):
        # 外部输入文件
        self.stdin_log = args.LogFile
        self.media_obj = args.MediaObjDefine
        self.char_tab = args.CharacterTable
        self.output_path = args.OutputPath
        # 显示配置
        self.Width = args.Width # 显示的分辨率
        self.Height = args.Height
        self.frame_rate = args.FramePerSecond # 帧率 单位fps
        self.zorder = args.Zorder.split(',') # 渲染图层顺序
        # 语音合成key
        self.accesskey = args.AccessKey
        self.accesskey_secret = args.AccessKeySecret
        self.appkey = args.Appkey
        self.azurekey = args.Azurekey
        self.service_region = args.ServRegion
        # 视频质量
        self.crf = args.Quality
        # 标志
        self.export_xml = args.ExportXML
        self.export_video = args.ExportVideo
        self.synth_anyway = args.SynthesisAnyway
        self.fix_screen = args.FixScreenZoom
        # 语言
        self.lang = args.Language
        # 初始化日志打印
        if self.lang == 'zh':
            # 中文
            Print.lang = 1 
            RplGenError.lang = 1
        else:
            # 英文
            Print.lang == 0
            RplGenError.lang = 0
        # 检查输入参数的合法性
        try:
            # 输入文件
            for path in [self.stdin_log,self.media_obj,self.char_tab]:
                if path is None:
                    raise ArgumentError('MissInput')
                if os.path.isfile(path) == False:
                    raise ArgumentError('FileNotFound',path)
            # 输出路径
            if self.output_path is None:
                if (self.synth_anyway == True) | (self.export_xml == True) | (self.export_video == True):
                    raise ArgumentError('NeedOutput')
            elif os.path.isdir(self.output_path) == False:
                raise ArgumentError('DirNotFound',self.output_path)
            else:
                self.output_path = self.output_path.replace('\\','/')
            # 显示参数
            if self.frame_rate <= 0:
                raise ArgumentError('FrameRate',str(self.frame_rate))
            elif self.frame_rate>30:
                print(WarningPrint('HighFPS',str(self.frame_rate)))

            if (self.Width<=0) | (self.Height<=0):
                raise ArgumentError('Resolution',str((self.Width,self.Height)))
            if self.Width*self.Height > 3e6:
                print(WarningPrint('HighRes'))
        except Exception as E:
            print(E)
            self.system_terminated('Error')
        # 媒体类，显示参数配置
        Filepath.Mediapath = os.path.dirname(self.media_obj.replace('\\','/'))
        MediaObj.screen_size = (self.Width,self.Height)
        MediaObj.frame_rate = self.frame_rate
        # 全局变量
        self.occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n')
        # 获取解释器的路径
        python3 = sys.executable.replace('\\','/')
        # python解释器 + 源码
        if python3.split('/')[-1] in ['py','py3','python','python3','python.exe','python3.exe']:
            # python RplGenCore.py --Modules replay_generator
            if 'RplGenCore.py' in sys.argv[0]:
                self.python3 = python3 + ' ' + sys.argv[0] +  ' --Modules {}'
            # python ./replay_generator.py
            else:
                self.python3 = python3 + ' ./{}.py'
        # 打包版 exe
        # RplGenCore.exe --Modules replay_generator
        elif 'RplGenCore' in python3.split('/')[-1]:
            self.python3 = python3 + ' --Modules {}'
        # 异常摆烂
        else:
            self.python3 = 'python ./{}.py'
        # 动态变量
        self.dynamic_globals = {
            #默认切换效果（立绘）
            'am_method_default' : '<replace=0>',
            #默认切换效果持续时间（立绘）
            'am_dur_default' : 10,
            #默认切换效果（文本框）
            'bb_method_default' : '<replace=0>',
            #默认切换效果持续时间（文本框）
            'bb_dur_default' : 10,
            #默认切换效果（背景）
            'bg_method_default' : '<replace=0>',
            #默认切换效果持续时间（背景）
            'bg_dur_default' : 10,
            #默认文本展示方式
            'tx_method_default' : '<all=0>',
            #默认单字展示时间参数
            'tx_dur_default' : 5,
            #语速，单位word per minute
            'speech_speed' : 220,
            #默认的曲线函数
            'formula' : linear,
            # 星标音频的句间间隔 a1.4.3，单位是帧，通过处理delay
            'asterisk_pause' : 20,
            # a 1.8.8 次要立绘的默认透明度
            'secondary_alpha' : 60,
            # 对话行内指定的方法的应用对象：animation、bubble、both、none
            'inline_method_apply' : 'both'
        }
        # 主流程
        self.main()
    # 解析对话行，返回(this_charactor,this_duration,am_method,am_dur,bb_method,bb_dur,ts,text_method,text_dur,this_sound)
    def get_dialogue_arg(self,text) -> tuple:
        try:
            cr,cre,ts,tse,se = RE_dialogue.findall(text)[0]
        except IndexError:
            raise ParserError('UnableDial')
        # 缺省星标时的默认小节持续时间 = 字数/语速 + 星标间隔
        this_duration = int(len(ts)/(self.dynamic_globals['speech_speed']/60/self.frame_rate)) + self.dynamic_globals['asterisk_pause']
        this_charactor = RE_characor.findall(cr)
        # 切换 method
        if (cre=='') | (self.dynamic_globals['inline_method_apply']=='none'): # 没有指定，或者禁用指定，都走默认值
            am_method,am_dur = RE_modify.findall(self.dynamic_globals['am_method_default'])[0]
            bb_method,bb_dur = RE_modify.findall(self.dynamic_globals['bb_method_default'])[0]
        elif self.dynamic_globals['inline_method_apply']=='animation': # 有指定，参照inline_method_apply
            am_method,am_dur = RE_modify.findall(cre)[0]
            bb_method,bb_dur = RE_modify.findall(self.dynamic_globals['bb_method_default'])[0]
        elif self.dynamic_globals['inline_method_apply']=='bubble':
            am_method,am_dur = RE_modify.findall(self.dynamic_globals['am_method_default'])[0]
            bb_method,bb_dur = RE_modify.findall(cre)[0]
        elif self.dynamic_globals['inline_method_apply']=='both':
            am_method,am_dur = RE_modify.findall(cre)[0]
            bb_method,bb_dur = am_method,am_dur
        # 切换 dur
        if am_dur == '':# 没有指定 走默认值
            am_dur = self.dynamic_globals['am_dur_default']
        else: # 有指定，走指定值
            am_dur = int(am_dur.replace('=',''))
        if bb_dur == '':
            bb_dur = self.dynamic_globals['bb_dur_default']
        else:
            bb_dur = int(bb_dur.replace('=',''))
        # 文本显示 method
        if tse=='':
            tse = self.dynamic_globals['tx_method_default']
        text_method,text_dur = RE_modify.findall(tse)[0] #<black=\d+> 
        # 文本显示 dur
        if text_dur == '':
            text_dur = self.dynamic_globals['tx_dur_default']
        else:
            text_dur = int(text_dur.replace('=',''))
        # 语音和音效参数
        if se == '':
            this_sound = []
        else:
            this_sound = RE_sound.findall(se)
        # 返回
        return (this_charactor,this_duration,am_method,am_dur,bb_method,bb_dur,ts,text_method,text_dur,this_sound)
    # 解析背景、立绘、气泡行，返回(objc,method,method_dur)
    def get_placeobj_arg(self,text) -> tuple:
        try:
            obj_type,obje,objc = RE_placeobj.findall(text)[0]
        except IndexError:
            raise ParserError('UnablePlace')
        if obje=='':
            if obj_type == 'background':
                obje = self.dynamic_globals['bg_method_default']
            elif obj_type == 'bubble':
                obje = self.dynamic_globals['bb_method_default']
            else: # obj_type == 'animation'
                obje = self.dynamic_globals['am_method_default']
        method,method_dur = RE_modify.findall(obje)[0]
        if method_dur == '':
            if obj_type == 'background':
                method_dur = self.dynamic_globals['bg_dur_default']
            elif obj_type == 'bubble':
                method_dur = self.dynamic_globals['bb_dur_default']
            else: # obj_type == 'animation'
                method_dur = self.dynamic_globals['am_dur_default']
        else:
            method_dur = int(method_dur.replace('=',''))
        return (objc,method,method_dur)
    # 解释设置行 <set:>
    def get_seting_arg(self,text) -> tuple:
        try:
            target,args = RE_setting.findall(text)[0]
        except IndexError:
            raise ParserError('UnableSet')
        return (target,args)
    # 处理am和bb类的动态切换效果，返回(alpha_timeline,pos_timeline)[ndarray]
    def ambb_methods(self,method_name,method_dur,this_duration,i) -> tuple:
        def dynamic(scale,duration,balance,cut,enable): # 动态(尺度,持续,平衡,进出,启用)
            if enable == True: # cutin=1,cutout=0
                if cut == balance:
                    return self.dynamic_globals['formula'](0,scale,duration)
                else:
                    return self.dynamic_globals['formula'](scale,0,duration)
            else: # enable == False:
                return np.ones(duration)*scale*balance
        
        if method_dur == 0:
            return np.ones(this_duration),'NA'
        method_keys = method_name.split('_')
        method_args = {'alpha':'replace','motion':'static','direction':'up','scale':'major','cut':'both'} #default
        scale_dic = {'major':0.3,'minor':0.12,'entire':1.0}
        direction_dic = {'up':0,'down':180,'left':90,'right':270} # up = 0 剩下的逆时针
        # parse method name
        for key in method_keys:
            if key in ['black','replace','delay']:
                method_args['alpha'] = key
            elif key in ['pass','leap','static','circular']:
                method_args['motion'] = key
            elif key in ['up','down','left','right']:
                method_args['direction'] = key
            elif key in ['major','minor','entire']:
                method_args['scale'] = key
            elif key in ['in','out','both']:
                method_args['cut'] = key
            elif 'DG' == key[0:2]:
                try:
                    method_args['direction'] = float(key[2:])
                except Exception:
                    raise ParserError('SwitchDial',method_name,str(i+1))
            else:
                try:
                    method_args['scale'] = int(key)
                except Exception:
                    raise ParserError('SwitchDial',method_name,str(i+1))
        # 切入，切出，或者双端
        cutin,cutout ={'in':(1,0),'out':(0,1),'both':(1,1)}[method_args['cut']]
        # alpha
        if method_args['alpha'] == 'replace': #--
            alpha_timeline = np.hstack(np.ones(this_duration)) # replace的延后功能撤销！
        elif method_args['alpha'] == 'delay': #_-
            alpha_timeline = np.hstack([np.zeros(method_dur),np.ones(this_duration-method_dur)]) # 延后功能
        else: # method_args['alpha'] == 'black':#>1<
            alpha_timeline = np.hstack([dynamic(1,method_dur,1,1,cutin),np.ones(this_duration-2*method_dur),dynamic(1,method_dur,1,0,cutout)])
        # static 的提前终止
        if method_args['motion'] == 'static':
            pos_timeline = 'NA'
            return alpha_timeline,pos_timeline
        # direction
        try:
            theta = np.deg2rad(direction_dic[method_args['direction']])
        except Exception: # 设定为角度
            theta = np.deg2rad(method_args['direction'])
        # scale
        if method_args['scale'] in ['major','minor','entire']: #上下绑定屏幕高度，左右绑定屏幕宽度*scale_dic[method_args['scale']]
            method_args['scale'] = ((np.cos(theta)*self.Height)**2+(np.sin(theta)*self.Width)**2)**(1/2)*scale_dic[method_args['scale']]
        else: # 指定了scale
            pass
        # motion
        if method_args['motion'] == 'pass': # >0>
            D1 = np.hstack([dynamic(method_args['scale']*np.sin(theta),method_dur,0,1,cutin),
                            np.zeros(this_duration-2*method_dur),
                            dynamic(-method_args['scale']*np.sin(theta),method_dur,0,0,cutout)])
            D2 = np.hstack([dynamic(method_args['scale']*np.cos(theta),method_dur,0,1,cutin),
                            np.zeros(this_duration-2*method_dur),
                            dynamic(-method_args['scale']*np.cos(theta),method_dur,0,0,cutout)])
        elif method_args['motion'] == 'leap': # >0<
            D1 = np.hstack([dynamic(method_args['scale']*np.sin(theta),method_dur,0,1,cutin),
                            np.zeros(this_duration-2*method_dur),
                            dynamic(method_args['scale']*np.sin(theta),method_dur,0,0,cutout)])
            D2 = np.hstack([dynamic(method_args['scale']*np.cos(theta),method_dur,0,1,cutin),
                            np.zeros(this_duration-2*method_dur),
                            dynamic(method_args['scale']*np.cos(theta),method_dur,0,0,cutout)])
        # 实验性质的功能，想必不可能真的有人用这么鬼畜的效果吧
        elif method_args['motion'] == 'circular': 
            theta_timeline = (
                np
                .repeat(self.dynamic_globals['formula'](0-theta,2*np.pi-theta,method_dur),np.ceil(this_duration/method_dur).astype(int))
                .reshape(method_dur,np.ceil(this_duration/method_dur).astype(int))
                .transpose().ravel())[0:this_duration]
            D1 = np.sin(theta_timeline)*method_args['scale']
            D2 = -np.cos(theta_timeline)*method_args['scale']
        else:
            pos_timeline = 'NA'
            return alpha_timeline,pos_timeline
        pos_timeline = concat_xy(D1,D2)
        return alpha_timeline,pos_timeline
    # 手动换行的l2l
    def get_l2l(self,ts,text_dur,this_duration) -> np.ndarray:
        lines = ts.split('#')
        wc_list = []
        len_this = 0
        for x,l in enumerate(lines): #x是井号的数量
            len_this = len_this +len(l)+1 #当前行的长度
            #print(len_this,len(l),x,ts[0:len_this])
            wc_list.append(np.ones(text_dur*len(l))*len_this)
        try:
            wc_list.append(np.ones(this_duration - (len(ts)-x)*text_dur)*len(ts)) #this_duration > est # 1.6.1 update
            word_count_timeline = np.hstack(wc_list)
        except Exception: 
            word_count_timeline = np.hstack(wc_list) # this_duration < est
            word_count_timeline = word_count_timeline[0:this_duration]
        return word_count_timeline.astype(int)
    # log 解析器，返回（timeline,breakpoint,builtinmeida）[DataFrame]
    def parser(self,stdin_text) -> tuple:
        # section:小节号, BG: 背景，Am：立绘，Bb：气泡，BGM：背景音乐，Voice：语音，SE：音效
        render_arg = [
        'section',
        'BG1','BG1_a','BG1_c','BG1_p','BG2','BG2_a','BG2_c','BG2_p',
        'Am1','Am1_t','Am1_a','Am1_c','Am1_p','Am2','Am2_t','Am2_a','Am2_c','Am2_p','Am3','Am3_t','Am3_a','Am3_c','Am3_p',
        'AmS','AmS_t','AmS_a','AmS_c','AmS_p',
        'Bb','Bb_main','Bb_header','Bb_a','Bb_c','Bb_p',
        'BbS','BbS_main','BbS_header','BbS_a','BbS_c','BbS_p',
        'BGM','Voice','SE'
        ]
        # 断点文件: index + 1 == section, 因为还要包含尾部，所以总长比section长1
        break_point = pd.Series(0,index=range(0,len(stdin_text)+1),dtype=int)
        # break_point[0]=0
        # 视频+音轨 时间轴
        render_timeline = pd.DataFrame(dtype=str,columns=render_arg)
        BGM_queue = []
        # 当前背景、放置立绘、放置气泡
        this_background = "black"
        last_placed_animation_section = 0
        this_placed_animation = ('NA','replace',0,'NA') # am,method,method_dur,center
        last_placed_bubble_section = 0
        this_placed_bubble = ('NA','replace',0,'','','all',0,'NA') # bb,method,method_dur,HT,MT,tx_method,tx_dur,center
        # 内建的媒体，主要指BIA
        bulitin_media = {}

        for i,text in enumerate(stdin_text):
            # 空白行
            if text == '':
                break_point[i+1]=break_point[i]
                continue
            # 注释行 格式： # word
            elif text[0] == '#':
                break_point[i+1]=break_point[i]
                continue
            # 对话行 格式： [角色1,角色2(30).happy]<replace=30>:巴拉#巴拉#巴拉<w2w=1>
            elif (text[0] == '[') & (']' in text):
                try:
                    # 从ts长度预设的 this_duration
                    this_charactor,this_duration,am_method,am_dur,bb_method,bb_dur,ts,text_method,text_dur,this_sound = self.get_dialogue_arg(text)
                    # a 1.3 从音频中加载持续时长 {SE1;*78} 注意，这里只需要载入星标时间，检查异常不在这里做：
                    asterisk_timeset = RE_asterisk.findall('\t'.join(this_sound)) #在音频标志中读取
                    if len(asterisk_timeset) == 0:  #没检测到星标
                        pass
                    elif len(asterisk_timeset) == 1: #检查到一个星标
                        try:
                            asterisk_time = float(asterisk_timeset[0][-1]) #取第二个，转化为浮点数
                            this_duration = self.dynamic_globals['asterisk_pause'] + np.ceil((asterisk_time)*self.frame_rate).astype(int) # a1.4.3 添加了句间停顿
                        except Exception:
                            print(WarningPrint('FailAster',str(i+1)))
                    else: #检测到复数个星标
                        raise ParserError('2muchAster',str(i+1))

                    # 确保时长不短于切换特效时长
                    if this_duration<(2*max(am_dur,bb_dur)+1):
                        this_duration = 2*max(am_dur,bb_dur)+1

                    # 建立本小节的timeline文件
                    this_timeline=pd.DataFrame(index=range(0,this_duration),dtype=str,columns=render_arg)
                    this_timeline['BG2'] = this_background
                    this_timeline['BG2_a'] = 100
                    # 载入切换效果
                    alpha_timeline_A,pos_timeline_A = self.ambb_methods(am_method,am_dur,this_duration,i)
                    alpha_timeline_B,pos_timeline_B = self.ambb_methods(bb_method,bb_dur,this_duration,i)
                    #各个角色：
                    if len(this_charactor) > 3:
                        raise ParserError('2muchChara',str(i+1))
                    for k,charactor in enumerate(this_charactor[0:3]):
                        name,alpha,subtype= charactor
                        # 处理空缺参数
                        if subtype == '':
                            subtype = '.default'
                        if alpha == '':
                            alpha = -1
                        else:
                            alpha = int(alpha[1:-1])
                        # 在角色表中找到指定角色 this_char_series -> pd.Series
                        try:
                            this_char_series = self.charactor_table.loc[name+subtype]
                        except KeyError as E: # 在角色表里面找不到name，raise在这里！
                            raise ParserError('UndefName',name+subtype,str(i+1),E)
                        # 如果index存在重复值，则this_char_series不是一个 Series # 在这里处理的角色表index重复值，之后不再考虑这个异常
                        if type(this_char_series) is not pd.Series:
                            raise ParserError('DupSubtype',name+subtype)
                        
                        # 立绘的参数
                        this_am = this_char_series['Animation']
                        this_timeline['Am'+str(k+1)] = this_am                        
                        # 动画帧的参数（tick）
                        if (this_am!=this_am) | (this_am=='NA'):# this_am 可能为空的，需要先处理这种情况！
                            this_timeline['Am'+str(k+1)+'_t'] = 0
                            this_timeline['Am'+str(k+1)+'_c'] = 'NA'
                        else:
                            try:
                                this_timeline['Am'+str(k+1)+'_t'] = eval('{am}.get_tick({dur})'.format(am=this_am,dur=this_duration))
                                this_timeline['Am'+str(k+1)+'_c'] = str(eval(this_am+'.pos'))
                            except NameError as E: # 指定的am没有定义！
                                raise ParserError('UndefAnime', this_am, name+subtype)
                        # 透明度参数（alpha）
                        if (alpha >= 0)&(alpha <= 100): # alpha 1.8.8 如果有指定合法的透明度，则使用指定透明度
                            this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*alpha
                        else: # 如果没有指定透明度
                            if k == 0: # 如果是首要角色，透明度为100
                                this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*100
                            else: # 如果是次要角色，透明度为secondary_alpha，默认值60
                                this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*self.dynamic_globals['secondary_alpha'] 
                        # 位置参数（pos)
                        this_timeline['Am'+str(k+1)+'_p'] = pos_timeline_A
                        # 气泡的参数
                        if k == 0:
                            this_bb = this_char_series['Bubble']
                            # 主要角色一定要有bubble！，次要的可用没有
                            if (this_bb!=this_bb) | (this_bb=='NA'):
                                raise ParserError('CharaNoBb',name+subtype,str(i+1))
                            # 获取目标的头文本
                            try:
                                # 存在:分隔，说明是聊天窗类，始终取:前面的内容识别为气泡
                                if ':' in this_bb:
                                    chatwindow_key = this_bb.split(':')[1]
                                    this_bb = this_bb.split(':')[0]
                                    # 聊天窗类的target采用子气泡的target
                                    bubble_obj = eval(this_bb)
                                    try:
                                        targets = bubble_obj.sub_Bubble[chatwindow_key].target
                                    except KeyError as E: # 指定的Key不存在！
                                        raise ParserError('InvalidKey', chatwindow_key, this_bb)
                                else:
                                    bubble_obj = eval(this_bb)
                                    if type(bubble_obj) is ChatWindow:
                                        # targets = bubble_obj.target ; AttributeError: 'ChatWindow' object has no attribute 'target'
                                        raise ParserError('CWUndepend', this_bb)
                                    elif type(bubble_obj) in [Bubble,Balloon,DynamicBubble]:
                                        targets = bubble_obj.target
                                    else:
                                        raise ParserError('NotBubble', this_bb, name+subtype)
                                # Bubble,DynamicBubble类：只有一个头文本
                                if type(bubble_obj) in [Bubble,DynamicBubble]:
                                    target_text = this_char_series[targets]
                                # Balloon 类：有若干个头文本，targets是一个list,用 | 分隔
                                elif type(bubble_obj) is Balloon:
                                    target_text = '|'.join(this_char_series[targets].values)
                                # ChatWindow 类：只有一个头文本，头文本不能包含|和#，还需要附上key
                                elif type(bubble_obj) is ChatWindow:
                                    if ('|' in this_char_series[targets]) | ('#' in this_char_series[targets]):
                                        raise ParserError('InvSymbpd',name+subtype)
                                    else:
                                        target_text = chatwindow_key+'#'+this_char_series[targets]
                                else:
                                    # raise NameError('Media object "' + this_bb + '" is not a Bubble!')
                                    raise ParserError('NotBubble', this_bb, name+subtype)
                            except NameError as E: # 指定的bb没有定义！
                                raise ParserError('UndefBubble', this_bb, name+subtype)
                            except KeyError as E: # 指定的target不存在！
                                raise ParserError('TgNotExist', E, this_bb)
                            # 针对文本内容的警告和报错
                            try:
                                this_line_limit = bubble_obj.MainText.line_limit
                            except AttributeError: # 'NoneType' object has no attribute 'line_limit'
                                if type(bubble_obj) is ChatWindow:
                                    this_line_limit = bubble_obj.sub_Bubble[chatwindow_key].MainText.line_limit
                                else:
                                    raise ParserError('MissMainTx',this_bb)
                            # ts或者target_text里面有非法字符，双引号，反斜杠
                            if ('"' in target_text) | ('\\' in target_text) | ('"' in ts) | ('\\' in ts):
                                raise ParserError('InvSymbqu',str(i+1))
                            # 未声明手动换行
                            if ('#' in ts)&(ts[0]!='^'):
                                ts = '^' + ts # 补齐申明符号
                                print(WarningPrint('UndeclMB',str(i+1)))
                            #行数过多的警告
                            if (len(ts)>this_line_limit*4) | (len(ts.split('#'))>4):
                                print(WarningPrint('More4line',str(i+1)))
                            # 手动换行的字数超限的警告
                            if ((ts[0]=='^')|('#' in ts))&(np.frompyfunc(len,1,1)(ts.replace('^','').split('#')).max()>this_line_limit):
                                print(WarningPrint('MBExceed',str(i+1)))
                            # 赋值给当前时间轴的Bb轨道
                            this_timeline['Bb'] = this_bb
                            this_timeline['Bb_main'] = ts
                            this_timeline['Bb_header'] = target_text
                            this_timeline['Bb_a'] = alpha_timeline_B*100
                            this_timeline['Bb_p'] = pos_timeline_B
                            this_timeline['Bb_c'] = str(eval(this_bb+'.pos'))

                    # 文字显示的参数
                    if text_method == 'all':
                        if text_dur == 0:
                            pass
                        else:
                            this_timeline.loc[0:text_dur,'Bb_main'] = '' #将前n帧的文本设置为空白
                    elif text_method == 'w2w':
                        word_count_timeline = np.arange(0,this_duration,1)//text_dur+1
                        this_timeline['Bb_main'] = UF_cut_str(this_timeline['Bb_main'],word_count_timeline)
                    elif text_method == 'l2l': 
                        if ((ts[0]=='^')|('#' in ts)): #如果是手动换行的列
                            word_count_timeline = self.get_l2l(ts,text_dur,this_duration) # 不保证稳定呢！
                        else:
                            line_limit = eval(this_timeline['Bb'][1]+'.MainText.line_limit') #获取主文本对象的line_limit参数 # 为什么是【1】？？
                            word_count_timeline = (np.arange(0,this_duration,1)//(text_dur*line_limit)+1)*line_limit
                        this_timeline['Bb_main'] = UF_cut_str(this_timeline['Bb_main'],word_count_timeline)
                    else:
                        raise ParserError('UnrecTxMet', text_method, str(i+1))
                    # 如果是ChatWindow
                    if type(bubble_obj) is ChatWindow:
                        # 记录本次需要添加的文本（最后一帧）
                        maintext_end = this_timeline['Bb_main'].values[-1]
                        header_end = this_timeline['Bb_header'].values[-1]
                        this_timeline['Bb_main'].values[-1]
                        this_timeline['Bb_header'].values[-1]
                        # 更新timeline对象，追加历史记录
                        this_timeline['Bb_header'] = bubble_obj.UF_add_header_text(this_timeline['Bb_header'])
                        this_timeline['Bb_main'] = bubble_obj.UF_add_main_text(this_timeline['Bb_main'])
                        # 更新bubble对象的历史记录
                        bubble_obj.append(maintext_end,header_end)
                    #音频信息
                    for sound in this_sound: #this_sound = ['{SE_obj;30}','{SE_obj;30}']
                        try:
                            se_obj,delay = sound[1:-1].split(';')#sound = '{SE_obj;30}'# 由于这个地方，音频框的分隔符号只能用分号
                        except Exception: # #sound = '{SE_obj}'
                            delay = '0'
                            se_obj = sound[1:-1] # 去掉花括号
                        if delay == '':
                            delay = 0
                        elif '*' in delay: # 如果是星标时间 delay 是asterisk_pause的一半
                            delay = int(self.dynamic_globals['asterisk_pause']/2)
                        elif int(delay) >= this_duration: # delay 不能比一个单元还长
                            delay = this_duration-1
                        else:
                            delay = int(delay)
                        if '*' in se_obj:
                            raise ParserError('UnpreAster', str(i+1))
                        if se_obj in self.media_list: # 如果delay在媒体里已经定义，则视为SE
                            this_timeline.loc[delay,'SE'] = se_obj
                        elif os.path.isfile(se_obj[1:-1]) == True: #或者指向一个确定的文件，则视为语音
                            this_timeline.loc[delay,'Voice'] = se_obj
                        elif se_obj in ['NA','']: # 如果se_obj是空值或NA，则什么都不做 alpha1.8.5
                            pass
                        else:
                            raise ParserError('SEnotExist', se_obj, str(i+1))
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0) #从BGM_queue里取第一个出来 alpha 1.13.5
                    # 时间轴延长
                    this_timeline['section'] = i
                    break_point[i+1]=break_point[i]+this_duration
                    this_timeline.index = range(break_point[i],break_point[i+1])
                    render_timeline = pd.concat([render_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrDial', str(i+1))
            # 背景设置行，格式： <background><black=30>:BG_obj
            elif text[0:12] == '<background>':
                try:
                    bgc,method,method_dur = self.get_placeobj_arg(text)
                    if bgc in self.media_list: # 检查是否是已定义的对象
                        next_background=bgc
                    else:
                        raise ParserError('UndefBackGd',bgc,str(i+1))
                    if method=='replace': #replace 改为立刻替换 并持续n秒
                        this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                        this_timeline['BG2']=next_background
                        this_timeline['BG2_a']=100
                        this_timeline['BG2_c']=str(eval(next_background+'.pos'))
                    elif method=='delay': # delay 等价于原来的replace，延后n秒，然后替换
                        this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                        this_timeline['BG2']=this_background
                        this_timeline['BG2_a']=100
                        this_timeline['BG2_c']=str(eval(this_background+'.pos'))
                    # 'black','white'
                    elif method in ['black','white']:
                        this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                        # 下图层BG2，前半程是旧图层，后半程是新图层，透明度均为100
                        this_timeline.loc[:(method_dur//2),'BG2'] = this_background
                        this_timeline.loc[(method_dur//2):,'BG2'] = next_background
                        this_timeline.loc[:(method_dur//2),'BG2_c']=str(eval(this_background+'.pos'))
                        this_timeline.loc[(method_dur//2):,'BG2_c']=str(eval(next_background+'.pos'))
                        this_timeline['BG2_a'] = 100
                        # 上图层BG1，是指定的颜色，透明度是100-abs(formula(100,-100,dur))
                        this_timeline['BG1'] = method
                        this_timeline['BG1_c']='(0,0)'
                        this_timeline['BG1_a']=100-np.abs(self.dynamic_globals['formula'](-100,100,method_dur))
                        pass
                    elif method in ['cross','push','cover']: # 交叉溶解，黑场，白场，推，覆盖
                        this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                        this_timeline['BG1']=next_background
                        this_timeline['BG1_c']=str(eval(next_background+'.pos'))
                        this_timeline['BG2']=this_background
                        this_timeline['BG2_c']=str(eval(this_background+'.pos'))
                        if method == 'cross':
                            this_timeline['BG1_a']=self.dynamic_globals['formula'](0,100,method_dur)
                            this_timeline['BG2_a']=100
                        elif method in ['push','cover']:
                            this_timeline['BG1_a']=100
                            this_timeline['BG2_a']=100
                            if method == 'push': # 新背景从右侧把旧背景推出去
                                this_timeline['BG1_p'] = concat_xy(self.dynamic_globals['formula'](self.Width,0,method_dur),np.zeros(method_dur))
                                this_timeline['BG2_p'] = concat_xy(self.dynamic_globals['formula'](0,-self.Width,method_dur),np.zeros(method_dur))
                            else: #cover 新背景从右侧进来叠在原图上面
                                this_timeline['BG1_p'] = concat_xy(self.dynamic_globals['formula'](self.Width,0,method_dur),np.zeros(method_dur))
                                this_timeline['BG2_p'] = 'NA'
                    else:
                        raise ParserError('SwitchBkGd',method,str(i+1))
                    this_background = next_background #正式切换背景
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0)
                    # 时间轴延长
                    this_timeline['section'] = i
                    break_point[i+1]=break_point[i]+len(this_timeline.index)
                    this_timeline.index = range(break_point[i],break_point[i+1])
                    render_timeline = pd.concat([render_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrBkGd',str(i+1))
            # 常驻立绘设置行，格式：<animation><black=30>:(Am_obj,Am_obj2)
            elif text[0:11] == '<animation>':
                # 处理上一次的
                last_placed_index = range(break_point[last_placed_animation_section],break_point[i])
                this_duration = len(last_placed_index)
                this_am,am_method,am_dur,am_center = this_placed_animation
                # 如果place的this_duration小于切换时间，则清除动态切换效果
                if (this_duration<(2*am_dur+1)) & (this_am != 'NA'):
                    print(i+1)
                    print(WarningPrint('PAmMetDrop'))
                    am_dur = 0
                    am_method = 'replace'
                render_timeline.loc[last_placed_index,'AmS'] = this_am
                # this_am 可能为空的，需要先处理这种情况！
                if (this_am!=this_am) | (this_am=='NA'):
                    render_timeline.loc[last_placed_index,'AmS_t'] = 0
                    render_timeline.loc[last_placed_index,'AmS_a'] = 0
                    render_timeline.loc[last_placed_index,'AmS_c'] = 'NA'
                    render_timeline.loc[last_placed_index,'AmS_p'] = 'NA'
                else:
                    alpha_timeline_A,pos_timeline_A = self.ambb_methods(am_method,am_dur,this_duration,i)
                    render_timeline.loc[last_placed_index,'AmS_a'] = alpha_timeline_A*100
                    render_timeline.loc[last_placed_index,'AmS_p'] = pos_timeline_A
                    render_timeline.loc[last_placed_index,'AmS_t'] = eval('{am}.get_tick({dur})'.format(am=this_am,dur=this_duration))
                    render_timeline.loc[last_placed_index,'AmS_c'] = am_center
                # 获取本次的
                try:
                    amc,method,method_dur = self.get_placeobj_arg(text)
                    # 获取立绘列表，检查立绘是否定义
                    if (amc[0] == '(') and (amc[-1] == ')'):
                        amc_list = amc[1:-1].split(',')
                        grouped_ampos = []
                        for amo in amc_list:
                            # 检验指定的名称是否是Animation
                            if amo not in self.media_list:
                                raise ParserError('UndefPAnime',amo,str(i+1))
                            else:
                                grouped_ampos.append(str(eval(amo).pos))
                        # 新建GA
                        Auto_media_name = 'BIA_'+str(i+1)
                        code_to_run = 'global {media_name} ;{media_name} = GroupedAnimation(subanimation_list={subanime},subanimation_current_pos={animepos})'
                        code_to_run = code_to_run.format(media_name=Auto_media_name,subanime='['+','.join(amc_list)+']',animepos='['+','.join(grouped_ampos)+']')
                        # print(code_to_run)
                        # 执行
                        exec(code_to_run)
                        # 添加到media_list和bulitin_media
                        self.media_list.append(Auto_media_name)
                        bulitin_media[Auto_media_name] = code_to_run
                        # 标记为下一次
                        this_placed_animation = (Auto_media_name,method,method_dur,'(0,0)') # 因为place的应用是落后于设置的，因此需要保留c参数！
                        last_placed_animation_section = i
                    # 只有一个立绘
                    elif amc in self.media_list:
                        if type(eval(amc)) in [Animation,BuiltInAnimation,GroupedAnimation]:
                            this_placed_animation = (amc,method,method_dur,str(eval(amc).pos))
                            last_placed_animation_section = i
                        else: # 如果type 不是 Animation 类，也 UndefPAnime
                            raise ParserError('UndefPAnime',amc,str(i+1))
                    # 取消place立绘
                    elif amc == 'NA':
                        this_placed_animation = ('NA','replace',0,'(0,0)')
                        last_placed_animation_section = i
                    else:
                        raise ParserError('UndefPAnime',amc,str(i+1))
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrAnime',str(i+1))
            # 常驻气泡设置行，格式：<bubble><black=30>:Bubble_obj("Header_text","Main_text",<text_method>)
            elif text[0:8] == '<bubble>':
                # 处理上一次的
                last_placed_index = range(break_point[last_placed_bubble_section],break_point[i])
                this_duration = len(last_placed_index)
                # bb,method,method_dur,HT,MT,text_method,tx_dur,center
                this_bb,bb_method,bb_dur,this_hd,this_tx,text_method,text_dur,bb_center = this_placed_bubble
                # 如果place的this_duration小于切换时间，则清除动态切换效果
                if (this_duration<(2*bb_dur+1)) & (this_bb != 'NA'):
                    print(WarningPrint('PBbMetDrop'))
                    bb_dur = 0
                    bb_method = 'replace'
                # 'BbS','BbS_main','BbS_header','BbS_a','BbS_c','BbS_p',
                render_timeline.loc[last_placed_index,'BbS'] = this_bb
                # this_bb 可能为空的，需要先处理这种情况！
                if (this_bb!=this_bb) | (this_bb=='NA'):
                    render_timeline.loc[last_placed_index,'BbS_main'] = ''
                    render_timeline.loc[last_placed_index,'BbS_header'] = ''
                    render_timeline.loc[last_placed_index,'BbS_a'] = 0
                    render_timeline.loc[last_placed_index,'BbS_c'] = 'NA'
                    render_timeline.loc[last_placed_index,'BbS_p'] = 'NA'
                else:
                    # 
                    alpha_timeline_B,pos_timeline_B = self.ambb_methods(bb_method,bb_dur,this_duration,i)
                    render_timeline.loc[last_placed_index,'BbS_a'] = alpha_timeline_B*100
                    render_timeline.loc[last_placed_index,'BbS_c'] = bb_center
                    render_timeline.loc[last_placed_index,'BbS_p'] = pos_timeline_B
                    render_timeline.loc[last_placed_index,'BbS_main'] = this_tx
                    render_timeline.loc[last_placed_index,'BbS_header'] = this_hd
                    # 文字显示的参数
                    if text_method == 'all':
                        if text_dur == 0:
                            pass
                        else:
                            # 将前n帧的文本设置为空白
                            render_timeline.loc[last_placed_index[0]:(last_placed_index[0]+text_dur),'BbS_main'] = ''
                    elif text_method == 'w2w':
                        word_count_timeline = np.arange(0,this_duration,1)//text_dur+1
                        render_timeline.loc[last_placed_index,'BbS_main'] = UF_cut_str(render_timeline.loc[last_placed_index,'BbS_main'],word_count_timeline)
                    elif text_method == 'l2l': 
                        if ((this_tx[0]=='^')|('#' in this_tx)): #如果是手动换行的列
                            word_count_timeline = self.get_l2l(this_tx,text_dur,this_duration) # 不保证稳定呢！
                        else:
                            line_limit = eval(this_bb+'.MainText.line_limit') #获取主文本对象的line_limit参数
                            word_count_timeline = (np.arange(0,this_duration,1)//(text_dur*line_limit)+1)*line_limit
                        render_timeline.loc[last_placed_index,'BbS_main'] = UF_cut_str(render_timeline.loc[last_placed_index,'BbS_main'],word_count_timeline)
                    else:
                        pass
                # 获取本次的
                try:
                    # type: str,str,int
                    bbc,method,method_dur = self.get_placeobj_arg(text)
                    # 如果是设置为NA
                    if bbc == 'NA':
                        # bb,method,method_dur,HT,MT,tx_method,tx_dur,center
                        this_placed_bubble = ('NA','replace',0,'','','all',0,'NA')
                        last_placed_bubble_section = i
                    # 如果是一个合法的Bubble表达式
                    else:
                        try:
                            this_bb,this_hd,this_tx,this_method_label,this_tx_method,this_tx_dur = RE_bubble.findall(bbc)[0]
                            # 检查Bubble类媒体的可用性
                            if this_bb not in self.media_list:
                                raise NameError(this_bb)
                            elif type(eval(this_bb)) not in [Bubble,Balloon,DynamicBubble,ChatWindow]:
                                raise NameError(this_bb)
                            else:
                                pass
                            # 检查，tx_method 的合法性
                            # 缺省文字效果
                            if this_method_label == '':
                                this_method_label = self.dynamic_globals['tx_method_default']
                                this_tx_method,this_tx_dur = RE_modify.findall(this_method_label)[0] #<black=\d+> 
                                # 直接获取下来的的 <all=0> all =0
                                this_tx_dur = this_tx_dur[1:]
                            elif this_tx_dur == '':
                                this_tx_dur = self.dynamic_globals['tx_dur_default']
                            # 如果是非法的
                            if this_tx_method not in ['all','w2w','l2l']:
                                raise ValueError(this_method_label)
                            else:
                                this_placed_bubble = (this_bb,method,method_dur,this_hd,this_tx,this_tx_method,int(this_tx_dur),str(eval(this_bb).pos))
                                last_placed_bubble_section = i
                        except IndexError:
                            raise ParserError('InvaPBbExp',bbc,str(i+1))
                        except ValueError: # ValueError: invalid literal for int() with base 10: 'asd'
                            raise ParserError('UnrecPBbTxM',this_method_label,str(i+1))
                        except NameError as E:
                            raise ParserError('UndefPBb',this_bb,str(i+1))
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrBb',str(i+1))
            # 参数设置行，格式：<set:speech_speed>:220
            elif (text[0:5] == '<set:') & ('>:' in text):
                try:
                    target,args = self.get_seting_arg(text)
                    # 整数类型的变量
                    if target in ['am_dur_default','bb_dur_default','bg_dur_default','tx_dur_default','speech_speed','asterisk_pause','secondary_alpha']:
                        try: 
                            args = int(args)
                            if args < 0:
                                raise ParserError('invalid args')
                            else:
                                self.dynamic_globals[target] = args
                        except Exception:
                            print(WarningPrint('Set2Invalid',target,args))
                    # <method>类型的变量
                    elif target in ['am_method_default','bb_method_default','bg_method_default','tx_method_default']:
                        # exec("global {0} ; {0} = {1}".format(target,'\"'+args+'\"')) # 当作文本型，无论是啥都接受
                        self.dynamic_globals[target] = args
                    # BGM路径或者对象类的变量
                    elif target == 'BGM':
                        if args in self.media_list:
                            BGM_queue.append(args)
                        elif os.path.isfile(args[1:-1]):
                            BGM_queue.append(args)
                        elif args == 'stop':
                            BGM_queue.append(args)
                        else:
                            raise ParserError('UndefBGM',args,str(i+1))
                    # formula类型的变量
                    elif target == 'formula':
                        if args in formula_available.keys():
                            self.dynamic_globals['formula'] = formula_available[args]
                        elif args[0:6] == 'lambda':
                            try:
                                self.dynamic_globals['formula'] = eval(args)
                                print(WarningPrint('UseLambda',str(self.dynamic_globals['formula'](0,1,2)),str(i+1)))                          
                            except Exception:
                                raise ParserError('UnspFormula',args,str(i+1))
                        else:
                            raise ParserError('UnspFormula',args,str(i+1))
                    # 枚举类型的变量
                    elif target == 'inline_method_apply':
                        if args in ['animation','bubble','both','none']:
                            self.dynamic_globals['inline_method_apply'] = args
                        else:
                            print(WarningPrint('Set2Invalid',target,args))
                    # 角色表中的自定义列
                    elif '.' in target:
                        target_split = target.split('.')
                        target_column = target_split[-1]
                        # 如果目标列不存在于角色表
                        if target_column not in self.charactor_table.columns:
                            raise ParserError('ModUndefCol',target_column)
                        # 如果尝试修改受保护的列
                        elif target_column in ['Name','Subtype','Animation','Bubble','Voice','SpeechRate','PitchRate']:
                            raise ParserError('ModProtcCol',target_column)
                        # 如果只指定了一个角色名和列名，则变更应用于角色名下所有的subtype
                        if len(target_split) == 2:
                            name = target_split[0]
                            if (name in self.charactor_table['Name'].values):
                                try:
                                    self.charactor_table.loc[self.charactor_table['Name']==name,target_column] = args
                                except Exception as E:
                                    raise ParserError('ModCTError',target,E)
                            else:
                                raise ParserError('UndefTgName',name,str(i+1))
                        # 如果只指定了角色名、差分名和列名，则变更仅应用于该subtype
                        elif len(target_split) == 3:
                            name,subtype = target_split[0:2]
                            if (name+'.'+subtype in self.charactor_table.index):
                                try:
                                    self.charactor_table.loc[name+'.'+subtype, target_column] = args
                                except Exception as E:
                                    raise ParserError('ModCTError',target,E)
                            else:
                                raise ParserError('UndefTgSubt',name+'.'+subtype,str(i+1))
                        # 如果超过4个指定项目，无法解析，抛出ParserError(不被支持的参数)
                        else:
                            raise ParserError('UnsuppSet',target,str(i+1))
                    # 重定位FreePos
                    elif target in self.media_list:
                        if type(eval(target)) is FreePos:
                            try:
                                eval(target).set(eval(args))
                            except Exception as E:
                                raise ParserError('IvSyFrPos',args,target,E)
                        else:
                            raise ParserError('UnsuppSet',target,str(i+1))
                    # 不被支持的参数
                    else:
                        raise ParserError('UnsuppSet',target,str(i+1))
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrSet',str(i+1))
            # 清除行，仅适用于ChatWindow
            elif (text[0:8] == '<clear>:'):
                clear_target_name = text[8:]
                if clear_target_name not in self.media_list:
                    print(WarningPrint('ClearUndef',clear_target_name))
                else:
                    clear_target_obj = eval(clear_target_name)
                    if type(clear_target_obj) is ChatWindow:
                        clear_target_obj.clear()
                    else:
                        print(WarningPrint('ClearNotCW',clear_target_name))
            # 预设动画，损失生命
            elif text[0:11] == '<hitpoint>:':
                try:
                    # 载入参数
                    name_tx,heart_max,heart_begin,heart_end = RE_hitpoint.findall(text)[0]
                    heart_max = int(heart_max)
                    heart_begin = int(heart_begin)
                    heart_end = int(heart_end)
                    # 建立小节
                    this_timeline=pd.DataFrame(index=range(0,self.frame_rate*4),dtype=str,columns=render_arg)
                    # 背景
                    #alpha_timeline,pos_timeline = ambb_methods('black',method_dur=frame_rate//2,this_duration=frame_rate*4,i=i)
                    alpha_timeline = np.hstack([self.dynamic_globals['formula'](0,1,self.frame_rate//2),np.ones(self.frame_rate*3-self.frame_rate//2),self.dynamic_globals['formula'](1,0,self.frame_rate)])
                    this_timeline['BG1'] = 'black' # 黑色背景
                    this_timeline['BG1_a'] = alpha_timeline * 80
                    this_timeline['BG2'] = this_background
                    this_timeline['BG2_a'] = 100
                    # 新建内建动画
                    Auto_media_name = 'BIA_'+str(i+1)
                    code_to_run = 'global {media_name}_{layer} ;{media_name}_{layer} = BuiltInAnimation(anime_type="hitpoint",anime_args=("{name}",{hmax},{hbegin},{hend}),screensize = {screensize},layer={layer})'
                    code_to_run_0 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str((self.Width,self.Height)),layer='0')
                    code_to_run_1 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str((self.Width,self.Height)),layer='1')
                    code_to_run_2 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str((self.Width,self.Height)),layer='2')
                    exec(code_to_run_0) # 灰色框
                    exec(code_to_run_1) # 留下的血
                    exec(code_to_run_2) # 丢掉的血
                    self.media_list.append(Auto_media_name+'_0')
                    self.media_list.append(Auto_media_name+'_1')
                    self.media_list.append(Auto_media_name+'_2')
                    bulitin_media[Auto_media_name+'_0'] = code_to_run_0
                    bulitin_media[Auto_media_name+'_1'] = code_to_run_1
                    bulitin_media[Auto_media_name+'_2'] = code_to_run_2
                    # 动画参数
                    this_timeline['Am3'] = Auto_media_name+'_0'
                    this_timeline['Am3_a'] = alpha_timeline * 100
                    this_timeline['Am3_t'] = 0
                    this_timeline['Am3_p'] = 'NA'
                    this_timeline['Am2'] = Auto_media_name+'_1'
                    this_timeline['Am2_a'] = alpha_timeline * 100
                    this_timeline['Am2_t'] = 0
                    this_timeline['Am2_p'] = 'NA'
                    this_timeline['Am1'] = Auto_media_name+'_2'
        
                    if heart_begin > heart_end: # 掉血模式
                        this_timeline['Am1_a'] = np.hstack([self.dynamic_globals['formula'](0,100,self.frame_rate//2),
                                                            np.ones(self.frame_rate*2-self.frame_rate//2)*100,
                                                            left(100,0,self.frame_rate//2),
                                                            np.zeros(self.frame_rate*2-self.frame_rate//2)]) #0-0.5出现，2-2.5消失
                        this_timeline['Am1_p'] = concat_xy(np.zeros(self.frame_rate*4),
                                                        np.hstack([np.zeros(self.frame_rate*2), # 静止2秒
                                                                    left(0,-int(self.Height*0.3),self.frame_rate//2), # 半秒切走
                                                                    int(self.Height*0.3)*np.ones(self.frame_rate*2-self.frame_rate//2)])) #1.5秒停止
                        this_timeline['Am1_t'] = 0
                    else: # 回血模式
                        this_timeline['Am1_a'] = alpha_timeline * 100 # 跟随全局血量
                        this_timeline['Am1_p'] = 'NA' # 不移动
                        this_timeline['Am1_t'] = np.hstack([np.zeros(self.frame_rate*1), # 第一秒静止
                                                            np.arange(0,self.frame_rate,1), # 第二秒播放
                                                            np.ones(self.frame_rate*2)*(self.frame_rate-1)]) # 后两秒静止
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0) #从BGM_queue里取出来一个 alpha 1.8.5
                    # 时间轴延长
                    this_timeline['section'] = i
                    break_point[i+1]=break_point[i]+len(this_timeline.index)
                    this_timeline.index = range(break_point[i],break_point[i+1])
                    render_timeline = pd.concat([render_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrHit',str(i+1))
            # 预设动画，骰子
            elif text[0:7] == '<dice>:':
                try:
                    # 获取参数
                    dice_args = RE_dice.findall(text[7:])
                    if len(dice_args) == 0:
                        raise ParserError('NoDice')
                    # 建立小节
                    this_timeline=pd.DataFrame(index=range(0,self.frame_rate*5),dtype=str,columns=render_arg) # 5s
                    # 背景
                    alpha_timeline = np.hstack([self.dynamic_globals['formula'](0,1,self.frame_rate//2),np.ones(self.frame_rate*4-self.frame_rate//2),self.dynamic_globals['formula'](1,0,self.frame_rate)])
                    this_timeline['BG1'] = 'black' # 黑色背景
                    this_timeline['BG1_a'] = alpha_timeline * 80
                    this_timeline['BG2'] = this_background
                    this_timeline['BG2_a'] = 100
                    # 新建内建动画
                    Auto_media_name = 'BIA_'+str(i+1)
                    code_to_run = 'global {media_name}_{layer} ;{media_name}_{layer} = BuiltInAnimation(anime_type="dice",anime_args={dice_args},screensize = {screensize},layer={layer})'
                    code_to_run_0 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str((self.Width,self.Height)),layer='0')
                    code_to_run_1 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str((self.Width,self.Height)),layer='1')
                    code_to_run_2 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str((self.Width,self.Height)),layer='2')
                    exec(code_to_run_0) # 描述和检定值
                    exec(code_to_run_1) # 老虎机
                    exec(code_to_run_2) # 输出结果
                    self.media_list.append(Auto_media_name+'_0')
                    self.media_list.append(Auto_media_name+'_1')
                    self.media_list.append(Auto_media_name+'_2')
                    bulitin_media[Auto_media_name+'_0'] = code_to_run_0
                    bulitin_media[Auto_media_name+'_1'] = code_to_run_1
                    bulitin_media[Auto_media_name+'_2'] = code_to_run_2
                    # 动画参数0
                    this_timeline['Am3'] = Auto_media_name+'_0'
                    this_timeline['Am3_a'] = alpha_timeline * 100
                    this_timeline['Am3_t'] = 0
                    this_timeline['Am3_p'] = 'NA'
                    # 1
                    this_timeline['Am2'] = np.hstack([np.repeat(Auto_media_name+'_1',int(self.frame_rate*2.5)),np.repeat('NA',self.frame_rate*5-int(self.frame_rate*2.5))]) # 2.5s
                    this_timeline['Am2_a'] = np.hstack([self.dynamic_globals['formula'](0,100,self.frame_rate//2),
                                                        np.ones(int(self.frame_rate*2.5)-2*(self.frame_rate//2))*100,
                                                        self.dynamic_globals['formula'](100,0,self.frame_rate//2),
                                                        np.zeros(self.frame_rate*5-int(self.frame_rate*2.5))])
                    this_timeline['Am2_t'] = np.hstack([np.arange(0,int(self.frame_rate*2.5)),np.zeros(self.frame_rate*5-int(self.frame_rate*2.5))])
                    this_timeline['Am2_p'] = 'NA'
                    # 2
                    this_timeline['Am1'] = np.hstack([np.repeat('NA',self.frame_rate*5-int(self.frame_rate*2.5)),np.repeat(Auto_media_name+'_2',int(self.frame_rate*2.5))])
                    this_timeline['Am1_a'] = np.hstack([np.zeros(self.frame_rate*5-int(self.frame_rate*2.5)),
                                                        self.dynamic_globals['formula'](0,100,self.frame_rate//2),
                                                        np.ones(int(self.frame_rate*2.5)-self.frame_rate//2-self.frame_rate)*100,
                                                        self.dynamic_globals['formula'](100,0,self.frame_rate)])
                    this_timeline['Am1_t'] = 0
                    this_timeline['Am1_p'] = 'NA'
                    # SE
                    this_timeline.loc[self.frame_rate//3,'SE'] = "'./media/SE_dice.wav'"
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0) #从BGM_queue里取第一个出来 alpha 1.13.5
                    # 时间轴延长
                    this_timeline['section'] = i
                    break_point[i+1]=break_point[i]+len(this_timeline.index)
                    this_timeline.index = range(break_point[i],break_point[i+1])
                    render_timeline = pd.concat([render_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrDice',str(i+1))
            # 等待行，停留在上一个小节的结束状态，不影响S图层
            elif text[0:7] == '<wait>:':
                # 获取参数
                try:
                    try:
                        this_dur = int(RE_wait.findall(text)[0])
                    except Exception as E:
                        raise ParserError('InvWaitArg',E)
                    # 持续指定帧，仅显示当前背景
                    this_timeline=pd.DataFrame(index=range(0,this_dur),dtype=str,columns=render_arg)
                    # 停留的帧：当前时间轴的最后一帧，不含S图层
                    wait_frame = render_timeline.iloc[-1].copy()
                    # 检查wait frame里面，有没有透明度为0，如果有则删除图层
                    for layer in self.zorder:
                        if wait_frame[layer+'_a'] == 0:
                            # 以防导出xml项目异常
                            wait_frame[layer] = 'NA'
                    # 应用
                    this_timeline[render_arg] = wait_frame
                    # BGM
                    if BGM_queue != []:
                        this_timeline.loc[0,'BGM'] = BGM_queue.pop(0)
                    # 时间轴延长
                    this_timeline['section'] = i
                    break_point[i+1]=break_point[i]+len(this_timeline.index)
                    this_timeline.index = range(break_point[i],break_point[i+1])
                    render_timeline = pd.concat([render_timeline,this_timeline],axis=0)
                    continue
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrWait',str(i+1))
            # 异常行，报出异常
            else:
                raise ParserError('UnrecLine',str(i+1))
            # 鲁棒性建议：把break_point的操作全部移入各个分支里独立处理，而不是靠continue
            break_point[i+1]=break_point[i]
        
        # 处理上一次的place最终一次：注意，这里已经是末端了
        try:
            # 处理上一次的place:AmS最终一次
            last_placed_index = range(break_point[last_placed_animation_section],break_point.iloc[-1])
            this_duration = len(last_placed_index)
            this_am,am_method,am_dur,am_center = this_placed_animation
            # 如果place的this_duration小于切换时间，则清除动态切换效果
            if (this_duration<(2*am_dur+1)) & (this_am != 'NA'):
                print(WarningPrint('PAmMetDrop'))
                am_dur = 0
                am_method = 'replace'
            render_timeline.loc[last_placed_index,'AmS'] = this_am
            # this_am 可能为空的，需要先处理这种情况！
            if (this_am!=this_am) | (this_am=='NA'):
                render_timeline.loc[last_placed_index,'AmS_t'] = 0
                render_timeline.loc[last_placed_index,'AmS_a'] = 0
                render_timeline.loc[last_placed_index,'AmS_c'] = 'NA'
                render_timeline.loc[last_placed_index,'AmS_p'] = 'NA'
            else:
                alpha_timeline_A,pos_timeline_A = self.ambb_methods(am_method,am_dur,this_duration,i)
                render_timeline.loc[last_placed_index,'AmS_a'] = alpha_timeline_A*100
                render_timeline.loc[last_placed_index,'AmS_p'] = pos_timeline_A
                render_timeline.loc[last_placed_index,'AmS_t'] = eval('{am}.get_tick({dur})'.format(am=this_am,dur=this_duration))
                render_timeline.loc[last_placed_index,'AmS_c'] = am_center

            # 处理上一次的place:BbS最终一次
            last_placed_index = range(break_point[last_placed_bubble_section],break_point.iloc[-1])
            this_duration = len(last_placed_index)
            # bb,method,method_dur,HT,MT,text_method,tx_dur,center
            this_bb,bb_method,bb_dur,this_hd,this_tx,text_method,text_dur,bb_center = this_placed_bubble
            # 如果place的this_duration小于切换时间，则清除动态切换效果
            if (this_duration<(2*bb_dur+1)) & (this_bb != 'NA'):
                print(WarningPrint('PBbMetDrop'))
                bb_dur = 0
                bb_method = 'replace'
            # 'BbS','BbS_main','BbS_header','BbS_a','BbS_c','BbS_p',
            render_timeline.loc[last_placed_index,'BbS'] = this_bb
            # this_bb 可能为空的，需要先处理这种情况！
            if (this_bb!=this_bb) | (this_bb=='NA'):
                render_timeline.loc[last_placed_index,'BbS_main'] = ''
                render_timeline.loc[last_placed_index,'BbS_header'] = ''
                render_timeline.loc[last_placed_index,'BbS_a'] = 0
                render_timeline.loc[last_placed_index,'BbS_c'] = 'NA'
                render_timeline.loc[last_placed_index,'BbS_p'] = 'NA'
            else:
                # 
                alpha_timeline_B,pos_timeline_B = self.ambb_methods(bb_method,bb_dur,this_duration,i)
                render_timeline.loc[last_placed_index,'BbS_a'] = alpha_timeline_B*100
                render_timeline.loc[last_placed_index,'BbS_c'] = bb_center
                render_timeline.loc[last_placed_index,'BbS_p'] = pos_timeline_B
                render_timeline.loc[last_placed_index,'BbS_main'] = this_tx
                render_timeline.loc[last_placed_index,'BbS_header'] = this_hd
                # 文字显示的参数
                if text_method == 'all':
                    if text_dur == 0:
                        pass
                    else:
                        # 将前n帧的文本设置为空白
                        render_timeline.loc[last_placed_index[0]:(last_placed_index[0]+text_dur),'BbS_main'] = ''
                elif text_method == 'w2w':
                    word_count_timeline = np.arange(0,this_duration,1)//text_dur+1
                    render_timeline.loc[last_placed_index,'BbS_main'] = UF_cut_str(render_timeline.loc[last_placed_index,'BbS_main'],word_count_timeline)
                elif text_method == 'l2l': 
                    if ((this_tx[0]=='^')|('#' in this_tx)): #如果是手动换行的列
                        word_count_timeline = self.get_l2l(this_tx,text_dur,this_duration) # 不保证稳定呢！
                    else:
                        line_limit = eval(this_bb+'.MainText.line_limit') #获取主文本对象的line_limit参数
                        word_count_timeline = (np.arange(0,this_duration,1)//(text_dur*line_limit)+1)*line_limit
                    render_timeline.loc[last_placed_index,'BbS_main'] = UF_cut_str(render_timeline.loc[last_placed_index,'BbS_main'],word_count_timeline)
                else:
                    pass
        except Exception as E:
            raise ParserError('ParErrCompl')

        # 去掉和前一帧相同的帧，节约了性能
        render_timeline = render_timeline.fillna('NA') #假设一共10帧
        timeline_diff = render_timeline.iloc[:-1].copy() #取第0-9帧
        timeline_diff.index = timeline_diff.index+1 #设置为第1-10帧
        timeline_diff.loc[0]='NA' #再把第0帧设置为NA
        dropframe = (render_timeline == timeline_diff.sort_index()).all(axis=1) # 这样，就是原来的第10帧和第9帧在比较了

        # 导出
        bulitin_media = pd.Series(bulitin_media,dtype=str)
        break_point = break_point.astype(int) # breakpoint 数据类型改为整数
        return render_timeline[dropframe == False].copy(),break_point,bulitin_media
    # 渲染单帧
    def render(self,this_frame):
        for layer in self.zorder:
            # 不渲染的条件：图层为"Na"，或者np.nan
            if (this_frame[layer]=='NA')|(this_frame[layer]!=this_frame[layer]):
                continue
            elif this_frame[layer+'_a']<=0: #或者图层的透明度小于等于0(由于fillna("NA"),出现的异常)
                continue
            elif this_frame[layer] not in self.media_list:
                raise RenderError('UndefMedia',this_frame[layer])
            # 渲染背景图层
            elif layer[0:2] == 'BG':
                try:
                    Object = eval(this_frame[layer])
                    Object.display(
                        surface=self.screen,alpha=this_frame[layer+'_a'],
                        adjust=this_frame[layer+'_p'],center=this_frame[layer+'_c']
                    )
                except Exception:
                    raise RenderError('FailRender',this_frame[layer],'Background')
            # 渲染立绘图层
            elif layer[0:2] == 'Am': # 兼容H_LG1(1)这种动画形式 alpha1.6.3
                try:
                    Object = eval(this_frame[layer])
                    Object.display(
                        surface=self.screen,alpha=this_frame[layer+'_a'],frame=this_frame[layer+'_t'],
                        adjust=this_frame[layer+'_p'],center=this_frame[layer+'_c']
                    )
                except Exception:
                    raise RenderError('FailRender',this_frame[layer],'Animation')
            # 渲染气泡图层
            elif layer[0:2] == 'Bb':
                try:
                    Object = eval(this_frame[layer])
                    Object.display(
                        surface=self.screen,alpha=this_frame[layer+'_a'],
                        text=this_frame[layer+'_main'],header=this_frame[layer+'_header'],
                        adjust=this_frame[layer+'_p'],center=this_frame[layer+'_c']
                    )
                except Exception:
                    raise RenderError('FailRender',this_frame[layer],'Bubble')
        # 播放音效
        for key in ['BGM','Voice','SE']:
            if (this_frame[key]=='NA')|(this_frame[key]!=this_frame[key]): #如果是空的
                continue
            elif this_frame[key] == 'stop': # a 1.6.0更新
                pygame.mixer.music.stop() #停止
                pygame.mixer.music.unload() #换碟
            elif (this_frame[key] not in self.media_list): # 不是预先定义的媒体，则一定是合法的路径
                try:
                    if key == 'BGM':
                        temp_BGM = BGM(filepath=this_frame[key][1:-1])
                        temp_BGM.display()
                    else:
                        temp_Audio = Audio(filepath=this_frame[key][1:-1])
                        temp_Audio.display(channel=self.channel_list[key]) # 这里的参数需要是对象
                except Exception as E:
                    print(E)
                    raise RenderError('FailPlay',this_frame[key])
            else: # 预先定义的媒体
                try:
                    if key == 'BGM':
                        eval(this_frame[key]).display() # 否则就直接播放对象
                        # exec('{0}.display()'.format(this_frame[key]))
                    else:
                        eval(this_frame[key]).display(channel=self.channel_list[key]) # 否则就直接播放对象
                        # exec('{0}.display(channel={1})'.format(this_frame[key],self.channel_list[key])) 
                except Exception as E:
                    print(E)
                    raise RenderError('FailPlay',this_frame[key])
        return 1
    # 执行语音合成子进程
    def flag_synthanyway(self) -> None:
        command = self.python3.format('speech_synthesizer') +' --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} --OutputPath {of} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP} '
        command = command + '--Azurekey {AZ} --ServRegion {SR} --Language {la}'
        command = command.format(lg = self.stdin_log.replace('\\','/'),md = self.media_obj.replace('\\','/'), of = self.output_path, ct = self.char_tab.replace('\\','/'),
                                AK = self.accesskey,AS = self.accesskey_secret,AP = self.appkey,AZ = self.azurekey, SR =self.service_region, la = self.lang)
        print(MainPrint('SythAnyway'))
        print(CMDPrint('Command',command))
        try:
            exit_status = os.system(command)
            print(CMDPrint('BreakLine'))
            # 0. 有覆盖原log，合成正常，可以继续执行主程序
            if exit_status == 0:
                pass
            # 1. 无覆盖原log，无需合成，可以继续执行主程序
            elif exit_status == 1:
                print(WarningPrint('NoValidSyth'))
            # 2. 无覆盖原log，合成未完成，不能继续执行主程序
            elif exit_status == 2:
                raise SynthesisError('CantBegin')
            # 3. 有覆盖原log，合成未完成，不能继续执行主程序
            elif exit_status == 3:
                raise SynthesisError('SynBreak')
            else:
                raise SynthesisError('Unknown')
        except Exception as E:
            print(E)
            self.system_terminated('Error')
    # 导出的子进程
    def flag_export(self) -> None:
        print(MainPrint('OutTime',self.output_path))
        # 如果有输出路径，导出时间轴文件
        timenow = '%d'%time.time()
        timeline_ofile = open(self.output_path+'/'+timenow+'.timeline','wb')
        pickle.dump([self.render_timeline,self.break_point,self.bulitin_media],timeline_ofile)
        timeline_ofile.close()
        # 如果导出PR项目
        if self.export_xml == True:
            command = self.python3.format('export_xml') + ' --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} --Language {la}'
            command = command.format(tm = self.output_path +'/'+timenow+'.timeline',
                                    md = self.media_obj.replace('\\','/'), of = self.output_path.replace('\\','/'), 
                                    fps = self.frame_rate, wd = self.Width, he = self.Height, zd = ','.join(self.zorder), la=self.lang)
            print(MainPrint('ExportXML'))
            print(CMDPrint('Command',command))
            try:
                exit_status = os.system(command)
                print(CMDPrint('BreakLine'))
                if exit_status != 0:
                    raise OSError('Major error occurred in export_xml!')
            except Exception as E:
                print(WarningPrint('XMLFail',E))
        # 如果导出视频文件
        if self.export_video == True:
            command = self.python3.format('export_video') + ' --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} --Quality {ql} --Language {la}'
            command = command.format(tm = self.output_path +'/'+timenow+'.timeline',
                                    md = self.media_obj.replace('\\','/'), of = self.output_path.replace('\\','/'), 
                                    fps = self.frame_rate, wd = self.Width, he = self.Height, zd = ','.join(self.zorder),ql = self.crf, la=self.lang)
            print(MainPrint('ExportMp4'))
            print(CMDPrint('Command',command))
            try:
                exit_status = os.system(command)
                print(CMDPrint('BreakLine'))
                if exit_status != 0:
                    raise OSError('Major error occurred in export_video!')
            except Exception as E:
                print(WarningPrint('Mp4Fail',E))
            # 如果导出为视频，则提前终止程序
            self.system_terminated('Video')
    # 载入媒体定义文件
    def load_medias(self) -> None:
        try:
            object_define_text = open(self.media_obj,'r',encoding='utf-8').read()#.split('\n') # 修改后的逻辑
        except UnicodeDecodeError as E:
            print(DecodeError('DecodeErr',E))
            self.system_terminated('Error')
        if object_define_text[0] == '\ufeff': # UTF-8 BOM
            print(WarningPrint('UFT8BOM'))
            object_define_text = object_define_text[1:] # 去掉首位
        object_define_text = object_define_text.split('\n')
        # 媒体列表
        self.media_list=[]
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
                    # instantiation = obj_type + obj_args
                    if obj_name in self.occupied_variable_name:
                        raise SyntaxsError('OccName')
                    elif (len(re.findall('\w+',obj_name))==0)|(obj_name[0].isdigit()):
                        raise SyntaxsError('InvaName')
                    else:
                        #对象实例化
                        # self.MediaObjects[obj_name] = eval(instantiation)
                        exec('global {}; '.format(obj_name) + text)
                        self.media_list.append(obj_name) #记录新增对象名称
                except Exception as E:
                    print(E)
                    print(SyntaxsError('MediaDef',text,str(i+1)))
                    self.system_terminated('Error')
        global black ; black = Background('black')
        global white ; white = Background('white')
        self.media_list.append('black')
        self.media_list.append('white')
    # 载入角色配置文件
    def load_chartab(self) -> None:
        try:
            if self.char_tab.split('.')[-1] in ['xlsx','xls']:
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore') # 禁用读取excel时报出的：UserWarning: Data Validation extension is not supported and will be removed
                    self.charactor_table = pd.read_excel(self.char_tab,dtype = str,sheet_name='角色配置').fillna('NA') # 支持excel格式的角色配置表
            else:
                self.charactor_table = pd.read_csv(self.char_tab,sep='\t',dtype = str).fillna('NA')
            self.charactor_table.index = self.charactor_table['Name']+'.'+self.charactor_table['Subtype']
            if ('Animation' not in self.charactor_table.columns) | ('Bubble' not in self.charactor_table.columns): # 139debug
                raise SyntaxsError('MissCol')
        except SyntaxsError as E:
            print(E)
            self.system_terminated('Error')
        except Exception as E:
            print(SyntaxsError('CharTab',E))
            self.system_terminated('Error')
    # 载入RplGenLog
    def load_rplgenlog(self) -> None:
        # 载入log文件
        try:
            stdin_text = open(self.stdin_log,'r',encoding='utf8').read()#.split('\n')
        except UnicodeDecodeError as E:
            print(DecodeError('DecodeErr',E))
            self.system_terminated('Error')
        if stdin_text[0] == '\ufeff': # 139 debug # 除非是完全空白的文件
            print(WarningPrint('UFT8BOM'))
            stdin_text = stdin_text[1:]
        stdin_text = stdin_text.split('\n')
        # 解析log文件
        try:
            self.stdin_text = stdin_text
            self.render_timeline,self.break_point,self.bulitin_media = self.parser(stdin_text)
        except ParserError as E:
            print(E)
            self.system_terminated('Error')
    # 倒计时：已禁用，待删除
    def timer(self,clock):
        white.display(self.screen)
        self.screen.blit(self.note_text.render('%d'%clock,fgcolor=(150,150,150,255),size=0.0926*self.Height)[0],(0.484*self.Width,0.463*self.Height)) # for 1080p
        pygame.display.update()
        pygame.time.delay(1000)
    # 终止音效
    def stop_SE(self) -> None:
        for Ch in self.channel_list.values():
            Ch.stop()
    # 暂停音效
    def pause_SE(self,stats) -> None:
        if stats == 0:
            pygame.mixer.music.pause()
            for Ch in self.channel_list.values():
                Ch.pause()
        else:
            pygame.mixer.music.unpause()
            for Ch in self.channel_list.values():
                Ch.unpause()
    # 播放窗口
    def preview_display(self) -> None:
        # 修复缩放错误
        if self.fix_screen == True:
            try:
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware() #修复错误的缩放，尤其是在移动设备。
            except Exception:
                print(WarningPrint('FixScrZoom'))
        # 初始化显示窗口
        pygame.init()
        pygame.display.set_caption('TRPG Replay Generator '+EDITION)
        fps_clock=pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.Width,self.Height))
        pygame.display.set_icon(pygame.image.load('./media/icon.png'))
        self.note_text = pygame.freetype.Font('./media/SourceHanSansCN-Regular.otf')
        # 建立音频轨道
        self.VOICE = pygame.mixer.Channel(1)
        self.SOUEFF = pygame.mixer.Channel(2)
        self.channel_list = {'Voice':self.VOICE,'SE':self.SOUEFF}
        # 转换媒体对象
        for media in self.media_list: 
            try:
                eval(media).convert()
            except Exception as E:
                print(MediaError('ErrCovert',media,E))
                self.system_terminated('Error')
        # 预备画面
        white.display(self.screen)
        self.screen.blit(pygame.transform.scale(pygame.image.load('./media/icon.png'),(self.Height//5,self.Height//5)),(0.01*self.Height,0.79*self.Height))
        self.screen.blit(self.note_text.render('Welcome to TRPG Replay Generator!',fgcolor=(150,150,150,255),size=0.0315*self.Width)[0],(0.230*self.Width,0.460*self.Height)) # for 1080p
        self.screen.blit(self.note_text.render(EDITION,fgcolor=(150,150,150,255),size=0.0278*self.Height)[0],(0.900*self.Width,0.963*self.Height))
        self.screen.blit(self.note_text.render('Press space to begin.',fgcolor=(150,150,150,255),size=0.0278*self.Height)[0],(0.417*self.Width,0.926*self.Height))
        pygame.display.update()
        begin = False
        while begin == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.system_terminated('User')
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.time.delay(1000)
                        pygame.quit()
                        self.system_terminated('User')
                    elif event.key == pygame.K_SPACE:
                        begin = True
                        break
        # 倒数计时：暂时先不要了
        #for s in np.arange(5,0,-1):
        #    self.timer(s)
        # 预览播放参数
        n=0 # 当前帧
        forward = 1 #forward==0代表暂停
        show_detail_info = 0 # show_detail_info == 1代表显示详细信息
        detail_info = {0:"Project: Resolution: {0}x{1} ; FrameRate: {2} fps;".format(self.Width,self.Height,self.frame_rate),
                    1:"Render Speed: {0} fps",
                    2:"Frame: {0}/"+str(self.break_point.max())+" ; Section: {1}/"+str(len(self.break_point)),
                    3:"Command: {0}",
                    4:"Zorder: {0}".format('>>>'+'>'.join(self.zorder)+'>>>'),
                    5:"Layer: BG1:{0}; BG2:{1};",
                    6:"Layer: Am1:{0}; Am2:{1}; Am3:{2}; AmS:{3}",
                    7:"Layer: Bb:{0}; HD:{1}; TX:{2}",
                    8:"Layer: BbS:{0}; HDS:{1}; TXS:{2}"
                    }
        resize_screen = 0 # 是否要强制缩小整个演示窗体
        # 主循环
        while n < self.break_point.max():
            ct = time.time()
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        self.system_terminated('User')
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.stop_SE()
                            pygame.time.delay(1000)
                            pygame.quit()
                            self.system_terminated('User')
                        elif event.key in [pygame.K_a,pygame.K_LEFT]:
                            n=self.break_point[(self.break_point-n)<0].max()
                            n=self.break_point[(self.break_point-n)<0].max()
                            if n != n: # 确保不会被a搞崩
                                n = 0
                            self.stop_SE()
                            continue
                        elif event.key in [pygame.K_d,pygame.K_RIGHT]:
                            n=self.break_point[(self.break_point-n)>0].min()
                            self.stop_SE()
                            continue
                        elif event.key in [pygame.K_F11, pygame.K_p]: # 调整缩放一半
                            from pygame._sdl2.video import Window
                            window = Window.from_display_module()
                            resize_screen = 1 - resize_screen
                            if resize_screen == 1:
                                self.screen_resized = pygame.display.set_mode((self.Width//2,self.Height//2))
                                self.screen = pygame.Surface((self.Width,self.Height),pygame.SRCALPHA)
                                window.position = (100,100)
                            else:
                                self.screen = pygame.display.set_mode((self.Width,self.Height))
                                window.position = (0,0)
                            pygame.display.update()
                        elif event.key in [pygame.K_F5, pygame.K_i]: # 详细信息
                            show_detail_info = 1 - show_detail_info # 1->0 0->1
                        elif event.key == pygame.K_SPACE: #暂停
                            forward = 1 - forward # 1->0 0->1
                            self.pause_SE(forward) # 0:pause,1:unpause
                        else:
                            pass
                if n in self.render_timeline.index:
                    this_frame = self.render_timeline.loc[n]
                    # 渲染！
                    self.render(this_frame)
                    # 如果正在暂停
                    if forward == 0:
                        self.screen.blit(self.note_text.render('Press space to continue.',fgcolor=MediaObj.cmap['notetext'],size=0.0278*self.Height)[0],(0.410*self.Width,0.926*self.Height)) # pause
                    # 显示详情模式
                    if show_detail_info == 1:
                        self.screen.blit(self.note_text.render(detail_info[0],fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10))
                        self.screen.blit(self.note_text.render(detail_info[2].format(n,this_frame['section']+1),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10+0.0666*self.Height))
                        self.screen.blit(self.note_text.render(detail_info[3].format(self.stdin_text[this_frame['section']]),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10+0.1*self.Height))
                        self.screen.blit(self.note_text.render(detail_info[4],fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10+0.1333*self.Height))
                        self.screen.blit(self.note_text.render(detail_info[5].format(this_frame['BG1'],this_frame['BG2']),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10+0.1666*self.Height))
                        self.screen.blit(self.note_text.render(detail_info[6].format(this_frame['Am1'],this_frame['Am2'],this_frame['Am3'],this_frame['AmS']),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10+0.2*self.Height))
                        self.screen.blit(self.note_text.render(detail_info[7].format(this_frame['Bb'],this_frame['Bb_header'],this_frame['Bb_main']),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10+0.2333*self.Height))
                        self.screen.blit(self.note_text.render(detail_info[8].format(this_frame['BbS'],this_frame['BbS_header'],this_frame['BbS_main']),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10+0.2666*self.Height))
                        self.screen.blit(self.note_text.render(detail_info[1].format(int(1/(time.time()-ct+1e-4))),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.Height)[0],(10,10+0.0333*self.Height))
                    # 仅显示帧率
                    else:
                        self.screen.blit(self.note_text.render('%d'%(1//(time.time()-ct+1e-4)),fgcolor=MediaObj.cmap['notetext'],size=0.0278*self.Height)[0],(10,10)) ##render rate +1e-4 to avoid float divmod()
                    # 如果缩放到一半大小
                    if resize_screen == 1:
                        self.screen_resized.blit(pygame.transform.scale(self.screen,(self.Width//2,self.Height//2)),(0,0))
                else:
                    pass # 节约算力
                pygame.display.update()
                n = n + forward #下一帧
                fps_clock.tick(self.frame_rate)
            except RenderError as E:
                print(E)
                print(RenderError('BreakFrame',n))
                pygame.quit()
                self.system_terminated('Error')
        pygame.quit()
        self.system_terminated('End')
    # 退出程序函数
    def system_terminated(self,exit_type='Error'):
        print(MainPrint(exit_type))
        if exit_type == 'Error':
            sys.exit(1) # 错误退出的代码
        else:
            sys.exit(0) # 正常退出的代码
    # 主流程
    def main(self):
        # welcome
        print(MainPrint('Welcome',EDITION))
        # 检查是否需要先做语音合成
        if self.synth_anyway == True:
            self.flag_synthanyway()
        # 载入媒体文件
        print(MainPrint('LoadMedef'))
        self.load_medias()
        # 载入角色配置文件
        print(MainPrint('LoadChrtab'))
        self.load_chartab()
        # 载入并解析log文件 parser()
        print(MainPrint('LoadRGL'))
        self.load_rplgenlog()
        # 判断是否指定输出路径，准备各种输出选项
        if self.output_path != None:
            self.flag_export()
        # 开始预览播放
        self.preview_display()

if __name__ == '__main__':
    import argparse
    # 外部参数输入
    # 参数处理
    ap = argparse.ArgumentParser(description="Generating your TRPG replay video from logfile.")
    ap.add_argument("-l", "--LogFile", help='The standerd input of this programme, which is mainly composed of TRPG log.',type=str)
    ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
    ap.add_argument("-t", "--CharacterTable", help='The correspondence between character and media elements, using tab separated text file or Excel table.',type=str)
    ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the project timeline and breakpoint file.',type=str,default=None)
    # 选项
    ap.add_argument("-F", "--FramePerSecond", help='Set the FPS of display, default is 30 fps, larger than this may cause lag.',type=int,default=30)
    ap.add_argument("-W", "--Width", help='Set the resolution of display, default is 1920, larger than this may cause lag.',type=int,default=1920)
    ap.add_argument("-H", "--Height", help='Set the resolution of display, default is 1080, larger than this may cause lag.',type=int,default=1080)
    ap.add_argument("-Z", "--Zorder", help='Set the display order of layers, not recommended to change the values unless necessary!',type=str,
                    default='BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS')
    # 用于语音合成的key
    ap.add_argument("-K", "--AccessKey", help='Your AccessKey, to use with --SynthsisAnyway',type=str,default="Your_AccessKey")
    ap.add_argument("-S", "--AccessKeySecret", help='Your AccessKeySecret, to use with --SynthsisAnyway',type=str,default="Your_AccessKey_Secret")
    ap.add_argument("-A", "--Appkey", help='Your Appkey, to use with --SynthsisAnyway',type=str,default="Your_Appkey")
    ap.add_argument("-U", "--Azurekey", help='Your Azure TTS key.',type=str,default="Your_Azurekey")
    ap.add_argument("-R", "--ServRegion", help='Service region of Azure.', type=str, default="eastasia")

    # 用于导出视频的质量值
    ap.add_argument("-Q", "--Quality", help='Choose the quality (ffmpeg crf) of output video, to use with --ExportVideo.',type=int,default=24)
    # Flags
    ap.add_argument('--ExportXML',help='Export a xml file to load in Premiere Pro, some .png file will be created at same time.',action='store_true')
    ap.add_argument('--ExportVideo',help='Export MP4 video file, this will disables interface display',action='store_true')
    ap.add_argument('--SynthesisAnyway',help='Execute speech_synthezier first, and process all unprocessed asterisk time label.',action='store_true')
    ap.add_argument('--FixScreenZoom',help='Windows system only, use this flag to fix incorrect windows zoom.',action='store_true')
    # 语言
    ap.add_argument("--Language",help='Choose the language of running log',default='en',type=str)
    # 主
    args = ap.parse_args()
    try:
        ReplayGenerator(args=args)
    except:
        from traceback import print_exc
        print_exc()