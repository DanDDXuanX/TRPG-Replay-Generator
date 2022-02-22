#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.6.1'

# 外部参数输入

import argparse
import sys
import os


ap = argparse.ArgumentParser(description="Generating your TRPG replay video from logfile.")
ap.add_argument("-l", "--LogFile", help='The standerd input of this programme, which is mainly composed of TRPG log.',type=str)
ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
ap.add_argument("-t", "--CharacterTable", help='The correspondence between character and media elements, using tab separated text file.(.csv)',type=str)
ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the project timeline and breakpoint file.',type=str,default=None)
# 增加一个，读取时间轴和断点文件的选项！
ap.add_argument("-F", "--FramePerSecond", help='Set the FPS of display, default is 30 fps, larger than this may cause lag.',type=int,default=30)
ap.add_argument("-W", "--Width", help='Set the resolution of display, default is 1920, larger than this may cause lag.',type=int,default=1920)
ap.add_argument("-H", "--Height", help='Set the resolution of display, default is 1080, larger than this may cause lag.',type=int,default=1080)
ap.add_argument("-Z", "--Zorder", help='Set the display order of layers, not recommended to change the values unless necessary!',type=str,
                default='BG3,BG2,BG1,Am3,Am2,Am1,Bb')

ap.add_argument('--ExportXML',help='Export a xml file to load in Premiere Pro, some .png file will be created at same time.',action='store_true')
ap.add_argument('--ExportVideo',help='Export MP4 video file, this will disables interface display',action='store_true')
ap.add_argument('--SynthesisAnyway',help='Execute speech_synthezier first, and process all unprocessed asterisk time label.',action='store_true')
ap.add_argument('--FixScreenZoom',help='Windows system only, use this flag to fix incorrect windows zoom.',action='store_true')

args = ap.parse_args()

media_obj = args.MediaObjDefine #媒体对象定义文件的路径
char_tab = args.CharacterTable #角色和媒体对象的对应关系文件的路径
stdin_log = args.LogFile #log路径
output_path = args.OutputPath #保存的时间轴，断点文件的目录

screen_size = (args.Width,args.Height) #显示的分辨率
frame_rate = args.FramePerSecond #帧率 单位fps
zorder = args.Zorder.split(',') #渲染图层顺序

exportXML = args.ExportXML #导出为XML
exportVideo = args.ExportVideo #导出为视频
synthfirst = args.SynthesisAnyway #是否先行执行语音合成
fixscreen = args.FixScreenZoom # 是否修复窗体缩放

try:
    for path in [stdin_log,media_obj,char_tab]:
        if path == None:
            raise OSError("[31m[ArgumentError]:[0m Missing principal input argument!")
        if os.path.isfile(path) == False:
            raise OSError("[31m[ArgumentError]:[0m Cannot find file "+path)

    if output_path == None:
        if (synthfirst == True) | (exportXML == True):
            raise OSError("[31m[ArgumentError]:[0m Some flags requires output path, but no output path is specified!")
    elif os.path.isdir(output_path) == False:
        raise OSError("[31m[ArgumentError]:[0m Cannot find directory "+output_path)
    else:
        output_path = output_path.replace('\\','/')

    # FPS
    if frame_rate <= 0:
        raise ValueError("[31m[ArgumentError]:[0m Invalid frame rate:"+str(frame_rate))
    elif frame_rate>30:
        print("[33m[warning]:[0m",'FPS is set to '+str(frame_rate)+', which may cause lag in the display!')

    if (screen_size[0]<=0) | (screen_size[1]<=0):
        raise ValueError("[31m[ArgumentError]:[0m Invalid resolution:"+str(screen_size))
    if screen_size[0]*screen_size[1] > 3e6:
        print("[33m[warning]:[0m",'Resolution is set to more than 3M, which may cause lag in the display!')
except Exception as E:
    print(E)
    sys.exit()

# 包导入

import pandas as pd
import numpy as np
import pygame
import pygame.freetype
import re
import time #开发模式，显示渲染帧率

# 类定义

# 文字对象
class Text:
    pygame.font.init()
    def __init__(self,fontfile='C:/Windows/Fonts/simhei.ttf',fontsize=40,color=(0,0,0,255),line_limit=20):
        self.text_render = pygame.font.Font(fontfile,fontsize)
        self.color=color
        self.size=fontsize
        self.line_limit = line_limit
    def draw(self,text):
        out_text = []
        if ('#' in text) | (text[0]=='^'): #如果有手动指定的换行符 # bug:如果手动换行，但是第一个#在30字以外，异常的显示
            if text[0]=='^': # 如果使用^指定的手动换行，则先去掉这个字符。
                text = text[1:]
            text_line = text.split('#')
            for tx in text_line:
                out_text.append(self.text_render.render(tx,True,self.color))
        elif len(text) > self.line_limit: #如果既没有主动指定，字符长度也超限
            for i in range(0,len(text)//self.line_limit+1):#较为简单粗暴的自动换行
                out_text.append(self.text_render.render(text[i*self.line_limit:(i+1)*self.line_limit],True,self.color))
        else:
            out_text = [self.text_render.render(text,True,self.color)]
        return out_text
    def convert(self):
        pass

# 对话框、气泡、文本框
class Bubble:
    def __init__(self,filepath,Main_Text=Text(),Header_Text=None,pos=(0,0),mt_pos=(0,0),ht_pos=(0,0),line_distance=1.5):
        self.media = pygame.image.load(filepath)
        self.pos = pos
        self.MainText = Main_Text
        self.mt_pos = mt_pos
        self.Header = Header_Text
        self.ht_pos = ht_pos
        self.line_distance = line_distance
    def display(self,surface,text,header='',alpha=100,adjust='NA'):
        if adjust in ['0,0','NA']:
            render_pos = self.pos
        else:
            adx,ady = split_xy(adjust)
            render_pos = (self.pos[0]+adx,self.pos[1]+ady)
        temp = self.media.copy()
        if (self.Header!=None) & (header!=''):    # Header 有定义，且输入文本不为空
            temp.blit(self.Header.draw(header)[0],self.ht_pos)
        x,y = self.mt_pos
        for i,s in enumerate(self.MainText.draw(text)):
            temp.blit(s,(x,y+i*self.MainText.size*self.line_distance))
        if alpha !=100:
            temp.set_alpha(alpha/100*255)            
        surface.blit(temp,render_pos)
    def convert(self):
        self.media = self.media.convert_alpha()

# 背景图片
class Background:
    def __init__(self,filepath,pos = (0,0)):
        if filepath in cmap.keys(): #添加了，对纯色定义的背景的支持
            self.media = pygame.surface.Surface(screen_size)
            self.media.fill(cmap[filepath])
        else:
            self.media = pygame.image.load(filepath)
        self.pos = pos
    def display(self,surface,alpha=100,adjust='NA'):
        if adjust in ['0,0','NA']:
            render_pos = self.pos
        else:
            adx,ady = split_xy(adjust)
            render_pos = (self.pos[0]+adx,self.pos[1]+ady)
        if alpha !=100:
            temp = self.media.copy()
            temp.set_alpha(alpha/100*255)
            surface.blit(temp,render_pos)
        else:
            surface.blit(self.media,render_pos)
    def convert(self):
        self.media = self.media.convert_alpha()

# 立绘图片
class Animation:
    def __init__(self,filepath,pos = (0,0)):
        self.media = pygame.image.load(filepath)
        self.pos = pos
    def display(self,surface,alpha=100,adjust='NA'):
        if adjust in ['0,0','NA']:
            render_pos = self.pos
        else:
            adx,ady = split_xy(adjust)
            render_pos = (self.pos[0]+adx,self.pos[1]+ady)
        if alpha !=100:
            temp = self.media.copy()
            temp.set_alpha(alpha/100*255)
            surface.blit(temp,render_pos)
        else:
            surface.blit(self.media,render_pos)
    def convert(self):
        self.media = self.media.convert_alpha()

# 音效
class Audio:
    pygame.mixer.init()
    def __init__(self,filepath):
        self.media = pygame.mixer.Sound(filepath)
    def display(self,channel,volume=100):
        channel.set_volume(volume/100)
        channel.play(self.media)
    def convert(self):
        pass

# 背景音乐
class BGM:
    def __init__(self,filepath,volume=100,loop=True):
        self.media = filepath
        self.volume = volume/100
        if loop == True:
            self.loop = -1 #大概是不可能能放完的
        else:
            self.loop = 0
        if filepath.split('.')[-1] not in ['ogg']: #建议的格式
            print("[33m[warning]:[0m",'A not recommend music format ['+filepath.split('.')[-1]+'] is specified, which may cause unstableness during displaying!')
    def display(self):
        if pygame.mixer.music.get_busy() == True: #如果已经在播了
            pygame.mixer.music.stop() #停止
            pygame.mixer.music.unload() #换碟
        else:
            pass
        pygame.mixer.music.load(self.media) #进碟
        pygame.mixer.music.play(loops=self.loop) #开始播放
        pygame.mixer.music.set_volume(self.volume) #设置音量
    def convert(self):
        pass

# 正则表达式定义

RE_dialogue = re.compile('^\[([\w\.\;\(\)\,]+)\](<[\w\=\d]+>)?:(.+?)(<[\w\=\d]+>)?({.+})?$')
RE_background = re.compile('^<background>(<[\w\=]+>)?:(.+)$')
RE_setting = re.compile('^<set:([\w\_]+)>:(.+)$')
RE_characor = re.compile('(\w+)(\(\d*\))?(\.\w+)?')
RE_modify = re.compile('<(\w+)(=\d+)?>')
RE_sound = re.compile('({.+?})')
RE_asterisk = re.compile('(\{([\w\.\\\/\'\":]*?[,;])?\*([\w\.\,，]*)?\})') # a 1.4.3 修改了星标的正则（和ss一致）
#RE_asterisk = re.compile('\{\w+[;,]\*(\d+\.?\d*)\}') # 这种格式对于{path;*time的}的格式无效！

# 绝对的全局变量

python3 = sys.executable.replace('\\','/') # 获取python解释器的路径

cmap = {'black':(0,0,0,255),'white':(255,255,255,255),'greenscreen':(0,177,64,255)}
#render_arg = ['BG1','BG1_a','BG2','BG2_a','BG3','BG3_a','Am1','Am1_a','Am2','Am2_a','Am3','Am3_a','Bb','Bb_main','Bb_header','Bb_a']
#render_arg = ['BG1','BG1_a','BG2','BG2_a','BG3','BG3_a','Am1','Am1_a','Am2','Am2_a','Am3','Am3_a','Bb','Bb_main','Bb_header','Bb_a','BGM','Voice','SE']
render_arg = ['BG1','BG1_a','BG1_p','BG2','BG2_a','BG2_p','BG3','BG3_a','BG3_p',
              'Am1','Am1_a','Am1_p','Am2','Am2_a','Am2_p','Am3','Am3_a','Am3_p',
              'Bb','Bb_main','Bb_header','Bb_a','Bb_p','BGM','Voice','SE']

# 数学函数定义 formula

def normalized(X):
    return (X-X.min())/(X.max()-X.min())

def linear(begin,end,dur):
    return np.linspace(begin,end,int(dur))

def quadratic(begin,end,dur):
    return (np.linspace(0,1,int(dur))**2)*(end-begin)+begin

def quadraticR(begin,end,dur):
    return (1-np.linspace(1,0,int(dur))**2)*(end-begin)+begin

def sigmoid(begin,end,dur,K=5):
    return normalized(1/(1+np.exp(np.linspace(K,-K,int(dur)))))*(end-begin)+begin

def right(begin,end,dur,K=4):
    return normalized(1/(1+np.exp((quadratic(K,-K,int(dur))))))*(end-begin)+begin

def left(begin,end,dur,K=4):
    return normalized(1/(1+np.exp((quadraticR(K,-K,int(dur))))))*(end-begin)+begin

formula_available={'linear':linear,'quadratic':quadratic,'quadraticR':quadraticR,
                   'sigmoid':sigmoid,'right':right,'left':left}

# 可以<set:keyword>动态调整的全局变量

am_method_default = '<replace=0>' #默认切换效果（文本框和立绘）
am_dur_default = 10 #默认切换效果持续时间（文本框和立绘）

bg_method_default = '<replace=0>' #默认切换效果（背景）
bg_dur_default = 10 #默认切换效果持续时间（背景）

tx_method_default = '<all=0>' #默认文本展示方式
tx_dur_default = 5 #默认单字展示时间参数

speech_speed = 220 #语速，单位word per minute
formula = linear #默认的曲线函数
asterisk_pause = 20 # 星标音频的句间间隔 a1.4.3，单位是帧，通过处理delay

# 其他函数定义

# 解析对话行 []
def get_dialogue_arg(text):
    cr,cre,ts,tse,se = RE_dialogue.findall(text)[0]
    this_duration = int(len(ts)/(speech_speed/60/frame_rate))
    this_charactor = RE_characor.findall(cr)
    # 切换参数
    if cre=='':
        cre = am_method_default
    method,method_dur = RE_modify.findall(cre)[0] #<black=\d+> 
    if method_dur == '':
        method_dur = am_dur_default
    else:
        method_dur = int(method_dur.replace('=',''))
    # 文本显示参数
    if tse=='':
        tse = tx_method_default
    text_method,text_dur = RE_modify.findall(tse)[0] #<black=\d+> 
    if text_dur == '':
        text_dur = tx_dur_default
    else:
        text_dur = int(text_dur.replace('=',''))
    # 语音和音效参数
    if se == '':
        this_sound = []
    else:
        this_sound = RE_sound.findall(se)

    return (this_charactor,this_duration,method,method_dur,ts,text_method,text_dur,this_sound)

# 解析背景行 <background>
def get_background_arg(text):
    bge,bgc = RE_background.findall(text)[0]
    if bge=='':
        bge = bg_method_default
    method,method_dur = RE_modify.findall(bge)[0]
    if method_dur == '':
        method_dur = bg_dur_default
    else:
        method_dur = int(method_dur.replace('=',''))
    return (bgc,method,method_dur)

# 解释设置行 <set:>
def get_seting_arg(text):
    target,args = RE_setting.findall(text)[0]
    return (target,args)

# 截断字符串
def cut_str(str_,len_):
    return str_[0:int(len_)]
UF_cut_str = np.frompyfunc(cut_str,2,1)

# 设定合理透明度范围
def alpha_range(x):
    if x>100:
        return 100
    if x<0:
        return 0
    else:
        return x

# UF : 将2个向量组合成"x,y"的形式
concat_xy = np.frompyfunc(lambda x,y:'%d'%x+','+'%d'%y,2,1)

# 把拼接起来的修正位置分隔开
def split_xy(concated):
    x,y = concated.split(',')
    return int(x),int(y)

def am_methods(method_name,method_dur,this_duration):
    Height = screen_size[1]
    if method_name =='replace': # replace 方法的method_dur 代表显示延迟，单位为帧
        alpha_timeline = np.hstack([np.zeros(method_dur),np.ones(this_duration-method_dur)])
        pos_timeline = 'NA'
    elif method_name == 'black': #淡入淡出
        alpha_timeline = np.hstack([formula(0,1,method_dur),np.ones(this_duration-2*method_dur),formula(1,0,method_dur)])
        pos_timeline = 'NA'
    elif method_name == 'pass_up': #下进上出
        alpha_timeline = np.hstack([formula(0,1,method_dur),np.ones(this_duration-2*method_dur),formula(1,0,method_dur)])
        pos_timeline = concat_xy(np.zeros(this_duration),np.hstack([formula(Height*0.2,0,method_dur),np.zeros(this_duration-2*method_dur),formula(0,-Height*0.2,method_dur)]))
    elif method_name == 'pass_down': #上进下出
        alpha_timeline = np.hstack([formula(0,1,method_dur),np.ones(this_duration-2*method_dur),formula(1,0,method_dur)])
        pos_timeline = concat_xy(np.zeros(this_duration),np.hstack([formula(Height*0.2,0,method_dur),np.zeros(this_duration-2*method_dur),formula(0,-Height*0.2,method_dur)]))
    else:
        raise ValueError('[31m[ParserError]:[0m Unrecognized switch method: ['+text_method+'] appeared in dialogue line ' + str(i+1)+'.')
    return alpha_timeline,pos_timeline

# 解析函数
def parser(stdin_text):
    # 断点
    global formula
    break_point = pd.Series(index=range(0,len(stdin_text)),dtype=int)
    break_point[0]=0
    # 视频+音轨 时间轴
    render_timeline = []
    BGM_queue = []
    this_background = "black"

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
        elif text[0] == '[':
            try:
                # 从ts长度预设的 this_duration
                this_charactor,this_duration,method,method_dur,ts,text_method,text_dur,this_sound = get_dialogue_arg(text)
                # a 1.3 从音频中加载持续时长 {SE1;*78} 注意，这里只需要载入星标时间，检查异常不在这里做：
                asterisk_timeset = RE_asterisk.findall('\t'.join(this_sound)) #在音频标志中读取
                if len(asterisk_timeset) == 0:  #没检测到星标
                    pass
                elif len(asterisk_timeset) == 1: #检查到一个星标
                    try:
                        asterisk_time = float(asterisk_timeset[0][-1]) #取第二个，转化为浮点数
                        this_duration = asterisk_pause + np.ceil((asterisk_time)*frame_rate).astype(int) # a1.4.3 添加了句间停顿
                    except:
                        print('[33m[warning]:[0m','Failed to load asterisk time in dialogue line ' + str(i+1)+'.')
                else: #检测到复数个星标
                    raise ValueError('[31m[ParserError]:[0m Too much asterisk time labels are set in dialogue line ' + str(i+1)+'.')

                # 确保时长不短于切换特效时长
                if this_duration<(2*method_dur+1):
                    this_duration = 2*method_dur+1
            except Exception as E:
                print(E)
                raise ValueError('[31m[ParserError]:[0m Parse exception occurred in dialogue line ' + str(i+1)+'.')

            this_timeline=pd.DataFrame(index=range(0,this_duration),dtype=str,columns=render_arg)
            this_timeline['BG1'] = this_background
            this_timeline['BG1_a'] = 100

            alpha_timeline,pos_timeline = am_methods(method,method_dur,this_duration) # 未来的版本中可能会被对象的binding_method 替代掉！

            #各个角色：
            if len(this_charactor) > 3:
                raise ValueError('[31m[ParserError]:[0m Too much charactor is specified in dialogue line ' + str(i+1)+'.')
            for k,charactor in enumerate(this_charactor[0:3]):
                name,alpha,subtype= charactor
                #处理空缺参数
                if subtype == '':
                    subtype = '.default'
                if alpha == '':
                    alpha = 100
                else:
                    alpha = int(alpha[1:-1])
                #立绘和气泡的参数
                try:
                    this_timeline['Am'+str(k+1)] = charactor_table.loc[name+subtype]['Animation']
                except Exception as E:
                    raise ValueError('[31m[ParserError]:[0m Undefined Name '+ name+subtype +' in dialogue line ' + str(i+1)+'.')
                if k == 0:
                    this_timeline['Bb'] = charactor_table.loc[name+subtype]['Bubble'] # 异常处理，未定义的名字
                    this_timeline['Bb_main'] = ts
                    this_timeline['Bb_header'] = name
                    this_timeline['Bb_a'] = alpha_timeline*100
                    this_timeline['Bb_p'] = pos_timeline

                if (k!=0)&(alpha==100):#如果非第一角色，且没有指定透明度，则使用正常透明度60%
                    this_timeline['Am'+str(k+1)+'_a']=alpha_timeline*60
                else:#否则，使用正常透明度
                    this_timeline['Am'+str(k+1)+'_a']=alpha_timeline*alpha
                # 位置时间轴信息
                this_timeline['Am'+str(k+1)+'_p'] = pos_timeline

            #文字显示的参数
            if text_method == 'all':
                if text_dur == 0:
                    pass
                else:
                    this_timeline.loc[0:text_dur,'Bb_main'] = '' #将前n帧的文本设置为空白
            elif text_method == 'w2w':
                word_count_timeline = np.arange(0,this_duration,1)//text_dur+1
                this_timeline['Bb_main'] = UF_cut_str(this_timeline['Bb_main'],word_count_timeline)
            elif text_method == 'l2l': 
                if '#' in ts: #如果是手动换行的列
                    word_count_timeline = get_l2l(ts,text_dur,this_duration) # 不保证稳定呢！
                else:
                    line_limit = eval(this_timeline['Bb'][1]+'.MainText.line_limit') #获取主文本对象的line_limit参数
                    word_count_timeline = (np.arange(0,this_duration,1)//(text_dur*line_limit)+1)*line_limit
                this_timeline['Bb_main'] = UF_cut_str(this_timeline['Bb_main'],word_count_timeline)
            else:
                raise ValueError('[31m[ParserError]:[0m Unrecognized text display method: ['+text_method+'] appeared in dialogue line ' + str(i+1)+'.')
            #音频信息
            if BGM_queue != []:
                this_timeline.loc[0,'BGM'] = BGM_queue.pop() #从BGM_queue里取出来一个
            for sound in this_sound: #this_sound = ['{SE_obj;30}','{SE_obj;30}']
                try:
                    se_obj,delay = sound[1:-1].split(';')#sound = '{SE_obj;30}'
                except: # #sound = '{SE_obj}'
                    delay = '0'
                    se_obj = sound[1:-1] # 去掉花括号
                if delay == '':
                    delay = 0
                elif '*' in delay: # 如果是星标时间 delay 是asterisk_pause的一半
                    delay = int(asterisk_pause/2)
                elif int(delay) >= this_duration: # delay 不能比一个单元还长
                    delay = this_duration-1
                else:
                    delay = int(delay)
                if '*' in se_obj:
                    raise IOError('[31m[ParserError]:[0m Unprocessed asterisk time label appeared in dialogue line ' + str(i+1) + '. Add --SynthesisAnyway may help.')
                if se_obj in media_list: # 如果delay在媒体里已经定义，则视为SE
                    this_timeline.loc[delay,'SE'] = se_obj
                elif os.path.isfile(se_obj[1:-1]) == True: #或者指向一个确定的文件，则视为语音
                    this_timeline.loc[delay,'Voice'] = se_obj
                else:
                    raise IOError('[31m[ParserError]:[0m The sound effect ['+se_obj+'] specified in dialogue line ' + str(i+1)+' is not exist!')
                
            render_timeline.append(this_timeline)
            break_point[i+1]=break_point[i]+this_duration
            continue
        # 背景设置行，格式： <background><black=30>:BG_obj
        elif '<background>' in text:
            try:
                bgc,method,method_dur = get_background_arg(text)
                next_background=bgc
            except:
                raise ValueError('[31m[ParserError]:[0m Parse exception occurred in background line ' + str(i+1)+'.')
                continue
    
            if method=='replace': #replace 方法的method_dur 代表延迟切换（总持续时间），单位为帧
                this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                this_timeline['BG1']=this_background
                this_timeline['BG1_a']=100
            elif method in ['cover','black','white']:
                this_timeline=pd.DataFrame(index=range(0,method_dur),dtype=str,columns=render_arg)
                this_timeline['BG1']=next_background
                this_timeline['BG2']=this_background
                if method in ['black','white']:
                    this_timeline['BG3']=method
                    this_timeline['BG1_a']=formula(-100,100,method_dur)
                    this_timeline['BG1_a']=this_timeline['BG1_a'].map(alpha_range)
                    this_timeline['BG2_a']=formula(100,-100,method_dur)
                    this_timeline['BG2_a']=this_timeline['BG2_a'].map(alpha_range)
                    this_timeline['BG3_a']=100
                if method in ['cover']:
                    this_timeline['BG1_a']=formula(0,100,method_dur)
                    this_timeline['BG2_a']=100
            else:
                raise ValueError('[31m[ParserError]:[0m Unrecognized switch method: ['+text_method+'] appeared in background line ' + str(i+1)+'.')
            this_background = next_background #正式切换背景
            render_timeline.append(this_timeline)
            break_point[i+1]=break_point[i]+len(this_timeline.index)
            continue
        # 参数设置行，格式：<set:speech_speed>:220
        elif ('<set:' in text) & ('>:' in text):
            try:
                target,args = get_seting_arg(text)
            except:
                raise ValueError('[31m[ParserError]:[0m Parse exception occurred in setting line ' + str(i+1)+'.')
                continue
            if target in ['speech_speed','am_method_default','am_dur_default','bg_method_default','bg_dur_default','tx_method_default','tx_dur_default','asterisk_pause']:
                try: #如果args是整数值型
                    test = int(args)
                    if test < 0:
                        print('[33m[warning]:[0m','Setting',target,'to invalid value',test,',the argument will not changed.')
                        test = eval(target) # 保持原数值不变
                    #print("global {0} ; {0} = {1}".format(target,str(test)))
                    exec("global {0} ; {0} = {1}".format(target,str(test)))
                except: #否则当作文本型
                    #print("global {0} ; {0} = {1}".format(target,'\"'+args+'\"'))
                    exec("global {0} ; {0} = {1}".format(target,'\"'+args+'\"'))
            elif target == 'BGM':
                if args in media_list:
                    BGM_queue.append(args)
                elif os.path.isfile(args[1:-1]):
                    BGM_queue.append(args)
                elif args == 'stop':
                    BGM_queue.append(args)
                else:
                    raise IOError('[31m[ParserError]:[0m The BGM ['+args+'] specified in setting line ' + str(i+1)+' is not exist!')
            elif target == 'formula':
                if args in formula_available.keys():
                    formula = formula_available[args]
                elif args[0:6] == 'lambda':
                    try:
                        formula = eval(args)
                        print('[33m[warning]:[0m','Using lambda formula range ',formula(0,1,2),
                              ' in line',str(i+1),', which may cause unstableness during displaying!')                            
                    except:
                        raise ValueError('[31m[ParserError]:[0m Unsupported formula ['+args+'] is specified in setting line ' + str(i+1)+'.')
                else:
                    raise ValueError('[31m[ParserError]:[0m Unsupported formula ['+args+'] is specified in setting line ' + str(i+1)+'.')
            else:
                raise ValueError('[31m[ParserError]:[0m Unsupported setting ['+target+'] is specified in setting line ' + str(i+1)+'.')
                continue
        # 异常行，报出异常
        else:
            raise ValueError('[31m[ParserError]:[0m Unrecognized line: '+ str(i+1)+'.')
        break_point[i+1]=break_point[i]
        
    render_timeline = pd.concat(render_timeline,axis=0)
    render_timeline.index = np.arange(0,len(render_timeline),1)
    render_timeline = render_timeline.fillna('NA') #假设一共10帧
    timeline_diff = render_timeline.iloc[:-1].copy() #取第0-9帧
    timeline_diff.index = timeline_diff.index+1 #设置为第1-10帧
    timeline_diff.loc[0]='NA' #再把第0帧设置为NA
    dropframe = (render_timeline == timeline_diff.sort_index()).all(axis=1) # 这样，就是原来的第10帧和第9帧在比较了
    # 这样就去掉了，和前一帧相同的帧，节约了性能
    return render_timeline[dropframe == False].copy(),break_point

# 渲染函数
def render(this_frame):
    global zorder,media_list
    for layer in zorder:
        # 不渲染的条件：图层为"Na"，或者np.nan
        if (this_frame[layer]=='NA')|(this_frame[layer]!=this_frame[layer]):
            continue
        elif this_frame[layer+'_a']<=0: #或者图层的透明度小于等于0(由于fillna("NA"),出现的异常)
            continue
        elif this_frame[layer] not in media_list:
            raise RuntimeError('[31m[RenderError]:[0m Undefined media object : ['+this_frame[layer]+'].')
            continue
        elif layer != 'Bb':
            exec('{0}.display(surface=screen,alpha={1},adjust={2})'.format(this_frame[layer],this_frame[layer+'_a'],'\"'+this_frame[layer+'_p']+'\"'))
        else:
            exec('{0}.display(surface=screen,text={2},header={3},alpha={1},adjust={4})'.format(this_frame[layer],
                                                                                               this_frame[layer+'_a'],
                                                                                               '\"'+this_frame[layer+'_main']+'\"',
                                                                                               '\"'+this_frame[layer+'_header']+'\"',
                                                                                               '\"'+this_frame[layer+'_p']+'\"'))
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
        else:
            #print('{0}.display(channel={1})'.format(this_frame[key],channel_list[key]))
            if key == 'BGM':
                exec('{0}.display()'.format(this_frame[key])) #否则就直接播放对象
            else:
                exec('{0}.display(channel={1})'.format(this_frame[key],channel_list[key])) #否则就直接播放对象
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
    except: 
        word_count_timeline = np.hstack(wc_list) # this_duration < est
        word_count_timeline = word_count_timeline[0:this_duration]
    return word_count_timeline.astype(int)

# 倒计时器
def timer(clock):
    global W,H
    white.display(screen)
    screen.blit(note_text.render('%d'%clock,fgcolor=(150,150,150,255),size=0.0926*H)[0],(0.484*W,0.463*H)) # for 1080p
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

# 检查是否需要先做语音合成

if synthfirst == True:
    command = python3 +' ./speech_synthesizer.py --LogFile {lg} --MediaObjDefine {md} --CharacterTable {ct} --OutputPath {of}'
    command = command.format(lg = stdin_log.replace('\\','/'),md = media_obj.replace('\\','/'), of = output_path, ct = char_tab.replace('\\','/'))
    print('[replay generator] Flag --SynthesisAnyway detected, running command:\n','[32m'+command+'[0m')
    try:
        os.system(command)
        # 将当前的标准输入调整为处理后的log文件
        if os.path.isfile(output_path+'/AsteriskMarkedLogFile.txt') == True:
            stdin_log = output_path+'/AsteriskMarkedLogFile.txt'
        else:
            raise OSError('Exception above')
        # 
    except Exception as E:
        print('[33m[warning]:[0m Failed to synthesis speech, due to:',E)

# 载入od文件
object_define_text = open(media_obj,'r',encoding='utf-8').read().split('\n')

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
            media_list.append(obj_name) #记录新增对象名称
        except Exception as E:
            print('[31m[SyntaxError]:[0m "'+text+'" appeared in media define file line ' + str(i+1)+' is invalid syntax.')
            sys.exit()
black = Background('black')
white = Background('white')
media_list.append('black')
media_list.append('white')
#print(media_list)

# 载入ct文件
try:
    charactor_table = pd.read_csv(char_tab,sep='\t')
    charactor_table.index = charactor_table['Name']+'.'+charactor_table['Subtype']
except:
    print('[31m[SyntaxError]:[0m Unable to load charactor table:',E)

# 载入log文件
stdin_text = open(stdin_log,'r',encoding='utf8').read().split('\n')
try:
    render_timeline,break_point = parser(stdin_text)
except Exception as E:
    print(E)
    sys.exit()

# 判断是否指定输出路径，准备各种输出选项
if output_path != None:
    print('[replay generator] The timeline and breakpoint file will be save at '+output_path)
    timenow = '%d'%time.time()
    render_timeline.to_pickle(output_path+'/'+timenow+'.timeline')
    break_point.to_pickle(output_path+'/'+timenow+'.breakpoint')
    if exportXML == True:
        command = python3 + ' ./export_xml.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd}'
        command = command.format(tm = output_path+'/'+timenow+'.timeline',
                                 md = media_obj.replace('\\','/'), of = output_path.replace('\\','/'), 
                                 fps = frame_rate, wd = screen_size[0], he = screen_size[1], zd = ','.join(zorder))
        print('[replay generator] Flag --ExportXML detected, running command:\n','[32m'+command+'[0m')
        try:
            os.system(command)
        except Exception as E:
            print('[33m[warning]:[0m Failed to export XML, due to:',E)
    if exportVideo == True:
        command = python3 + ' ./export_video.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd}'
        command = command.format(tm = output_path+'/'+timenow+'.timeline',
                                 md = media_obj.replace('\\','/'), of = output_path.replace('\\','/'), 
                                 fps = frame_rate, wd = screen_size[0], he = screen_size[1], zd = ','.join(zorder))
        print('[replay generator] Flag --ExportVideo detected, running command:\n','[32m'+command+'[0m')
        try:
            os.system(command)
        except Exception as E:
            print('[33m[warning]:[0m Failed to export Video, due to:',E)
        sys.exit() # 如果导出为视频，则提前终止程序

# 初始化界面

if fixscreen == True:
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware() #修复错误的缩放，尤其是在移动设备。
    except:
        print('[33m[warning]:[0m OS exception, --FixScreenZoom is only avaliable on windows system!')

pygame.init()
pygame.display.set_caption('TRPG Replay Generator '+edtion)
fps_clock=pygame.time.Clock()
screen = pygame.display.set_mode(screen_size)
note_text = pygame.freetype.Font('C:/Windows/Fonts/msyh.ttc')

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
        sys.exit()

# 预备画面
W,H = screen_size
white.display(screen)
screen.blit(note_text.render('Welcome to TRPG Replay Generator!',fgcolor=(150,150,150,255),size=0.0315*W)[0],(0.230*W,0.460*H)) # for 1080p
screen.blit(note_text.render(edtion,fgcolor=(150,150,150,255),size=0.0278*H)[0],(0.900*W,0.963*H))
screen.blit(note_text.render('Press space to begin.',fgcolor=(150,150,150,255),size=0.0278*H)[0],(0.417*W,0.926*H))
pygame.display.update()
begin = False
while begin == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.time.delay(1000)
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_SPACE:
                begin = True
                break
for s in np.arange(5,0,-1):
    timer(s)

# 主循环
n=0
forward = 1 #forward==0代表暂停
while n < break_point.max():
    ct = time.time()
    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_SE()
                    pygame.time.delay(1000)
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_a:
                    n=break_point[(break_point-n)<0].max()
                    n=break_point[(break_point-n)<0].max()
                    if n != n: # 确保不会被a搞崩
                        n = 0
                    stop_SE()
                    continue
                elif event.key == pygame.K_d:
                    n=break_point[(break_point-n)>0].min()
                    stop_SE()
                    continue
                elif event.key == pygame.K_SPACE: #暂停
                    forward = 1 - forward # 1->0 0->1
                    pause_SE(forward) # 0:pause,1:unpause

        if n in render_timeline.index:
            this_frame = render_timeline.loc[n]
            render(this_frame)
            if forward == 1:
                screen.blit(note_text.render('%d'%(1//(time.time()-ct)),fgcolor=(100,255,100,255),size=0.0278*H)[0],(10,10)) ##render rate 
            else:
                screen.blit(note_text.render('Press space to continue.',fgcolor=(100,255,100,255),size=0.0278*H)[0],(0.410*W,0.926*H)) # pause
        else:
            pass # 节约算力
        pygame.display.update()
        n = n + forward #下一帧
        fps_clock.tick(frame_rate)
    except Exception as E:
        print(E)
        pygame.quit()
        sys.exit()
pygame.quit()
sys.exit()
