#!/usr/bin/env python
# coding: utf-8
# 标记语言 <-> json{dic}

import numpy as np
import pandas as pd

from .Exceptions import DecodeError,ParserError,WarningPrint,SyntaxsError
from .Regexs import *
from .Formulas import *

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
    def charactor_parser(self,cr:str,i=0)->dict: # [CH1,CH2,CH3]
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
        return this_charactor_set
    def method_parser(self,method:str)->dict: # <method=0>
        this_section = {}
        if method == '':
            this_section['method'] = 'default'
            this_section['method_dur'] = 'default'
        else:
            this_section['method'],method_dur =RE_modify.findall(method)[0]
            if method_dur == '':
                this_section['method_dur'] = 'default'
            else:
                this_section['method_dur'] = int(method_dur[1:])
        return this_section
    def sound_parser(self,sound:str,i=0)->dict: # {SE;30}
        this_sound_set = {}
        if sound == '':
            return this_sound_set
        else:
            # 星标列表 {*}
            list_of_AS = RE_asterisk.findall(sound)
            # 没检测到星标
            if len(list_of_AS) == 0:  
                pass
            # 检查到一个星标
            elif len(list_of_AS) == 1:
                # obj;  time
                this_asterisk = {}
                # 音效
                if list_of_AS[0][1] == '':
                    this_asterisk['sound'] = False
                else:
                    this_asterisk['sound'] = list_of_AS[0][1][:-1] # 去除最后存在的分号
                # 时间
                if list_of_AS[0][-1] == '':
                    this_asterisk['time'] = False
                else:
                    try:
                        this_asterisk['time'] = float(list_of_AS[0][-1])
                    except Exception:
                        this_asterisk['time'] = False
                        if this_asterisk['sound'] == False:
                            # 指定发言内容
                            this_asterisk['specified_speech'] = list_of_AS[0][-1]
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
            list_of_SE = RE_sound_simple.findall(sound)
            for k,se in enumerate(list_of_SE): #this_sound = ['{SE_obj;30}','{SE_obj;30}']
                this_soundeff = {}
                if ';' in se:
                    this_soundeff['sound'],delay = se[1:-1].split(';')
                    try:
                        this_soundeff['delay'] = int(delay)
                    except Exception:
                        this_soundeff['delay'] = 0
                else:
                    this_soundeff['sound'] = se[1:-1]
                    this_soundeff['delay'] = 0
                this_sound_set[k] = this_soundeff
            # 给到上一层
            return this_sound_set
    def bubble_parser(self,bubble_exp:str,i=0)->dict: # Bubble("header_","main_text",<w2w=1>)
        # 解析
        try:
            this_bb,this_hd,this_tx,this_method_label,this_tx_method,this_tx_dur = RE_bubble.findall(bubble_exp)[0]
        except IndexError:
            raise ParserError('InvaPBbExp',bubble_exp,str(i+1))
        # 结构
        this_bubble = {}
        # 对象
        this_bubble['bubble'] = this_bb
        # 文字
        this_bubble['header_text'] = this_hd
        this_bubble['main_text'] = this_tx
        # 文字效果
        this_bubble['tx_method'] = self.method_parser(this_method_label)
        # 返回
        return this_bubble
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
                this_section['charactor_set'] = self.charactor_parser(cr=cr,i=1)
                # <效果>
                this_section['ab_method'] =  self.method_parser(cre)
                # :文本
                this_section['content'] = ts
                # <文本效果>
                this_section['tx_method'] = self.method_parser(tse)
                # {音效}
                this_section['sound_set'] = self.sound_parser(sound=se,i=i)
            # 背景设置行，格式： <background><black=30>:BG_obj
            elif text[0:12] == '<background>':
                # 解析
                try:
                    obj_type,obje,objc = RE_placeobj.findall(text)[0]
                    # 类型
                    this_section['type'] = obj_type
                except IndexError:
                    raise ParserError('UnablePlace')
                # <效果>
                this_section['bb_method'] = self.method_parser(obje)
                # 对象
                this_section['object'] = objc
            # 常驻立绘设置行，格式：<animation><black=30>:(Am_obj,Am_obj2)
            elif text[0:11] == '<animation>':
                # 解析
                try:
                    obj_type,obje,objc = RE_placeobj.findall(text)[0]
                    # 类型
                    this_section['type'] = obj_type
                except IndexError:
                    raise ParserError('UnablePlace')
                # <效果>
                this_section['am_method'] = self.method_parser(obje)
                # 对象
                if objc == 'NA' or objc == 'None':
                    this_section['object'] = False
                elif (objc[0] == '(') and (objc[-1] == ')'):
                    # 如果是一个集合
                    this_GA_set = {} # GA
                    animation_list = objc[1:-1].split(',')
                    for k,am in enumerate(animation_list):
                        this_GA_set[k] = am
                    this_section['object'] = this_GA_set
                else:
                    this_section['object'] = objc
            # 常驻气泡设置行，格式：<bubble><black=30>:Bubble_obj("Header_text","Main_text",<text_method>)
            elif text[0:8] == '<bubble>':
                # 解析
                try:
                    obj_type,obje,objc = RE_placeobj.findall(text)[0]
                    # 类型
                    this_section['type'] = obj_type
                except IndexError:
                    raise ParserError('UnablePlace')
                # <效果>
                this_section['bb_method'] = self.method_parser(obje)
                # 对象
                if objc == 'NA' or objc == 'None':
                    this_section['object'] = False
                else:
                    this_section['object'] = self.bubble_parser(bubble_exp=objc,i=i)
            # 参数设置行，格式：<set:speech_speed>:220
            elif (text[0:5] == '<set:') & ('>:' in text):
                try:
                    target,args = RE_setting.findall(text)[0]
                except IndexError:
                    raise ParserError('UnableSet')
                # 类型
                this_section['type'] = 'set'
                this_section['target'] = target
                # 类型1：整数型
                if target in ['am_dur_default','bb_dur_default','bg_dur_default','tx_dur_default','speech_speed','asterisk_pause','secondary_alpha']:
                    this_section['arg_type'] = 'digit' # natural number
                    try:
                        this_section['args'] = int(args)
                    except:
                        print(WarningPrint('Set2Invalid',target,args))
                        this_section['args'] = args
                # 类型2：method
                elif target in ['am_method_default','bb_method_default','bg_method_default','tx_method_default']:
                    this_section['arg_type'] = 'method'
                    try:
                        this_section['args'] = self.method_parser(args)
                    except IndexError:
                        raise ParserError('SetInvMet',target,args)
                # 类型3：BGM
                elif target == 'BGM':
                    this_section['arg_type'] = 'music'
                    this_section['args'] = args
                # 类型4：函数
                elif target == 'formula':
                    this_section['arg_type'] = 'function'
                    if args in formula_available.keys() or args[0:6] == 'lambda':
                        this_section['args'] = args
                    else:
                        raise ParserError('UnspFormula',args,str(i+1))
                # 类型5：枚举
                elif target == 'inline_method_apply':
                    this_section['arg_type'] = 'enumerate'
                    this_section['args'] = args
                # 类型6：角色表
                elif '.' in target:
                    this_section['arg_type'] = 'chartab'
                    this_target = {}
                    target_split = target.split('.')
                    if len(target_split) == 2:
                        this_target['name'],this_target['column'] = target_split
                        this_target['subtype'] = False
                    elif len(target_split) == 3:
                        this_target['name'],this_target['subtype'],this_target['column'] = target_split
                    # 如果超过4个指定项目，无法解析，抛出ParserError(不被支持的参数)
                    else:
                        raise ParserError('UnsuppSet',target,str(i+1))
                    this_section['target'] = this_target
                    this_section['args'] = args
                # 类型7：尚且无法定性的，例如FreePos
                else:
                    this_section['arg_type'] = 'unknown'
                    this_section['args'] = args
            # 清除行，仅适用于ChatWindow
            elif (text[0:8] == '<clear>:'):
                this_section['type'] = 'clear'
                this_section['object'] = text[8:]
            # 预设动画，损失生命
            elif text[0:11] == '<hitpoint>:':
                this_section['type'] = 'hitpoint'
                name_tx,heart_max,heart_begin,heart_end = RE_hitpoint.findall(text)[0]
                this_section['content'] = name_tx
                try:
                    this_section['hp_max'] = int(heart_max)
                    this_section['hp_begin'] = int(heart_begin)
                    this_section['hp_end'] = int(heart_end)
                except Exception as E:
                    print(E)
                    raise ParserError('ParErrHit',str(i+1))
            # 预设动画，骰子
            elif text[0:7] == '<dice>:':
                this_section['type'] = 'dice'
                dice_args = RE_dice.findall(text[7:])
                if len(dice_args) == 0:
                    raise ParserError('NoDice')
                else:
                    try:
                        this_dice_set = {}
                        for k,dice in enumerate(dice_args):
                            this_dice = {}
                            tx,dicemax,check,face = dice
                            this_dice['content'] = tx
                            this_dice['dicemax'] = int(dicemax)
                            this_dice['face'] = int(face)
                            if check == 'NA':
                                this_dice['check'] = 'NA'
                            else:
                                this_dice['check'] = int(check)
                            this_dice_set[k] = this_dice
                        this_section['dice_set'] = this_dice_set
                    except Exception as E:
                        print(E)
                        raise ParserError('ParErrDice',str(i+1))
            # 等待行，停留在上一个小节的结束状态，不影响S图层
            elif text[0:7] == '<wait>:':
                this_section['type'] = 'wait'
                try:
                    this_section['time'] = int(RE_wait.findall(text)[0])
                except Exception as E:
                    raise ParserError('InvWaitArg',E)
            # 异常行，报出异常
            else:
                raise ParserError('UnrecLine',str(i+1))
            struct[i] = this_section
        # 返回值
        return struct

class MediaDef:
    # 外部输入参数
    type_keyword_position = {'Pos':['pos'],'FreePos':['pos'],'PosGrid':['pos','end','x_step','y_step'],
                            'Text':['fontfile','fontsize','color','line_limit','label_color'],
                            'StrokeText':['fontfile','fontsize','color','line_limit','edge_color','edge_width','projection','label_color'],
                            'Bubble':['filepath','Main_Text','Header_Text','pos','mt_pos','ht_pos','ht_target','align','line_distance','label_color'],
                            'Balloon':['filepath','Main_Text','Header_Text','pos','mt_pos','ht_pos','ht_target','align','line_distance','label_color'],
                            'DynamicBubble':['filepath','Main_Text','Header_Text','pos','mt_pos','mt_end','ht_pos','ht_target','fill_mode','fit_axis','line_distance','label_color'],
                            'ChatWindow':['filepath','sub_key','sub_Bubble','sub_Anime','sub_align','pos','sub_pos','sub_end','am_left','am_right','sub_distance','label_color'],
                            'Background':['filepath','pos','label_color'],
                            'Animation':['filepath','pos','tick','loop','label_color'],
                            'Audio':['filepath','label_color'],
                            'BGM':['filepath','volume','loop','label_color']}
    # 初始化
    def __init__(self,filepath:str=None,json:dict=None) -> None:
        # json 输入
        if json is not None:
            self.struct = json
        # RGL 输入
        elif filepath is not None:
            self.struct = self.MDF_parser(filepath=filepath)
        # 如果没有输入
        else:
            self.struct = {}
    # MDF -> struct
    def value_parser(self,value:str):
        # 1. 是数值
        if re.match('^-?[\d\.]+(e-?\d+)?$',value):
            if '.' in value:
                return float(value)
            else:
                return int(value)
        # 2. 是字符串
        if re.match('^(\".+\"|\'.+\')$',value):
            return value[1:-1]
        # 3. 是列表或者元组：不能嵌套！
        if re.match('^\[.+\]|\(.+\)$',value):
            pass
        # 4. 是另一个实例化: Class()
        if re.match('^[a-zA-Z_]\w*\(.*\)$',value):
            print(value)
        # 5. 是一个subscript: Obj[1]
        # 6. 是一个对象 Obj
    def args_parser(self,obj_type:str,obj_args:str) -> dict:
        args_list = RE_mediadef_args.findall(obj_args)
        this_args_set = {}
        allow_position_args = True
        for i,arg in enumerate(args_list):
            keyword,value:str = arg
            # 关键字
            if keyword == '':
                # option arg
                if allow_position_args == True:
                    keyword = self.type_keyword_position[obj_type][i]
                else:
                    raise SyntaxsError('BadPosArg')
            else:
                allow_position_args = False
            # 值
            # 该怎么做呢？
        return this_args_set
    def MDF_parser(self,filepath:str) -> dict:
        try:
            object_define_text = open(filepath,'r',encoding='utf-8').read()#.split('\n') # 修改后的逻辑
        except UnicodeDecodeError as E:
            raise DecodeError('DecodeErr',E)
        # 清除 UTF-8 BOM
        if object_define_text[0] == '\ufeff':
            print(WarningPrint('UFT8BOM'))
            object_define_text = object_define_text[1:] # 去掉首位
        # 分割小节
        object_define_text = object_define_text.split('\n')
        # 结构体
        struct = {}
        # 逐句读取小节
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
                this_section = {}
                try:
                    # instantiation = obj_type + obj_args
                    if obj_name in self.occupied_variable_name:
                        raise SyntaxsError('OccName')
                    elif (len(re.findall('\w+',obj_name))==0)|(obj_name[0].isdigit()):
                        raise SyntaxsError('InvaName')
                    else:
                        this_section['type'] = obj_type
                        #对象实例化
                        # self.MediaObjects[obj_name] = eval(instantiation)
                        exec('global {}; '.format(obj_name) + text)
                        self.media_list.append(obj_name) #记录新增对象名称
                except Exception as E:
                    print(E)
                    print(SyntaxsError('MediaDef',text,str(i+1)))
                    self.system_terminated('Error')