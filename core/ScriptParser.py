#!/usr/bin/env python
# coding: utf-8
# 标记语言 <-> json{dic}

import numpy as np
import pandas as pd

import json

from .Exceptions import DecodeError,ParserError,WarningPrint,SyntaxsError
from .Regexs import *
from .Formulas import *

# 输入文件，基类
class Script:
    # 初始化
    def __init__(self,string_input=None,dict_input=None,file_input=None,json_input=None) -> None:
        # 字典 输入：不安全的方法
        if dict_input is not None:
            self.struct:dict = dict_input
        # 字符串输入
        elif string_input is not None:
            self.struct:dict = self.parser(script=string_input)
        # 如果输入了脚本文件
        elif file_input is not None:
            self.struct:dict = self.parser(script=self.load_file(filepath=file_input))
        # 如果输入了json文件：不安全的方法
        elif json_input is not None:
            self.struct:dict = self.load_json(filepath=json_input)
        # 如果没有输入
        else:
            self.struct:dict = {}
    # 读取文本文件
    def load_file(self,filepath:str)->str:
        try:
            stdin_text = open(filepath,'r',encoding='utf-8').read()
        except UnicodeDecodeError as E:
            raise DecodeError('DecodeErr',E)
        # 清除 UTF-8 BOM
        if stdin_text[0] == '\ufeff':
            print(WarningPrint('UFT8BOM'))
            stdin_text = stdin_text[1:]
        return stdin_text
    # 将读取的文本文件解析为json
    def load_json(self,filepath:str)->dict:
        return json.loads(self.load_file(filepath=filepath))
    # 保存为文本文件
    def dump_file(self,filepath:str)->None:
        list_of_scripts = self.export()
        with open(filepath,'w',encoding='utf-8') as of:
            of.write(list_of_scripts)
    # 保存为json
    def dump_json(self,filepath:str)->None:
        with open(filepath,'w',encoding='utf-8') as of:
            of.write(json.dumps(self.struct,indent=4))
    # 待重载的：
    def parser(self,script:str)->dict:
        return {}
    def export(self):
        return ''

# log文件
class RplGenLog(Script):
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
                this_charactor['alpha'] = None
            else:
                this_charactor['alpha'] = int(alpha[1:-1]) # 去掉首尾括号
            this_charactor_set[str(k)] = this_charactor
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
                    this_asterisk['sound'] = None
                else:
                    this_asterisk['sound'] = list_of_AS[0][1][:-1] # 去除最后存在的分号
                # 时间
                if list_of_AS[0][-1] == '':
                    this_asterisk['time'] = None
                else:
                    try:
                        this_asterisk['time'] = float(list_of_AS[0][-1])
                    except Exception:
                        this_asterisk['time'] = None
                        if this_asterisk['sound'] is None:
                            # 指定发言内容
                            this_asterisk['specified_speech'] = list_of_AS[0][-1]
                if this_asterisk['sound'] is None or this_asterisk['time'] is None:
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
                this_sound_set[str(k)] = this_soundeff
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
    def parser(self,script:str) -> dict:
        # 分割小节
        stdin_text = script.split('\n')
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
                this_section['bg_method'] = self.method_parser(obje)
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
                    this_section['object'] = None
                elif (objc[0] == '(') and (objc[-1] == ')'):
                    # 如果是一个集合
                    this_GA_set = {} # GA
                    animation_list = objc[1:-1].split(',')
                    for k,am in enumerate(animation_list):
                        this_GA_set[str(k)] = am
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
                    this_section['object'] = None
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
                    this_section['value_type'] = 'digit' # natural number
                    try:
                        this_section['value'] = int(args)
                    except:
                        print(WarningPrint('Set2Invalid',target,args))
                        this_section['value'] = args
                # 类型2：method
                elif target in ['am_method_default','bb_method_default','bg_method_default','tx_method_default']:
                    this_section['value_type'] = 'method'
                    try:
                        this_section['value'] = self.method_parser(args)
                    except IndexError:
                        raise ParserError('SetInvMet',target,args)
                # 类型3：BGM
                elif target == 'BGM':
                    this_section['value_type'] = 'music'
                    this_section['value'] = args
                # 类型4：函数
                elif target == 'formula':
                    this_section['value_type'] = 'function'
                    if args in formula_available.keys() or args[0:6] == 'lambda':
                        this_section['value'] = args
                    else:
                        raise ParserError('UnspFormula',args,str(i+1))
                # 类型5：枚举
                elif target == 'inline_method_apply':
                    this_section['value_type'] = 'enumerate'
                    this_section['value'] = args
                # 类型6：角色表
                elif '.' in target:
                    this_section['value_type'] = 'chartab'
                    this_target = {}
                    target_split = target.split('.')
                    if len(target_split) == 2:
                        this_target['name'],this_target['column'] = target_split
                        this_target['subtype'] = None
                    elif len(target_split) == 3:
                        this_target['name'],this_target['subtype'],this_target['column'] = target_split
                    # 如果超过4个指定项目，无法解析，抛出ParserError(不被支持的参数)
                    else:
                        raise ParserError('UnsuppSet',target,str(i+1))
                    this_section['target'] = this_target
                    this_section['value'] = args
                # 类型7：尚且无法定性的，例如FreePos
                else:
                    this_section['value_type'] = 'unknown'
                    this_section['value'] = args
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
                                this_dice['check'] = None
                            else:
                                this_dice['check'] = int(check)
                            this_dice_set[str(k)] = this_dice
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
            struct[str(i)] = this_section
        # 返回值
        return struct
    # struct -> RGL
    def method_export(self,method_obj:dict)->str:
        if method_obj['method'] == 'default':
            return ''
        else:
            if method_obj['method_dur'] == 'default':
                return '<'+ method_obj['method'] +'>'
            else:
                return '<'+ method_obj['method'] + '=' + str(method_obj['method_dur']) +'>'
    def sound_export(self,sound_obj_set:dict)->str:
        sound_script_list = []
        for key in sound_obj_set.keys():
            sound_obj = sound_obj_set[key]
            if key == '*': # {sound;*50}
                sound_script_list.append('{' + sound_obj['sound'] + ';*' + str(sound_obj['time']) + '}')
            elif key == '{*}':
                if 'specified_speech' not in sound_obj.key(): # {*abc}
                    sound_script_list.append('{*' + str(sound_obj['specified_speech']) + '}')
                elif sound_obj['sound'] is not None: # {sound;*}
                    sound_script_list.append('{' + str(sound_obj['sound']) + ';*}')
                else:
                    sound_script_list.append('{*}') # {*}
            else:
                if sound_obj['delay'] != 0: # {sound;5}
                    sound_script_list.append('{' + str(sound_obj['sound']) +';'+ str(sound_obj['delay']) +'}')
                else: # {sound}
                    sound_script_list.append('{' + str(sound_obj['sound']) + '}')
        return ''.join(sound_script_list)
    def export(self) -> str:
        list_of_scripts = []
        for key in self.struct.keys():
            this_section:dict = self.struct[key]
            type_this:str = this_section['type']
            # 空行
            if type_this == 'blank':
                this_script = ''
            # 备注
            elif type_this == 'comment':
                this_script = '#' + this_section['content']
            # 对话行
            elif this_section['type'] == 'dialog':
                # 角色
                charactor_set:dict = this_section['charactor_set']
                charactor_script_list:list = []
                for key in charactor_set.keys():
                    charactor = charactor_set[key]
                    charactor_script = charactor['name']
                    if charactor['alpha'] is not None:
                        charactor_script = charactor_script + '(%d)'%charactor['alpha']
                    if charactor['subtype'] != 'default':
                        charactor_script = charactor_script + '.' + charactor['subtype']
                    charactor_script_list.append(charactor_script)
                CR = '[' + ','.join(charactor_script_list) + ']'
                # 媒体效果
                MM = self.method_export(this_section['ab_method'])
                TM = self.method_export(this_section['tx_method'])
                SE = self.sound_export(this_section['sound_set'])
                this_script = CR + MM + ':' + this_section['content'] + TM + SE
            # 背景
            elif this_section['type'] == 'background':
                MM = self.method_export(this_section['bg_method'])
                this_script = '<background>' + MM + ':' + this_section['object']
            # 立绘
            elif this_section['type'] == 'animation':
                MM = self.method_export(this_section['am_method'])
                if this_section['object'] is None:
                    OB = 'NA'
                elif type(this_section['object']) is str:
                    OB =  this_section['object']
                else:
                    OB = '(' + ','.join(this_section['object'].values()) + ')'
                this_script = '<animation>' + MM + ':' + OB
            # 气泡
            elif this_section['type'] == 'bubble':
                MM = self.method_export(this_section['bb_method'])
                if this_section['object'] is None:
                    OB = 'NA'
                else:
                    bubble_object = this_section['object']
                    TM = self.method_export(bubble_object['tx_method'])
                    OB = '{}("{}","{}"{})'.format(
                        bubble_object['bubble'],
                        bubble_object['header_text'],
                        bubble_object['main_text'],TM)
                this_script = '<bubble>' + MM + ':' + OB
            # 设置
            elif this_section['type'] == 'set':
                if this_section['value_type'] == 'digit':
                    value = str(this_section['value'])
                    target = this_section['target']
                elif this_section['value_type'] in ['music','function','enumerate','unknown']:
                    value = this_section['value']
                    target = this_section['target']
                elif this_section['value_type'] == 'method':
                    value = self.method_export(this_section['value'])
                    target = this_section['target']
                elif this_section['value_type'] == 'chartab':
                    value = this_section['value']
                    if this_section['target']['subtype'] is None:
                        target = this_section['target']['name'] +'.'+ this_section['target']['column']
                    else:
                        target = this_section['target']['name'] +'.'+ this_section['target']['subtype'] +'.'+ this_section['target']['column']
                else:
                    continue
                this_script = '<set:{}>:{}'.format(target,value)
            # 清除
            elif this_section['type'] == 'clear':
                this_script = '<clear>:' + this_section['object']
            # 生命值
            elif this_section['type'] == 'hitpoint':
                this_script = '<hitpoint>:({},{},{},{})'.format(
                    this_section['content'],
                    this_section['hp_max'],
                    this_section['hp_begin'],
                    this_section['hp_end']
                )
            # 骰子
            elif this_section['type'] == 'dice':
                list_of_dice_express = []
                for key in this_section['dice_set'].keys():
                    this_dice = this_section['dice_set'][key]
                    if this_dice['check'] is None:
                        CK = 'NA'
                    else:
                        CK = int(this_dice['check'])
                    list_of_dice_express.append(
                        '({},{},{},{})'.format(
                            this_dice['content'],
                            this_dice['dicemax'],
                            CK,
                            this_dice['face']))
                    this_script = '<dice>:' + ','.join(list_of_dice_express)
            elif this_section['type'] == 'wait':
                this_script = '<wait>:{}'.format(this_section['time'])
            else:
                this_script = ''
            # 添加到列表
            list_of_scripts.append(this_script)
        # 返回
        return '\n'.join(list_of_scripts)

# 媒体定义文件
class MediaDef(Script):
    # 参数
    type_keyword_position = {'Pos':['pos'],'FreePos':['pos'],'PosGrid':['pos','end','x_step','y_step'],
                            'Text':['fontfile','fontsize','color','line_limit','label_color'],
                            'StrokeText':['fontfile','fontsize','color','line_limit','edge_color','edge_width','projection','label_color'],
                            'Bubble':['filepath','scale','Main_Text','Header_Text','pos','mt_pos','ht_pos','ht_target','align','line_distance','label_color'],
                            'Balloon':['filepath','scale','Main_Text','Header_Text','pos','mt_pos','ht_pos','ht_target','align','line_distance','label_color'],
                            'DynamicBubble':['filepath','scale','Main_Text','Header_Text','pos','mt_pos','mt_end','ht_pos','ht_target','fill_mode','fit_axis','line_distance','label_color'],
                            'ChatWindow':['filepath','scale','sub_key','sub_Bubble','sub_Anime','sub_align','pos','sub_pos','sub_end','am_left','am_right','sub_distance','label_color'],
                            'Background':['filepath','scale','pos','label_color'],
                            'Animation':['filepath','scale','pos','tick','loop','label_color'],
                            'Audio':['filepath','label_color'],
                            'BGM':['filepath','volume','loop','label_color']}
    # MDF -> struct
    def list_parser(self,list_str:str)->list:
        # 列表，元组，不包含外括号
        list_str = list_str.replace(' ','')
        values = re.findall("(\w+\(\)|\[[-\w,.\ ]+\]|\([-\d,.\ ]+\)|\w+\[[\d\,]+\]|[^,()]+)",list_str)
        this_list = []
        for value in values:
            this_list.append(self.value_parser(value))
        return this_list
    def subscript_parser(self,obj_name:str,sub_indexs:str)->dict:
        # Object[1,2]
        this_subscript = {'type':'subscript','object':'$'+obj_name}
        this_subscript['index'] = self.list_parser(sub_indexs)
        return this_subscript
    def value_parser(self,value:str):
    # 数值、字符串、列表、实例化、subs、对象
        # 1. 是数值
        if re.match('^-?[\d\.]+(e-?\d+)?$',value):
            if '.' in value:
                return float(value)
            else:
                return int(value)
        # 2. 是字符串
        elif re.match('^(\".+\"|\'.+\')$',value):
            return value[1:-1]
        # 3. 是列表或者元组：不能嵌套！
        elif re.match('^\[.+\]|\(.+\)$',value):
            return self.list_parser(value[1:-1])
        # 4. 是另一个实例化: Class()
        elif re.match('^[a-zA-Z_]\w*\(.*\)$',value):
            obj_type,obj_value = re.findall('^([a-zA-Z_]\w*)\((.*)\)$',string=value)[0]
            return self.instance_parser(obj_type,obj_value)
        # 5. 是一个subscript: Obj[1]
        elif re.match('^\w+\[[\d\, ]+\]$',value):
            obj_name,sub_indexs = re.findall('(\w+)\[([\d\, ]+)\]$',string=value)[0]
            return self.subscript_parser(obj_name,sub_indexs)
        # 6. 是特殊的常量
        elif value in ('False','True','None'):
            return {'False':False,'True':True,'None':None}[value]
        # 7. 是一个对象名 Obj
        elif re.match('^\w*$',value) and value[0].isdigit()==False:
            return '$' + value
        else:
            raise SyntaxsError('InvExp',value)
    def instance_parser(self,obj_type:str,obj_args:str)->dict:
        # 实例化
        this_instance = {'type':obj_type}
        # Pos 类型
        if obj_type in ['Pos','FreePos']:
            this_instance['pos'] = self.list_parser(obj_args)
            return this_instance
        # 其他类型
        else:
            args_list = RE_mediadef_args.findall(obj_args)
            allow_position_args = True
            for i,arg in enumerate(args_list):
                keyword,value = arg
                # 关键字
                if keyword == '':
                    if allow_position_args == True:
                        try:
                            keyword = self.type_keyword_position[obj_type][i]
                        except IndexError:
                            # 给媒体指定了过多的参数
                            SyntaxsError('ToMuchArgs',obj_type)
                    else:
                        # 非法使用的顺序参数
                        print(args_list)
                        raise SyntaxsError('BadPosArg')
                else:
                    allow_position_args = False
                # 值
                this_instance[keyword] = self.value_parser(value)
            return this_instance
    def parser(self,script:str) -> dict:
        # 分割小节
        object_define_text = script.split('\n')
        # 结构体
        struct = {}
        # 逐句读取小节
        for i,text in enumerate(object_define_text):
            # 空行
            if text == '':
                struct[str(i)] = {'type':'blank'}
                continue
            # 备注
            elif text[0] == '#':
                struct[str(i)] = {'type':'comment','content':text[1:]}
                continue
            # 有内容的
            try:
                # 尝试解析媒体定义文件
                obj_name,obj_type,obj_args = RE_mediadef.findall(text)[0]
            except:
                # 格式不合格的行直接报错
                try:
                    obj_name,value_obj = RE_subscript_def.findall(text)[0]
                    struct[obj_name] = self.value_parser(value_obj)
                    continue
                except Exception:
                    raise SyntaxsError('MediaDef',text,str(i+1))
            else:
                # 格式合格的行开始解析
                try:
                    # 如果是非法的标识符
                    if (len(re.findall('\w+',obj_name))==0)|(obj_name[0].isdigit()):
                        raise SyntaxsError('InvaName')
                    else:
                        this_section = self.instance_parser(obj_type,obj_args[1:-1])
                except Exception as E:
                    print(E)
                    raise SyntaxsError('MediaDef',text,str(i+1))
                struct[obj_name] = this_section
        return struct
    # struct -> MDF
    def instance_export(self,media_object:dict)->str:
        type_this = media_object['type']
        if type_this == 'subscript':
            return media_object['object'] + self.list_export(media_object['index'],is_tuple=False)
        elif type_this in ['Pos','FreePos']:
            return type_this + self.list_export(media_object['pos'],is_tuple=True)
        else:
            argscript_list = []
            for key in media_object.keys():
                if key == 'type':
                    continue
                else:
                    argscript_list.append(key + '=' + self.value_export(media_object[key]))
            return type_this + '(' + ','.join(argscript_list) + ')'
    def list_export(self,list_object:list,is_tuple=True)->str:
        list_unit = []
        for unit in list_object:
            if type(unit) not in [int,float]:
                is_tuple = False
            list_unit.append(self.value_export(unit))
        # 注意：纯数值组成的列表使用tuple
        if is_tuple:
            return '(' + ','.join(list_unit) + ')'
        # 反之必须使用list，源于解析的要求
        else:
            return '[' + ','.join(list_unit) + ']'
    def value_export(self,unit:object)->str:
        # 常量
        if type(unit) in [int,float]:
            return str(unit)
        elif type(unit) is bool:
            return {False:'False',True:'True'}[unit]
        elif unit is None:
            return 'None'
        # 字符串
        elif type(unit) is str:
            # 如果是一个引用对象
            if unit[0] == '$':
                return unit[1:]
            else:
                if "'" in unit:
                    unit.replace("'","\\'")
                return "'" + unit + "'"
        # 列表
        elif type(unit) is list:
            return self.list_export(unit)
        # 对象
        elif type(unit) is dict:
            return self.instance_export(unit)
        # 其他
        else:
            return ''       
    def export(self)->str:
        list_of_scripts = []
        for key in self.struct.keys():
            obj_this:dict = self.struct[key]
            type_this:str = obj_this['type']
            # 空行
            if type_this == 'blank':
                this_script = ''
            # 备注
            elif type_this == 'comment':
                this_script = '#' + obj_this['content']
            # 实例化
            else:
                this_script = key + ' = ' + self.instance_export(obj_this)
            # 添加到列表
            list_of_scripts.append(this_script)
        # 返回
        return '\n'.join(list_of_scripts)

# 角色配置文件
