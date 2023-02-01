#!/usr/bin/env python
# coding: utf-8
# 标记语言 <-> json{dic}

import numpy as np
import pandas as pd

from .Exceptions import DecodeError,ParserError,WarningPrint
from .Regexs import *

class RplGenLog:
    # 初始化
    def __init__(self,filepath:str=None,json:dict=None) -> None:
        # json 输入
        if json is not None:
            self.struct = json
        # RGL 输入
        elif filepath is not None:
            self.struct = self.RGL_parser(filepath=filepath)
        # 如果没有输入
        else:
            self.struct = {}
    # RGL -> struct
    def RGL_parser(self,filepath) -> dict:
        # 读取文本文件
        try:
            stdin_text = open(filepath,'r',encoding='utf8').read()
        except UnicodeDecodeError as E:
            raise DecodeError('DecodeErr',E)
        # 清除 UTF-8 BOM
        if stdin_text[0] == '\ufeff':
            print(WarningPrint('UFT8BOM'))
            stdin_text = stdin_text[1:]
        # 分割小节
        stdin_text = stdin_text.split('\n')
        # 结构体
        struct = {}
        # 逐句读取小节
        for i,text in enumerate(stdin_text):
            # 本行的结构体
            this_section = {}
            # 空白行
            if text == '':
                this_section['type'] = 'blank'
            # 注释行 格式： # word
            elif text[0] == '#':
                this_section['type'] = 'comment'
                this_section['content'] = text[1:]
            # 对话行 格式： [角色1,角色2(30).happy]<replace=30>:巴拉#巴拉#巴拉<w2w=1>
            elif (text[0] == '[') & (']' in text):
                # 类型
                this_section['type'] = 'dialog'
                # 拆分为：[角色框]、<效果>、:文本、<文本效果>、{音效}
                try:
                    cr,cre,ts,tse,se = RE_dialogue.findall(text)[0]
                except IndexError:
                    raise ParserError('UnableDial')
                # [角色框]
                list_of_CR = RE_characor.findall(cr)
                this_charactor_set = {}
                if len(list_of_CR) > 3:
                    # 角色不能超过3个!
                    raise ParserError('2muchChara',str(i+1))
                for k,charactor in enumerate(list_of_CR[0:3]):
                    this_charactor = {}
                    # 名字 (透明度) .差分
                    this_charactor['name'],alpha,subtype= charactor
                    if subtype == '':
                        this_charactor['subtype'] = 'default'
                    else:
                        this_charactor['subtype'] = subtype[1:] # 去除首字符.
                    if alpha == '':
                        this_charactor['alpha'] = -1
                    else:
                        this_charactor['alpha'] = int(alpha[1:-1]) # 去掉首尾括号
                    this_charactor_set[k] = this_charactor
                this_section['charactor_set'] = this_charactor_set
                # <效果>
                if cre == '':
                    this_section['ab_method'] = 'default'
                    this_section['ab_method_dur'] = 'default'
                else:
                    this_section['ab_method'],method_dur =RE_modify.findall(cre)[0]
                    if method_dur == '':
                        this_section['ab_method_dur'] = 'default'
                    else:
                        this_section['ab_method_dur'] = int(method_dur[1:])
                # :文本
                this_section['content'] = ts
                # <文本效果>
                if tse == '':
                    this_section['tx_method'] = 'default'
                    this_section['tx_method_dur'] = 'default'
                else:
                    this_section['tx_method'],method_dur =RE_modify.findall(tse)[0]
                    if method_dur == '':
                        this_section['tx_method_dur'] = 'default'
                    else:
                        this_section['tx_method_dur'] = int(method_dur[1:])
                # {音效}
                if se == '':
                    this_section['sound_set'] = {}
                else:
                    this_sound_set = {}
                    
                    # 星标列表 {*}
                    asterisk_timeset = RE_asterisk.findall(se)
                    # 没检测到星标
                    if len(asterisk_timeset) == 0:  
                        pass
                    # 检查到一个星标
                    elif len(asterisk_timeset) == 1:
                        # obj;  time
                        this_asterisk = {}
                        # 音效
                        if asterisk_timeset[0][1] == '':
                            this_asterisk['sound'] = False
                        else:
                            this_asterisk['sound'] = asterisk_timeset[0][1][:-1] # 去除最后存在的分号
                        # 时间
                        if asterisk_timeset[0][-1] == '':
                            this_asterisk['time'] = False
                        else:
                            try:
                                this_asterisk['time'] = float(asterisk_timeset[0][-1])
                            except Exception:
                                this_asterisk['time'] = False
                                if this_asterisk['sound'] == False:
                                    # 指定发言内容
                                    this_asterisk['specified_speech'] = asterisk_timeset[0][-1]
                        if this_asterisk['sound'] == False or this_asterisk['time'] == False:
                            # 如果是待合成的
                            this_sound_set['{*}'] = this_asterisk
                        else:
                            # 如果是合规的
                            this_sound_set['*'] = this_asterisk
                    # 检测到复数个星标
                    else:
                        raise ParserError('2muchAster',str(i+1))
                    
                    # 音效列表 {}
                    list_of_SE = RE_sound_simple.findall(se)
                    for k,sound in enumerate(list_of_SE): #this_sound = ['{SE_obj;30}','{SE_obj;30}']
                        this_sound = {}
                        if ';' in sound:
                            this_sound['sound'],delay = sound[1:-1].split(';')
                            try:
                                this_sound['delay'] = int(delay)
                            except Exception:
                                this_sound['delay'] = 0
                        else:
                            this_sound['sound'] = sound[1:-1]
                            this_sound['delay'] = 0
                        this_sound_set[k] = this_sound
                    # 给到上一层
                    this_section['sound_set'] = this_sound_set
            # 背景设置行，格式： <background><black=30>:BG_obj
            elif text[0:12] == '<background>':
                pass
            # 常驻立绘设置行，格式：<animation><black=30>:(Am_obj,Am_obj2)
            elif text[0:11] == '<animation>':
                pass
            # 常驻气泡设置行，格式：<bubble><black=30>:Bubble_obj("Header_text","Main_text",<text_method>)
            elif text[0:8] == '<bubble>':
                pass
            # 参数设置行，格式：<set:speech_speed>:220
            elif (text[0:5] == '<set:') & ('>:' in text):
                pass
            # 清除行，仅适用于ChatWindow
            elif (text[0:8] == '<clear>:'):
                pass
            # 预设动画，损失生命
            elif text[0:11] == '<hitpoint>:':
                pass
            # 预设动画，骰子
            elif text[0:7] == '<dice>:':
                pass
            # 等待行，停留在上一个小节的结束状态，不影响S图层
            elif text[0:7] == '<wait>:':
                pass
            else:
                raise ParserError('UnrecLine',str(i+1))
            struct[i] = this_section
        # 返回值
        return struct