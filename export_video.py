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
from core.Medias import Audio
from core.Medias import BGM
# 文件路径
from core.FilePaths import Filepath
# 正则
from core.Regexs import RE_mediadef

from core.ScriptParser import MediaDef,CharTable,RplGenLog
from core.ProjConfig import Config

from replay_generator_new import OutputMediaType

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
        main_Track = pydub.AudioSegment.silent(duration=int(self.break_point.values.max()/self.frame_rate*1000),frame_rate=48000) # 主轨道
        # 开始逐个音轨完成混音
        for tr in tracks:
            # 新建当前轨道
            this_Track = pydub.AudioSegment.silent(duration=int(self.break_point.values.max()/self.frame_rate*1000),frame_rate=48000)
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
                        end = self.break_point.values.max()
                    # 混合音轨
                    this_Track = this_Track.overlay(
                        BGM_obj.recode(begin=begin,end=end),
                        position = int(begin/self.frame_rate*1000)
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
                        position = int(begin/self.frame_rate*1000)
                        )
            # 将当前轨道叠加到主轨道
            main_Track = main_Track.overlay(this_Track) #合成到主音轨
            print(VideoPrint('TrackDone',tr))
        # 导出音频文件
        main_Track.export(ofile,format='mp3',codec='mp3',bitrate='256k')
        return ofile
    # 渲染视频流
    def build_video(self):
        # 初始化pygame，建立一个不显示的主画面
        pygame.init()
        self.screen = pygame.display.set_mode((self.Width,self.Height),pygame.HIDDEN)
        # 转换媒体对象
        self.convert_media_init()
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
