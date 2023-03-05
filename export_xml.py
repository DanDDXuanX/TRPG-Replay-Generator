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

from replay_generator_new import OutputMediaType

# 导出PR项目模块
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
