#!/usr/bin/env python
# coding: utf-8
from Utils import edtion

# 外部参数输入

import argparse
import sys
import os

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
                default='BG3,BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS')
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

args = ap.parse_args()

Width,Height = args.Width,args.Height #显示的分辨率
frame_rate = args.FramePerSecond #帧率 单位fps
zorder = args.Zorder.split(',') #渲染图层顺序

# 退出程序
def system_terminated(exit_type='Error'):
    exit_print = {'Error':'A major error occurred. Execution terminated!',
                  'User':'Display terminated, due to user commands.',
                  'Video':'Video exported. Execution terminated!',
                  'End':'Display finished!'}
    print('[replay generator]: '+exit_print[exit_type])
    if exit_type == 'Error':
        import traceback
        traceback.print_exc()
        sys.exit(1) # 错误退出的代码
    else:
        sys.exit(0) # 正常退出的代码

try:
    for path in [args.LogFile,args.MediaObjDefine,args.CharacterTable]:
        if path is None:
            raise OSError("[31m[ArgumentError]:[0m Missing principal input argument!")
        if os.path.isfile(path) == False:
            raise OSError("[31m[ArgumentError]:[0m Cannot find file "+path)

    if args.OutputPath is None:
        if (args.SynthesisAnyway == True) | (args.ExportXML == True) | (args.ExportVideo == True):
            raise OSError("[31m[ArgumentError]:[0m Some flags requires output path, but no output path is specified!")
    elif os.path.isdir(args.OutputPath) == False:
        raise OSError("[31m[ArgumentError]:[0m Cannot find directory "+args.OutputPath)
    else:
        args.OutputPath = args.OutputPath.replace('\\','/')

    # FPS
    if frame_rate <= 0:
        raise ValueError("[31m[ArgumentError]:[0m Invalid frame rate:"+str(frame_rate))
    elif frame_rate>30:
        print("[33m[warning]:[0m",'FPS is set to '+str(frame_rate)+', which may cause lag in the display!')

    if (Width<=0) | (Height<=0):
        raise ValueError("[31m[ArgumentError]:[0m Invalid resolution:"+str((Width,Height)))
    if Width*Height > 3e6:
        print("[33m[warning]:[0m",'Resolution is set to more than 3M, which may cause lag in the display!')
except Exception as E:
    print(E)
    system_terminated('Error')

# 包导入

import pandas as pd
import numpy as np
import pygame
import pygame.freetype
import re
import time #开发模式，显示渲染帧率

# 自由点
from FreePos import Pos,FreePos,PosGrid

# 类定义 alpha 1.11.0
from Medias import Text
from Medias import StrokeText
from Medias import Bubble
from Medias import Balloon
from Medias import Background
from Medias import Animation
from Medias import GroupedAnimation
from Medias import BuiltInAnimation
from Medias import Audio
from Medias import BGM
# 窗体参数
from Medias import screen_config
screen_config['screen_size'] = (Width,Height)
screen_config['frame_rate'] = frame_rate
# 色图
from Medias import cmap

# 异常定义 
from Exceptions import ParserError

# 正则表达式
from Regexs import *

# 曲线函数
from Formulas import linear,quadratic,quadraticR,sigmoid,right,left,sincurve,normalized
from Formulas import formula_available

# 小工具们
from Utils import *

# python的绝对路径
python3 = sys.executable.replace('\\','/')
# 被占用的变量名 # 1.7.7
occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n')

# section:小节号, BG: 背景，Am：立绘，Bb：气泡，BGM：背景音乐，Voice：语音，SE：音效
render_arg = [
    'section',
    'BG1','BG1_a','BG1_c','BG1_p','BG2','BG2_a','BG2_c','BG2_p','BG3','BG3_a','BG3_c','BG3_p',
    'Am1','Am1_t','Am1_a','Am1_c','Am1_p','Am2','Am2_t','Am2_a','Am2_c','Am2_p','Am3','Am3_t','Am3_a','Am3_c','Am3_p',
    'AmS','AmS_t','AmS_a','AmS_c','AmS_p',
    'Bb','Bb_main','Bb_header','Bb_a','Bb_c','Bb_p',
    'BbS','BbS_main','BbS_header','BbS_a','BbS_c','BbS_p',
    'BGM','Voice','SE'
    ]

# 可以<set:keyword>动态调整的全局变量
dynamic_globals = {
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
}

# 其他函数定义

# 解析对话行 []
def get_dialogue_arg(text):
    try:
        cr,cre,ts,tse,se = RE_dialogue.findall(text)[0]
    except IndexError:
        raise ParserError("[31m[ParserError]:[0m","Unable to parse as dialogue line, due to invalid syntax!")
    this_duration = int(len(ts)/(dynamic_globals['speech_speed']/60/frame_rate))
    this_charactor = RE_characor.findall(cr)
    # 切换参数
    if cre=='': # 没有指定 都走默认值
        am_method,am_dur = RE_modify.findall(dynamic_globals['am_method_default'])[0]
        bb_method,bb_dur = RE_modify.findall(dynamic_globals['bb_method_default'])[0]
    else: # 有指定，变得相同
        am_method,am_dur = RE_modify.findall(cre)[0] 
        bb_method,bb_dur = am_method,am_dur
    if am_dur == '':# 没有指定 都走默认值
        am_dur = dynamic_globals['am_dur_default']
    else:# 有指定，变得相同
        am_dur = int(am_dur.replace('=',''))
    if bb_dur == '':
        bb_dur = dynamic_globals['bb_dur_default']
    else:
        bb_dur = int(bb_dur.replace('=',''))
    # 文本显示参数
    if tse=='':
        tse = dynamic_globals['tx_method_default']
    text_method,text_dur = RE_modify.findall(tse)[0] #<black=\d+> 
    if text_dur == '':
        text_dur = dynamic_globals['tx_dur_default']
    else:
        text_dur = int(text_dur.replace('=',''))
    # 语音和音效参数
    if se == '':
        this_sound = []
    else:
        this_sound = RE_sound.findall(se)

    return (this_charactor,this_duration,am_method,am_dur,bb_method,bb_dur,ts,text_method,text_dur,this_sound)

# 解析背景行 <background>
def get_placeobj_arg(text):
    try:
        obj_type,obje,objc = RE_placeobj.findall(text)[0]
    except IndexError:
        raise ParserError("[31m[ParserError]:[0m","Unable to parse as " + obj_type + " line, due to invalid syntax!")
    if obje=='':
        if obj_type == 'background':
            obje = dynamic_globals['bg_method_default']
        elif obj_type == 'bubble':
            obje = dynamic_globals['bb_method_default']
        else: # obj_type == 'animation'
            obje = dynamic_globals['am_method_default']
    method,method_dur = RE_modify.findall(obje)[0]
    if method_dur == '':
        if obj_type == 'background':
            method_dur = dynamic_globals['bg_dur_default']
        elif obj_type == 'bubble':
            method_dur = dynamic_globals['bb_dur_default']
        else: # obj_type == 'animation'
            method_dur = dynamic_globals['am_dur_default']
    else:
        method_dur = int(method_dur.replace('=',''))
    return (objc,method,method_dur)

# 解释设置行 <set:>
def get_seting_arg(text):
    try:
        target,args = RE_setting.findall(text)[0]
    except IndexError:
        raise ParserError("[31m[ParserError]:[0m","Unable to parse as setting line, due to invalid syntax!")
    return (target,args)

# 处理am和bb类的动态切换效果
def ambb_methods(method_name,method_dur,this_duration,i):
    def dynamic(scale,duration,balance,cut,enable): # 动态(尺度,持续,平衡,进出,启用)
        if enable == True: # cutin=1,cutout=0
            if cut == balance:
                return dynamic_globals['formula'](0,scale,duration)
            else:
                return dynamic_globals['formula'](scale,0,duration)
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
                raise ParserError('[31m[ParserError]:[0m Unrecognized switch method: "'+method_name+'" appeared in dialogue line ' + str(i+1)+'.')
        else:
            try:
                method_args['scale'] = int(key)
            except Exception:
                raise ParserError('[31m[ParserError]:[0m Unrecognized switch method: "'+method_name+'" appeared in dialogue line ' + str(i+1)+'.')
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
        method_args['scale'] = ((np.cos(theta)*Height)**2+(np.sin(theta)*Width)**2)**(1/2)*scale_dic[method_args['scale']]
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
            .repeat(dynamic_globals['formula'](0-theta,2*np.pi-theta,method_dur),np.ceil(this_duration/method_dur).astype(int))
            .reshape(method_dur,np.ceil(this_duration/method_dur).astype(int))
            .transpose().ravel())[0:this_duration]
        D1 = np.sin(theta_timeline)*method_args['scale']
        D2 = -np.cos(theta_timeline)*method_args['scale']
    else:
        pos_timeline = 'NA'
        return alpha_timeline,pos_timeline
    pos_timeline = concat_xy(D1,D2)
    return alpha_timeline,pos_timeline

# 解析函数
def parser(stdin_text):
    # 断点文件
    break_point = pd.Series(0,index=range(0,len(stdin_text)),dtype=int)
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
                this_charactor,this_duration,am_method,am_dur,bb_method,bb_dur,ts,text_method,text_dur,this_sound = get_dialogue_arg(text)
                # a 1.3 从音频中加载持续时长 {SE1;*78} 注意，这里只需要载入星标时间，检查异常不在这里做：
                asterisk_timeset = RE_asterisk.findall('\t'.join(this_sound)) #在音频标志中读取
                if len(asterisk_timeset) == 0:  #没检测到星标
                    pass
                elif len(asterisk_timeset) == 1: #检查到一个星标
                    try:
                        asterisk_time = float(asterisk_timeset[0][-1]) #取第二个，转化为浮点数
                        this_duration = dynamic_globals['asterisk_pause'] + np.ceil((asterisk_time)*frame_rate).astype(int) # a1.4.3 添加了句间停顿
                    except Exception:
                        print('[33m[warning]:[0m','Failed to load asterisk time in dialogue line ' + str(i+1)+'.')
                else: #检测到复数个星标
                    raise ParserError('[31m[ParserError]:[0m Too much asterisk time labels are set in dialogue line ' + str(i+1)+'.')

                # 确保时长不短于切换特效时长
                if this_duration<(2*max(am_dur,bb_dur)+1):
                    this_duration = 2*max(am_dur,bb_dur)+1

                # 建立本小节的timeline文件
                this_timeline=pd.DataFrame(index=range(0,this_duration),dtype=str,columns=render_arg)
                this_timeline['BG1'] = this_background
                this_timeline['BG1_a'] = 100
                # 载入切换效果
                alpha_timeline_A,pos_timeline_A = ambb_methods(am_method,am_dur,this_duration,i)
                alpha_timeline_B,pos_timeline_B = ambb_methods(bb_method,bb_dur,this_duration,i)
                #各个角色：
                if len(this_charactor) > 3:
                    raise ParserError('[31m[ParserError]:[0m Too much charactor is specified in dialogue line ' + str(i+1)+'.')
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
                        this_char_series = charactor_table.loc[name+subtype]
                    except KeyError as E: # 在角色表里面找不到name，raise在这里！
                        raise ParserError('[31m[ParserError]:[0m Undefined Name '+ name+subtype +' in dialogue line ' + str(i+1)+'. due to:',E)
                    # 如果index存在重复值，则this_char_series不是一个 Series # 在这里处理的角色表index重复值，之后不再考虑这个异常
                    if type(this_char_series) is not pd.Series:
                        raise ParserError('[31m[ParserError]:[0m'+' Duplicate subtype '+name+subtype+' is set in charactor table!')
                    
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
                            raise ParserError('[31m[ParserError]:[0m',E,', which is specified to',name+subtype,'as Animation!')
                    # 透明度参数（alpha）
                    if (alpha >= 0)&(alpha <= 100): # alpha 1.8.8 如果有指定合法的透明度，则使用指定透明度
                        this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*alpha
                    else: # 如果没有指定透明度
                        if k == 0: # 如果是首要角色，透明度为100
                            this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*100
                        else: # 如果是次要角色，透明度为secondary_alpha，默认值60
                            this_timeline['Am'+str(k+1)+'_a']=alpha_timeline_A*dynamic_globals['secondary_alpha'] 
                    # 位置参数（pos)
                    this_timeline['Am'+str(k+1)+'_p'] = pos_timeline_A
                    # 气泡的参数
                    if k == 0:
                        this_bb = this_char_series['Bubble']
                        # 主要角色一定要有bubble！，次要的可用没有
                        if (this_bb!=this_bb) | (this_bb=='NA'):
                            raise ParserError('[31m[ParserError]:[0m','No bubble is specified to major charactor',name+subtype,'of dialogue line '+str(i+1)+'.')
                        # 获取目标的头文本
                        try:
                            targets = eval(this_bb+'.target')
                            # Balloon 类
                            if type(targets) is list:
                                target_text = '|'.join(this_char_series[targets].values)
                            # Bubble 类
                            else:
                                target_text = this_char_series[targets]
                        except NameError as E: # 指定的bb没有定义！
                            raise ParserError('[31m[ParserError]:[0m',E,', which is specified to',name+subtype,'as Bubble!')
                        except KeyError as E: # 指定的target不存在！
                            raise ParserError('[31m[ParserError]:[0m','Target columns',E,'specified to Bubble object \''+this_bb+'\' is not exist!')
                        # 针对文本内容的警告和报错
                        try:
                            this_line_limit = eval(this_bb+'.MainText.line_limit')
                        except AttributeError: # 'NoneType' object has no attribute 'line_limit'
                            raise ParserError('[31m[ParserError]:[0m','Main_Text of "{0}" is None!'.format(this_bb))
                        # ts或者target_text里面有非法字符，双引号，反斜杠
                        if ('"' in target_text) | ('\\' in target_text) | ('"' in ts) | ('\\' in ts):
                            raise ParserError('[31m[ParserError]:[0m','Invalid symbol (double quote or backslash) appeared in speech text in dialogue line ' + str(i+1)+'.')
                        # 未声明手动换行
                        if ('#' in ts)&(ts[0]!='^'):
                            ts = '^' + ts # 补齐申明符号
                            print('[33m[warning]:[0m','Undeclared manual break dialogue line ' + str(i+1)+'.')
                        #行数过多的警告
                        if (len(ts)>this_line_limit*4) | (len(ts.split('#'))>4):
                            print('[33m[warning]:[0m','More than 4 lines will be displayed in dialogue line ' + str(i+1)+'.')
                        # 手动换行的字数超限的警告
                        if ((ts[0]=='^')|('#' in ts))&(np.frompyfunc(len,1,1)(ts.replace('^','').split('#')).max()>this_line_limit):
                            print('[33m[warning]:[0m','Manual break line length exceed the Bubble line_limit in dialogue line ' + str(i+1)+'.') #alpha1.6.3
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
                        word_count_timeline = get_l2l(ts,text_dur,this_duration) # 不保证稳定呢！
                    else:
                        line_limit = eval(this_timeline['Bb'][1]+'.MainText.line_limit') #获取主文本对象的line_limit参数 # 为什么是【1】？？
                        word_count_timeline = (np.arange(0,this_duration,1)//(text_dur*line_limit)+1)*line_limit
                    this_timeline['Bb_main'] = UF_cut_str(this_timeline['Bb_main'],word_count_timeline)
                else:
                    raise ParserError('[31m[ParserError]:[0m Unrecognized text display method: "'+text_method+'" appeared in dialogue line ' + str(i+1)+'.')
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
                        delay = int(dynamic_globals['asterisk_pause']/2)
                    elif int(delay) >= this_duration: # delay 不能比一个单元还长
                        delay = this_duration-1
                    else:
                        delay = int(delay)
                    if '*' in se_obj:
                        raise ParserError('[31m[ParserError]:[0m Unprocessed asterisk time label appeared in dialogue line ' + str(i+1) + '. Add --SynthesisAnyway may help.')
                    if se_obj in media_list: # 如果delay在媒体里已经定义，则视为SE
                        this_timeline.loc[delay,'SE'] = se_obj
                    elif os.path.isfile(se_obj[1:-1]) == True: #或者指向一个确定的文件，则视为语音
                        this_timeline.loc[delay,'Voice'] = se_obj
                    elif se_obj in ['NA','']: # 如果se_obj是空值或NA，则什么都不做 alpha1.8.5
                        pass
                    else:
                        raise ParserError('[31m[ParserError]:[0m The sound effect "'+se_obj+'" specified in dialogue line ' + str(i+1)+' is not exist!')
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
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in dialogue line ' + str(i+1)+'.')
        # 背景设置行，格式： <background><black=30>:BG_obj
        elif text[0:12] == '<background>':
            try:
                bgc,method,method_dur = get_placeobj_arg(text)
                if bgc in media_list: # 检查是否是已定义的对象
                    next_background=bgc
                else:
                    raise ParserError('[31m[ParserError]:[0m The background "'+bgc+'" specified in background line ' + str(i+1)+' is not defined!')
                if method=='replace': #replace 改为立刻替换 并持续n秒
                    this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                    this_timeline['BG1']=next_background
                    this_timeline['BG1_a']=100
                    this_timeline['BG1_c']=str(eval(next_background+'.pos'))
                elif method=='delay': # delay 等价于原来的replace，延后n秒，然后替换
                    this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                    this_timeline['BG1']=this_background
                    this_timeline['BG1_a']=100
                    this_timeline['BG1_c']=str(eval(this_background+'.pos'))
                elif method in ['cross','black','white','push','cover']: # 交叉溶解，黑场，白场，推，覆盖
                    this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                    this_timeline['BG1']=next_background
                    this_timeline['BG1_c']=str(eval(next_background+'.pos'))
                    this_timeline['BG2']=this_background
                    this_timeline['BG2_c']=str(eval(this_background+'.pos'))
                    if method in ['black','white']:
                        this_timeline['BG3']=method
                        this_timeline['BG3_c']='(0,0)'
                        this_timeline['BG1_a']=dynamic_globals['formula'](-100,100,method_dur)
                        this_timeline['BG1_a']=this_timeline['BG1_a'].map(alpha_range)
                        this_timeline['BG2_a']=dynamic_globals['formula'](100,-100,method_dur)
                        this_timeline['BG2_a']=this_timeline['BG2_a'].map(alpha_range)
                        this_timeline['BG3_a']=100
                    elif method == 'cross':
                        this_timeline['BG1_a']=dynamic_globals['formula'](0,100,method_dur)
                        this_timeline['BG2_a']=100
                    elif method in ['push','cover']:
                        this_timeline['BG1_a']=100
                        this_timeline['BG2_a']=100
                        if method == 'push': # 新背景从右侧把旧背景推出去
                            this_timeline['BG1_p'] = concat_xy(dynamic_globals['formula'](Width,0,method_dur),np.zeros(method_dur))
                            this_timeline['BG2_p'] = concat_xy(dynamic_globals['formula'](0,-Width,method_dur),np.zeros(method_dur))
                        else: #cover 新背景从右侧进来叠在原图上面
                            this_timeline['BG1_p'] = concat_xy(dynamic_globals['formula'](Width,0,method_dur),np.zeros(method_dur))
                            this_timeline['BG2_p'] = 'NA'
                else:
                    raise ParserError('[31m[ParserError]:[0m Unrecognized switch method: "'+method+'" appeared in background line ' + str(i+1)+'.')
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
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in background line ' + str(i+1)+'.')
        # 常驻立绘设置行，格式：<animation><black=30>:(Am_obj,Am_obj2)
        elif text[0:11] == '<animation>':
            # 处理上一次的
            last_placed_index = range(break_point[last_placed_animation_section],break_point[i])
            this_duration = len(last_placed_index)
            this_am,am_method,am_dur,am_center = this_placed_animation
            # 如果place的this_duration小于切换时间，则清除动态切换效果
            if this_duration<(2*am_dur+1):
                print('[33m[warning]:[0m','The switch method of placed animation is dropped, due to short duration!')
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
                alpha_timeline_A,pos_timeline_A = ambb_methods(am_method,am_dur,this_duration,i)
                render_timeline.loc[last_placed_index,'AmS_a'] = alpha_timeline_A*100
                render_timeline.loc[last_placed_index,'AmS_p'] = pos_timeline_A
                render_timeline.loc[last_placed_index,'AmS_t'] = eval('{am}.get_tick({dur})'.format(am=this_am,dur=this_duration))
                render_timeline.loc[last_placed_index,'AmS_c'] = am_center
            # 获取本次的
            try:
                amc,method,method_dur = get_placeobj_arg(text)
                # 获取立绘列表，检查立绘是否定义
                if (amc[0] == '(') and (amc[-1] == ')'):
                    amc_list = amc[1:-1].split(',')
                    grouped_ampos = []
                    for amo in amc_list:
                        # 检验指定的名称是否是Animation
                        if amo not in media_list:
                            raise ParserError('[31m[ParserError]:[0m The Animation "'+amo+'" specified in animation line ' + str(i+1)+' is not defined!')
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
                    media_list.append(Auto_media_name)
                    bulitin_media[Auto_media_name] = code_to_run
                    # 标记为下一次
                    this_placed_animation = (Auto_media_name,method,method_dur,'(0,0)') # 因为place的应用是落后于设置的，因此需要保留c参数！
                    last_placed_animation_section = i
                # 只有一个立绘
                elif amc in media_list:
                    this_placed_animation = (amc,method,method_dur,str(eval(amc).pos))
                    last_placed_animation_section = i
                # 取消place立绘
                elif amc == 'NA':
                    this_placed_animation = ('NA','replace',0,'(0,0)')
                    last_placed_animation_section = i
                else:
                    raise ParserError('[31m[ParserError]:[0m The Animation "'+amc+'" specified in animation line ' + str(i+1)+' is not defined!')
            except Exception as E:
                print(E)
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in animation line ' + str(i+1)+'.')
        # 常驻气泡设置行，格式：<bubble><black=30>:Bubble_obj("Header_text","Main_text",<text_method>)
        elif text[0:8] == '<bubble>':
            # 处理上一次的
            last_placed_index = range(break_point[last_placed_bubble_section],break_point[i])
            this_duration = len(last_placed_index)
            # bb,method,method_dur,HT,MT,text_method,tx_dur,center
            this_bb,bb_method,bb_dur,this_hd,this_tx,text_method,text_dur,bb_center = this_placed_bubble
            # 如果place的this_duration小于切换时间，则清除动态切换效果
            if this_duration<(2*bb_dur+1):
                print('[33m[warning]:[0m','The switch method of placed bubble is dropped, due to short duration!')
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
                alpha_timeline_B,pos_timeline_B = ambb_methods(bb_method,bb_dur,this_duration,i)
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
                        word_count_timeline = get_l2l(this_tx,text_dur,this_duration) # 不保证稳定呢！
                    else:
                        line_limit = eval(this_bb+'.MainText.line_limit') #获取主文本对象的line_limit参数
                        word_count_timeline = (np.arange(0,this_duration,1)//(text_dur*line_limit)+1)*line_limit
                    render_timeline.loc[last_placed_index,'BbS_main'] = UF_cut_str(render_timeline.loc[last_placed_index,'BbS_main'],word_count_timeline)
                else:
                    raise ParserError('[31m[ParserError]:[0m However impossible!')
            # 获取本次的
            try:
                # type: str,str,int
                bbc,method,method_dur = get_placeobj_arg(text)
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
                        if this_bb not in media_list:
                            raise NameError(this_bb)
                        # 检查，tx_method 的合法性
                        if this_tx_method not in ['all','w2w','l2l']:
                            raise ValueError(this_method_label)
                        else:
                            this_placed_bubble = (this_bb,method,method_dur,this_hd,this_tx,this_tx_method,int(this_tx_dur),str(eval(this_bb).pos))
                            last_placed_bubble_section = i
                    except IndexError:
                        raise ParserError('[31m[ParserError]:[0m The Bubble expression "'+bbc+'" specified in bubble line ' + str(i+1)+' is invalid syntax!')
                    except ValueError: # ValueError: invalid literal for int() with base 10: 'asd'
                        raise ParserError('[31m[ParserError]:[0m Unrecognized text display method: "'+this_method_label+'" appeared in bubble line ' + str(i+1)+'.')
                    except NameError as E:
                        raise ParserError('[31m[ParserError]:[0m The Bubble "'+E+'" specified in bubble line ' + str(i+1)+' is not defined!')
            except Exception as E:
                print(E)
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in bubble line ' + str(i+1)+'.')
        # 参数设置行，格式：<set:speech_speed>:220
        elif (text[0:5] == '<set:') & ('>:' in text):
            try:
                target,args = get_seting_arg(text)
                # 整数类型的变量
                if target in ['am_dur_default','bb_dur_default','bg_dur_default','tx_dur_default','speech_speed','asterisk_pause','secondary_alpha']:
                    try: 
                        args = int(args)
                        if args < 0:
                            raise ParserError('invalid args')
                        else:
                            dynamic_globals[target] = args
                    except Exception:
                        print('[33m[warning]:[0m','Setting',target,'to invalid value',args,',the argument will not changed.')
                # <method>类型的变量
                elif target in ['am_method_default','bb_method_default','bg_method_default','tx_method_default']:
                    # exec("global {0} ; {0} = {1}".format(target,'\"'+args+'\"')) # 当作文本型，无论是啥都接受
                    dynamic_globals[target] = args
                # BGM路径或者对象类的变量
                elif target == 'BGM':
                    if args in media_list:
                        BGM_queue.append(args)
                    elif os.path.isfile(args[1:-1]):
                        BGM_queue.append(args)
                    elif args == 'stop':
                        BGM_queue.append(args)
                    else:
                        raise ParserError('[31m[ParserError]:[0m The BGM "'+args+'" specified in setting line ' + str(i+1)+' is not exist!')
                # formula类型的变量
                elif target == 'formula':
                    if args in formula_available.keys():
                        dynamic_globals['formula'] = formula_available[args]
                    elif args[0:6] == 'lambda':
                        try:
                            dynamic_globals['formula'] = eval(args)
                            print('[33m[warning]:[0m','Using lambda formula range ',dynamic_globals['formula'](0,1,2),
                                  ' in line',str(i+1),', which may cause unstableness during displaying!')                            
                        except Exception:
                            raise ParserError('[31m[ParserError]:[0m Unsupported formula "'+args+'" is specified in setting line ' + str(i+1)+'.')
                    else:
                        raise ParserError('[31m[ParserError]:[0m Unsupported formula "'+args+'" is specified in setting line ' + str(i+1)+'.')
                # 角色表中的自定义列
                elif '.' in target:
                    target_split = target.split('.')
                    target_column = target_split[-1]
                    # 如果目标列不存在于角色表
                    if target_column not in charactor_table.columns:
                        raise ParserError('[31m[ParserError]:[0m Try to modify a undefined column \''+target_column+'\' in charactor table!')
                    # 如果尝试修改受保护的列
                    elif target_column in ['Name','Subtype','Animation','Bubble','Voice','SpeechRate','PitchRate']:
                        raise ParserError('[31m[ParserError]:[0m Try to modify a protected column \''+target_column+'\' in charactor table!')
                    # 如果只指定了一个角色名和列名，则变更应用于角色名下所有的subtype
                    if len(target_split) == 2:
                        name = target_split[0]
                        if (name in charactor_table['Name'].values):
                            try:
                                charactor_table.loc[charactor_table['Name']==name,target_column] = args
                            except Exception as E:
                                raise ParserError('[31m[ParserError]:[0m Error occurred while modifying charactor table: ' + target + ', due to:',E)
                        else:
                            raise ParserError('[31m[ParserError]:[0m Target name \''+ name +'\' in setting line '+str(i+1)+' is not undefined!')
                    # 如果只指定了角色名、差分名和列名，则变更仅应用于该subtype
                    elif len(target_split) == 3:
                        name,subtype = target_split[0:2]
                        if (name+'.'+subtype in charactor_table.index):
                            try:
                                charactor_table.loc[name+'.'+subtype, target_column] = args
                            except Exception as E:
                                raise ParserError('[31m[ParserError]:[0m Error occurred while modifying charactor table: ' + target + ', due to:',E)
                        else:
                            raise ParserError('[31m[ParserError]: Target subtype '+ name+'.'+subtype +' in setting line '+str(i+1)+' is not undefined!')
                    # 如果超过4个指定项目，无法解析，抛出ParserError(不被支持的参数)
                    else:
                        raise ParserError('[31m[ParserError]:[0m Unsupported setting "'+target+'" is specified in setting line ' + str(i+1)+'.')
                # 重定位FreePos
                elif type(eval(target)) is FreePos:
                    try:
                        eval(target).set(eval(args))
                    except Exception as E:
                        raise ParserError('[31m[ParserError]:[0m Invalid Syntax \''+args+'\' appeared  while repositioning FreePos object \''+target+'\', due to:',E)
                # 不被支持的参数
                else:
                    raise ParserError('[31m[ParserError]:[0m Unsupported setting "'+target+'" is specified in setting line ' + str(i+1)+'.')
            except Exception as E:
                print(E)
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in setting line ' + str(i+1)+'.')
        # 预设动画，损失生命
        elif text[0:11] == '<hitpoint>:':
            try:
                # 载入参数
                name_tx,heart_max,heart_begin,heart_end = RE_hitpoint.findall(text)[0]
                heart_max = int(heart_max)
                heart_begin = int(heart_begin)
                heart_end = int(heart_end)
                # 建立小节
                this_timeline=pd.DataFrame(index=range(0,frame_rate*4),dtype=str,columns=render_arg)
                # 背景
                #alpha_timeline,pos_timeline = ambb_methods('black',method_dur=frame_rate//2,this_duration=frame_rate*4,i=i)
                alpha_timeline = np.hstack([dynamic_globals['formula'](0,1,frame_rate//2),np.ones(frame_rate*3-frame_rate//2),dynamic_globals['formula'](1,0,frame_rate)])
                this_timeline['BG1'] = 'black' # 黑色背景
                this_timeline['BG1_a'] = alpha_timeline * 80
                this_timeline['BG2'] = this_background
                this_timeline['BG2_a'] = 100
                # 新建内建动画
                Auto_media_name = 'BIA_'+str(i+1)
                code_to_run = 'global {media_name}_{layer} ;{media_name}_{layer} = BuiltInAnimation(anime_type="hitpoint",anime_args=("{name}",{hmax},{hbegin},{hend}),screensize = {screensize},layer={layer})'
                code_to_run_0 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str((Width,Height)),layer='0')
                code_to_run_1 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str((Width,Height)),layer='1')
                code_to_run_2 = code_to_run.format(media_name=Auto_media_name,name=name_tx,hmax='%d'%heart_max,hbegin='%d'%heart_begin,hend='%d'%heart_end,screensize=str((Width,Height)),layer='2')
                exec(code_to_run_0) # 灰色框
                exec(code_to_run_1) # 留下的血
                exec(code_to_run_2) # 丢掉的血
                media_list.append(Auto_media_name+'_0')
                media_list.append(Auto_media_name+'_1')
                media_list.append(Auto_media_name+'_2')
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
                    this_timeline['Am1_a'] = np.hstack([dynamic_globals['formula'](0,100,frame_rate//2),
                                                        np.ones(frame_rate*2-frame_rate//2)*100,
                                                        left(100,0,frame_rate//2),
                                                        np.zeros(frame_rate*2-frame_rate//2)]) #0-0.5出现，2-2.5消失
                    this_timeline['Am1_p'] = concat_xy(np.zeros(frame_rate*4),
                                                       np.hstack([np.zeros(frame_rate*2), # 静止2秒
                                                                  left(0,-int(Height*0.3),frame_rate//2), # 半秒切走
                                                                  int(Height*0.3)*np.ones(frame_rate*2-frame_rate//2)])) #1.5秒停止
                    this_timeline['Am1_t'] = 0
                else: # 回血模式
                    this_timeline['Am1_a'] = alpha_timeline * 100 # 跟随全局血量
                    this_timeline['Am1_p'] = 'NA' # 不移动
                    this_timeline['Am1_t'] = np.hstack([np.zeros(frame_rate*1), # 第一秒静止
                                                        np.arange(0,frame_rate,1), # 第二秒播放
                                                        np.ones(frame_rate*2)*(frame_rate-1)]) # 后两秒静止
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
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in hitpoint line ' + str(i+1)+'.')
        # 预设动画，骰子
        elif text[0:7] == '<dice>:':
            try:
                # 获取参数
                dice_args = RE_dice.findall(text[7:])
                if len(dice_args) == 0:
                    raise ParserError('[31m[ParserError]:[0m','Invalid syntax, no dice args is specified!')
                # 建立小节
                this_timeline=pd.DataFrame(index=range(0,frame_rate*5),dtype=str,columns=render_arg) # 5s
                # 背景
                alpha_timeline = np.hstack([dynamic_globals['formula'](0,1,frame_rate//2),np.ones(frame_rate*4-frame_rate//2),dynamic_globals['formula'](1,0,frame_rate)])
                this_timeline['BG1'] = 'black' # 黑色背景
                this_timeline['BG1_a'] = alpha_timeline * 80
                this_timeline['BG2'] = this_background
                this_timeline['BG2_a'] = 100
                # 新建内建动画
                Auto_media_name = 'BIA_'+str(i+1)
                code_to_run = 'global {media_name}_{layer} ;{media_name}_{layer} = BuiltInAnimation(anime_type="dice",anime_args={dice_args},screensize = {screensize},layer={layer})'
                code_to_run_0 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str((Width,Height)),layer='0')
                code_to_run_1 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str((Width,Height)),layer='1')
                code_to_run_2 = code_to_run.format(media_name=Auto_media_name,dice_args=str(dice_args),screensize=str((Width,Height)),layer='2')
                exec(code_to_run_0) # 描述和检定值
                exec(code_to_run_1) # 老虎机
                exec(code_to_run_2) # 输出结果
                media_list.append(Auto_media_name+'_0')
                media_list.append(Auto_media_name+'_1')
                media_list.append(Auto_media_name+'_2')
                bulitin_media[Auto_media_name+'_0'] = code_to_run_0
                bulitin_media[Auto_media_name+'_1'] = code_to_run_1
                bulitin_media[Auto_media_name+'_2'] = code_to_run_2
                # 动画参数0
                this_timeline['Am3'] = Auto_media_name+'_0'
                this_timeline['Am3_a'] = alpha_timeline * 100
                this_timeline['Am3_t'] = 0
                this_timeline['Am3_p'] = 'NA'
                # 1
                this_timeline['Am2'] = np.hstack([np.repeat(Auto_media_name+'_1',int(frame_rate*2.5)),np.repeat('NA',frame_rate*5-int(frame_rate*2.5))]) # 2.5s
                this_timeline['Am2_a'] = np.hstack([dynamic_globals['formula'](0,100,frame_rate//2),
                                                    np.ones(int(frame_rate*2.5)-2*(frame_rate//2))*100,
                                                    dynamic_globals['formula'](100,0,frame_rate//2),
                                                    np.zeros(frame_rate*5-int(frame_rate*2.5))])
                this_timeline['Am2_t'] = np.hstack([np.arange(0,int(frame_rate*2.5)),np.zeros(frame_rate*5-int(frame_rate*2.5))])
                this_timeline['Am2_p'] = 'NA'
                # 2
                this_timeline['Am1'] = np.hstack([np.repeat('NA',frame_rate*5-int(frame_rate*2.5)),np.repeat(Auto_media_name+'_2',int(frame_rate*2.5))])
                this_timeline['Am1_a'] = np.hstack([np.zeros(frame_rate*5-int(frame_rate*2.5)),
                                                    dynamic_globals['formula'](0,100,frame_rate//2),
                                                    np.ones(int(frame_rate*2.5)-frame_rate//2-frame_rate)*100,
                                                    dynamic_globals['formula'](100,0,frame_rate)])
                this_timeline['Am1_t'] = 0
                this_timeline['Am1_p'] = 'NA'
                # SE
                this_timeline.loc[frame_rate//3,'SE'] = "'./media/SE_dice.wav'"
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
                raise ParserError('[31m[ParserError]:[0m Parse exception occurred in dice line ' + str(i+1)+'.')
        # 异常行，报出异常
        else:
            raise ParserError('[31m[ParserError]:[0m Unrecognized line: '+ str(i+1)+'.')
        break_point[i+1]=break_point[i]
    
    # 处理上一次的place最终一次
    try:
        # 处理上一次的place:AmS最终一次
        last_placed_index = range(break_point[last_placed_animation_section],break_point[i])
        this_duration = len(last_placed_index)
        this_am,am_method,am_dur,am_center = this_placed_animation
        render_timeline.loc[last_placed_index,'AmS'] = this_am
        # this_am 可能为空的，需要先处理这种情况！
        if (this_am!=this_am) | (this_am=='NA'):
            render_timeline.loc[last_placed_index,'AmS_t'] = 0
            render_timeline.loc[last_placed_index,'AmS_a'] = 0
            render_timeline.loc[last_placed_index,'AmS_c'] = 'NA'
            render_timeline.loc[last_placed_index,'AmS_p'] = 'NA'
        else:
            alpha_timeline_A,pos_timeline_A = ambb_methods(am_method,am_dur,this_duration,i)
            render_timeline.loc[last_placed_index,'AmS_a'] = alpha_timeline_A*100
            render_timeline.loc[last_placed_index,'AmS_p'] = pos_timeline_A
            render_timeline.loc[last_placed_index,'AmS_t'] = eval('{am}.get_tick({dur})'.format(am=this_am,dur=this_duration))
            render_timeline.loc[last_placed_index,'AmS_c'] = am_center

        # 处理上一次的place:BbS最终一次
        last_placed_index = range(break_point[last_placed_bubble_section],break_point[i])
        this_duration = len(last_placed_index)
        # bb,method,method_dur,HT,MT,text_method,tx_dur,center
        this_bb,bb_method,bb_dur,this_hd,this_tx,text_method,text_dur,bb_center = this_placed_bubble
        # 如果place的this_duration小于切换时间，则清除动态切换效果
        if this_duration<(2*bb_dur+1):
            print('[33m[warning]:[0m','The switch method of placed bubble is dropped, due to short duration!')
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
            alpha_timeline_B,pos_timeline_B = ambb_methods(bb_method,bb_dur,this_duration,i)
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
                    word_count_timeline = get_l2l(this_tx,text_dur,this_duration) # 不保证稳定呢！
                else:
                    line_limit = eval(this_bb+'.MainText.line_limit') #获取主文本对象的line_limit参数
                    word_count_timeline = (np.arange(0,this_duration,1)//(text_dur*line_limit)+1)*line_limit
                render_timeline.loc[last_placed_index,'BbS_main'] = UF_cut_str(render_timeline.loc[last_placed_index,'BbS_main'],word_count_timeline)
            else:
                raise ParserError('[31m[ParserError]:[0m However impossible!')
    except Exception as E:
        raise ParserError('[31m[ParserError]:[0m Exception occurred while completing the placed medias.')

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

# 渲染函数
def render(this_frame):
    global media_list
    for layer in zorder:
        # 不渲染的条件：图层为"Na"，或者np.nan
        if (this_frame[layer]=='NA')|(this_frame[layer]!=this_frame[layer]):
            continue
        elif this_frame[layer+'_a']<=0: #或者图层的透明度小于等于0(由于fillna("NA"),出现的异常)
            continue
        elif this_frame[layer] not in media_list:
            raise RuntimeError('[31m[RenderError]:[0m Undefined media object : "'+this_frame[layer]+'".')
        elif layer[0:2] == 'BG':
            try:
                exec('{0}.display(surface=screen,alpha={1},adjust={2},center={3})'.format(this_frame[layer],
                                                                                          this_frame[layer+'_a'],
                                                                                          '\"'+this_frame[layer+'_p']+'\"',
                                                                                          '\"'+this_frame[layer+'_c']+'\"'))
            except Exception:
                raise RuntimeError('[31m[RenderError]:[0m Failed to render "'+this_frame[layer]+'" as Background.')
        elif layer[0:2] == 'Am': # 兼容H_LG1(1)这种动画形式 alpha1.6.3
            try:
                exec('{0}.display(surface=screen,alpha={1},adjust={2},frame={3},center={4})'.format(
                                                                                         this_frame[layer],
                                                                                         this_frame[layer+'_a'],
                                                                                         '\"'+this_frame[layer+'_p']+'\"',
                                                                                         this_frame[layer+'_t'],
                                                                                         '\"'+this_frame[layer+'_c']+'\"'))
            except Exception:
                raise RuntimeError('[31m[RenderError]:[0m Failed to render "'+this_frame[layer]+'" as Animation.')
        elif layer[0:2] == 'Bb':
            try:
                exec('{0}.display(surface=screen,text={2},header={3},alpha={1},adjust={4},center={5})'.format(this_frame[layer],
                                                                                                   this_frame[layer+'_a'],
                                                                                                   '\"'+this_frame[layer+'_main']+'\"',
                                                                                                   '\"'+this_frame[layer+'_header']+'\"',
                                                                                                   '\"'+this_frame[layer+'_p']+'\"',
                                                                                                   '\"'+this_frame[layer+'_c']+'\"'))
            except Exception:
                raise RuntimeError('[31m[RenderError]:[0m Failed to render "'+this_frame[layer]+'" as Bubble.')
    for key in ['BGM','Voice','SE']:
        if (this_frame[key]=='NA')|(this_frame[key]!=this_frame[key]): #如果是空的
            continue
        elif this_frame[key] == 'stop': # a 1.6.0更新
            pygame.mixer.music.stop() #停止
            pygame.mixer.music.unload() #换碟
        elif (this_frame[key] not in media_list): #不是预先定义的媒体，则一定是合法的路径
            if key == 'BGM':
                temp_BGM = BGM(filepath=this_frame[key][1:-1])
                temp_BGM.display()
            else:
                temp_Audio = Audio(filepath=this_frame[key][1:-1])
                temp_Audio.display(channel=eval(channel_list[key]))#这里的参数需要是对象
        else: # 预先定义的媒体
            try:
                if key == 'BGM':
                    exec('{0}.display()'.format(this_frame[key])) #否则就直接播放对象
                else:
                    exec('{0}.display(channel={1})'.format(this_frame[key],channel_list[key])) #否则就直接播放对象
            except Exception:
                raise RuntimeError('[31m[RenderError]:[0m Failed to play audio "'+this_frame[key]+'"') # v 1.10.7 debug
    return 1
# 手动换行的l2l
def get_l2l(ts,text_dur,this_duration): #如果是手动换行的列
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

# 倒计时器
def timer(clock):
    white.display(screen)
    screen.blit(note_text.render('%d'%clock,fgcolor=(150,150,150,255),size=0.0926*Height)[0],(0.484*Width,0.463*Height)) # for 1080p
    pygame.display.update()
    pygame.time.delay(1000)

def stop_SE():
    for Ch in channel_list.values():
        exec(Ch+'.stop()')

def pause_SE(stats):
    if stats == 0:
        pygame.mixer.music.pause()
        for Ch in channel_list.values():
            exec(Ch+'.pause()')
    else:
        pygame.mixer.music.unpause()
        for Ch in channel_list.values():
            exec(Ch+'.unpause()')

# Main():

print('[replay generator]: Welcome to use TRPG-replay-generator '+edtion)

# 检查是否需要先做语音合成

if args.SynthesisAnyway == True:
    command = python3 +' ./speech_synthesizer.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} --OutputPath {of} --AccessKey {AK} --AccessKeySecret {AS} --Appkey {AP} '
    command = command + '--Azurekey {AZ} --ServRegion {SR}'
    command = command.format(lg = args.LogFile.replace('\\','/'),md = args.MediaObjDefine.replace('\\','/'), of = args.OutputPath, ct = args.CharacterTable.replace('\\','/'),
                             AK = args.AccessKey,AS = args.AccessKeySecret,AP = args.Appkey,AZ = args.Azurekey, SR =args.ServRegion)
    print('[replay generator]: Flag --SynthesisAnyway detected, running command:\n'+'[32m'+command+'[0m')
    try:
        exit_status = os.system(command)
        print('[32m------------------------------------------------------------[0m')
        # 0. 有覆盖原log，合成正常，可以继续执行主程序
        if exit_status == 0:
            pass
        # 1. 无覆盖原log，无需合成，可以继续执行主程序
        elif exit_status == 1:
            print('[33m[warning]:[0m','No valid asterisk label synthesised!')
        # 2. 无覆盖原log，合成未完成，不能继续执行主程序
        elif exit_status == 2:
            raise RuntimeError('Speech synthesis cannot begin.')
        # 3. 有覆盖原log，合成未完成，不能继续执行主程序
        elif exit_status == 3:
            raise RuntimeError('Speech synthesis breaked, due to unresolvable error.')
        else:
            raise RuntimeError('Unknown Exception.')
    except Exception as E:
        print('[31m[SynthesisError]:[0m',E)
        system_terminated('Error')

# 载入od文件
print('[replay generator]: Loading media definition file.')

try:
    object_define_text = open(args.MediaObjDefine,'r',encoding='utf-8').read()#.split('\n') # 修改后的逻辑
except UnicodeDecodeError as E:
    print('[31m[DecodeError]:[0m',E)
    system_terminated('Error')
if object_define_text[0] == '\ufeff': # UTF-8 BOM
    print('[33m[warning]:[0m','UTF8 BOM recognized in MediaDef, it will be drop from the begin of file!')
    object_define_text = object_define_text[1:] # 去掉首位
object_define_text = object_define_text.split('\n')

media_list=[]
for i,text in enumerate(object_define_text):
    if text == '':
        continue
    elif text[0] == '#':
        continue
    else:
        try:
            exec(text) #对象实例化
            obj_name = text.split('=')[0]
            obj_name = obj_name.replace(' ','')
            if obj_name in occupied_variable_name:
                raise SyntaxError('Obj name occupied')
            elif (len(re.findall('\w+',obj_name))==0)|(obj_name[0].isdigit()):
                raise SyntaxError('Invalid Obj name')
            media_list.append(obj_name) #记录新增对象名称
        except Exception as E:
            print(E)
            print('[31m[SyntaxError]:[0m "'+text+'" appeared in media define file line ' + str(i+1)+' is invalid syntax:')
            system_terminated('Error')
black = Background('black')
white = Background('white')
media_list.append('black')
media_list.append('white')

# 载入ct文件
print('[replay generator]: Loading charactor table.')

try:
    if args.CharacterTable.split('.')[-1] in ['xlsx','xls']:
        charactor_table = pd.read_excel(args.CharacterTable,dtype = str).fillna('NA') # 支持excel格式的角色配置表
    else:
        charactor_table = pd.read_csv(args.CharacterTable,sep='\t',dtype = str).fillna('NA')
    charactor_table.index = charactor_table['Name']+'.'+charactor_table['Subtype']
    if ('Animation' not in charactor_table.columns) | ('Bubble' not in charactor_table.columns): # 139debug
        raise SyntaxError('missing necessary columns.')
except Exception as E:
    print('[31m[SyntaxError]:[0m Unable to load charactor table:',E)
    system_terminated('Error')

# 载入log文件 parser()
print('[replay generator]: Parsing Log file.')

try:
    stdin_text = open(args.LogFile,'r',encoding='utf8').read()#.split('\n')
except UnicodeDecodeError as E:
    print('[31m[DecodeError]:[0m',E)
    system_terminated('Error')
if stdin_text[0] == '\ufeff': # 139 debug # 除非是完全空白的文件
    print('[33m[warning]:[0m','UTF8 BOM recognized in Logfile, it will be drop from the begin of file!')
    stdin_text = stdin_text[1:]
stdin_text = stdin_text.split('\n')
try:
    render_timeline,break_point,bulitin_media = parser(stdin_text)
except ParserError as E:
    print(E)
    system_terminated('Error')

# 判断是否指定输出路径，准备各种输出选项
if args.OutputPath != None:
    print('[replay generator]: The timeline and breakpoint file will be save at '+args.OutputPath)
    timenow = '%d'%time.time()
    render_timeline.to_pickle(args.OutputPath+'/'+timenow+'.timeline')
    break_point.to_pickle(args.OutputPath+'/'+timenow+'.breakpoint')
    bulitin_media.to_pickle(args.OutputPath+'/'+timenow+'.bulitinmedia')
    if args.ExportXML == True:
        command = python3 + ' ./export_xml.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd}'
        command = command.format(tm = args.OutputPath+'/'+timenow+'.timeline',
                                 md = args.MediaObjDefine.replace('\\','/'), of = args.OutputPath.replace('\\','/'), 
                                 fps = frame_rate, wd = Width, he = Height, zd = args.Zorder)
        print('[replay generator]: Flag --ExportXML detected, running command:\n'+'[32m'+command+'[0m')
        try:
            exit_status = os.system(command)
            print('[32m------------------------------------------------------------[0m')
            if exit_status != 0:
                raise OSError('Major error occurred in export_xml!')
        except Exception as E:
            print('[33m[warning]:[0m Failed to export XML, due to:',E)
    if args.ExportVideo == True:
        command = python3 + ' ./export_video.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd} --Quality {ql}'
        command = command.format(tm = args.OutputPath+'/'+timenow+'.timeline',
                                 md = args.MediaObjDefine.replace('\\','/'), of = args.OutputPath.replace('\\','/'), 
                                 fps = frame_rate, wd = Width, he = Height, zd = args.Zorder,ql = args.Quality)
        print('[replay generator]: Flag --ExportVideo detected, running command:\n'+'[32m'+command+'[0m')
        try:
            exit_status = os.system(command)
            print('[32m------------------------------------------------------------[0m')
            if exit_status != 0:
                raise OSError('Major error occurred in export_video!')
        except Exception as E:
            print('[33m[warning]:[0m Failed to export Video, due to:',E)
        system_terminated('Video') # 如果导出为视频，则提前终止程序

# 初始化界面

if args.FixScreenZoom == True:
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware() #修复错误的缩放，尤其是在移动设备。
    except Exception:
        print('[33m[warning]:[0m OS exception, --FixScreenZoom is only avaliable on windows system!')

pygame.init()
pygame.display.set_caption('TRPG Replay Generator '+edtion)
fps_clock=pygame.time.Clock()
screen = pygame.display.set_mode((Width,Height))
pygame.display.set_icon(pygame.image.load('./media/icon.ico'))
note_text = pygame.freetype.Font('./media/SourceHanSansCN-Regular.otf')

# 建立音频轨道
VOICE = pygame.mixer.Channel(1)
SOUEFF = pygame.mixer.Channel(2)
channel_list = {'Voice':'VOICE','SE':'SOUEFF'}

# 转换媒体对象
for media in media_list: 
    try:
        exec(media+'.convert()')
    except Exception as E:
        print('[31m[MediaError]:[0m Exception during converting',media,':',E)
        system_terminated('Error')

# 预备画面
# W,H = Width,Height
white.display(screen)
screen.blit(pygame.transform.scale(pygame.image.load('./media/icon.png'),(Height//5,Height//5)),(0.01*Height,0.79*Height))
screen.blit(note_text.render('Welcome to TRPG Replay Generator!',fgcolor=(150,150,150,255),size=0.0315*Width)[0],(0.230*Width,0.460*Height)) # for 1080p
screen.blit(note_text.render(edtion,fgcolor=(150,150,150,255),size=0.0278*Height)[0],(0.900*Width,0.963*Height))
screen.blit(note_text.render('Press space to begin.',fgcolor=(150,150,150,255),size=0.0278*Height)[0],(0.417*Width,0.926*Height))
pygame.display.update()
begin = False
while begin == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            system_terminated('User')
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.time.delay(1000)
                pygame.quit()
                system_terminated('User')
            elif event.key == pygame.K_SPACE:
                begin = True
                break
for s in np.arange(5,0,-1):
    timer(s)

# 主循环
n=0
forward = 1 #forward==0代表暂停
show_detail_info = 0 # show_detail_info == 1代表显示详细信息
detail_info = {0:"Project: Resolution: {0}x{1} ; FrameRate: {2} fps;".format(Width,Height,frame_rate),
               1:"Render Speed: {0} fps",
               2:"Frame: {0}/"+str(break_point.max())+" ; Section: {1}/"+str(len(break_point)),
               3:"Command: {0}",
               4:"Zorder: {0}".format('>>>'+'>'.join(zorder)+'>>>'),
               5:"Layer: BG1:{0}; BG2:{1}; BG3:{2}",
               6:"Layer: Am1:{0}; Am2:{1}; Am3:{2}",
               7:"Layer: Bb:{0}; HD:{1}; TX:{2}",
               }
resize_screen = 0 # 是否要强制缩小整个演示窗体
while n < break_point.max():
    ct = time.time()
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                system_terminated('User')
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_SE()
                    pygame.time.delay(1000)
                    pygame.quit()
                    system_terminated('User')
                elif event.key in [pygame.K_a,pygame.K_LEFT]:
                    n=break_point[(break_point-n)<0].max()
                    n=break_point[(break_point-n)<0].max()
                    if n != n: # 确保不会被a搞崩
                        n = 0
                    stop_SE()
                    continue
                elif event.key in [pygame.K_d,pygame.K_RIGHT]:
                    n=break_point[(break_point-n)>0].min()
                    stop_SE()
                    continue
                elif event.key in [pygame.K_F11, pygame.K_p]: # 调整缩放一半
                    from pygame._sdl2.video import Window
                    window = Window.from_display_module()
                    resize_screen = 1 - resize_screen
                    if resize_screen == 1:
                        screen_resized = pygame.display.set_mode((Width//2,Height//2))
                        screen = pygame.Surface((Width,Height),pygame.SRCALPHA)
                        window.position = (100,100)
                    else:
                        screen = pygame.display.set_mode((Width,Height))
                        window.position = (0,0)
                    pygame.display.update()
                elif event.key in [pygame.K_F5, pygame.K_i]: # 详细信息
                    show_detail_info = 1 - show_detail_info # 1->0 0->1
                elif event.key == pygame.K_SPACE: #暂停
                    forward = 1 - forward # 1->0 0->1
                    pause_SE(forward) # 0:pause,1:unpause
                else:
                    pass
        if n in render_timeline.index:
            this_frame = render_timeline.loc[n]
            render(this_frame)
            # 如果正在暂停
            if forward == 0:
                screen.blit(note_text.render('Press space to continue.',fgcolor=cmap['notetext'],size=0.0278*Height)[0],(0.410*Width,0.926*Height)) # pause
            # 显示详情模式
            if show_detail_info == 1:
                screen.blit(note_text.render(detail_info[0],fgcolor=cmap['notetext'],size=0.0185*Height)[0],(10,10))
                screen.blit(note_text.render(detail_info[2].format(n,this_frame['section']+1),fgcolor=cmap['notetext'],size=0.0185*Height)[0],(10,10+0.0666*Height))
                screen.blit(note_text.render(detail_info[3].format(stdin_text[this_frame['section']]),fgcolor=cmap['notetext'],size=0.0185*Height)[0],(10,10+0.1*Height))
                screen.blit(note_text.render(detail_info[4],fgcolor=cmap['notetext'],size=0.0185*Height)[0],(10,10+0.1333*Height))
                screen.blit(note_text.render(detail_info[5].format(this_frame['BG1'],this_frame['BG2'],this_frame['BG3']),fgcolor=cmap['notetext'],size=0.0185*Height)[0],(10,10+0.1666*Height))
                screen.blit(note_text.render(detail_info[6].format(this_frame['Am1'],this_frame['Am2'],this_frame['Am3']),fgcolor=cmap['notetext'],size=0.0185*Height)[0],(10,10+0.2*Height))
                screen.blit(note_text.render(detail_info[7].format(this_frame['Bb'],this_frame['Bb_header'],this_frame['Bb_main']),fgcolor=cmap['notetext'],size=0.0185*Height)[0],(10,10+0.2333*Height))
                screen.blit(note_text.render(detail_info[1].format(int(1/(time.time()-ct+1e-4))),fgcolor=cmap['notetext'],size=0.0185*Height)[0],(10,10+0.0333*Height))
            # 仅显示帧率
            else:
                screen.blit(note_text.render('%d'%(1//(time.time()-ct+1e-4)),fgcolor=cmap['notetext'],size=0.0278*Height)[0],(10,10)) ##render rate +1e-4 to avoid float divmod()
            # 如果缩放到一半大小
            if resize_screen == 1:
                screen_resized.blit(pygame.transform.scale(screen,(Width//2,Height//2)),(0,0))
        else:
            pass # 节约算力
        pygame.display.update()
        n = n + forward #下一帧
        fps_clock.tick(frame_rate)
    except RuntimeError as E:
        print(E)
        print('[31m[RenderError]:[0m','Render exception at frame:',n)
        pygame.quit()
        system_terminated('Error')
pygame.quit()
system_terminated('End')
