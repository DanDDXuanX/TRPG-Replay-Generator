#!/usr/bin/env python
# coding: utf-8

# 项目资源管理器，项目视图的元素之一。
# 包含：标题图，项目管理按钮，媒体、角色、剧本的可折叠容器

from PIL import Image, ImageTk
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.scrolled import ScrolledFrame
from .ScriptParser import MediaDef, CharTable, RplGenLog, Script
from .ProjConfig import Config
# 项目视图-文件管理器-RGPJ
class RplGenProJect(Script):
    def __init__(self, json_input=None) -> None:
        # 新建空白工程
        if json_input is None:
            self.struct = {
                'mediadef':{
                    'Text'      :MediaDef(),
                    'Pos'       :MediaDef(),
                    'Animation' :MediaDef(),
                    'Bubble'    :MediaDef(),
                    'Audio'     :MediaDef(),
                },
                'chartab':{},
                'logfile':{},
                'config' :Config()
            }
        # 载入json工程文件
        else:
            super().__init__(None, None, None, json_input)
            # media
            for key in self.struct['mediadef'].keys():
                self.struct['mediadef'][key] = MediaDef(dict_input=self.struct['mediadef'][key])
            # chartab
            for key in self.struct['chartab'].keys():
                self.struct['chartab'][key] = CharTable(dict_input=self.struct['chartab'][key])
            # logfile
            for key in self.struct['logfile'].keys():
                self.struct['logfile'][key] = RplGenLog(dict_input=self.struct['logfile'][key])
            # config
            self.struct['config'] = Config(dict_input=self.struct['config'])

# 项目视图-文件管理器
class FileManager(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
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
        # 文件内容
        self.project_contene = ScrolledFrame(master=self,borderwidth=0,bootstyle='light',autohide=True)
        self.project_contene.vscroll.config(bootstyle='warning-round')
        self.items = {
            'mediadef'  : MDFCollapsing(master=self.project_contene,screenzoom=self.sz,content=MediaDef()),
            'chartab'   : CTBCollapsing(master=self.project_contene,screenzoom=self.sz,content=CharTable(file_input = './toy/CharactorTable.tsv')),
            'rplgenlog' : RGLCollapsing(master=self.project_contene,screenzoom=self.sz,content=RplGenLog()),
        }
        # 放置
        self.update_item()
        self.project_contene.pack(fill='both',expand=True,side='top')
    def update_item(self):
        for idx,key in enumerate(self.items):
            fileitem:ttk.Button = self.items[key]
            fileitem.pack(fill='x',pady=0,side='top')
# 项目视图-可折叠类容器-基类
class FileCollapsing(ttk.Frame):
    def __init__(self,master,screenzoom:float,fileclass:str,content):
        self.sz = screenzoom
        SZ_5 = int(self.sz * 5)
        SZ_2 = int(self.sz * 2)
        super().__init__(master=master,borderwidth=0)
        self.class_text = {'mediadef':'媒体库','chartab':'角色配置','rplgenlog':'剧本文件'}[fileclass]
        self.collapbutton = ttk.Button(master=self,text=self.class_text,command=self.update_toggle,bootstyle='warning')
        self.content_frame = ttk.Frame(master=self)
        self.button_padding = (SZ_5,SZ_2,SZ_5,SZ_2)
        self.items = {}
        # self.update_item()
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
# 项目视图-可折叠类容器-媒体类
class MDFCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content):
        super().__init__(master, screenzoom, 'mediadef', content)
        self.items = {
            'Pos'       :   ttk.Button(master=self.content_frame,text='位置 (Pos)',bootstyle='light',padding=self.button_padding,compound='left'),
            'Animation' :   ttk.Button(master=self.content_frame,text='立绘 (Animation)',bootstyle='light',padding=self.button_padding,compound='left'),
            'Bubble'    :   ttk.Button(master=self.content_frame,text='气泡 (Bubble)',bootstyle='light',padding=self.button_padding,compound='left'),
            'Background':   ttk.Button(master=self.content_frame,text='背景 (Background)',bootstyle='light',padding=self.button_padding,compound='left'),
            'Audio'     :   ttk.Button(master=self.content_frame,text='音频 (Audio)',bootstyle='light',padding=self.button_padding,compound='left'),
        }
        self.update_item()
# 项目视图-可折叠类容器-角色类
class CTBCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:CharTable):
        super().__init__(master, screenzoom, 'chartab', content)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0)
        self.add_button.pack(side='right',padx=SZ_10,pady=SZ_5,ipady=SZ_1,ipadx=SZ_3)
        self.table = content.export()
        self.items = {}
        for name in self.table['Name'].unique():
            self.items[name] = ttk.Button(master=self.content_frame,text=name,bootstyle='light',padding=self.button_padding,compound='left')
        self.update_item()
# 项目视图-可折叠类容器-剧本类
class RGLCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:RplGenLog):
        super().__init__(master, screenzoom, 'rplgenlog', content)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0)
        self.add_button.pack(side='right',padx=SZ_10,pady=SZ_5,ipady=SZ_1,ipadx=SZ_3)
        self.items = {
            '1'     :   ttk.Button(master=self.content_frame,text='第1集',bootstyle='light',padding=self.button_padding,compound='left'),
            '2'     :   ttk.Button(master=self.content_frame,text='第2集',bootstyle='light',padding=self.button_padding,compound='left'),
            '3'     :   ttk.Button(master=self.content_frame,text='第3集',bootstyle='light',padding=self.button_padding,compound='left'),
        }
        self.update_item()
