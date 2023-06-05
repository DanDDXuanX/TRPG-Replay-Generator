#!/usr/bin/env python
# coding: utf-8

# 页面，项目视图的元素之一。
# 包含：标签页、文件内容页面内容：
from .ScriptParser import MediaDef, CharTable, RplGenLog, Script
# MDF页面
# CTB页面
# RGL页面

import ttkbootstrap as ttk
import tkinter as tk
from PIL import Image,ImageTk

from .GUI_PageElement import SearchBar, OutPutCommand
from .GUI_Container import RGLContainer, MDFContainer, CTBContainer
from .GUI_PreviewCanvas import MDFPreviewCanvas, CTBPreviewCanvas, RGLPreviewCanvas
from .GUI_Edit import EditWindow, CharactorEdit, MediaEdit, LogEdit

# 项目视图-页面-总体
class PageFrame(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        self.page_notebook = PageNotes(master=self, screenzoom=self.sz)
        self.empty_bg = ImageTk.PhotoImage(name='logo_bg',image=Image.open('./media/icon2.png'))
        self.page_dict = {
            'empty' : ttk.Label(master=self,image='logo_bg',anchor='center',bootstyle='primary')
        }
        self.page_show = self.page_dict['empty']
        # 引用对象：初始化状态
        self.ref_medef = MediaDef()
        self.ref_chartab = CharTable()
        # MDFPage(master=self, screenzoom=self.sz ,mdf=MediaDef(file_input="./toy/MediaObject.txt"),media_type='Text')
        self.update_item()
    def update_item(self):
        SZ_30 = int(self.sz * 30)
        self.page_notebook.place(x=0,y=0,height=SZ_30,relwidth=1)
        # 初始化显示
        self.page_show.place(x=0,y=SZ_30,relheight=1,height=-SZ_30,relwidth=1)
    def add_active_page(self,name:str,file_type:str,content_obj:Script,content_type=False):
        # 将对象添加到 page_dict
        PageType = {
            'MDF' : MDFPage,
            'CTB' : CTBPage,
            'RGL' : RGLPage
        }[file_type]
        self.page_dict[name] = PageType(
            master      = self,
            screenzoom  = self.sz,
            content_obj = content_obj,
            content_type= content_type
            )
        # 在标签页中新建一个标签
        self.page_notebook.add(name=name)
    def switch_page(self,name:str):
        # 切换页面
        SZ_30 = int(self.sz * 30)
        self.page_show.place_forget()
        self.page_show = self.page_dict[name]
        self.page_show.place(x=0,y=SZ_30,relheight=1,height=-SZ_30,relwidth=1)
    def goto_page(self,name:str):
        self.page_notebook.active_tabs[name].get_pressed()

# 项目视图-页面标签
class PageNotes(ttk.Frame):
    """
    相对布局对象，不考虑缩放比例
    """
    def __init__(self,master,screenzoom)->None:
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='secondary')
        self.master = master
        self.active_tabs = {}
        self.active_tabs_name_list = []
        self.selected_tabs = None
        self.update_item()
    def update_item(self):
        SZ_1 = int(self.sz * 1)
        for idx,key in enumerate(self.active_tabs):
            page_label:ttk.Button = self.active_tabs[key]
            page_label.pack_forget()
            page_label.pack(fill='y',padx=SZ_1,side='left',pady=0)
    def add(self,name):
        # 添加对象
        self.active_tabs[name] = TabNote(master=self,text=name,bootstyle='primary',screenzoom=self.sz)
        self.active_tabs_name_list.append(name)
        # 触发点击事件
        self.active_tabs[name].get_pressed()
        # 刷新
        self.update_item()
    def delete(self,name):
        # 获取前一个对象
        del_index = self.active_tabs_name_list.index(name)
        this_index = self.active_tabs_name_list.index(self.selected_tabs)
        if del_index != this_index:
            pass
        else:
            if len(self.active_tabs_name_list) == 1:
                self.master.switch_page(name='empty')
            elif this_index == 0:
                next_name = self.active_tabs_name_list[del_index+1]
                self.active_tabs[next_name].get_pressed()
            else:
                next_name = self.active_tabs_name_list[del_index-1]
                self.active_tabs[next_name].get_pressed()
        # 移除页面
        page_this = self.master.page_dict[name]
        page_this.destroy()
        self.master.page_dict.pop(name)
        # 移除标签
        this_tab:ttk.Button = self.active_tabs[name]
        this_tab.destroy()
        self.active_tabs.pop(name)
        self.active_tabs_name_list.remove(name)
        # 刷新
        self.update_item()

# 项目视图-页面标签-标签
class TabNote(ttk.Button):
    def __init__(self,master,screenzoom,text,bootstyle)->None:
        self.sz = screenzoom
        SZ_5 = int(self.sz * 5)
        SZ_21 = int(self.sz * 21)
        SZ_24 = int(self.sz * 24)
        SZ_30 = int(self.sz * 30)
        super().__init__(master,bootstyle=bootstyle,text=text,compound='left',padding=(SZ_5,SZ_5,SZ_30,SZ_5),command=self.get_pressed)
        self.name = text
        self.bootstyle = bootstyle
        self.is_change = tk.StringVar(master=self,value='×')
        self.dele = ttk.Button(master=self,textvariable=self.is_change,bootstyle=bootstyle,padding=0,command=self.press_delete)
        self.dele.place(x=-SZ_24,relx=1,rely=0.15,width=SZ_21,relheight=0.70)
    def set_change(self):
        if self.is_change.get() == '×':
            self.is_change.set('●')
        else:
            self.is_change.set('×')
    def get_pressed(self):
        # 切换页面 TabNote.PageNotes.PageFrame
        self.master.master.switch_page(name=self.name)
        # 设置选中的标签
        self.master.selected_tabs = self.name
        # 复原所有已点击
        for key in self.master.active_tabs:
            self.master.active_tabs[key].recover()
        self.config(bootstyle='light')
        self.dele.config(bootstyle='light')
    def recover(self):
        self.config(bootstyle=self.bootstyle)
        self.dele.config(bootstyle=self.bootstyle)
    def press_delete(self):
        self.master.delete(name=self.name)
# 页面视图：Log文件
class RGLPage(ttk.Frame):
    def __init__(self,master,screenzoom,content_obj:dict,content_type):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        # 内容
        self.content:RplGenLog = content_obj[content_type]
        # 是否被修改
        self.is_modified:bool = False
        # 引用媒体对象
        self.ref_medef = self.master.ref_medef
        self.ref_chartab = self.master.ref_chartab
        # 元件
        self.preview = RGLPreviewCanvas(master=self,screenzoom=self.sz, mediadef=self.ref_medef, chartab=self.ref_chartab, rplgenlog=self.content)
        self.edit = LogEdit(master=self,screenzoom=self.sz)
        self.container = RGLContainer(master=self,content=self.content,screenzoom=self.sz)
        self.searchbar = SearchBar(master=self,screenzoom=self.sz,container=self.container)
        self.outputcommand = OutPutCommand(master=self,screenzoom=self.sz)
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
        'Text'      : ['Text', 'StrokeText', 'RichText'],
        'Pos'       : ['Pos','FreePos','PosGrid'],
        'Animation' : ['Animation'],
        'Bubble'    : ['Bubble','Balloon','DynamicBubble','ChatWindow'],
        'Background': ['Background'],
        'Audio'     : ['Audio','BGM'],
    }
    def __init__(self,master,screenzoom,content_obj:MediaDef,content_type='Animation'):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        # 内容
        self.content:MediaDef = content_obj
        # 是否被修改
        self.is_modified:bool = False
        # 元件
        self.edit = MediaEdit(master=self,screenzoom=self.sz)
        self.preview = MDFPreviewCanvas(master=self,screenzoom=self.sz,mediadef=self.content)
        self.container = MDFContainer(master=self,content=content_obj,typelist=self.categroy_dict[content_type],screenzoom=self.sz)
        self.searchbar = SearchBar(master=self,screenzoom=self.sz,container=self.container)
        # 放置元件
        SZ_40 = int(self.sz * 40)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.5)
        self.edit.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.5)

# 页面视图：角色配置文件
class CTBPage(ttk.Frame):
    def __init__(self,master,screenzoom,content_obj:CharTable,content_type:str):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        # 内容
        self.content:CharTable = content_obj
        # 是否被修改
        self.is_modified:bool = False
        # 引用媒体对象
        self.ref_medef = self.master.ref_medef
        # 元件
        self.preview = CTBPreviewCanvas(master=self,screenzoom=self.sz,chartab=self.content,mediadef=self.ref_medef)
        self.edit = CharactorEdit(master=self,screenzoom=self.sz)
        self.container = CTBContainer(master=self,content=content_obj,name=content_type,screenzoom=self.sz)
        self.searchbar = SearchBar(master=self,screenzoom=self.sz,container=self.container)
        # 放置元件
        SZ_40 = int(self.sz * 40)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.5)
        self.edit.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.5)