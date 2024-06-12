#!/usr/bin/env python
# coding: utf-8

# 代码补全工具

import re
import tkinter as tk
import ttkbootstrap as ttk
from chlorophyll import CodeView
import pandas as pd
from .ProjConfig import preference
from .Medias import Audio
from .ScriptParser import CharTable, MediaDef
from .GUI_CustomDialog import abmethod_query
from .GUI_DialogWindow import browse_file,color_chooser
from .GUI_Link import Link
from .GUI_Language import Localize
from .Utils import rgb_2_hex,available_label_color

class CodeSnippet(ttk.Menu):
    def __init__(self,master):
        super().__init__(master=master, tearoff=0, font=(Link['terminal_font_family'],10))

class RGLSnippets(CodeSnippet, Localize):
    Snippets = {
        'zh':{
            "command":{
                "dialog"        :['对话行','[]:',1],
                "wait"          :['停顿','<wait>:',7],
                "sep1"          :'sep',
                "background"    :['切换背景','<background>:',13],
                "animation"     :['常驻立绘','<animation>:()',13],
                "bubble"        :['常驻气泡','<bubble>:',9],
                "BGM"           :['背景音乐','<BGM>:',6],
                "sep2"          :'sep',
                "set"           :['设置','<set:>:',5],
                "table"         :['修改角色表','<table:>:',7],
                "move"          :['移动媒体','<move:>:',6],
                "clear"         :['清空聊天窗','<clear>:',8],
                "sep3"          :'sep',
                "hitpoint"      :['血量动画','<hitpoint>:(描述,10,10,5)',14],
                "dice"          :['骰子动画','<dice>:(描述,100,50,75),(描述,100,50,25)',10],
                "sep4"          :'sep',
                "comment"       :['注释','# ',2]
            },
            "set":{
                "am_method_default"     :["默认切换效果-立绘","am_method_default",19],
                "bb_method_default"     :["默认切换效果-气泡","bb_method_default",19],
                "bg_method_default"     :["默认切换效果-背景","bg_method_default",19],
                "tx_method_default"     :["默认文字效果","tx_method_default",19],
                "sep1"                  :'sep',
                "speech_speed"          :["无语音句子的播放速度","speech_speed",14],
                "asterisk_pause"        :["句子的间隔时间","asterisk_pause",16],
                "inline_method_apply"   :["对话行中效果的作用对象","inline_method_apply",21],
                "method_protocol"       :["停用默认切换效果的条件","method_protocol",17],
                "sep2"                  :'sep',
                "secondary_alpha"       :["非发言角色的立绘透明度","secondary_alpha",17],
                "secondary_brightness"  :["非发言角色的立绘亮度","secondary_brightness",22],
                "sep3"                  :'sep',
                "am_dur_default"        :["默认切换时间-立绘","am_dur_default",16],
                "bb_dur_default"        :["默认切换时间-气泡","bb_dur_default",16],
                "bg_dur_default"        :["默认切换时间-背景","bg_dur_default",16],
                "tx_dur_default"        :["默认文字效果时间","tx_dur_default",16],
                "sep4"                  :'sep',
                "formula"               :["动画曲线","formula",9],
            },
            "am_dur":{
                "0"    : ["0","0",1],
                "10"    : ["10","10",2],
                "20"    : ["20","20",2],
                "30"    : ["30","30",2],
                "60"    : ["60","60",2],
                "100"   : ["100","100",3],
            },
            "tx_dur":{
                "1"     : ["1","1",1],
                "2"     : ["2","2",1],
                "3"     : ["3","3",1],
                "10"    : ["10","10",2],
                "30"    : ["30","30",2],
            },
            "speed":{
                "220"   : ["220","220",3],
                "300"   : ["300","300",3],
                "600"   : ["600","600",3],
                "900"   : ["900","900",3],
                "1800"  : ["1800","1800",4],
            },
            "formula":{
                "linear"    : ["线性","linear",6],
                "quadratic" : ["二次","quadratic",9],
                "quadraticR": ["反二次","quadraticR",10],
                "sigmoid"   : ["正S形","sigmoid",7],
                "right"     : ["右S形","right",5],
                "left"      : ["左S形","left",4],
                "sincurve"  : ["正弦","sincurve",8],
            },
            "inline":{
                "both"      : ["全部","both",4],
                "amimation" : ["立绘","animation",9],
                "bubble"    : ["气泡","bubble",6],
                "none"      : ["禁用","none",4],
            },
            "protocol":{
                "identical" : ["完全一致","identical",9],
                "charactor" : ["同一角色","charactor",9],
                "subtype"   : ["同一差分名","subtype",7],
                "none"      : ["禁用","none",4],
            },
            "tx_met":{
                "all"   : ["全部","<all=>",5],
                "w2w"   : ["逐字","<w2w=>",5],
                "l2l"   : ["逐行","<l2l=>",5],
                "run"   : ["滚动","<run=>",5],
            },
            "bg_met":{
                "replace"   : ["直接替换","<replace=>",9],
                "delay"     : ["延迟替换","<delay=>",7],
                "cross"     : ["交叉溶解","<cross=>",7],
                "black"     : ["黑场","<black=>",7],
                "white"     : ["白场","<white=>",7],
                "push"      : ["推入","<push=>",6],
                "cover"     : ["覆盖","<cover=>",7],
            },
            "ab_met":{
                "replace"   : ["直接替换","<replace=>",9],
                "cross"     : ["交叉溶解","<cross=>",7],
                "black"     : ["淡入淡出","<black=>",7],
                "pass"      : ["左进右出","<black_pass_left_minor=>",23],
                "leap"      : ["上进上出","<black_leap_down_minor=>",23],
                "shake"     : ["震动*"   , "<shake_in_minor=45>",19],
            },
            "rich":{
                "bold"          : ["加粗","b",2],
                "italic"        : ["斜体","i",2],
                "underline"     : ["下划线","u",2],
                "strickout"     : ["删除线","x",2],
                "sep1"          : 'sep',
                "foreground"    : ["字体颜色","fg:",3],
                "background"    : ["底纹颜色","bg:",3],
                "fontsize"      : ["字号","fs:",3],
                "sep2"          : 'sep',
                "breakline"     : ["换行","#",2]
            },
            "unrich":{
                "bold"          : ["加粗","/b",3],
                "italic"        : ["斜体","/i",3],
                "underline"     : ["下划线","/u",3],
                "strickout"     : ["删除线","/x",3],
                "sep1"          : 'sep',
                "foreground"    : ["字体颜色","/fg",4],
                "background"    : ["底纹颜色","/bg",4],
                "fontsize"      : ["字号","/fs",4],
            },
            "dot":{
                "dot"           : [".(差分)",'.',1],
                "comma"         : [",(下一个)",',',1]
            }
        },
        'en':{
            "command":{
                "dialog"        :['[dialog]','[]:',1],
                "wait"          :['<wait>','<wait>:',7],
                "sep1"          :'sep',
                "background"    :['<background>','<background>:',13],
                "animation"     :['<animation>','<animation>:()',13],
                "bubble"        :['<bubble>','<bubble>:',9],
                "BGM"           :['<BGM>','<BGM>:',6],
                "sep2"          :'sep',
                "set"           :['<set:__>','<set:>:',5],
                "table"         :['<table:__>','<table:>:',7],
                "move"          :['<move:__>','<move:>:',6],
                "clear"         :['<clear>','<clear>:',8],
                "sep3"          :'sep',
                "hitpoint"      :['<hitpoint>','<hitpoint>:(description,10,10,5)',23],
                "dice"          :['<dice>','<dice>:(description,100,50,75),(description,100,50,25)',19],
                "sep4"          :'sep',
                "comment"       :['# comment','# ',2]
            },
            "set":{
                "am_method_default"     :["am_method_default","am_method_default",19],
                "bb_method_default"     :["bb_method_default","bb_method_default",19],
                "bg_method_default"     :["bg_method_default","bg_method_default",19],
                "tx_method_default"     :["tx_method_default","tx_method_default",19],
                "sep1"                  :'sep',
                "speech_speed"          :["speech_speed","speech_speed",14],
                "asterisk_pause"        :["asterisk_pause","asterisk_pause",16],
                "inline_method_apply"   :["inline_method_apply","inline_method_apply",21],
                "method_protocol"       :["method_protocol","method_protocol",17],
                "sep2"                  :'sep',
                "secondary_alpha"       :["secondary_alpha","secondary_alpha",17],
                "secondary_brightness"  :["secondary_brightness","secondary_brightness",22],
                "sep3"                  :'sep',
                "am_dur_default"        :["am_dur_default","am_dur_default",16],
                "bb_dur_default"        :["bb_dur_default","bb_dur_default",16],
                "bg_dur_default"        :["bg_dur_default","bg_dur_default",16],
                "tx_dur_default"        :["tx_dur_default","tx_dur_default",16],
                "sep4"                  :'sep',
                "formula"               :["formula","formula",9],
            },
            "am_dur":{
                "0"    : ["0","0",1],
                "10"    : ["10","10",2],
                "20"    : ["20","20",2],
                "30"    : ["30","30",2],
                "60"    : ["60","60",2],
                "100"   : ["100","100",3],
            },
            "tx_dur":{
                "1"     : ["1","1",1],
                "2"     : ["2","2",1],
                "3"     : ["3","3",1],
                "10"    : ["10","10",2],
                "30"    : ["30","30",2],
            },
            "speed":{
                "220"   : ["220","220",3],
                "300"   : ["300","300",3],
                "600"   : ["600","600",3],
                "900"   : ["900","900",3],
                "1800"  : ["1800","1800",4],
            },
            "formula":{
                "linear"    : ["linear","linear",6],
                "quadratic" : ["quadratic","quadratic",9],
                "quadraticR": ["quadraticR","quadraticR",10],
                "sigmoid"   : ["sigmoid","sigmoid",7],
                "right"     : ["right","right",5],
                "left"      : ["left","left",4],
                "sincurve"  : ["sincurve","sincurve",8],
            },
            "inline":{
                "both"      : ["both","both",4],
                "amimation" : ["animation","animation",9],
                "bubble"    : ["bubble","bubble",6],
                "none"      : ["none","none",4],
            },
            "protocol":{
                "identical" : ["identical","identical",9],
                "charactor" : ["charactor","charactor",9],
                "subtype"   : ["subtype","subtype",7],
                "none"      : ["none","none",4],
            },
            "tx_met":{
                "all"   : ["<all=_>","<all=>",5],
                "w2w"   : ["<w2w=_>","<w2w=>",5],
                "l2l"   : ["<l2l=_>","<l2l=>",5],
                "run"   : ["<run=_>","<run=>",5],
            },
            "bg_met":{
                "replace"   : ["<replace=_>","<replace=>",9],
                "delay"     : ["<delay=_>","<delay=>",7],
                "cross"     : ["<cross=_>","<cross=>",7],
                "black"     : ["<black=_>","<black=>",7],
                "white"     : ["<white=_>","<white=>",7],
                "push"      : ["<push=_>","<push=>",6],
                "cover"     : ["<cover=_>","<cover=>",7],
            },
            "ab_met":{
                "replace"   : ["<replace=_>","<replace=>",9],
                "cross"     : ["<cross=_>","<cross=>",7],
                "black"     : ["<black=_>","<black=>",7],
                "pass"      : ["<pass=_>","<black_pass_left_minor=>",23],
                "leap"      : ["<leap=_>","<black_leap_down_minor=>",23],
                "shake"     : ["<shake=_>","<shake_in_minor=45>",19],
            },
            "rich":{
                "bold"          : ["bold","b",2],
                "italic"        : ["italic","i",2],
                "underline"     : ["underline","u",2],
                "strickout"     : ["strickout","x",2],
                "sep1"          : 'sep',
                "foreground"    : ["foreground","fg:",3],
                "background"    : ["background","bg:",3],
                "fontsize"      : ["fontsize","fs:",3],
                "sep2"          : 'sep',
                "breakline"     : ["breakline","n",2]
            },
            "unrich":{
                "bold"          : ["bold","/b",2],
                "italic"        : ["italic","/i",2],
                "underline"     : ["underline","/u",2],
                "strickout"     : ["strickout","/x",2],
                "sep1"          : 'sep',
                "foreground"    : ["foreground","/fg",3],
                "background"    : ["background","/bg",3],
                "fontsize"      : ["fontsize","/fs",3],
            },
            "dot":{
                "dot"           : [".(subtype)",'.',1],
                "comma"         : [",(next)",',',1]
            }
        }
    }
    language = {
        'en' : {
            "（自定义）": '(Custom)',
            '（全部差分）': '(All Subtype)',
            '（黑）': '(Black)',
            '（白）': '(White)',
            '（无）': '(None)',
            '（停止）': '(Stop)',
            '（导入文件）': '(Load Files)',
            '（语音合成）': '(TTS Mark)',
            '立绘':  'Animation',
            '气泡':  'Bubble',
            '背景':  'Background',
            '（坐标）': '(Coordinate)',
            '文字效果': 'Text Method',
            '音效': 'Sound Effect',
            '启用效果': 'Enable Label',
            '取消效果': 'Disable Label',
            '黑': 'Black',
            '白': 'White',
            "（选择颜色）": "(Choose Color)"
        }
    }
    color_name = {
        'zh':{
            'Violet':'紫罗兰紫',
            'Iris':'鸢尾花色蓝',
            'Caribbean':'加勒比海蓝',
            'Lavender':'薰衣草粉',
            'Cerulean':'天蓝色',
            'Forest':'森林绿',
            'Rose':'玫瑰红',
            'Mango':'芒果橙',
            'Purple':'紫色',
            'Blue':'蓝色',
            'Teal':'深青色',
            'Magenta':'洋红色',
            'Tan':'棕黄色',
            'Green':'绿色',
            'Brown':'棕色',
            'Yellow':'黄色'
        },
        'en':{
            'Violet':'Violet',
            'Iris':'Iris',
            'Caribbean':'Caribbean',
            'Lavender':'Lavender',
            'Cerulean':'Cerulean',
            'Forest':'Forest',
            'Rose':'Rose',
            'Mango':'Mango',
            'Purple':'Purple',
            'Blue':'Blue',
            'Teal':'Teal',
            'Magenta':'Magenta',
            'Tan':'Tan',
            'Green':'Green',
            'Brown':'Brown',
            'Yellow':'Yellow'
        }
    }
    localize = preference.lang
    def __init__(self, master, mediadef:MediaDef, chartab:CharTable):
        # 初始化菜单
        super().__init__(master=master)
        self.codeview:CodeView = master
        # 引用媒体
        self.ref_media = mediadef
        self.ref_char = chartab
        # 标签颜色
        self.label_color_name = self.color_name[preference.lang]
        # 光标位置
        try:
            index_,x,y = self.get_insert_curser()
            self.curser_idx = index_
            self.curser_pos = (x,y)
        except TypeError:
            # 如果光标在屏幕外面，get_insert_curser会typeError
            return
        # 初始化
        self.parse_up_down_stream()
        # 显示
        self.post(
            x = self.codeview.winfo_rootx()+self.curser_pos[0],
            y = self.codeview.winfo_rooty()+self.curser_pos[1]+int(preference.editer_fontsize*Link['sz']*1.6)
            )
    # 获取当前光标位置
    def get_insert_curser(self):
        index_ = self.codeview.index('insert')
        x, y, _, _ = self.codeview.bbox(index_)
        return index_,x,y
    # 获取上下文
    def parse_up_down_stream(self):
        row,col = self.curser_idx.split('.')
        # 当前行的全部内容
        text_this = self.codeview.get(f'{row}.0', f'{row}.end')
        text_upstream = text_this[:int(col)]
        text_downstream = text_this[int(col):]
        # 如果是空行开头
        if text_upstream == '' and text_downstream == '':
            self.init_snippets_options('command')
        # 对话行添加
        elif re.fullmatch('^\[([\w\ \.\(\)]+,)*',text_upstream):
            self.init_snippets_options('charactor',dot=False)
        # 差分添加
        elif re.fullmatch('^\[([\w\ \.\(\)]+,)*([\w\ ]+(\(\d+\))?)\.',text_upstream):
            # 提取角色名
            name = re.fullmatch('^\[([\w\ \.\(\)]+,)*([\w\ ]+(\(\d+\))?)\.',text_upstream).group(2)
            self.init_snippets_options('subtype',name=name,dot=False)
        # 逗号句号
        elif re.fullmatch('^\[([\w\ \.\(\)]+,){0,2}([\w\ \.\(\)]+)',text_upstream):
            if text_downstream != '':
                if text_downstream[0] not in [',','.']:
                    comma = True
                    dot = True
                    # 是否有逗号
                    if text_upstream.count(',') >= 2:
                        comma = False
                    # 是否有句号
                    name = re.findall('^\[([\w\ \.\(\)]+,){0,2}([\w\ \.\(\)]+)',text_upstream)[0][-1]
                    if '.' in name:
                        dot = False
                    self.init_snippets_options('dot',dot=dot,comma=comma)
        # 停顿
        elif text_upstream == '<wait>:' and text_downstream == '':
            self.init_snippets_options('am_dur')
        # 背景、立绘、气泡、bgm
        elif re.fullmatch('<background>(<\w+(=\d+)?>)?:',text_upstream) and text_downstream == '':
            self.init_snippets_options('background')
        elif re.fullmatch('<animation>(<\w+(=\d+)?>)?:\(?(\w+,)*',text_upstream):
            self.init_snippets_options('animation')
        elif re.fullmatch('<bubble>(<\w+(=\d+)?>)?:',text_upstream) and text_downstream == '':
            self.init_snippets_options('bubble')
        elif re.fullmatch('<(BGM|bgm)>:',text_upstream) and text_downstream == '':
            self.init_snippets_options('bgm')
        # 音效:如果光标已经在最后
        elif re.fullmatch('^\[[\w\ \.\,\(\)]+\](<\w+(=\d+)?>)?:[^\\"]+',text_upstream) and text_downstream == '':
            # 如果前面已经有切换效果和音效了
            if text_upstream[-1] in ['>','}']:
                # 检查上游是否已经包含了星标了
                if re.findall('{.*?\*.*?}',text_upstream):
                    self.init_snippets_options('audio',asterisk=False)
                else:
                    self.init_snippets_options('audio',asterisk=True)
            # 如果上游
            else:
                self.init_snippets_options('audio|tx_met')
        elif re.fullmatch('^\[[\w\ \.\,\(\)]+\](<\w+(=\d+)>)?:[^\\"]+',text_upstream) and re.fullmatch('\{.+\}',text_downstream):
            self.init_snippets_options('tx_met')
        elif re.fullmatch('^\[[\w\ \.\,\(\)]+\](<\w+(=\d+)>)?:[^\\"]+\{\w+;',text_upstream) and text_downstream[0]=='}':
            self.init_snippets_options('am_dur') # TODO，稍微优化一下这个补全
        # 文字效果
        # 富文本
        elif re.fullmatch('^\[[\w\ \.\,\(\)]+\](<\w+(=\d+)?>)?:[^\\"]*\[',text_upstream) and text_downstream.startswith(']'):
            self.init_snippets_options('rich')
        elif (text_upstream.endswith("[fg:") or text_upstream.endswith("[bg:")) and text_downstream.startswith("]"):
            self.init_snippets_options('color')
        elif text_upstream.endswith("[fs:") and text_downstream.startswith("]"):
            self.init_snippets_options('fontsize')
        # 清除
        elif text_upstream == '<clear>:' and text_downstream == '':
            self.init_snippets_options('chatwindow')
        # 设置
        elif text_upstream == '<set:' and text_downstream[0:2]=='>:':
            self.init_snippets_options('set')
        elif re.fullmatch('^<set:(\w+)>:',text_upstream) and text_downstream=='':
            to_set = re.fullmatch('^<set:(\w+)>:',text_upstream).group(1)
            if to_set in ['am_dur_default','bb_dur_default','bg_dur_default','asterisk_pause','secondary_alpha','secondary_brightness']:
                self.init_snippets_options('am_dur')
            elif to_set in ['am_method_default','bb_method_default']:
                self.init_snippets_options('ab_met')
            elif to_set == 'bg_method_default':
                self.init_snippets_options('bg_met')
            elif to_set == 'tx_dur_default':
                self.init_snippets_options('tx_dur')
            elif to_set == 'tx_method_default':
                self.init_snippets_options('tx_met')
            elif to_set == 'formula':
                self.init_snippets_options('formula')
            elif to_set == 'inline_method_apply':
                self.init_snippets_options('inline')
            elif to_set == 'method_protocol':
                self.init_snippets_options('protocol')
            elif to_set == 'speech_speed':
                self.init_snippets_options('speed')
        # 移动
        elif text_upstream == '<move:' and text_downstream[0:2]=='>:':
            self.init_snippets_options('move')
        elif re.fullmatch("^<move:(\w+)>:([^\+\-]+?)",text_upstream) and text_downstream == '':
            self.init_snippets_options('operator')
        elif re.fullmatch("^<move:(\w+)>:((.+) *(\+|\-) *)?",text_upstream) and text_downstream == '':
            self.init_snippets_options('posexp')
        # 表格
        elif text_upstream == '<table:' and text_downstream[0:2] == '>:':
            self.init_snippets_options('charactor',dot=True)
        elif re.fullmatch("<table:([\w\ ]+)\.",text_upstream) and text_downstream[0:2] == '>:':
            name = re.fullmatch("<table:([\w\ ]+)\.",text_upstream).group(1)
            self.init_snippets_options('subtype',name=name,dot=True)
        elif re.fullmatch("<table:([\w\ ]+)\.(\w+)\.",text_upstream) and text_downstream[0:2] == '>:':
            self.init_snippets_options('columns')
        # 效果
        elif text_upstream == '<background>' and text_downstream[0]==':':
            self.init_snippets_options('bg_met')
        elif (text_upstream in ['<animation>','<bubble>'] or re.fullmatch('^\[[\w\ \.\,\(\)]+\]',text_upstream)) and text_downstream[0]==':' and text_downstream[1:]!='NA':
            self.init_snippets_options('ab_met')
        elif re.fullmatch("(.+)<(\w+)=",text_upstream) and text_downstream[0]=='>':
            method = re.fullmatch("(.+)<(\w+)=",text_upstream).group(2)
            if method in ['w2w','l2l','all']:
                self.init_snippets_options('tx_dur')
            else:
                self.init_snippets_options('am_dur')
    # 从self.Snippets的结构里面创建菜单
    def bulid_menu_from_dict(self,menu,dictionary:dict):
        for keyword in dictionary:
            if dictionary[keyword] == 'sep':
                menu.add_separator()
            else:
                option, snippet, cpos = dictionary[keyword]
                menu.add_command(label=option, command=self.insert_snippets(snippet, cpos))
        return menu
    def init_snippets_options(self,type_='command',**kw_args):
        self.snippets_type = type_
        # 行命令
        if self.snippets_type in ['command','set','am_dur','tx_dur','formula','inline','protocol','speed','bg_met','ab_met','tx_met']:
            self.snippets_content = self.Snippets[self.localize][self.snippets_type]
            self.bulid_menu_from_dict(menu=self,dictionary=self.snippets_content)
            # 立绘切换效果的特殊之处
            if self.snippets_type == 'ab_met':
                self.add_command(label=self.tr('（自定义）'),command=self.custom_ab_method)
        # 角色联想
        elif self.snippets_type=='charactor':
            list_of_snippets = self.ref_char.get_names()
            for name in list_of_snippets:
                if kw_args['dot']:
                    self.add_command(label=name, command=self.insert_snippets(name+'.', len(name)+1))
                else:
                    self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 点联想
        elif self.snippets_type=='dot':
            content = self.Snippets[self.localize][self.snippets_type]
            for keyword in ['comma','dot']:
                if kw_args[keyword]:
                    label, text, length = content[keyword]
                    self.add_command(label=label,command=self.insert_snippets(text, length))
        # 差分联想
        elif self.snippets_type=='subtype':
            char_name = kw_args['name']
            list_of_snippets = self.ref_char.get_subtype(char_name)
            for name in list_of_snippets:
                if kw_args['dot']:
                    self.add_command(label=name, command=self.insert_snippets(name+'.', len(name)+1))
                else:
                    self.add_command(label=name, command=self.insert_snippets(name, len(name)))
            if kw_args['dot']:
                menu = CodeSnippet(master=self)
                list_of_columns = self.ref_char.customize_col
                for name in list_of_columns:
                    menu.add_command(label=name, command=self.insert_snippets(name, len(name)+2))
                self.add_separator()
                self.add_cascade(label=self.tr('（全部差分）'),menu=menu)
        # 背景
        elif self.snippets_type=='background':
            self.add_command(label=self.tr('（黑）'), command=self.insert_snippets("black", 5))
            self.add_command(label=self.tr('（白）'), command=self.insert_snippets("white", 5))
            self.add_media_selection('background')
        # 立绘
        elif self.snippets_type=='animation':
            self.add_command(label=self.tr('（无）'), command=self.force_line("<animation>:NA"))
            self.add_separator()
            self.add_media_selection('anime')
        # 气泡联想，聊天窗以对象而不是关键字的形式返回
        elif self.snippets_type=='bubble':
            self.add_command(label=self.tr('（无）'), command=self.force_line("<bubble>:NA"))
            self.add_separator()
            self.add_media_selection('bubble',_format='{media}("","")',move_back=2,cw=False)
            self.add_media_selection('chatwindow',_format='{media}("","")',move_back=2)
        # 背景音乐
        elif self.snippets_type=='bgm':
            self.add_command(label=self.tr('（停止）'), command=self.insert_snippets("stop", 4))
            self.add_separator() # --------------------
            self.add_media_selection('bgm')
            self.add_separator() # --------------------
            self.add_command(label=self.tr('（导入文件）'), command=self.open_browse_file(mtype='BGM'))
        # 音效
        elif self.snippets_type=='audio':
            if kw_args['asterisk']:
                self.add_command(label=self.tr('（语音合成）'), command=self.insert_snippets("{*}", 3))
                self.add_command(label=self.tr('（导入文件）'), command=self.open_browse_file(mtype='SE',asterisk=True))
            else:
                self.add_command(label=self.tr('（语音合成）'), command=self.insert_snippets("{*}", 3), state='disabled')
                self.add_command(label=self.tr('（导入文件）'), command=self.open_browse_file(mtype='SE'))
            self.add_separator() # --------------------
            self.add_command(label=self.tr('（无）'), command=self.insert_snippets(r"{NA}", 4))
            self.add_separator() # --------------------
            self.add_media_selection(_type='audio',_format="{{{media}}}",move_back=2)
        # 清除对话框
        elif self.snippets_type=='chatwindow':
            self.add_media_selection('chatwindow')
        # 移动
        elif self.snippets_type=='move':
            dict_of_snippets = self.ref_media.get_moveable()
            # freepos
            for name in dict_of_snippets['Freepos']:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)+2))
            self.add_separator()
            # animation，bubble，background
            menus = {}
            for label,keyword in zip([self.tr('立绘'),self.tr('气泡'),self.tr('背景')],['Animation','Bubble','Background']):
                menus[keyword] = CodeSnippet(master=self)
                for name in dict_of_snippets[keyword]:
                    menus[keyword].add_command(label=name, command=self.insert_snippets(name, len(name)+2))
                self.add_cascade(label=f'{label} ({keyword})',menu=menus[keyword])
        elif self.snippets_type=='operator':
            self.add_command(label='+', command=self.insert_snippets('+', 1))
            self.add_command(label='-', command=self.insert_snippets('-', 1))
        elif self.snippets_type=='posexp':
            dict_of_snippets = self.ref_media.get_pos_coord()
            # 媒体点
            if dict_of_snippets['pos']:
                for name in dict_of_snippets['pos']:
                    self.add_command(label=name, command=self.insert_snippets(name, len(name)))
                self.add_separator()
            # 网格
            if dict_of_snippets['posgrid']:
                for name in dict_of_snippets['posgrid']:
                    self.add_command(label=name, command=self.insert_snippets(name+'[0,0]', len(name)+5))
                self.add_separator()
            # 坐标
            coord_menu = CodeSnippet(master=self)
            for name in dict_of_snippets['coord']:
                coord_menu.add_command(label=name, command=self.insert_snippets(name, len(name)))
            self.add_cascade(label=self.tr('（坐标）'),menu=coord_menu)
        # 角色表
        elif self.snippets_type=='columns':
            list_of_snippets = self.ref_char.customize_col
            for name in list_of_snippets:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)+2))
        # 音效和文字效果组合
        elif self.snippets_type=='audio|tx_met':
            self.add_command(label=self.tr('（语音合成）'), command=self.insert_snippets("{*}", 3))
            self.add_command(label=self.tr('（导入文件）'), command=self.open_browse_file(mtype='SE',asterisk=True))
            self.add_separator()
            tx_met_menu = CodeSnippet(master=self)
            audio_menu = CodeSnippet(master=self)
            self.add_cascade(label=self.tr('文字效果'),menu=tx_met_menu)
            self.add_cascade(label=self.tr('音效'),menu=audio_menu)
            # 文字效果
            dict_of_snippets = self.Snippets[self.localize]['tx_met']
            for keyword in dict_of_snippets:
                option, snippet, cpos = dict_of_snippets[keyword]
                tx_met_menu.add_command(label=option, command=self.insert_snippets(snippet, cpos))
            # 音效
            audio_menu.add_command(label=self.tr('（无）'), command=self.insert_snippets(r"{NA}", 4))
            audio_menu.add_separator() #------------------------
            self.add_media_selection(_target=audio_menu, _type='audio',_format="{{{media}}}",move_back=2)
        # 富文本
        elif self.snippets_type=='rich':
            enable_rich_menu = CodeSnippet(master=self)
            disable_rich_menu = CodeSnippet(master=self)
            self.bulid_menu_from_dict(menu=enable_rich_menu,dictionary=self.Snippets[self.localize]['rich'])
            self.bulid_menu_from_dict(menu=disable_rich_menu,dictionary=self.Snippets[self.localize]['unrich'])
            self.add_cascade(label=self.tr('启用效果'),menu=enable_rich_menu)
            self.add_cascade(label=self.tr('取消效果'),menu=disable_rich_menu)
        elif self.snippets_type=='color':
            self.add_command(label=self.tr('黑'), command=self.insert_snippets("#000000", 8))
            self.add_command(label=self.tr('白'), command=self.insert_snippets("#ffffff", 8))
            self.add_separator() #------------------------
            self.add_command(label=self.tr('（选择颜色）'), command=self.choose_color())
        elif self.snippets_type=='fontsize':
            for i in range(10,101,10):
                text = '%d'%i
                self.add_command(label=text, command=self.insert_snippets(text, len(text)+1))
    # 插入媒体选择
    def add_media_selection(self,_type,_target=None,_format='{media}',move_back=0,**kwargs):
        if _target is None:
            _target = self
        if 0: # add a preference
            list_of_snippets = self.ref_media.get_type(_type,**kwargs)
            for name in list_of_snippets:
                snippet_text = _format.format(media=name)
                _target.add_command(label=name, command=self.insert_snippets(snippet_text, len(name)+move_back))
        elif 0: # add a preference
            series_of_snippets:pd.Series = self.ref_media.get_color_labeled_type(_type,**kwargs)
            for name,color in series_of_snippets.items():
                snippet_text = _format.format(media=name)
                _target.add_command(
                    label=name, 
                    command=self.insert_snippets(snippet_text, len(name)+move_back),
                    foreground=available_label_color[color],
                    activebackground=available_label_color[color]
                )
        else: # add a preference
            series_of_snippets:pd.Series = self.ref_media.get_color_labeled_type(_type,**kwargs)
            all_color = series_of_snippets.unique()
            for color in all_color:
                sub_menu = CodeSnippet(master=self)
                all_name = series_of_snippets.index[series_of_snippets==color]
                for name in all_name:
                    snippet_text = _format.format(media=name)
                    sub_menu.add_command(label=name, command=self.insert_snippets(snippet_text, len(name)+move_back))
                _target.add_cascade(label=self.label_color_name[color],menu=sub_menu,foreground=available_label_color[color],activebackground=available_label_color[color])
    # 闭包
    def insert_snippets(self, snippet, cpos):
        # 命令内容
        def command():
            self.codeview.insert(self.curser_idx,chars=snippet)
            self.codeview.mark_set("insert",f'{self.curser_idx}+{cpos}c')
            self.codeview.highlight_all()
        return command
    def force_line(self,snippet):
        def command():
            row = self.curser_idx.split('.')[0]
            self.codeview.delete(f'{row}.0',f'{row}.end')
            self.codeview.insert(f'{row}.0',chars=snippet)
            self.codeview.mark_set("insert",f'{row}.end')
            self.codeview.highlight_all()
        return command
    # 自定义切换效果
    def custom_ab_method(self):
        method = abmethod_query(master=self.codeview,screenzoom=self.codeview.winfo_toplevel().sz)
        if method:
            snippet = f'<{method}=>'
            cpos = len(method) + 2
            self.codeview.insert(self.curser_idx,chars=snippet)
            self.codeview.mark_set("insert",f'{self.curser_idx}+{cpos}c')
            self.codeview.highlight_all()
    # 导入文件：闭包
    def open_browse_file(self,mtype='SE',asterisk=False):
        def insert(snippet,cpos):
            self.codeview.insert(self.curser_idx,chars=snippet)
            self.codeview.mark_set("insert",f'{self.curser_idx}+{cpos}c')
            self.codeview.highlight_all()
        def command():
            browsed_file = tk.StringVar(value='')
            if mtype == 'SE':
                browse_file(master=self.codeview,text_obj=browsed_file,method='file',filetype='soundeff',related=True,convert=True,quote=True)
                getfile = browsed_file.get()
                if getfile != '':
                    if asterisk and preference.asterisk_import:
                        try:
                            audio_length = round(Audio(getfile[1:-1]).media.get_length(),2)
                            text = '{' + f'{getfile};*{audio_length}' + '}'
                            insert(text, len(text))
                        except Exception as E:
                            print(E)
                            insert('{'+getfile+'}',len(getfile)+2)
                    else:
                        insert('{'+getfile+'}',len(getfile)+2)
            elif mtype == 'BGM':
                browse_file(master=self.codeview,text_obj=browsed_file,method='file',filetype='BGM',related=True,convert=True,quote=True)
                getfile = browsed_file.get()
                if getfile != '':                
                    insert(getfile,len(getfile))
        return command
    # 选择颜色：闭包
    def choose_color(self):
        def insert(snippet,cpos):
            self.codeview.insert(self.curser_idx,chars=snippet)
            self.codeview.mark_set("insert",f'{self.curser_idx}+{cpos}c')
            self.codeview.highlight_all()
        def command():
            # 启用取色器
            result = color_chooser(master=self.codeview,text_obj=tk.StringVar())
            if result:
                R,G,B,A = result
                hex_color = rgb_2_hex(R,G,B)
                insert(hex_color,len(hex_color)+1)
        return command
class VirtualEvent:
    def __init__(self,key):
        self.keysym = key

class RGLRightClick(ttk.Menu, Localize):
    language = {
        'en':{
            '全选': 'Select All',
            '复制': 'Copy',
            '黏贴': 'Paste',
            '剪切': 'Cut',
            '撤回': 'Undo',
            '重做': 'Redo',
            '上移': 'Shift Up',
            '下移': 'Shift Down ',
            '拆分': 'Split',
            '保存': 'Save',
            '刷新': 'Reload',
            '查找替换': 'Find & Repl',
        }
    }
    localize = preference.lang
    def __init__(self, master:CodeView,frame, mediadef:MediaDef, chartab:CharTable, event):
        # 初始化菜单
        super().__init__(master=master, tearoff=0)
        self.codeview:CodeView = master
        self.codeframe = frame
        # 固定的结构
        self.TableStruct = {
            'all'       : [self.tr('全选'), 'ctrl+A',self.codeview._select_all],
            'sep1'      : 'sep',
            'copy'      : [self.tr('复制'), 'ctrl+C', self.codeview._copy],
            'paste'     : [self.tr('黏贴'), 'ctrl+V', self.codeview._paste],
            'cut'       : [self.tr('剪切'), 'ctrl+X', lambda: self.codeview.event_generate("<<Cut>>")],
            'sep2'      : 'sep',
            're'        : [self.tr('撤回'), 'ctrl+Z', self.codeview.edit_undo],
            'redo'      : [self.tr('重做'), 'ctrl+Y', self.codeview.redo],
            'sep3'      : 'sep',
            'up'        : [self.tr('上移'), 'alt+↑', lambda: self.codeframe.swap_lines(VirtualEvent('Up'))],
            'down'      : [self.tr('下移'), 'alt+↓', lambda: self.codeframe.swap_lines(VirtualEvent('Down'))],
            'split'     : [self.tr('拆分'), 'alt+enter', lambda: self.codeframe.split_dialog(None)],
            'sep4'      : 'sep',
            'save'      : [self.tr('保存'), 'ctrl+S', lambda: self.codeframe.save_command(None)],
            'refresh'   : [self.tr('刷新'), 'ctrl+R', lambda: self.codeframe.update_codeview(None)],
            'search'    : [self.tr('查找替换'),'ctrl+F',lambda: self.codeframe.show_search(None)]
        }
        # 引用媒体
        self.ref_media = mediadef
        self.ref_char = chartab
        # 鼠标位置
        self.mouse_x = event.x_root
        self.mouse_y = event.y_root
        # 当前选中的文本
        self.select_start = self.codeview.index("sel.first")
        self.select_end = self.codeview.index("sel.last")
        # 初始化
        self.init_menu_options()
        # 显示
        self.post(
            x = self.mouse_x,
            y = self.mouse_y
            )
    def init_menu_options(self):
        self.seperator = {}
        self.element = {}
        for keyword in self.TableStruct:
            if self.TableStruct[keyword] == 'sep':
                self.add_separator()
            else:
                label,accelerator,command = self.TableStruct[keyword]
                self.add_command(label=label,accelerator=accelerator,command=command)