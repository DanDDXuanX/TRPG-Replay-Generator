#!/usr/bin/env python
# coding: utf-8

# 项目资源管理器，项目视图的元素之一。
# 包含：标题图，项目管理按钮，媒体、角色、剧本的可折叠容器

import json
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.scrolled import ScrolledFrame
from .ScriptParser import MediaDef, CharTable, RplGenLog, Script
from .FilePaths import Filepath
from .ProjConfig import Config
from .GUI_TabPage import PageFrame, RGLPage, CTBPage, MDFPage
# 项目视图-文件管理器-RGPJ
class RplGenProJect(Script):
    def __init__(self, json_input=None) -> None:
        # 新建空白工程
        if json_input is None:
            self.config     = Config()
            self.mediadef   = MediaDef(file_input='./toy/MediaObject.txt')
            # 设置当前路径
            Filepath.Mediapath = './toy/' #self.media_path
            self.chartab    = CharTable(file_input='./toy/CharactorTable.tsv')
            self.logfile    = {
                '示例项目1' : RplGenLog(file_input='./toy/LogFile.rgl'),
                '示例项目2' : RplGenLog(file_input='./toy/LogFile2.rgl')
                }
        # 载入json工程文件
        else:
            super().__init__(None, None, None, json_input)
            # config
            self.config     = Config(dict_input=self.struct['config'])
            # media
            self.mediadef   = MediaDef(dict_input=self.struct['mediadef'])
            # chartab
            self.chartab    = CharTable(dict_input=self.struct['chartab'])
            # logfile
            self.logfile    = {}
            for key in self.struct['logfile'].keys():
                self.logfile[key] = RplGenLog(dict_input=self.struct['logfile'][key])
    def dump_json(self, filepath: str) -> None:
        logfile_dict = {}
        for key in self.logfile.keys():
            logfile_dict[key] = self.logfile[key].struct
        with open(filepath,'w',encoding='utf-8') as of:
            of.write(
                json.dumps(
                    {
                        'config'  : self.config.get_struct(),
                        'mediadef': self.mediadef.struct,
                        'chartab' : self.chartab.struct,
                        'logfile' : logfile_dict,
                    }
                    ,indent=4
                )
            )

# 项目视图-文件管理器
class FileManager(ttk.Frame):
    def __init__(self,master,screenzoom,page_frame:PageFrame)->None:
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        self.master = master
        # 图形
        SZ_30 = int(self.sz * 30)
        SZ_300 = int(self.sz * 300)
        SZ_180 = int(self.sz * 180)
        icon_size = [SZ_30,SZ_30]
        self.image = {
            'title'     : ImageTk.PhotoImage(name='title',   image=Image.open('./toy/media/bg1.jpg').resize([SZ_300,SZ_180])),
            'save'      : ImageTk.PhotoImage(name='save' ,   image=Image.open('./media/icon/save.png').resize(icon_size)),
            'config'    : ImageTk.PhotoImage(name='config',   image=Image.open('./media/icon/setting.png').resize(icon_size)),
            'import'    : ImageTk.PhotoImage(name='import',   image=Image.open('./media/icon/import.png').resize(icon_size)),
            'export'    : ImageTk.PhotoImage(name='export',   image=Image.open('./media/icon/export.png').resize(icon_size)),
        }
        # 标题
        self.project_title = ttk.Frame(master=self,borderwidth=0,bootstyle='light')
        self.title_pic = ttk.Label(master=self.project_title,image='title',borderwidth=0)
        self.buttons = {
            'save'      : ttk.Button(master=self.project_title,image='save'  ),
            'config'    : ttk.Button(master=self.project_title,image='config'),
            'import'    : ttk.Button(master=self.project_title,image='import'),
            'export'    : ttk.Button(master=self.project_title,image='export'),
        }
        # 放置
        self.title_pic.pack(fill='none',side='top')
        for idx,key in enumerate(self.buttons):
            buttons:ttk.Button = self.buttons[key]
            buttons.pack(expand=True,fill='x',side='left',anchor='se',padx=0,pady=0)
        self.project_title.pack(fill='x',side='top',padx=0,pady=0,ipadx=0,ipady=0)
        # 文件管理器的项目对象
        self.project:RplGenProJect = RplGenProJect()
        # 文件浏览器元件
        self.project_content = ScrolledFrame(master=self,borderwidth=0,bootstyle='light',autohide=True)
        self.project_content.vscroll.config(bootstyle='warning-round')
        # 对应的page_frame对象
        self.page_frame:PageFrame = page_frame
        self.page_frame.ref_medef = self.project.mediadef
        self.page_frame.ref_chartab = self.project.mediadef
        # 元件
        self.items = {
            'mediadef'  : MDFCollapsing(master=self.project_content,screenzoom=self.sz,content=self.project.mediadef,page_frame=self.page_frame),
            'chartab'   : CTBCollapsing(master=self.project_content,screenzoom=self.sz,content=self.project.chartab,page_frame=self.page_frame),
            'rplgenlog' : RGLCollapsing(master=self.project_content,screenzoom=self.sz,content=self.project.logfile,page_frame=self.page_frame),
        }
        # 放置
        self.update_item()
        self.project_content.pack(fill='both',expand=True,side='top')
    def update_item(self):
        for idx,key in enumerate(self.items):
            fileitem:ttk.Button = self.items[key]
            fileitem.pack(fill='x',pady=0,side='top')
# 项目视图-可折叠类容器-基类
class FileCollapsing(ttk.Frame):
    def __init__(self,master,screenzoom:float,fileclass:str,content,page_frame:PageFrame):
        self.sz = screenzoom
        self.page_frame = page_frame
        SZ_5 = int(self.sz * 5)
        SZ_2 = int(self.sz * 2)
        super().__init__(master=master,borderwidth=0)
        self.class_text = {'mediadef':'媒体库','chartab':'角色配置','rplgenlog':'剧本文件'}[fileclass]
        self.collapbutton = ttk.Button(master=self,text=self.class_text,command=self.update_toggle,bootstyle='warning')
        self.content_frame = ttk.Frame(master=self)
        self.button_padding = (SZ_5,SZ_2,SZ_5,SZ_2)
        # 内容
        self.content = content
        self.items = {}
    def update_item(self):
        for idx in self.items:
            this_button = self.items[idx]
            this_button.pack(fill='x',side='top')
        self.collapbutton.pack(fill='x',side='top')
        self.expand:bool = False
        self.update_toggle()
    def update_toggle(self):
        if self.expand:
            self.content_frame.pack_forget()
            self.expand:bool = False
        else:
            self.content_frame.pack(fill='x',side='top')
            self.expand:bool = True
    def add_item(self):
        pass
    def delete_item(self):
        pass
    def rename_item(self):
        pass
    def open_item_as_page(self,keyword,file_type,file_index):
        # 检查是否是Page_frame中的活跃页
        if keyword not in self.page_frame.page_dict.keys():
            # 如果不是活动页，新增活跃页
            self.page_frame.add_active_page(
                name        = keyword,
                file_type   = file_type,
                content_obj = self.content,
                content_type= file_index
                )
        else:
            # 如果是活动页，切换到活跃页
            self.page_frame.goto_page(name=keyword)
    def closure_open_item_as_page(self,file_index:str):
        def open_the_pressed_file():
            self.open_item_as_page(file_index=str(file_index))
        return open_the_pressed_file
# 项目视图-可折叠类容器-媒体类
class MDFCollapsing(FileCollapsing):
    media_type_name = {
        'Pos'       :   '位置',
        'Text'      :   '文本',
        'Bubble'    :   '气泡',
        'Animation' :   '立绘',
        'Background':   '背景',
        'Audio'     :   '音频',
    }
    def __init__(self, master, screenzoom: float, content:MediaDef, page_frame:PageFrame):
        super().__init__(master, screenzoom, 'mediadef', content, page_frame)
        for mediatype in ['Pos', 'Text', 'Bubble', 'Animation', 'Background', 'Audio']:
            command  = self.closure_open_item_as_page(mediatype)
            filename = self.media_type_name[mediatype]
            showname = "{} ({})".format(filename,mediatype)
            self.items[mediatype] = ttk.Button(
                master      = self.content_frame,
                text        = showname,
                bootstyle   = 'light',
                padding     = self.button_padding,
                compound    = 'left',
                command     = command
                )
        self.update_item()
    def open_item_as_page(self,file_index:str):
        filename = self.media_type_name[file_index]
        super().open_item_as_page(
            keyword     = '媒体-' + filename, # '媒体-立绘'
            file_type   = 'MDF',
            file_index  = file_index # 'Animation'
            ) 
# 项目视图-可折叠类容器-角色类
class CTBCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:CharTable, page_frame:PageFrame):
        super().__init__(master, screenzoom, 'chartab', content, page_frame)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0)
        self.add_button.pack(side='right',padx=SZ_10,pady=SZ_5,ipady=SZ_1,ipadx=SZ_3)
        self.table = self.content.export()
        # 内容
        for name in self.table['Name'].unique():
            command  = self.closure_open_item_as_page(name)
            self.items[name] = ttk.Button(
                master      = self.content_frame,
                text        = name,
                bootstyle   = 'light',
                padding     = self.button_padding,
                compound    = 'left',
                command     = command
                )
        self.update_item()
    def open_item_as_page(self,file_index:str):
        super().open_item_as_page(
            keyword     = '角色-'+file_index,
            file_type   = 'CTB',
            file_index  = file_index
            ) 
# 项目视图-可折叠类容器-剧本类
class RGLCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:dict, page_frame:PageFrame):
        super().__init__(master, screenzoom, 'rplgenlog', content, page_frame)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0)
        self.add_button.pack(side='right',padx=SZ_10,pady=SZ_5,ipady=SZ_1,ipadx=SZ_3)
        # 内容
        for key in self.content.keys():
            command  = self.closure_open_item_as_page(key)
            self.items[key] = ttk.Button(
                master      = self.content_frame,
                text        = key,
                bootstyle   = 'light',
                padding     = self.button_padding,
                compound    = 'left',
                command     = command
                )
        self.update_item()
    def open_item_as_page(self,file_index:str):
        super().open_item_as_page(
            keyword     = '剧本-'+file_index,
            file_type   = 'RGL',
            file_index  = file_index
            )
