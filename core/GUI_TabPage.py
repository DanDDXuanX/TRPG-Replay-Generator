#!/usr/bin/env python
# coding: utf-8

# 页面，项目视图的元素之一。
# 包含：标签页、文件内容页面内容：
# MDF页面
# CTB页面
# RGL页面

import ttkbootstrap as ttk
import tkinter as tk
from PIL import Image,ImageTk

from .ScriptParser import MediaDef, CharTable, RplGenLog, Script
from .GUI_PageElement import SearchBar, OutPutCommand, NewElementCommand, VerticalOutputCommand
from .GUI_CodeView import RGLCodeViewFrame
from .GUI_Container import RGLContainer, MDFContainer, CTBContainer
from .GUI_PreviewCanvas import MDFPreviewCanvas, CTBPreviewCanvas, RGLPreviewCanvas
from .GUI_Edit import EditWindow, CharactorEdit, MediaEdit, LogEdit
from .GUI_Link import Link

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
    # 将对象添加到 page_dict
    def add_active_page(self,name:str,image:str,file_type:str,content_obj:Script,content_type=False):
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
        self.page_notebook.add(name=name,image=image)
    # 切换页面
    def switch_page(self,name:str):
        SZ_30 = int(self.sz * 30)
        self.page_show.place_forget()
        self.page_show = self.page_dict[name]
        self.page_show.place(x=0,y=SZ_30,relheight=1,height=-SZ_30,relwidth=1)
    def goto_page(self,name:str):
        self.page_notebook.active_tabs[name].get_pressed()
    # 刷新目前某一类标签页的显示，导入文件时需要调用
    def update_pages_elements(self,ftype='medef'):
        # 设置目标类型
        if ftype == 'medef':
            page_type = MDFPage
        elif ftype == 'chartab':
            page_type = CTBPage
        else:
            return
        # 执行刷新
        for keyword in self.page_dict:
            page_this:MDFPage = self.page_dict[keyword]
            if type(page_this) == page_type:
                page_this.container.refresh_item()
# 项目视图-页面标签
class PageNotes(ttk.Frame):
    """
    相对布局对象，不考虑缩放比例
    """
    def __init__(self,master,screenzoom)->None:
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='dark')
        self.master = master
        self.active_tabs = {}
        self.active_tabs_name_list = []
        self.selected_tabs = None
        # 全局连接
        Link['active_tabs'] = self.active_tabs
        # 更新显示
        self.update_item()
    def update_item(self):
        SZ_2 = int(self.sz * 2)
        for idx,key in enumerate(self.active_tabs):
            page_label:ttk.Button = self.active_tabs[key]
            page_label.pack_forget()
            page_label.pack(fill='y',padx=(0,SZ_2),side='left',pady=0)
    def add(self,name,image):
        # 添加对象
        self.active_tabs[name] = TabNote(master=self,text=name,image=image,bootstyle='secondary',screenzoom=self.sz)
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
    def __init__(self,master,screenzoom,text,image,bootstyle)->None:
        self.sz = screenzoom
        SZ_5 = int(self.sz * 5)
        SZ_21 = int(self.sz * 21)
        SZ_24 = int(self.sz * 24)
        SZ_30 = int(self.sz * 30)
        super().__init__(
            master,
            bootstyle=bootstyle,
            text=text,
            image=image,
            compound='left',
            padding=(SZ_5,SZ_5,SZ_30,SZ_5),
            command=self.get_pressed
        )
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
        self.config(bootstyle=self.bootstyle+'-link')
        self.dele.config(bootstyle=self.bootstyle+'-link')
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
        self.ref_config = self.master.ref_config
        # 初始化
        self.update_items_codeview()
    # 放置元件
    def update_items_visual(self):
        SZ_40 = int(self.sz * 40)
        # 代码编辑区
        try:
            self.codeviewframe.destroy()
            self.outputcommand.destroy()
        except Exception:
            pass
        # 元件
        self.preview = RGLPreviewCanvas(master=self,screenzoom=self.sz, mediadef=self.ref_medef, chartab=self.ref_chartab, rplgenlog=self.content)
        self.edit = LogEdit(master=self,screenzoom=self.sz)
        self.container = RGLContainer(master=self,content=self.content,screenzoom=self.sz)
        self.searchbar = SearchBar(master=self,screenzoom=self.sz,container=self.container)
        self.outputcommand = OutPutCommand(master=self,screenzoom=self.sz)
        # 可视化编辑区
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-2*SZ_40)
        self.outputcommand.place(x=0,y=-SZ_40,rely=1,relwidth=0.5,height=SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.44)
        self.edit.place(relx=0.5,rely=0.44,relwidth=0.5,relheight=0.56)
    # 放置编辑器
    def update_items_codeview(self):
        # 可视化编辑区
        try:
            self.searchbar.destroy()
            self.container.destroy()
            self.outputcommand.destroy()
            self.preview.destroy()
            self.edit.destroy()
        except Exception:
            pass
        # 脚本模式
        self.codeviewframe = RGLCodeViewFrame(
            master      = self,
            screenzoom  = self.sz,
            rplgenlog   = self.content,
            mediadef    = self.ref_medef,
            chartab     = self.ref_chartab
        )
        self.outputcommand = VerticalOutputCommand(
            master=self,
            screenzoom=self.sz
        )
        # 代码编辑区
        self.codeviewframe.pack(side='left',fill='both',expand=True)
        self.outputcommand.pack(side='left',fill='y')
        # self.codeviewframe.place(x=0,y=0,relwidth=1,relheight=1)
        # self.codeviewframe.place(x=0,y=0,relwidth=1,relheight=1)

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
        self.ref_medef = self.content
        # 是否被修改
        self.is_modified:bool = False
        # 元件
        self.edit = MediaEdit(master=self,screenzoom=self.sz)
        self.preview = MDFPreviewCanvas(master=self,screenzoom=self.sz,mediadef=self.content)
        self.container = MDFContainer(master=self,content=content_obj,typelist=self.categroy_dict[content_type],screenzoom=self.sz)
        self.searchbar = SearchBar(master=self,screenzoom=self.sz,container=self.container)
        self.newelementcommand = NewElementCommand(master=self,screenzoom=self.sz,pagetype=content_type)
        # 初始显示
        self.update_items()
    def update_items(self):
        # 取消全屏预览（假如）
        self.preview.pack_forget()
        # 放置元件
        SZ_40 = int(self.sz * 40)
        # self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        # self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-SZ_40)
        # self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.44)
        # self.edit.place(relx=0.5,rely=0.44,relwidth=0.5,relheight=0.56)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-2*SZ_40)
        self.newelementcommand.place(x=0,y=-SZ_40,rely=1,relwidth=0.5,height=SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.44)
        self.edit.place(relx=0.5,rely=0.44,relwidth=0.5,relheight=0.56)
        # 标志
        self.isfull = False
    def update_fullviews(self):
        # 取消全部显示
        self.searchbar.place_forget()
        self.container.place_forget()
        self.preview.place_forget()
        self.edit.place_forget()
        self.newelementcommand.place_forget()
        # 显示全屏预览
        self.preview.pack(fill='both',expand=True)
        # 标志
        self.isfull = True
    def set_fullview(self):
        if self.isfull:
            self.update_items()
        else:
            self.update_fullviews()

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
        self.newelementcommand = NewElementCommand(master=self,screenzoom=self.sz,pagetype='charactor')
        # 放置元件
        # SZ_40 = int(self.sz * 40)
        # self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        # self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-SZ_40)
        # self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.44)
        # self.edit.place(relx=0.5,rely=0.44,relwidth=0.5,relheight=0.56)
        self.update_items()
    def update_items(self):
        # 取消全屏预览（假如）
        # self.preview.pack_forget()
        # 放置元件
        SZ_40 = int(self.sz * 40)
        # self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        # self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-SZ_40)
        # self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.44)
        # self.edit.place(relx=0.5,rely=0.44,relwidth=0.5,relheight=0.56)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-2*SZ_40)
        self.newelementcommand.place(x=0,y=-SZ_40,rely=1,relwidth=0.5,height=SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.44)
        self.edit.place(relx=0.5,rely=0.44,relwidth=0.5,relheight=0.56)