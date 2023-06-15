#!/usr/bin/env python
# coding: utf-8

# 新建空白项目，新建智能项目的窗口

import os
import pandas as pd
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox, Dialog
from tkinter.filedialog import askdirectory
from .GUI_Util import KeyValueDescribe
from .GUI_EditTableStruct import NewProjectTable
from .GUI_DialogWindow import browse_file

class CreateProject(ttk.Frame):
    table_struct = {}
    def __init__(self,master,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        self.seperator = {}
        self.elements = {}
        self.build_struct()
        self.update_item()
    def build_struct(self):
        for sep in self.table_struct:
            this_sep = self.table_struct[sep]
            self.seperator[sep] = ttk.LabelFrame(master=self,text=this_sep['Text'])
            for keyword in this_sep['Content']:
                this_kwd = this_sep['Content'][keyword]
                self.elements[keyword] = KeyValueDescribe(
                    master=self.seperator[sep],
                    screenzoom=self.sz,
                    key=this_kwd['ktext'],
                    value={
                        'type':this_kwd['vtype'],
                        'style':this_kwd['vitem'],
                        'value':this_kwd['default']
                    },
                    describe={
                        "type":this_kwd['ditem'],
                        "text":this_kwd['dtext']
                    },
                    tooltip=this_kwd['tooltip']
                )
    def update_item(self):
        SZ_5 = int(5*self.sz)
        SZ_10 = int(10*self.sz)
        SZ_15 = int(15*self.sz)
        for key in self.seperator:
            item = self.seperator[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(SZ_10,SZ_10))
        for key in self.elements:
            item = self.elements[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5))
    def clear_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.destroy()
        for key in self.seperator:
            item = self.seperator[key]
            item.destroy()
        self.elements.clear()
        self.seperator.clear()

class CreateEmptyProject(CreateProject):
    # 原件：
    # 1. 基本（项目名称、项目封面、位置）
    # 2. 视频（分辨率、帧率）
    # 3. 图层（图层顺序）
    table_struct = NewProjectTable['EmptyProject']
    video_preset = {
        '自定义':   None,
        '横屏-高清 (1920x1080, 30fps)'  : [1920, 1080, 30],
        '横屏-标清（1280x720, 30fps)'   : [1280, 720, 30],
        '竖屏-高清 (1080x1920, 30fps)'  : [1080, 1920, 30],
        '竖屏-标清（720x1280, 30fps）'   : [720, 1280, 30],
        '横屏-高清 (1920x1080, 25fps)'  : [1920, 1080, 25],
        '横屏-标清 (1280x720, 25fps)'   : [1280, 720, 25],
    }
    zorder_preset = {
        '自定义'    :None,
        '背景->立绘->气泡'  : "BG2,BG1,Am3,Am2,Am1,AmS,Bb,BbS",
        '背景->气泡->立绘'  : "BG2,BG1,Bb,BbS,Am3,Am2,Am1,AmS"
    }
    def build_struct(self):
        super().build_struct()
        # 绑定功能
        self.elements['proj_cover'].bind_button(dtype='picture-file',quote=False)
        self.elements['save_pos'].bind_button(dtype='dir',quote=False)
        self.elements['preset_video'].input.configure(values=list(self.video_preset.keys()), state='readonly')
        self.elements['preset_layer'].input.configure(values=list(self.zorder_preset.keys()), state='readonly')
        self.elements['preset_video'].input.bind('<<ComboboxSelected>>', self.update_preset,'+')
        self.elements['preset_layer'].input.bind('<<ComboboxSelected>>', self.update_preset,'+')
        self.update_preset(None)
    def update_preset(self,event):
        video_preset_args = self.video_preset[self.elements['preset_video'].get()]
        zorder_preset_args = self.zorder_preset[self.elements['preset_layer'].get()]
        if video_preset_args:
            W,H,F = video_preset_args
            # 修改值
            self.elements['video_width'].value.set(W)
            self.elements['video_height'].value.set(H)
            self.elements['frame_rate'].value.set(F)
            # 设置参数为仅只读
            self.elements['video_width'].input.configure(state='disabled')
            self.elements['video_height'].input.configure(state='disabled')
            self.elements['frame_rate'].input.configure(state='disabled')
        else:
            # 如果是自定义，则启用编辑
            self.elements['video_width'].input.configure(state='normal')
            self.elements['video_height'].input.configure(state='normal')
            self.elements['frame_rate'].input.configure(state='normal')
        if zorder_preset_args:
            self.elements['layer_zorder'].value.set(zorder_preset_args)
            self.elements['layer_zorder'].input.configure(state='disabled')
        else:
            self.elements['layer_zorder'].input.configure(state='normal')

class CreateIntelProject(ttk.Frame):
    pass