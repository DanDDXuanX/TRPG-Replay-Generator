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
# 动态切换效果类
from core.Motion import MotionMethod
# 正则表达式
from core.Regexs import *
# 曲线函数
from core.Formulas import linear,quadratic,quadraticR,sigmoid,right,left,sincurve,normalized
from core.Formulas import formula_available
# 小工具们
from core.Utils import *
# 配置
from core.ProjConfig import Config
from core.ScriptParser import RplGenLog,MediaDef,CharTable,Script

class ReplayGenerator:
    # 初始化参数
    def __init__(self,args):
        try:
            # 外部输入文件
            self.log_path = args.LogFile
            self.media_path = args.MediaObjDefine
            self.char_path = args.CharacterTable
            self.output_path = args.OutputPath
            self.json_path = args.Json
            # 配置
            if self.json_path != None:
                # 如果是json输入
                input_json = Script(json_input=self.json_input)
                self.config = Config(dict_input=input_json.struct['config'])
                # 读取输入工程结构
                self.medef = MediaDef(dict_input=input_json.struct['medef'])
                self.chartab = CharTable(dict_input=input_json.struct['chartab'])
                self.rplgenlog = RplGenLog(dict_input=input_json.struct['rplgenlog'])
            else:
                # 通过args输入
                self.config = Config(argparse_input=args)
                # 检查输入文件可用性
                for path in [self.log_path,self.media_path,self.char_path]:
                    if path is None:
                        raise ArgumentError('MissInput')
                    if os.path.isfile(path) == False:
                        raise ArgumentError('FileNotFound',path)
                    self.medef = MediaDef(file_input=self.media_path)
                    self.chartab = CharTable(file_input=self.char_path)
                    self.rplgenlog = RplGenLog(file_input=self.log_path)
        # debug
        except ArgumentError as E:
            self.medef = MediaDef(file_input='./toy/MediaObject.txt')
            self.chartab = CharTable(file_input='./toy/CharactorTable.tsv')
            self.rplgenlog = RplGenLog(file_input='./toy/LogFile.rgl')
            self.output_path = './test_output'
        except Exception as E:
            print(E)
            self.system_terminated('Error')
        self.main()
    # 渲染单帧
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
                            Object = self.rplgenlog.medias[cross[layer]]
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
                            Object = self.rplgenlog.medias[cross[layer]]
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
            elif this_frame[layer] not in self.rplgenlog.medias.keys():
                raise RenderError('UndefMedia',this_frame[layer])
            # 渲染背景图层
            elif layer[0:2] == 'BG':
                try:
                    Object = self.rplgenlog.medias[this_frame[layer]]
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
                    Object = self.rplgenlog.medias[this_frame[layer]]
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
                    Object = self.rplgenlog.medias[this_frame[layer]]
                    Object.display(
                        surface=surface,alpha=this_frame[layer+'_a'],
                        text=this_frame[layer+'_main'],header=this_frame[layer+'_header'],
                        effect=this_frame[layer+'_main_e'],
                        adjust=this_frame[layer+'_p'],center=this_frame[layer+'_c']
                    )
                except Exception as E:
                    print(E)
                    raise RenderError('FailRender',this_frame[layer],'Bubble')
        # 播放音效
        for key in ['BGM','Voice','SE']:
            if (this_frame[key]=='NA')|(this_frame[key]!=this_frame[key]): #如果是空的
                continue
            elif this_frame[key] == 'stop': # a 1.6.0更新
                pygame.mixer.music.stop() #停止
                pygame.mixer.music.unload() #换碟
            elif (this_frame[key] not in self.rplgenlog.medias.keys()): # 不是预先定义的媒体，则一定是合法的路径
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
                        self.rplgenlog.medias[this_frame[key]].display() # 否则就直接播放对象
                        # exec('{0}.display()'.format(this_frame[key]))
                    else:
                        self.rplgenlog.medias[this_frame[key]].display(channel=self.channel_list[key]) # 否则就直接播放对象
                        # exec('{0}.display(channel={1})'.format(this_frame[key],self.channel_list[key])) 
                except Exception as E:
                    print(E)
                    raise RenderError('FailPlay',this_frame[key])
        return 1
    # 执行语音合成子进程
    # def flag_synthanyway(self) -> None:
    # 导出的子进程
    # def flag_export(self) -> None:
    # 执行输入文件
    def execute_input(self):
        MediaObj.export_xml = True
        MediaObj.output_path = self.output_path
        # log
        try:
            self.timeline = self.rplgenlog.execute(media_define=self.medef,char_table=self.chartab,config=self.config)
            self.breakpoint = self.rplgenlog.break_point
        except Exception as E:
            print(E)
            self.system_terminated('Error')
    # 倒计时：已禁用，待删除
    def timer(self,clock):
        self.rplgenlog.medias['white'].display(self.screen)
        self.screen.blit(self.note_text.render('%d'%clock,fgcolor=(150,150,150,255),size=0.0926*self.config.Height)[0],(0.484*self.config.Width,0.463*self.config.Height)) # for 1080p
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
                            this_color = self.rplgenlog.medias[section_first_frame[layer]].label_color
                        except:
                            # 交叉溶解模式
                            this_color = self.rplgenlog.medias[section_first_frame[layer].split(' <- ')[0]].label_color
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
    # 播放窗口
    def preview_display(self) -> None:
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
        fps_clock=pygame.time.Clock()
        self.screen = pygame.display.set_mode(size=(self.config.Width,self.config.Height),flags=pygame.SHOWN)
        self.display_size = (self.config.Width,self.config.Height)
        pygame.display.set_icon(pygame.image.load('./media/icon.png'))
        # 用来写注释的文本
        self.note_text = pygame.freetype.Font('./media/SourceHanSansCN-Regular.otf')
        # 建立图形轨道
        self.image = pygame.Surface((self.config.Width,self.config.Height))
        self.annot = pygame.Surface((self.config.Width,self.config.Height),pygame.SRCALPHA)
        # 建立音频轨道
        self.VOICE = pygame.mixer.Channel(1)
        self.SOUEFF = pygame.mixer.Channel(2)
        self.channel_list = {'Voice':self.VOICE,'SE':self.SOUEFF}
        # 转换媒体对象
        for media in self.rplgenlog.medias.keys(): 
            try:
                self.rplgenlog.medias[media].convert()
            except Exception as E:
                print(MediaError('ErrCovert',media,E))
                self.system_terminated('Error')
        # 预备画面
        self.rplgenlog.medias['white'].display(self.screen)
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
                        self.system_terminated('User')
                    # 键盘事件
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.stop_SE()
                            pygame.time.delay(1000)
                            pygame.quit()
                            self.system_terminated('User')
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
                fps_clock.tick(self.config.frame_rate)
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
        # if self.synth_anyway == True:
        #     self.flag_synthanyway()
        # 载入媒体文件
        # print(MainPrint('LoadMedef'))
        # self.load_medias()
        # # 载入角色配置文件
        # print(MainPrint('LoadChrtab'))
        # self.load_chartab()
        # # 载入并解析log文件 parser()
        # print(MainPrint('LoadRGL'))
        # self.load_rplgenlog()
        # 判断是否指定输出路径，准备各种输出选项
        # if self.output_path != None:
        #     self.flag_export()
        self.execute_input()
        # 开始预览播放
        # self.preview_display()
        from export_xml import ExportXML
        ExportXML(rplgenlog=self.rplgenlog,config=self.config,output_path=self.output_path)

if __name__ == '__main__':
    import argparse
    # 外部参数输入
    # 参数处理
    ap = argparse.ArgumentParser(description="Generating your TRPG replay video from logfile.")
    ap.add_argument("-l", "--LogFile", help='The standerd input of this programme, which is mainly composed of TRPG log.',type=str)
    ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
    ap.add_argument("-t", "--CharacterTable", help='The correspondence between character and media elements, using tab separated text file or Excel table.',type=str)
    ap.add_argument("-j", "--Json", help='Use the config from json file, instead of arguments from command.',type=str)
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
    ap.add_argument("--ForceSplitClip", help='Force to separate clips at breakpoints while exporting PR sequence.',action='store_true' )
    # 语言
    ap.add_argument("--Language",help='Choose the language of running log',default='en',type=str)
    # 主
    args = ap.parse_args()
    try:
        ReplayGenerator(args=args)
    except:
        from traceback import print_exc
        print_exc()