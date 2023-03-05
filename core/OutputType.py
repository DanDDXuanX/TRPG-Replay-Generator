#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import pygame
import ffmpeg
import time
import sys
import os

import pygame.freetype

from .ScriptParser import RplGenLog, MediaDef, CharTable
from .ProjConfig import Config

from .Exceptions import RenderError, MediaError
from .Exceptions import WarningPrint, MainPrint, VideoPrint, PrxmlPrint
from .Medias import *

from .Utils import EDITION

# 输出模式：预览、XML或者MP4

# 输出媒体的基类
class OutputMediaType:
    # 初始化模块功能，载入外部参数
    def __init__(self,rplgenlog:RplGenLog,config:Config,output_path):
        # 载入项目
        self.timeline:pd.DataFrame = rplgenlog.main_timeline
        self.breakpoint:pd.Series  = rplgenlog.break_point
        self.medias:dict           = rplgenlog.medias
        self.config:Config         = config
        # 全局变量
        self.stdin_name:str  = '%d'%time.time()
        self.output_path:str = output_path
    # 从timeline渲染一个单帧到一个Surface
    def render(self,surface:pygame.Surface,this_frame:pd.Series):
        for layer in self.config.zorder:
            # 不渲染的条件：图层为"Na"，或者np.nan
            if (this_frame[layer]=='NA')|(this_frame[layer]!=this_frame[layer]):
                continue
            # 如果是包含了交叉溶解的图层
            elif (' <- ' in this_frame[layer]) | (' -> ' in this_frame[layer]):
                if layer[0:2] == 'Bb':
                    cross_1 = this_frame[[layer,layer+'_header',layer+'_main',layer+'_main_e',layer+'_a',layer+'_p',layer+'_c']].replace('(.+) (->|<-) (.+)',r'\1',regex=True)
                    cross_2 = this_frame[[layer,layer+'_header',layer+'_main',layer+'_main_e',layer+'_a',layer+'_p',layer+'_c']].replace('(.+) (->|<-) (.+)',r'\3',regex=True)
                    if ' -> ' in this_frame[layer]:
                        cross_zorder = [cross_1,cross_2]
                    else:
                        cross_zorder = [cross_2,cross_1]
                    for cross in cross_zorder:
                        try:
                            Object = self.medias[cross[layer]]
                            Object.display(
                                surface=surface,alpha=float(cross[layer+'_a']),
                                text=cross[layer+'_main'],header=cross[layer+'_header'],
                                effect=int(cross[layer+'_main_e']),
                                adjust=cross[layer+'_p'],center=cross[layer+'_c']
                            )
                        except Exception as E:
                            print(E)
                            raise RenderError('FailRender',cross[layer],'Bubble')
                elif layer[0:2] == 'Am':
                    cross_1 = this_frame[[layer,layer+'_a',layer+'_t',layer+'_p',layer+'_c']].replace('(.+) (->|<-) (.+)',r'\1',regex=True)
                    cross_2 = this_frame[[layer,layer+'_a',layer+'_t',layer+'_p',layer+'_c']].replace('(.+) (->|<-) (.+)',r'\3',regex=True)
                    if ' -> ' in this_frame[layer]:
                        cross_zorder = [cross_1,cross_2]
                    else:
                        cross_zorder = [cross_2,cross_1]
                    for cross in cross_zorder:
                        try:
                            Object = self.medias[cross[layer]]
                            Object.display(
                                surface=surface,alpha=float(cross[layer+'_a']),frame=int(cross[layer+'_t']),
                                adjust=cross[layer+'_p'],center=cross[layer+'_c']
                            )
                        except Exception as E:
                            print(E)
                            raise RenderError('FailRender',cross[layer],'Animation')
            #或者图层的透明度小于等于0(由于fillna("NA"),出现的异常)
            elif this_frame[layer+'_a']<=0: 
                continue
            # 如果媒体不存在
            elif this_frame[layer] not in self.medias.keys():
                raise RenderError('UndefMedia',this_frame[layer])
            # 渲染背景图层
            elif layer[0:2] == 'BG':
                try:
                    Object = self.medias[this_frame[layer]]
                    Object.display(
                        surface=surface,alpha=this_frame[layer+'_a'],
                        adjust=this_frame[layer+'_p'],center=this_frame[layer+'_c']
                    )
                except Exception as E:
                    print(E)
                    raise RenderError('FailRender',this_frame[layer],'Background')
            # 渲染立绘图层
            elif layer[0:2] == 'Am': # 兼容H_LG1(1)这种动画形式 alpha1.6.3
                try:
                    Object = self.medias[this_frame[layer]]
                    Object.display(
                        surface=surface,alpha=this_frame[layer+'_a'],frame=this_frame[layer+'_t'],
                        adjust=this_frame[layer+'_p'],center=this_frame[layer+'_c']
                    )
                except Exception as E:
                    print(E)
                    raise RenderError('FailRender',this_frame[layer],'Animation')
            # 渲染气泡图层
            elif layer[0:2] == 'Bb':
                try:
                    Object = self.medias[this_frame[layer]]
                    Object.display(
                        surface=surface,alpha=this_frame[layer+'_a'],
                        text=this_frame[layer+'_main'],header=this_frame[layer+'_header'],
                        effect=this_frame[layer+'_main_e'],
                        adjust=this_frame[layer+'_p'],center=this_frame[layer+'_c']
                    )
                except Exception as E:
                    print(E)
                    raise RenderError('FailRender',this_frame[layer],'Bubble')
    # 解析timeline中的 Am 和 Bg 图层，返回clip列表
    def parse_timeline_anime(self,layer:str) -> list:
        break_at_breakpoint = ((layer[0:2]!='BG') & (layer[-1]!='S')) | self.force_split_clip
        track = self.timeline[[layer,layer+'_c']]
        clips = []
        item,begin,end = 'NA',0,0
        center:str = '(0,0)'
        for key,values in track.iterrows():
            # 检查是否有交叉溶解标记
            if ' -> ' in values[layer]:
                item_this = values[layer].split(' -> ')[0]
                center_this = values[layer + '_c'].split(' -> ')[0]
            elif ' <- ' in values[layer]:
                item_this = values[layer].split(' <- ')[0]
                center_this = values[layer + '_c'].split(' <- ')[0]
            else:
                item_this = values[layer]
                center_this = values[layer + '_c']
            #如果item变化了，或者进入了指定的断点(仅断点分隔的图层)
            if (item_this != item) | ((key in self.breakpoint.values) & break_at_breakpoint): 
                if (item == 'NA') | (item!=item): # 如果item是空 
                    pass # 则不输出什么
                else:
                    end = key #否则把当前key作为一个clip的断点
                    clips.append((item,begin,end,center)) #并记录下这个断点
                #无论如何，重设item和begin和center
                item = item_this 
                begin = key
                center = center_this
            #如果不满足断点要求，那么就什么都不做
            else:
                pass            
        # 循环结束之后，最后检定一次是否需要输出一个clips
        #end = key # alpha 1.7.5 debug: 循环结束时的key有可能并不是时间轴的终点
        end = int(self.breakpoint.max()) # 因为有可能到终点为止，所有帧都是一样的，而导致被去重略去
        if (item == 'NA') | (item!=item):
            pass
        else:
            clips.append((item,begin,end,center))
        # 返回一个clip的列表
        return clips
    # 解析timeline中的 Bb 图层，返回clip列表
    def parse_timeline_bubble(self,layer:str) -> list:
        break_at_breakpoint = ((layer[0:2]!='BG') & (layer[-1]!='S')) | self.force_split_clip
        track = self.timeline[[layer,layer+'_main',layer+'_header',layer+'_c']]
        clips = []
        item,begin,end = 'NA',0,0
        center:str = '(0,0)'
        for key,values in track.iterrows():
            # 检查是否有交叉溶解标记
            if ' -> ' in values[layer]:
                item_this = values[layer].split(' -> ')[0]
                center_this = values[layer + '_c'].split(' -> ')[0]
                header_this = values[layer + '_header'].split(' -> ')[0]
                main_this = values[layer + '_main'].split(' -> ')[0]
            elif ' <- ' in values[layer]:
                item_this = values[layer].split(' <- ')[0]
                center_this = values[layer + '_c'].split(' <- ')[0]
                header_this = values[layer + '_header'].split(' <- ')[0]
                main_this = values[layer + '_main'].split(' <- ')[0]
            else:
                item_this = values[layer]
                center_this = values[layer + '_c']
                header_this = values[layer + '_header']
                main_this = values[layer + '_main']
            #如果item变化了，或者进入了指定的断点(这是保证断句的关键！)(仅断点分隔的图层)
            if (item_this != item) | ((key in self.breakpoint.values) & break_at_breakpoint): 
                if (item == 'NA') | (item!=item): # 如果item是空 item 指前一个小节的元素
                    pass # 则不输出什么
                else:
                    end = key #否则把当前key作为一个clip的断点
                    clips.append((item,main_text,header_text,begin,end,center)) #并记录下这个断点
                # 无论如何，重设item和begin
                item = item_this
                begin = key
                center = center_this
            else: #如果不满足断点要求，那么就什么都不做
                pass
            # 然后更新文本内容
            main_text = main_this
            header_text = header_this
            
        # 循环结束之后，最后检定一次是否需要输出一个clips
        #end = key
        end = int(self.breakpoint.max()) # alpha 1.7.5 debug: 而breakpoint的最大值一定是时间轴的终点
        if (item == 'NA') | (item!=item):
            pass
        else:
            clips.append((item,main_text,header_text,begin,end,center))
        # 返回一个clip的列表(str,str,str,int,int,str)
        return clips 
    # 解析timeline中的 BGM 和 SE 图层，返回clip列表
    def parse_timeline_audio(self,layer:str) -> list:
        # 音效轨道始终不受到强制切割序列的影响！
        break_at_breakpoint = False
        track = self.timeline[[layer]]
        clips = []
        item,begin,end = 'NA',0,0
        for key,values in track.iterrows():
            #如果item变化了，或者进入了指定的断点(仅断点分隔的图层)
            if (values[layer] != item) | ((key in self.breakpoint.values) & break_at_breakpoint): 
                if (item == 'NA') | (item!=item): # 如果item是空 
                    pass # 则不输出什么
                else:
                    end = key #否则把当前key作为一个clip的断点
                    clips.append((item,begin,end)) #并记录下这个断点
                #无论如何，重设item和begin和center
                item = values[layer] 
                begin = key
            #如果不满足断点要求，那么就什么都不做
            else:
                pass            
        # 循环结束之后，最后检定一次是否需要输出一个clips
        #end = key # alpha 1.7.5 debug: 循环结束时的key有可能并不是时间轴的终点
        end = int(self.breakpoint.max()) # 因为有可能到终点为止，所有帧都是一样的，而导致被去重略去
        if (item == 'NA') | (item!=item):
            pass
        else:
            clips.append((item,begin,end))
        # 返回一个clip的列表
        return clips 
    # 在建立播放后，初始化全体媒体对象
    def convert_media_init(self):
        # 转换媒体对象
        for media in self.medias.keys(): 
            try:
                self.medias[media].convert()
            except Exception as E:
                print(MediaError('ErrCovert',media,E))
                sys.exit(1)

# 以前台预览的形式播放
class PreviewDisplay(OutputMediaType):
    def __init__(self, rplgenlog: RplGenLog, config: Config, output_path):
        super().__init__(rplgenlog, config, output_path)
        self.main()
    # 重载render，继承显示画面的同时，播放声音
    def render(self, surface: pygame.Surface, this_frame: pd.Series):
        super().render(surface, this_frame)
        # 播放音效
        for key in ['BGM','Voice','SE']:
            if (this_frame[key]=='NA')|(this_frame[key]!=this_frame[key]): #如果是空的
                continue
            elif this_frame[key] == 'stop': # a 1.6.0更新
                pygame.mixer.music.stop() #停止
                pygame.mixer.music.unload() #换碟
            elif (this_frame[key] not in self.medias.keys()): # 不是预先定义的媒体，则一定是合法的路径
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
                        self.medias[this_frame[key]].display() # 否则就直接播放对象
                    else:
                        self.medias[this_frame[key]].display(channel=self.channel_list[key]) # 否则就直接播放对象
                except Exception as E:
                    print(E)
                    raise RenderError('FailPlay',this_frame[key])
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
    # 生成进度条
    def progress_bar(self) -> tuple:
        available_label_color = {'Violet':'#a690e0','Iris':'#729acc','Caribbean':'#29d698','Lavender':'#e384e3',
                                'Cerulean':'#2fbfde','Forest':'#51b858','Rose':'#f76fa4','Mango':'#eda63b',
                                'Purple':'#970097','Blue':'#3c3cff','Teal':'#008080','Magenta':'#e732e7',
                                'Tan':'#cec195','Green':'#1d7021','Brown':'#8b4513','Yellow':'#e2e264'}
        # 新建纯黑图层：width = screen, height = screen//30
        progress_bar_surface = pygame.Surface((self.config.Width,self.config.Height//60),pygame.SRCALPHA)
        progress_bar_surface.fill((0,0,0,255))
        # 每个小节的长度，不包含0
        len_of_section = self.breakpoint.diff().dropna()
        # 整个timeline的总长度：
        timeline_len = self.breakpoint.max()
        # 遍历breakpoint：breakpoint 的值是每个小节的终点，key-1才是起点
        for key in len_of_section.index:
            # 如果key是0，或者本小节的长度是0，跳过本小节
            if (key == 0) or (len_of_section[key] == 0):
                continue
            # 否则，渲染这个图层
            else:
                # 小节颜色：尝试获取立绘Am1、气泡Bb、背景BG2 的colorlabel
                section_first_frame:pd.Series = self.timeline.loc[self.breakpoint[key-1]]
                for layer in ['Am1','Am2','Am3','Bb','BG2']:
                    if section_first_frame[layer] != 'NA' and section_first_frame[layer]==section_first_frame[layer]:
                        try:
                            this_color = self.medias[section_first_frame[layer]].label_color
                        except:
                            # 交叉溶解模式
                            this_color = self.medias[section_first_frame[layer].split(' <- ')[0]].label_color
                        break
                # 小节位置和宽度
                section_pos_x = self.config.Width*(self.breakpoint[key-1] / timeline_len)
                section_width = self.config.Width*(len_of_section[key] / timeline_len)
                if section_width < 1:
                    section_width = 1
                # 渲染
                pygame.draw.rect(
                    surface=progress_bar_surface,
                    color=available_label_color[this_color],
                    rect=(section_pos_x,0,section_width,self.config.Height//60),
                    width=0
                    )
                pygame.draw.rect(
                    surface=progress_bar_surface,
                    color=(0,0,0,255),
                    rect=(section_pos_x,0,section_width,self.config.Height//60),
                    width=1
                    )
        # 设置为半透明：还是算了
        # progress_bar_surface.set_alpha(75)
        # 三角形
        unit = self.config.Height//60
        triangular_surface = pygame.Surface((unit,unit*2),pygame.SRCALPHA)
        triangular_surface.fill((0,0,0,0))
        pygame.draw.polygon(
            surface=triangular_surface,
            color=(255,255,255,255),
            points=[(0,0),(unit,0),(unit/2,unit)]
            )
        pygame.draw.line(
            surface=triangular_surface,
            color=(255,255,255,255),
            start_pos=(unit/2,0),
            end_pos=(unit/2,2*unit),
            width=3
            )
        return (progress_bar_surface,triangular_surface)
    # 初始化播放窗口
    def display_init(self)->None:
        # 修复缩放错误
        # if self.fix_screen == True:
        if True:
            try:
                import ctypes
                ctypes.windll.user32.SetProcessDPIAware() #修复错误的缩放，尤其是在移动设备。
            except Exception:
                print(WarningPrint('FixScrZoom'))
        # 初始化显示窗口
        pygame.init()
        pygame.display.set_caption('TRPG Replay Generator '+EDITION)
        pygame.display.set_icon(pygame.image.load('./media/icon.png'))
        self.fps_clock    = pygame.time.Clock()
        self.screen       = pygame.display.set_mode(size=(self.config.Width,self.config.Height),flags=pygame.SHOWN)
        self.display_size = (self.config.Width,self.config.Height)
        # 用来写注释的文本
        self.note_text = pygame.freetype.Font('./media/SourceHanSansCN-Regular.otf')
        # 建立图形轨道
        self.image  = pygame.Surface((self.config.Width,self.config.Height))
        self.annot  = pygame.Surface((self.config.Width,self.config.Height),pygame.SRCALPHA)
        # 建立音频轨道
        self.VOICE  = pygame.mixer.Channel(1)
        self.SOUEFF = pygame.mixer.Channel(2)
        self.channel_list = {'Voice':self.VOICE,'SE':self.SOUEFF}
        # 转换媒体对象
        self.convert_media_init()
    # 欢迎界面
    def welcome(self) -> None:
        self.medias['white'].display(self.screen)
        self.screen.blit(pygame.transform.scale(pygame.image.load('./media/icon.png'),(self.config.Height//5,self.config.Height//5)),(0.01*self.config.Height,0.79*self.config.Height))
        self.screen.blit(self.note_text.render('Welcome to TRPG Replay Generator!',fgcolor=(150,150,150,255),size=0.0315*self.config.Width)[0],(0.230*self.config.Width,0.460*self.config.Height)) # for 1080p
        self.screen.blit(self.note_text.render(EDITION,fgcolor=(150,150,150,255),size=0.0278*self.config.Height)[0],(0.900*self.config.Width,0.963*self.config.Height))
        self.screen.blit(self.note_text.render('Press space to begin.',fgcolor=(150,150,150,255),size=0.0278*self.config.Height)[0],(0.417*self.config.Width,0.926*self.config.Height))
        pygame.display.update()
        begin = False
        while begin == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.time.delay(1000)
                        pygame.quit()
                        sys.exit(0)
                    elif event.key == pygame.K_SPACE:
                        begin = True
                        break
    # 播放窗口
    def preview_display(self) -> None:
        # 预览播放参数
        timeline_len = self.breakpoint.max() # 时间轴总长度
        n=0 # 当前帧
        forward = 1 #forward==0代表暂停
        show_detail_info = 0 # show_detail_info == 1代表显示详细信息
        detail_info = {0:"Project: Resolution: {0}x{1} ; FrameRate: {2} fps;".format(self.config.Width,self.config.Height,self.config.frame_rate),
                    1:"Render Speed: {0} fps",
                    2:"Frame: {0}/"+str(timeline_len)+" ; Section: {1}/"+str(len(self.breakpoint)),
                    # 3:"Command: {0}",
                    4:"Zorder: {0}".format('>>>'+'>'.join(self.config.zorder)+'>>>'),
                    5:"Layer: BG1:{0}; BG2:{1};",
                    6:"Layer: Am1:{0}; Am2:{1}; Am3:{2}; AmS:{3}",
                    7:"Layer: Bb:{0}; HD:{1}; TX:{2}",
                    8:"Layer: BbS:{0}; HDS:{1}; TXS:{2}"
                    }
        resize_screen = 0 # 是否要强制缩小整个演示窗体
        # 进度条
        progress_bar,triangular = self.progress_bar()
        # self.screen.blit(progress_bar,(0,self.config.Height-self.config.Height//30))
        # 主循环
        while n < timeline_len:
            ct = time.time()
            try:
                # 响应操作事件
                for event in pygame.event.get():
                    # 关闭窗口事件
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
                    # 键盘事件
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.stop_SE()
                            pygame.time.delay(1000)
                            pygame.quit()
                            sys.exit(0)
                        elif event.key in [pygame.K_a,pygame.K_LEFT]:
                            # 警告：这个地方真的是要执行2次的！
                            n=self.breakpoint[(self.breakpoint-n)<0].max()
                            n=self.breakpoint[(self.breakpoint-n)<0].max()
                            if n != n: # 确保不会被a搞崩
                                n = 0
                            self.stop_SE()
                            continue
                        elif event.key in [pygame.K_d,pygame.K_RIGHT]:
                            n=self.breakpoint[(self.breakpoint-n)>0].min()
                            self.stop_SE()
                            continue
                        elif event.key in [pygame.K_F11, pygame.K_p]: # 调整缩放一半
                            from pygame._sdl2.video import Window
                            window = Window.from_display_module()
                            resize_screen = 1 - resize_screen
                            if resize_screen == 1:
                                self.screen = pygame.display.set_mode((self.config.Width//2,self.config.Height//2),flags=pygame.RESIZABLE)
                                self.display_size = (self.config.Width//2,self.config.Height//2)
                                window.position = (100,100)
                            else:
                                self.screen = pygame.display.set_mode((self.config.Width,self.config.Height),flags=pygame.SHOWN)
                                self.display_size = (self.config.Width,self.config.Height)
                                window.position = (0,0)
                            pygame.display.update()
                        elif event.key in [pygame.K_F5, pygame.K_i]: # 详细信息
                            show_detail_info = 1 - show_detail_info # 1->0 0->1
                        elif event.key == pygame.K_SPACE: #暂停
                            forward = 1 - forward # 1->0 0->1
                            self.pause_SE(forward) # 0:pause,1:unpause
                        else:
                            pass
                    # 鼠标点击事件
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: # 左键
                            click_x, click_y = event.pos
                            if resize_screen:
                                click_x = click_x * 2
                                click_y = click_y * 2
                            if click_y >= (self.config.Height - self.config.Height//60): # 进度条区区域
                                # 被点击的帧
                                frame_click = int(click_x / self.config.Width * timeline_len)
                                # 定位到小节起始点
                                n = self.breakpoint[(self.breakpoint-frame_click)<0].max()
                                if n != n: # 确保不会被a搞崩
                                    n = 0
                                self.stop_SE()
                                pygame.mixer.music.stop()
                                continue
                            else:
                                pass
                        else:
                            pass
                    elif event.type == pygame.VIDEORESIZE:
                        self.display_size = (event.w,event.h)
                # 渲染画面
                if n in self.timeline.index:
                    this_frame = self.timeline.loc[n]
                    # 渲染！
                    self.render(self.image,this_frame)
                else:
                    pass
                # 显示进度条
                self.annot.fill([0,0,0,0])
                self.annot.blit(progress_bar,(0,self.config.Height-self.config.Height//60))
                # 显示进度条箭头
                self.annot.blit(triangular,(
                    n/timeline_len*self.config.Width-self.config.Height//120, # x
                    self.config.Height-self.config.Height//30) # y
                    )
                # 小节数显示
                section_display = self.note_text.render('%d'%(this_frame['section']+1),fgcolor=MediaObj.cmap['white'],size=0.02*self.config.Height)[0]
                self.annot.blit(section_display,(
                        n/timeline_len*self.config.Width-section_display.get_size()[0]/2,
                        self.config.Height-self.config.Height//30-self.config.Height//50
                    ))
                # 如果正在暂停
                if forward == 0:
                    self.annot.blit(self.note_text.render('Press space to continue.',fgcolor=MediaObj.cmap['notetext'],size=0.0278*self.config.Height)[0],(0.410*self.config.Width,0.926*self.config.Height)) # pause
                # 显示详情模式
                if show_detail_info == 1:
                    self.annot.blit(self.note_text.render(detail_info[0],fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10))
                    self.annot.blit(self.note_text.render(detail_info[2].format(n,this_frame['section']+1),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10+0.0666*self.config.Height))
                    # self.screen.blit(self.note_text.render(detail_info[3].format(self.rplgenlog.export[this_frame['section']]),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10+0.1*self.config.Height))
                    self.annot.blit(self.note_text.render(detail_info[4],fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10+0.1333*self.config.Height))
                    self.annot.blit(self.note_text.render(detail_info[5].format(this_frame['BG1'],this_frame['BG2']),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10+0.1666*self.config.Height))
                    self.annot.blit(self.note_text.render(detail_info[6].format(this_frame['Am1'],this_frame['Am2'],this_frame['Am3'],this_frame['AmS']),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10+0.2*self.config.Height))
                    self.annot.blit(self.note_text.render(detail_info[7].format(this_frame['Bb'],this_frame['Bb_header'],this_frame['Bb_main']),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10+0.2333*self.config.Height))
                    self.annot.blit(self.note_text.render(detail_info[8].format(this_frame['BbS'],this_frame['BbS_header'],this_frame['BbS_main']),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10+0.2666*self.config.Height))
                    self.annot.blit(self.note_text.render(detail_info[1].format(int(1/(time.time()-ct+1e-4))),fgcolor=MediaObj.cmap['notetext'],size=0.0185*self.config.Height)[0],(10,10+0.0333*self.config.Height))
                # 仅显示帧率
                else:
                    self.annot.blit(self.note_text.render('%d'%(1//(time.time()-ct+1e-4)),fgcolor=MediaObj.cmap['notetext'],size=0.0278*self.config.Height)[0],(10,10)) ##render rate +1e-4 to avoid float divmod()
                # 显示到屏幕
                if resize_screen == 1:
                    # 如果缩放尺寸
                    self.screen.blit(pygame.transform.smoothscale(self.image,self.display_size),(0,0))
                    self.screen.blit(pygame.transform.smoothscale(self.annot,self.display_size),(0,0))
                else:
                    # 如果不缩放
                    self.screen.blit(self.image,(0,0))
                    self.screen.blit(self.annot,(0,0))
                pygame.display.update()
                n = n + forward #下一帧
                self.fps_clock.tick(self.config.frame_rate)
            except RenderError as E:
                print(E)
                print(RenderError('BreakFrame',n))
                pygame.quit()
                sys.exit(1)
        pygame.quit()
        sys.exit(0)
    # 主流程
    def main(self):
        # 初始化窗口
        self.display_init()
        # 显示欢迎页
        self.welcome()
        # 开始播放
        self.preview_display()
        # 终止
        sys.exit(0)

# 导出为MP4视频
class ExportVideo(OutputMediaType):
    # 初始化模块功能，载入外部参数
    def __init__(self, rplgenlog: RplGenLog, config: Config, output_path):
        super().__init__(rplgenlog, config, output_path)
        self.main()
    # 从timeline生成音频文件，返回MP3文件的路径
    def bulid_audio(self) -> str:
        # 输出文件的名称
        ofile = self.output_path+'/'+self.stdin_name+'.mp3'
        # 需要混合的轨道
        tracks = ['SE','Voice','BGM']
        # 主音轨，pydub音频对象
        main_Track = pydub.AudioSegment.silent(duration=int(self.breakpoint.values.max()/self.config.frame_rate*1000),frame_rate=48000) # 主轨道
        # 开始逐个音轨完成混音
        for tr in tracks:
            # 新建当前轨道
            this_Track = pydub.AudioSegment.silent(duration=int(self.breakpoint.values.max()/self.config.frame_rate*1000),frame_rate=48000)
            # 如果是BGM轨道
            if tr == 'BGM':
                BGM_clips = self.parse_timeline_audio(tr)
                for i,item in enumerate(BGM_clips):
                    voice,begin,drop = item
                    # 遇到stop，直切切到下一段
                    if voice == 'stop':
                        continue
                    # 如果是路径形式
                    elif voice not in self.medias.keys():
                        BGM_obj:BGM = BGM(voice[1:-1]) # 去除引号
                    else:
                        BGM_obj:BGM = self.medias[voice]
                    # BGM的终止点，总是在下一个起始点
                    try:
                        end = BGM_clips[i+1][1]
                    except IndexError:
                        end = self.breakpoint.values.max()
                    # 混合音轨
                    this_Track = this_Track.overlay(
                        BGM_obj.recode(begin=begin,end=end),
                        position = int(begin/self.config.frame_rate*1000)
                        )
            # 如果是语音和音效的轨道
            else:
                for item in self.parse_timeline_audio(tr):
                    voice,begin,drop = item
                    # 如果是路径形式
                    if voice not in self.medias.keys():
                        AU_obj:Audio = Audio(voice[1:-1]) # 去除引号
                    else:
                        AU_obj:Audio = self.medias[voice]
                    this_Track = this_Track.overlay(
                        AU_obj.recode(),
                        position = int(begin/self.config.frame_rate*1000)
                        )
            # 将当前轨道叠加到主轨道
            main_Track = main_Track.overlay(this_Track) #合成到主音轨
            print(VideoPrint('TrackDone',tr))
        # 导出音频文件
        main_Track.export(ofile,format='mp3',codec='mp3',bitrate='256k')
        self.audio_path = ofile
        return self.audio_path
    # 渲染视频流
    def build_video(self):
        # 初始化pygame，建立一个不显示的主画面
        pygame.init()
        self.screen = pygame.display.set_mode((self.config.Width,self.config.Height),pygame.HIDDEN)
        # 转换媒体对象
        self.convert_media_init()
        # 建立 ffmpeg 导出引擎
        self.ffmpeg_output()
        # 开始视频渲染
        begin_time = time.time() # 起始时间
        # 主循环
        n=0
        while n < self.breakpoint.max():
            try:
                if n in self.timeline.index:
                    this_frame = self.timeline.loc[n]
                    self.render(self.screen,this_frame)
                    obyte = pygame.image.tostring(self.screen,'RGB')
                else:
                    pass # 节约算力
                self.output_engine.stdin.write(obyte) # 写入视频
                n = n + 1 #下一帧
            except Exception as E:
                print(E)
                print(RenderError('BreakFrame',n))
                self.output_engine.stdin.close()
                pygame.quit()
                sys.exit(1)
            if n%self.config.frame_rate == 1:
                finish_rate = n/self.breakpoint.values.max()
                used_time = time.time()-begin_time
                est_time = int(used_time/finish_rate * (1-finish_rate))
                print(VideoPrint('Progress',
                                '\x1B[33m' + int(finish_rate*50)*'━' + '\x1B[30m' + (50-int(50*finish_rate))*'━' + '\x1B[0m',
                                '%.1f'%(finish_rate*100)+'%', n, '%d'%self.breakpoint.values.max(), 
                                'eta: '+time.strftime("%H:%M:%S", time.gmtime(est_time))), end = "\r")

        # 改一个bug，如果最后一帧正好是显示帧，那么100% 不会正常显示
        print(VideoPrint('Progress', '\x1B[32m' + 50*'━' + '\x1B[0m', '%.1f'%100+'%', n, n ,' '*15))
        self.output_engine.stdin.close()
        pygame.quit()
        # 消耗的时间
        used_time = time.time()-begin_time
        # 最终的显示
        print(VideoPrint('CostTime', time.strftime("%H:%M:%S", time.gmtime(used_time))))
        print(VideoPrint('RendSpeed', '%.2f'%(self.breakpoint.max()/used_time)))
        print(VideoPrint('Done',self.output_path+'/'+self.stdin_name+'.mp4'))
    # ffmepg 导出视频的接口
    def ffmpeg_output(self):
        self.vidio_path = self.output_path +'/'+ self.stdin_name+'.mp4'
        self.output_engine = (
            ffmpeg
            .input(
                'pipe:',
                format = 'rawvideo',
                r      = self.config.frame_rate,
                pix_fmt= 'rgb24',
                s      ='{0}x{1}'.format(self.config.Width,self.config.Height)
                ) # 视频来源
            .output(
                ffmpeg.input(self.audio_path).audio,
                self.vidio_path,
                pix_fmt = 'yuv420p',
                r       = self.config.frame_rate,
                crf     = self.config.crf,
                **{'loglevel':'quiet'}
                ) # 输出
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
        return self.vidio_path
    # 主流程
    def main(self):
        # 欢迎
        print(VideoPrint('Welcome',EDITION))
        print(VideoPrint('SaveAt',self.output_path))
        # 载入外部输入文件
        # self.load_medias()
        # 合成音轨
        print(VideoPrint('VideoBegin'))
        self.bulid_audio()
        print(VideoPrint('AudioDone'))
        # 导出视频
        print(VideoPrint('EncoStart'))
        self.build_video()
        # 终止
        sys.exit(0)

# 导出PR项目
class ExportXML(OutputMediaType):
    # 初始化模块功能，载入外部参数
    def __init__(self,rplgenlog:RplGenLog,config:Config,output_path):
        super().__init__(rplgenlog, config, output_path)
        # 全局变量
        self.Is_NTSC:bool    = self.config.frame_rate % 30 == 0
        self.Audio_type:str  = 'Stereo'
        # 是否强制切割序列，默认是False
        self.force_split_clip:bool = False
        # 初始化媒体
        MediaObj.Is_NTSC = self.Is_NTSC
        MediaObj.Audio_type = self.Audio_type
        # 开始执行主程序
        self.main()
    # 构建序列
    def bulid_sequence(self) -> str:
        # 载入xml模板
        project_tplt = open('./xml_templates/tplt_sequence.xml','r',encoding='utf8').read()
        track_tplt = open('./xml_templates/tplt_track.xml','r',encoding='utf8').read()
        audio_track_tplt = open('./xml_templates/tplt_audiotrack.xml','r',encoding='utf8').read()
        # 轨道列表
        video_tracks = []
        audio_tracks = []
        # 逐图层生成轨道
        for layer in self.config.zorder + ['SE','Voice']:
            # 气泡图层
            if layer[0:2] == 'Bb':
                track_items = self.parse_timeline_bubble(layer)
                bubble_clip_list = []
                text_clip_list = []
                for item in track_items:
                    bubble_this,text_this = self.medias[item[0]].export(
                        text   = item[1],
                        header = item[2],
                        begin  = item[3],
                        end    = item[4],
                        center = item[5]
                        )
                    if bubble_this is not None:
                        # 气泡的返回值可能为空！
                        bubble_clip_list.append(bubble_this)
                    # 文本始终会有一个返回值
                    text_clip_list.append(text_this)
                video_tracks.append(track_tplt.format(**{'targeted':'False','clips':'\n'.join(bubble_clip_list)}))
                video_tracks.append(track_tplt.format(**{'targeted':'True','clips':'\n'.join(text_clip_list)}))
            # 音效图层
            elif layer in ['SE','Voice']:
                track_items = self.parse_timeline_audio(layer)
                clip_list = []
                for item in track_items:
                    if item[0] in self.medias.keys():
                        clip_list.append(self.medias[item[0]].export(begin=item[1]))
                    elif os.path.isfile(item[0][1:-1]) == True: # 注意这个位置的item[0]首尾应该有个引号
                        temp = Audio(item[0][1:-1])
                        clip_list.append(temp.export(begin=item[1]))
                    else:
                        print(WarningPrint('BadAuFile',item[0]))
                audio_tracks.append(audio_track_tplt.format(**{'type':self.Audio_type,'clips':'\n'.join(clip_list)}))
            # 立绘或者背景图层
            else:
                track_items = self.parse_timeline_anime(layer)
                clip_list = []
                for item in track_items:
                    clip_list.append(self.medias[item[0]].export(
                        begin=item[1],
                        end=item[2],
                        center=item[3]
                        ))
                video_tracks.append(track_tplt.format(**{'targeted':'False','clips':'\n'.join(clip_list)}))

        main_output = project_tplt.format(**{
            'timebase'     : '%d'%self.config.frame_rate,
            'ntsc'         : self.Is_NTSC,
            'sequence_name': self.stdin_name,
            'screen_width' : '%d'%self.config.Width,
            'screen_height': '%d'%self.config.Height,
            'tracks_vedio' : '\n'.join(video_tracks),
            'tracks_audio' : '\n'.join(audio_tracks)
            })
        return main_output
    # 主流程
    def main(self):
        # 欢迎
        print(PrxmlPrint('Welcome',EDITION))
        print(PrxmlPrint('SaveAt',self.output_path))
        # 载入od文件
        # self.load_medias()
        # 开始生成
        print(PrxmlPrint('ExpBegin'))
        main_output = self.bulid_sequence()
        # 出入生成的xml文件
        ofile = open(self.output_path+'/'+self.stdin_name+'.xml','w',encoding='utf-8')
        ofile.write(main_output)
        ofile.close()
        print(PrxmlPrint('Done',self.output_path+'/'+self.stdin_name+'.xml'))