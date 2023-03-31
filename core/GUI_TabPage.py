#!/usr/bin/env python
# coding: utf-8

# 页面，项目视图的元素之一。
# 包含：标签页、文件内容页面内容：
from .ScriptParser import MediaDef, CharTable, RplGenLog
# MDF页面
# CTB页面
# RGL页面

import ttkbootstrap as ttk
import tkinter as tk

from .GUI_PageElement import SearchBar, OutPutCommand
from .GUI_Container import RGLContainer, MDFContainer, CTBContainer
from .GUI_PreviewCanvas import PreviewCanvas
from .GUI_Edit import EditWindow

# 项目视图-页面标签
class PageNotes(ttk.Frame):
    """
    相对布局对象，不考虑缩放比例
    """
    def __init__(self,master,screenzoom)->None:
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='secondary')
        self.master = master
        self.active_page = {
            '1': TabNote(master=self,text='媒体库',bootstyle='primary',screenzoom=self.sz),
            '2': TabNote(master=self,text='角色配置',bootstyle='primary',screenzoom=self.sz),
            '3': TabNote(master=self,text='剧本',bootstyle='primary',screenzoom=self.sz),
        }
        self.update_item()
    def update_item(self):
        SZ_1 = int(self.sz * 1)
        for idx,key in enumerate(self.active_page):
            page_label:ttk.Button = self.active_page[key]
            page_label.pack(fill='y',padx=SZ_1,side='left',pady=0)
# 项目视图-页面标签-标签
class TabNote(ttk.Button):
    def __init__(self,master,screenzoom,text,bootstyle)->None:
        self.sz = screenzoom
        SZ_5 = int(self.sz * 5)
        SZ_21 = int(self.sz * 21)
        SZ_24 = int(self.sz * 24)
        SZ_30 = int(self.sz * 30)
        super().__init__(master,bootstyle=bootstyle,text=text,compound='left',padding=(SZ_5,SZ_5,SZ_30,SZ_5),command=self.get_pressed)
        self.bootstyle = bootstyle
        self.is_change = tk.StringVar(master=self,value='×')
        self.dele = ttk.Button(master=self,textvariable=self.is_change,bootstyle=bootstyle,padding=0,command=self.set_change)
        self.dele.place(x=-SZ_24,relx=1,rely=0.15,width=SZ_21,relheight=0.70)
    def set_change(self):
        if self.is_change.get() == '×':
            self.is_change.set('●')
        else:
            self.is_change.set('×')
    def get_pressed(self):
        # 复原所有已点击
        for key in self.master.active_page:
            this_tab = self.master.active_page[key].recover()
        self.config(bootstyle='light')
        self.dele.config(bootstyle='light')
    def recover(self):
        self.config(bootstyle=self.bootstyle)
        self.dele.config(bootstyle=self.bootstyle)
        
# 页面视图：Log文件
class RGLPage(ttk.Frame):
    def __init__(self,master,screenzoom,rgl:RplGenLog):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        # 元件
        self.searchbar = SearchBar(master=self,screenzoom=self.sz)
        self.container = RGLContainer(master=self,content=rgl,screenzoom=self.sz)
        self.outputcommand = OutPutCommand(master=self,screenzoom=self.sz)
        self.preview = PreviewCanvas(master=self,screenzoom=self.sz)
        self.edit = EditWindow(master=self,screenzoom=self.sz,section=rgl.struct['0'])
        # 放置元件
        SZ_40 = int(self.sz * 40)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-2*SZ_40)
        self.outputcommand.place(x=0,y=-SZ_40,rely=1,relwidth=0.5,height=SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.5)
        self.edit.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.5)

# 页面视图：媒体定义文件
class MDFPage(ttk.Frame):
    categroy_dict = {
        'Text'      : ['Text', 'StrokeText'],
        'Pos'       : ['Pos','FreePos','PosGrid'],
        'Animation' : ['Animation'],
        'Bubble'    : ['Bubble','Balloon','DynamicBubble','ChatWindow'],
        'Background': ['Background'],
        'Audio'     : ['Audio','BGM'],
    }
    def __init__(self,master,screenzoom,mdf:MediaDef,media_type='Animation'):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        # 元件
        self.searchbar = SearchBar(master=self,screenzoom=self.sz)
        self.container = MDFContainer(master=self,content=mdf,typelist=self.categroy_dict[media_type],screenzoom=self.sz)
        self.preview = PreviewCanvas(master=self,screenzoom=self.sz)
        self.edit = EditWindow(master=self,screenzoom=self.sz,section=mdf.struct['0'])
        # 放置元件
        SZ_40 = int(self.sz * 40)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.5)
        self.edit.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.5)

# 页面视图：角色配置文件
class CTBPage(ttk.Frame):
    def __init__(self,master,screenzoom,ctb:CharTable,name:str):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        # 元件
        self.searchbar = SearchBar(master=self,screenzoom=self.sz)
        self.container = CTBContainer(master=self,content=ctb,name=name,screenzoom=self.sz)
        self.preview = PreviewCanvas(master=self,screenzoom=self.sz)
        self.edit = EditWindow(master=self,screenzoom=self.sz,section={'type':'False'})
        # 放置元件
        SZ_40 = int(self.sz * 40)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.5)
        self.edit.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.5)