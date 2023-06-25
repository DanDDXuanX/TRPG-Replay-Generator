#!/usr/bin/env python
# coding: utf-8

# 代码补全工具

import re
import tkinter as tk
import ttkbootstrap as ttk
from chlorophyll import CodeView
from .ScriptParser import CharTable, MediaDef

class RGLSnippets(ttk.Menu):
    Snippets = {
        "command":{
            "dialog"        :['对话行','[]:',1],
            "wait"          :['停顿','<wait>:',7],
            "background"    :['切换背景','<background>:',13],
            "animation"     :['显示立绘','<animation>:()',13],
            "bubble"        :['显示气泡','<bubble>:',9],
            "BGM"           :['背景音乐','<BGM>:',6],
            "set"           :['设置','<set:>:',5],
            "table"         :['修改角色表','<table:>:',7],
            "move"          :['移动媒体','<move:>:',6],
            "clear"         :['清空聊天窗','<clear>:',8],
            "hitpoint"      :['血量动画','<hitpoint>:(描述,10,10,10)',14],
            "dice"          :['骰子动画','<dice>:(描述,100,50,75),(描述,100,50,25)',10],
            "comment"       :['注释','# ',2]
        },
        "set":{
            "am_method_default"     :["默认切换效果-立绘","am_method_default",17],
            "bb_method_default"     :["默认切换效果-气泡","bb_method_default",17],
            "bg_method_default"     :["默认切换效果-背景","bg_method_default",17],
            "tx_method_default"     :["默认文字效果","tx_method_default",17],
            "speech_speed"          :["无语音句子的语速","speech_speed",12],
            "asterisk_pause"        :["星标间隔时间","asterisk_pause",14],
            "secondary_alpha"       :["默认次要立绘透明度","secondary_alpha",15],
            "inline_method_apply"   :["对话行类效果的作用对象","inline_method_apply",19],
            "am_dur_default"        :["默认切换时间-立绘","am_dur_default",14],
            "bb_dur_default"        :["默认切换时间-气泡","bb_dur_default",14],
            "bg_dur_default"        :["默认切换时间-背景","bg_dur_default",14],
            "tx_dur_default"        :["默认文字效果时间","tx_dur_default",14],
            "formula"               :["动画曲线","formula",7],
        }
    }
    def __init__(self, master, mediadef:MediaDef, chartab:CharTable):
        # 初始化菜单
        super().__init__(master=master, tearoff=0)
        self.codeview:CodeView = master
        # 引用媒体
        self.ref_media = mediadef
        self.ref_char = chartab
        # 光标位置
        index_,x,y = self.get_insert_curser()
        self.curser_idx = index_
        self.curser_pos = (x,y)
        # 初始化
        self.parse_up_down_stream()
        # 显示
        self.post(
            x = self.codeview.winfo_rootx()+self.curser_pos[0],
            y = self.codeview.winfo_rooty()+self.curser_pos[1]
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
            self.init_snippets_options('charactor')
        # 差分添加
        elif re.fullmatch('^\[([\w\ \.\(\)]+,)*([\w\ ]+(\(\d+\))?)\.',text_upstream):
            # 提取角色名
            name = re.fullmatch('^\[([\w\ \.\(\)]+,)*([\w\ ]+(\(\d+\))?)\.',text_upstream).group(2)
            self.init_snippets_options('subtype',name=name)
        # 背景、立绘、气泡、bgm
        elif re.fullmatch('<background>(<\w+(=\d+)?>)?:',text_upstream) and text_downstream == '':
            self.init_snippets_options('background')
        elif re.fullmatch('<animation>(<\w+(=\d+)?>)?:\(?(\w+,)*',text_upstream):
            self.init_snippets_options('animation')
        elif re.fullmatch('<bubble>(<\w+(=\d+)?>)?:',text_upstream) and text_downstream == '':
            self.init_snippets_options('bubble')
        elif re.fullmatch('<(BGM|bgm)>:',text_upstream) and text_downstream == '':
            self.init_snippets_options('bgm')
        # 设置
        elif text_upstream == '<set:' and text_downstream[0:2]=='>:':
            self.init_snippets_options('set')
    def init_snippets_options(self,type_='command',**kw_args):
        self.snippets_type = type_
        # 行命令
        if self.snippets_type=='command':
            self.snippets_content = self.Snippets[self.snippets_type]
            for keyword in self.snippets_content:
                option, snippet, cpos = self.snippets_content[keyword]
                self.add_command(label=option, command=self.insert_snippets(snippet, cpos))
        # 设置
        if self.snippets_type=='set':
            self.snippets_content = self.Snippets[self.snippets_type]
            for keyword in self.snippets_content:
                option, snippet, cpos = self.snippets_content[keyword]
                self.add_command(label=option, command=self.insert_snippets(snippet, cpos+2))
        # 角色联想
        elif self.snippets_type=='charactor':
            char_names = self.ref_char.get_names()
            for name in char_names:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 差分联想
        elif self.snippets_type=='subtype':
            char_name = kw_args['name']
            char_subtypes = self.ref_char.get_subtype(char_name)
            for name in char_subtypes:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 背景
        elif self.snippets_type=='background':
            char_subtypes = self.ref_media.get_type('background')
            for name in char_subtypes:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 立绘
        elif self.snippets_type=='animation':
            char_subtypes = self.ref_media.get_type('anime')
            for name in char_subtypes:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
        # 气泡联想，聊天窗以对象而不是关键字的形式返回
        elif self.snippets_type=='bubble':
            char_subtypes = self.ref_media.get_type('bubble',cw=False) + self.ref_media.get_type('chatwindow')
            for name in char_subtypes:
                self.add_command(label=name, command=self.insert_snippets(name+'("","")', len(name)+2))
        # 背景音乐
        elif self.snippets_type=='bgm':
            char_subtypes = self.ref_media.get_type('bgm')
            for name in char_subtypes:
                self.add_command(label=name, command=self.insert_snippets(name, len(name)))
    # 闭包
    def insert_snippets(self, snippet, cpos):
        # 命令内容
        def command():
            self.codeview.insert(self.curser_idx,chars=snippet)
            self.codeview.mark_set("insert",f'{self.curser_idx}+{cpos}c')
            self.codeview.highlight_all()
        return command

    