#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from PIL import Image, ImageTk
from .GUI_Util import FreeToolTip
from .GUI_Link import Link
from .ProjConfig import preference

# 空白的首页

class RecentProject(ttk.Button):
    def __init__(self,master,screenzoom,name,path,callback):
        # 缩放比例
        self.sz = screenzoom
        SZ_3 = int(self.sz * 3)
        SZ_20 = int(self.sz * 20)
        self.name = name
        self.path = path
        self.text = name+'\t'+path
        super().__init__(
            master,
            padding=(SZ_20,SZ_3,SZ_20,SZ_3),
            bootstyle='light',
            text=self.text,
            command=lambda:callback(self.path)
            )
        self.tooltip = FreeToolTip(
            widget=self,
            text=self.path,
            bootstyle='light-inverse',
            wraplength=3000,
            delay=1000
            )
class HomePageElements(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
        # 缩放比例
        self.sz = screenzoom
        SZ_150 = int(self.sz * 150)
        SZ_10 = int(self.sz * 10)
        icon_size = (SZ_150, SZ_150)
        super().__init__(master,borderwidth=0,bootstyle='light')
        # color
        self.font_color = {
            'rplgenlight'   : '#606060',
            'rplgendark'    : '#b0b0b0',
        }[preference.theme]
        # slogan
        self.slogan = ttk.Frame(master=self,padding=(SZ_10,SZ_10,SZ_10,0))
        self.labels = {
            'welcome' : ttk.Label(
                master=self.slogan,
                text='回声工坊',
                font=(Link['system_font_family'],30,'bold'),
                foreground=self.font_color
                ),
            # "Embrace your imagination, weave tales untold."
            'poetry'  : ttk.Label(
                master=self.slogan,
                text='点亮创作火花',
                font=(Link['system_font_family'],15),
                foreground=self.font_color
                )
        }
        # buttons
        self.buttons = ttk.Frame(master=self,padding=(SZ_10,0,SZ_10,0))
        self.image = {
            'open_p' : ImageTk.PhotoImage(name='open_p',  image=Image.open('./assets/icon/open.png').resize(icon_size)),
            'new_p'  : ImageTk.PhotoImage(name='new_p',   image=Image.open('./assets/icon/new.png').resize(icon_size)),
            'intel_p': ImageTk.PhotoImage(name='intel_p', image=Image.open('./assets/icon/intel.png').resize(icon_size)),
        }
        self.open_project_buttons = {
            'open_p' : ttk.Button(master=self.buttons, text='打开项目',     compound='top', image='open_p' ,bootstyle='info',command=self.master.open_project),
            'new_p'  : ttk.Button(master=self.buttons, text='新建空白项目', compound='top', image='new_p'  ,bootstyle='info',command=self.master.empty_project),
            'intel_p': ttk.Button(master=self.buttons, text='新建智能项目', compound='top', image='intel_p',bootstyle='info',command=self.master.intel_project),
        }
        self.tooltips = {
            'open_p' : FreeToolTip(widget=self.open_project_buttons['open_p'], text='从文件夹中打开一个现有的项目。',bootstyle='light-inverse'),
            'new_p'  : FreeToolTip(widget=self.open_project_buttons['new_p'], text='创建一个空白的项目，导入回声工坊1.0版本的工程文件，或者从头开始创建你的项目。',bootstyle='light-inverse',screenzoom=self.sz),
            'intel_p': FreeToolTip(widget=self.open_project_buttons['intel_p'], text='选择样式模板，智能解析导入聊天记录或者染色器log文件，直接创建一个半成品项目。',bootstyle='light-inverse',screenzoom=self.sz),
        }
        # 最近的项目
        self.recent_project = ttk.Frame(master=self,padding=(SZ_10,0,SZ_10,SZ_10*2))
        self.title = ttk.Label(
            master=self.recent_project,
            text='最近项目：',
            font=(Link['system_font_family'],15,'bold'),
            foreground=self.font_color
        )
        self.clear = ttk.Button(
            master=self.title,
            text='清除记录',
            bootstyle='secondary-link',
            command=self.clear_recent,
            padding=0
        )
        self.empty = ttk.Label(
            master=self.recent_project,
            text='无记录',
            font=(Link['system_font_family'],12),
            foreground=self.font_color,
            anchor='center'
        )
        self.recents = {}
        self.load_recent_project()
        # 显示
        self.update_items()
    def update_items(self):
        SZ_1 = int(self.sz *1)
        SZ_5 = int(self.sz * 5)
        SZ_10 = int(self.sz * 10)
        # slogan
        for keyword in self.labels:
            self.labels[keyword].pack(fill='x',expand=True,side='top',padx=SZ_10)
        # button
        for keyword in self.open_project_buttons:
            this_button:ttk.Button = self.open_project_buttons[keyword]
            this_button.pack(side='left', fill='both',expand=True,padx=SZ_10,pady=SZ_10)
        # recent
        self.title.pack(fill='x',side='top',pady=(0,SZ_5),padx=SZ_10)
        self.clear.place(relx=1,x=-6*SZ_10,rely=0.2,width=6*SZ_10,relheight=0.8)
        for keyword in self.recents:
            this_button:RecentProject = self.recents[keyword]
            this_button.pack(side='top', fill='x',expand=False,padx=SZ_10,pady=SZ_1)
        if len(self.recents) == 0: # 空白的时候，显示无记录
            self.empty.pack(side='top', fill='both',expand=True)
        # frame
        SZ_100 = int(self.sz * 100)
        self.slogan.place(relx=0,relwidth=1,y=0,height=SZ_100)
        self.buttons.place(relx=0,relwidth=1,y=SZ_100,relheight=1,height=-3*SZ_100)
        self.recent_project.place(relx=0,relwidth=1,y=-2*SZ_100,rely=1,height=2*SZ_100)
    def load_recent_project(self):
        list_of_project:list = Link['recent_files'][:5] # 前5个
        for i,text in enumerate(list_of_project):
            if text == '':
                continue
            name,path = text.split('\t')
            self.recents[i] = RecentProject(
                master=self.recent_project,
                screenzoom=self.sz,
                name=name,
                path=path,
                callback=self.master.open_project_file
                )
    def clear_recent(self):
        Link['recent_files'].clear()
        for keyword in self.recents:
            self.recents[keyword].destroy()
        self.empty.pack(side='top', fill='both',expand=True)