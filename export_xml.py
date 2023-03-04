#!/usr/bin/env python
# coding: utf-8
from core.Utils import EDITION

# 异常定义

from core.Exceptions import RplGenError, Print
from core.Exceptions import ArgumentError, DecodeError, SyntaxsError
from core.Exceptions import PrxmlPrint, WarningPrint

# 包导入

import sys
import os

import pandas as pd
import numpy as np
import re
import pickle
import time
# 媒体路径
from core.FilePaths import Filepath
# 媒体导入
from core.FreePos import Pos,FreePos,PosGrid
from core.Medias import MediaObj
from core.Medias import Text,StrokeText
from core.Medias import Bubble,Balloon,DynamicBubble,ChatWindow
from core.Medias import Background
from core.Medias import Animation,GroupedAnimation,BuiltInAnimation
from core.Medias import Audio,BGM
# 正则
from core.Regexs import RE_mediadef

from core.ScriptParser import MediaDef,CharTable,RplGenLog
from core.ProjConfig import Config

# 导出PR项目模块
class ExportXML:
    # 初始化模块功能，载入外部参数
    def __init__(self,rplgenlog:RplGenLog,config:Config,output_path):
        # 载入项目
        self.timeline:pd.DataFrame = rplgenlog.main_timeline
        self.break_point:pd.Series = rplgenlog.break_point
        self.medias:dict           = rplgenlog.medias
        self.config:Config         = config
        # 全局变量
        self.Is_NTSC:bool    = self.config.frame_rate % 30 == 0
        self.Audio_type:str  = 'Stereo'
        self.stdin_name:str  = '%d'%time.time()
        self.output_path:str = output_path
        # 是否强制切割序列，默认是False
        self.force_split_clip:bool = False
        # 初始化媒体
        MediaObj.Is_NTSC = self.Is_NTSC
        # 开始执行主程序
        self.main()
    # 载入媒体定义文件和bulitintimeline
    # def load_medias(self):
    # 处理bg 和 am 的parser
    def parse_timeline_anime(self,layer) -> list:
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
            if (item_this != item) | ((key in self.break_point.values) & break_at_breakpoint): 
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
        end = int(self.break_point.max()) # 因为有可能到终点为止，所有帧都是一样的，而导致被去重略去
        if (item == 'NA') | (item!=item):
            pass
        else:
            clips.append((item,begin,end,center))
        return clips #返回一个clip的列表
    # 处理se 和 bgm 的parser
    def parse_timeline_audio(self,layer) -> list:
        break_at_breakpoint = ((layer[0:2]!='BG') & (layer[-1]!='S')) | self.force_split_clip
        track = self.timeline[[layer]]
        clips = []
        item,begin,end = 'NA',0,0
        for key,values in track.iterrows():
            #如果item变化了，或者进入了指定的断点(仅断点分隔的图层)
            if (values[layer] != item) | ((key in self.break_point.values) & break_at_breakpoint): 
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
        end = int(self.break_point.max()) # 因为有可能到终点为止，所有帧都是一样的，而导致被去重略去
        if (item == 'NA') | (item!=item):
            pass
        else:
            clips.append((item,begin,end))
        return clips #返回一个clip的列表
    # 处理Bb 的parser
    def parse_timeline_bubble(self,layer) -> list:
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
            if (item_this != item) | ((key in self.break_point.values) & break_at_breakpoint): 
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
        end = int(self.break_point.max()) # alpha 1.7.5 debug: 而breakpoint的最大值一定是时间轴的终点
        if (item == 'NA') | (item!=item):
            pass
        else:
            clips.append((item,main_text,header_text,begin,end,center))
        return clips #返回一个clip的列表(str,str,str,int,int,str)
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

# 入口
if __name__ == '__main__':
    pass
    # import argparse
    # # 外部输入参数
    # ap = argparse.ArgumentParser(description="Export Premiere Pro XML from timeline file.")
    # ap.add_argument("-l", "--TimeLine", help='Timeline (and break_point with same name), which was generated by replay_generator.py.',type=str)
    # ap.add_argument("-d", "--MediaObjDefine", help='Definition of the media elements, using real python code.',type=str)
    # ap.add_argument("-t", "--CharacterTable", help='This program do not need CharacterTable.',type=str)
    # ap.add_argument("-o", "--OutputPath", help='Choose the destination directory to save the project timeline and break_point file.',type=str,default=None)
    # # 导出选项
    # ap.add_argument("-F", "--FramePerSecond", help='Set the FPS of display, default is 30 fps, larger than this may cause lag.',type=int,default=30)
    # ap.add_argument("-W", "--Width", help='Set the resolution of display, default is 1920, larger than this may cause lag.',type=int,default=1920)
    # ap.add_argument("-H", "--Height", help='Set the resolution of display, default is 1080, larger than this may cause lag.',type=int,default=1080)
    # ap.add_argument("-Z", "--Zorder", help='Set the display order of layers, not recommended to change the values unless necessary!',type=str,
    #                 default='BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS')
    # # Flag
    # ap.add_argument("--ForceSplitClip", help='Force to separate clips at breakpoints while exporting PR sequence.',action='store_true' )
    # # 语言
    # ap.add_argument("--Language",help='Choose the language of running log',default='en',type=str)
    # args = ap.parse_args()
    # # 主
    # try:
    #     ExportXML(args=args)
    # except:
    #     from traceback import print_exc
    #     print_exc()