#!/usr/bin/env python
# coding: utf-8

# 版本
from core.Utils import EDITION
# 异常定义
from core.Exceptions import RplGenError, Print
from core.Exceptions import ArgumentError, DecodeError, MediaError, RenderError, SyntaxsError
from core.Exceptions import VideoPrint, WarningPrint
# 包导入
import sys
import os
import pandas as pd
import numpy as np
import pygame
import ffmpeg
import pydub
import time
import re
import pickle
# 媒体定义
from core.FreePos import Pos,FreePos,PosGrid
from core.Medias import MediaObj
from core.Medias import Text
from core.Medias import StrokeText
from core.Medias import Bubble
from core.Medias import Balloon
from core.Medias import DynamicBubble
from core.Medias import ChatWindow
from core.Medias import Background
from core.Medias import Animation
from core.Medias import GroupedAnimation
from core.Medias import BuiltInAnimation
from core.Medias import Audio_Video as Audio
from core.Medias import BGM_Video as BGM
# 文件路径
from core.FilePaths import Filepath
# 正则
from core.Regexs import RE_mediadef

class ExportVideo:
    # 初始化模块功能，载入外部参数
    def __init__(self,args):
        # 外部参数
        self.Width = args.Width #显示的分辨率
        self.Height = args.Height
        self.frame_rate = args.FramePerSecond #帧率 单位fps
        self.zorder = args.Zorder.split(',') #渲染图层顺序
        self.stdin_log = args.TimeLine
        self.media_obj = args.MediaObjDefine
        self.char_tab = args.CharacterTable
        self.output_path = args.OutputPath
        self.crf = args.Quality
        # 初始化日志打印
        if args.Language == 'zh':
            # 中文
            Print.lang = 1 
            RplGenError.lang = 1
        else:
            # 英文
            Print.lang == 0
            RplGenError.lang = 0
        # 检查外部参数的合法性
        try:
            for path in [self.stdin_log,self.media_obj]:
                if path is None:
                    print(path)
                    raise ArgumentError('MissInput')
                if os.path.isfile(path) == False:
                    raise ArgumentError('FileNotFound',path)

            if self.output_path is None:
                pass 
            elif os.path.isdir(self.output_path) == False:
                try:
                    os.makedirs(self.output_path)
                except Exception:
                    raise ArgumentError('MkdirErr',self.output_path)
            self.output_path = self.output_path.replace('\\','/')

            # FPS
            if self.frame_rate <= 0:
                raise ArgumentError('FrameRate',str(self.frame_rate))
            elif self.frame_rate>30:
                print(WarningPrint('HighFPS', str(self.frame_rate)))

            if (self.Width<=0) | (self.Height<=0):
                raise ArgumentError('Resolution',str((self.Width,self.Height)))
            if self.Width*self.Height > 3e6:
                print(WarningPrint('HighRes'))
        except Exception as E:
            print(E)
            sys.exit(1)
        # 媒体类，配置
        Filepath.Mediapath = os.path.dirname(self.media_obj.replace('\\','/'))
        MediaObj.screen_size = (self.Width,self.Height)
        MediaObj.frame_rate = self.frame_rate
        # 全局变量
        self.stdin_name = self.stdin_log.replace('\\','/').split('/')[-1]
        self.occupied_variable_name = open('./media/occupied_variable_name.list','r',encoding='utf8').read().split('\n')
        # 载入外部输入参数
        timeline_ifile = open(self.stdin_log,'rb')
        self.timeline,self.break_point,self.bulitin_media = pickle.load(timeline_ifile)
        timeline_ifile.close()
        # 开始执行主流程
        self.main()
    # 载入媒体定义文件和bulitintimeline
    def load_medias(self):
        # 载入od文件
        try:
            object_define_text = open(self.media_obj,'r',encoding='utf-8').read()#.split('\n')
        except UnicodeDecodeError as E:
            print(DecodeError('DecodeErr',E))
            sys.exit(1)
        if object_define_text[0] == '\ufeff': # 139 debug
            print(WarningPrint('UFT8BOM'))
            object_define_text = object_define_text[1:]
        object_define_text = object_define_text.split('\n')
        # 媒体名列表
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
                    sys.exit(1)
        # self.MediaObjects['black'] = Background('black')
        # self.MediaObjects['white'] = Background('white')
        global black ; black = Background('black')
        global white ; white = Background('white')
        self.media_list.append('black')
        self.media_list.append('white')
        # alpha 1.6.5 载入导出的内建媒体
        for key,values in self.bulitin_media.iteritems():
            # 更新：改写内建媒体的value,只需要保留 instantiation 就行了
            exec(values)
            # obj_name = key
            # obj_name,obj_type,obj_args = RE_mediadef.findall(values.split(';')[-1])[0]
            # instantiation = obj_type + obj_args
            # self.MediaObjects[obj_name] = eval(instantiation) 
            self.media_list.append(key)
    # 处理bg 和 am 的parser
    def parse_timeline(self,layer) -> list:
        track = self.timeline[[layer]]
        clips = []
        item,begin,end = 'NA',0,0
        for key,values in track.iterrows():
            #如果item变化了，或者进入了指定的断点
            if (values[layer] != item) | (key in self.break_point.values): 
                if (item == 'NA') | (item!=item): # 如果itme是空 
                    pass # 则不输出什么
                else:
                    end = key #否则把当前key作为一个clip的断点
                    clips.append((item,begin,end)) #并记录下这个断点
                item = values[layer] #无论如何，重设item和begin
                begin = key
            else: #如果不满足断点要求，那么就什么都不做
                pass
        # 循环结束之后，最后检定一次是否需要输出一个clips
        end = key
        if (item == 'NA') | (item!=item):
            pass
        else:
            clips.append((item,begin,end))
        return clips #返回一个clip的列表
    # 渲染一个单帧
    def render(self,this_frame):
        # this_frame -> Series
        for layer in self.zorder:
            # 不渲染的条件：图层为"Na"，或者np.nan
            if (this_frame[layer]=='NA')|(this_frame[layer]!=this_frame[layer]):
                continue
            # 如果是包含了交叉溶解的图层
            elif (' <- ' in this_frame[layer]) | (' -> ' in this_frame[layer]):
                if layer[0:2] == 'Bb':
                    cross_1 = this_frame[[layer,layer+'_header',layer+'_main',layer+'_a',layer+'_p',layer+'_c']].replace('(.+) (->|<-) (.+)',r'\1',regex=True)
                    cross_2 = this_frame[[layer,layer+'_header',layer+'_main',layer+'_a',layer+'_p',layer+'_c']].replace('(.+) (->|<-) (.+)',r'\3',regex=True)
                    if ' -> ' in this_frame[layer]:
                        cross_zorder = [cross_1,cross_2]
                    else:
                        cross_zorder = [cross_2,cross_1]
                    for cross in cross_zorder:
                        try:
                            Object = eval(cross[layer])
                            Object.display(
                                surface=self.screen,alpha=float(cross[layer+'_a']),
                                text=cross[layer+'_main'],header=cross[layer+'_header'],
                                adjust=cross[layer+'_p'],center=cross[layer+'_c']
                            )
                        except Exception:
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
                            Object = eval(cross[layer])
                            Object.display(
                                surface=self.screen,alpha=float(cross[layer+'_a']),frame=int(cross[layer+'_t']),
                                adjust=cross[layer+'_p'],center=cross[layer+'_c']
                            )
                        except Exception:
                            raise RenderError('FailRender',cross[layer],'Animation')
            #或者图层的透明度小于等于0(由于fillna("NA"),出现的异常)
            elif this_frame[layer+'_a']<=0: 
                continue
            # 如果媒体不存在
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
    # 混合音频文件
    def bulid_audio(self):
        # 需要混合的轨道
        tracks = ['SE','Voice','BGM']
        # 主音轨，pydub音频对象
        main_Track = pydub.AudioSegment.silent(duration=int(self.break_point.values.max()/self.frame_rate*1000),frame_rate=48000) # 主轨道
        # 开始逐个音轨完成混音
        for tr in tracks:
            # 新建当前轨道
            this_Track = pydub.AudioSegment.silent(duration=int(self.break_point.values.max()/self.frame_rate*1000),frame_rate=48000)
            # 如果是BGM轨道
            if tr == 'BGM':
                BGM_clips = self.parse_timeline('BGM')
                for i,item in enumerate(BGM_clips):
                    voice,begin,drop = item
                    if voice == 'stop':
                        continue # 遇到stop，直切切到下一段
                    elif voice not in self.media_list: # 如果是路径形式
                        temp_BGM = BGM(voice[1:-1]) # 去除引号
                        voice = 'temp_BGM'
                    try:
                        end = BGM_clips[i+1][1]
                    except IndexError:
                        end = self.break_point.values.max()
                    this_Track = this_Track.overlay(
                        pydub.AudioSegment.silent(duration=int((end-begin)/self.frame_rate*1000),frame_rate=48000).overlay(eval(voice+'.media'),loop=eval(voice+'.loop')),
                        position = int(begin/self.frame_rate*1000)
                        )
            # 如果是语音和音效的轨道
            else:
                for item in self.parse_timeline(tr):
                    voice,begin,drop = item
                    if voice not in self.media_list: # 如果是路径形式
                        temp_AU = Audio(voice[1:-1]) # 去除引号
                        voice = 'temp_AU'
                    this_Track = this_Track.overlay(eval(voice+'.media'),position = int(begin/self.frame_rate*1000))
            # 将当前轨道叠加到主轨道
            main_Track = main_Track.overlay(this_Track) #合成到主音轨
            print(VideoPrint('TrackDone',tr))
        # 导出音频文件
        main_Track.export(self.output_path+'/'+self.stdin_name+'.mp3',format='mp3',codec='mp3',bitrate='256k')
    # 渲染视频流
    def build_video(self):
        # 初始化pygame，建立主画面
        pygame.init()
        self.screen = pygame.display.set_mode((self.Width,self.Height),pygame.HIDDEN)
        # 转换媒体对象
        for media in self.media_list: 
            try:
                exec(media+'.convert()')
            except Exception as E:
                print(MediaError('ErrCovert', media, E))
                sys.exit(1)
        # 建立 ffmpeg 导出引擎
        self.ffmpeg_output()
        # 开始视频渲染
        begin_time = time.time() # 起始时间
        # 主循环
        n=0
        while n < self.break_point.max():
            try:
                if n in self.timeline.index:
                    this_frame = self.timeline.loc[n]
                    self.render(this_frame)
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
            if n%self.frame_rate == 1:
                finish_rate = n/self.break_point.values.max()
                used_time = time.time()-begin_time
                est_time = int(used_time/finish_rate * (1-finish_rate))
                print(VideoPrint('Progress',
                                '\x1B[33m' + int(finish_rate*50)*'━' + '\x1B[30m' + (50-int(50*finish_rate))*'━' + '\x1B[0m',
                                '%.1f'%(finish_rate*100)+'%', n, '%d'%self.break_point.values.max(), 
                                'eta: '+time.strftime("%H:%M:%S", time.gmtime(est_time))), end = "\r")

        # 改一个bug，如果最后一帧正好是显示帧，那么100% 不会正常显示
        print(VideoPrint('Progress', '\x1B[32m' + 50*'━' + '\x1B[0m', '%.1f'%100+'%', n, n ,' '*15))
        self.output_engine.stdin.close()
        pygame.quit()
        # 消耗的时间
        used_time = time.time()-begin_time
        # 最终的显示
        print(VideoPrint('CostTime', time.strftime("%H:%M:%S", time.gmtime(used_time))))
        print(VideoPrint('RendSpeed', '%.2f'%(self.break_point.max()/used_time)))
        print(VideoPrint('Done',self.output_path+'/'+self.stdin_name+'.mp4'))
    # ffmepg 导出视频的接口
    def ffmpeg_output(self):
        self.output_engine = (
            ffmpeg
            .input('pipe:',format='rawvideo',r=self.frame_rate,pix_fmt='rgb24', s='{0}x{1}'.format(self.Width,self.Height)) # 视频来源
            .output(ffmpeg.input(self.output_path+'/'+self.stdin_name+'.mp3').audio,
                    self.output_path +'/'+ self.stdin_name+'.mp4',
                    pix_fmt='yuv420p', r=self.frame_rate, crf=self.crf,
                    **{'loglevel':'quiet'}) # 输出
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
    # 主流程
    def main(self):
        # 欢迎
        print(VideoPrint('Welcome',EDITION))
        print(VideoPrint('SaveAt',self.output_path))
        # 载入外部输入文件
        self.load_medias()
        # 合成音轨
        print(VideoPrint('VideoBegin'))
        self.bulid_audio()
        print(VideoPrint('AudioDone'))
        # 导出视频
        print(VideoPrint('EncoStart'))
        self.build_video()
        # 终止
        sys.exit(0)
# 入口
if __name__ == '__main__':
    import argparse
    # 外部参数输入
    ap = argparse.ArgumentParser(description="Export MP4 video from timeline file.")
    ap.add_argument("-l", "--TimeLine", help='Timeline (and break_point with same name), which was generated by replay_generator.py.',type=str)
    ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
    ap.add_argument("-t", "--CharacterTable", help='This program do not need CharacterTable.',type=str)
    ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the project timeline and break_point file.',type=str,default=None)
    # 增加一个，读取时间轴和断点文件的选项！
    ap.add_argument("-F", "--FramePerSecond", help='Set the FPS of display, default is 30 fps, larger than this may cause lag.',type=int,default=30)
    ap.add_argument("-W", "--Width", help='Set the resolution of display, default is 1920, larger than this may cause lag.',type=int,default=1920)
    ap.add_argument("-H", "--Height", help='Set the resolution of display, default is 1080, larger than this may cause lag.',type=int,default=1080)
    ap.add_argument("-Z", "--Zorder", help='Set the display order of layers, not recommended to change the values unless necessary!',type=str,
                    default='BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS')
    ap.add_argument("-Q", "--Quality", help='Choose the quality (ffmpeg crf) of output video.',type=int,default=24)
    # 语言
    ap.add_argument("--Language",help='Choose the language of running log',default='en',type=str)
    args = ap.parse_args()
    # 主
    try:
        ExportVideo(args=args)
    except:
        from traceback import print_exc
        print_exc()