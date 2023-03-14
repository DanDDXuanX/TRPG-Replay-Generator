#!/usr/bin/env python
# coding: utf-8

import sys

import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk

from .ProjConfig import Preference
from .Utils import EDITION

class RplGenStudioMainWindow(ttk.Window):
    def __init__(
            self,preference:Preference = Preference()
            )->None:
        super().__init__(
            title       = '回声工坊' + EDITION,
            themename   = 'litera',
            iconphoto   = './media/icon.png',
            size        = (1500,800),
            resizable   = (True,True),
        )
        # 样式
        self.style.configure('secondary.TButton',anchor='w',font="-family 微软雅黑 -size 20 -weight bold",compound='left',padding=(3,0,0,0))
        # 导航栏
        self.navigate_bar = NavigateBar(master=self)
        self.navigate_bar.place(x=0,y=0,width=100,relheight=1)
        # event
        self.navigate_bar.bind('<ButtonRelease-1>', self.navigateBar_get_click)
        # 视图
        self.view = {
            'project': ProjectView(master=self)
            }
        self.view_show('project')
    # 当导航栏被点击时
    def navigateBar_get_click(self,event):
        is_wide = not self.navigate_bar.is_wide
        navigate_bar_width = {True:220,False:100}[is_wide]
        self.navigate_bar.place_widgets(is_wide)
        self.navigate_bar.place_configure(width=navigate_bar_width)
        self.view[self.show].place_configure(x=navigate_bar_width,width=-navigate_bar_width)
    # 显示指定的视图
    def view_show(self,show:str):
        navigate_bar_width = {True:220,False:100}[self.navigate_bar.is_wide]
        self.view[show].place_forget()
        self.view[show].place(x=navigate_bar_width,y=0,relwidth=1,relheight=1,width=-navigate_bar_width)
        self.show = show

class NavigateBar(ttk.Frame):
    def __init__(self,master) -> None:
        super().__init__(master,borderwidth=10,bootstyle='secondary')
        icon_size = [70,70]
        self.master = master
        self.is_wide = False
        # 图形
        self.image = {
            'logo'      : ImageTk.PhotoImage(name='logo',   image=Image.open('./media/icon.png').resize(icon_size)),
            'setting'   : ImageTk.PhotoImage(name='setting',image=Image.open('./media/icon/setting.png').resize(icon_size)),
            'project'   : ImageTk.PhotoImage(name='project',image=Image.open('./media/icon/project.png').resize(icon_size)),
            'script'    : ImageTk.PhotoImage(name='script', image=Image.open('./media/icon/script.png').resize(icon_size)),
            'console'   : ImageTk.PhotoImage(name='console',image=Image.open('./media/icon/console.png').resize(icon_size)),
        }
        # 顶部
        self.titles = {
            'logo'      : ttk.Button(master=self,image='logo',bootstyle='secondary-solid'),
            'set'       : ttk.Button(master=self,image ='setting',text=' 首选项',command=lambda :self.press_button('setting'),bootstyle='secondary-solid',compound='left')
        } 
        # 分割线
        self.separator = ttk.Separator(master=self,orient='horizontal',bootstyle='light')
        # 按钮
        self.buttons = {
            'project'   : ttk.Button(master=self,image='project',text=' 项目',command=lambda :self.press_button('project'),bootstyle='secondary-solid',compound='left'),
            'script'    : ttk.Button(master=self,image='script',text=' 脚本',command=lambda :self.press_button('script'),bootstyle='secondary-solid',compound='left'),
            'console'   : ttk.Button(master=self,image='console',text=' 控制台',command=lambda :self.press_button('console'),bootstyle='secondary-solid',compound='left'),
        }
        # 高亮的线
        self.choice = ttk.Frame(master=self,bootstyle='primary')
        # self.titles
        self.place_widgets(self.is_wide)
    # 放置元件
    def place_widgets(self,is_wide:bool):
        self.is_wide = is_wide
        if is_wide:
            width = 200
        else:
            width = 80
        # self.titles
        for idx,key in enumerate(self.titles.keys()):
            button = self.titles[key]
            if len(button.place_info())==0:
                button.place(width=width,height=80,x=0,y=idx*100)
            else:
                button.place_configure(width=width)
        # ----------
        if len(self.separator.place_info()) == 0:
            self.separator.place(width=width,x=0,y= idx*100+100)
        else:
            self.separator.place_configure(width=width)
        y_this = idx*100 + 120
        # self.buttons
        for idx,key in enumerate(self.buttons.keys()):
            button = self.buttons[key]
            if len(button.place_info())==0:
                button.place(width=width,height=80,x=0, y= y_this + idx*100)
            else:
                button.place_configure(width=width)
    # 点击按键的绑定事件
    def press_button(self,botton):
        position = {'setting':100,'project':220,'script':320,'console':420}[botton]
        if len(self.choice.place_info()) == 0:
            self.choice.place(width=5,height=80,x=-5,y= position)
        else:
            self.choice.place_configure(y=position)
        self.master.view_show(botton)

# 项目视图
class ProjectView(ttk.Frame):
    def __init__(self,master)->None:
        super().__init__(master,borderwidth=0,bootstyle='light')
        self.file_manager  = FileManager(master=self)
        self.page_notebook = PageNotes(master=self)
        self.page_view     = ttk.Frame(master=self,bootstyle='secondary')
        self.file_manager.place(x=0,y=0,width=300,relheight=1)
        self.page_notebook.place(x=300,y=0,height=30,relwidth=1,width=-300)
        self.page_view.place(x=300,y=30,relheight=1,height=-30,relwidth=1,width=-300)

# 项目视图-文件管理器
class FileManager(ttk.Frame):
    def __init__(self,master)->None:
        super().__init__(master,borderwidth=0,bootstyle='primary')
        self.master = master
        # 图形
        self.image = {
            'title'     : ImageTk.PhotoImage(name='title',   image=Image.open('./toy/media/bg1.jpg').resize([300,180])),
            'save'      : ImageTk.PhotoImage(name='save' ,   image=Image.open('./media/icon/save.png').resize([30,30])),
            'config'    : ImageTk.PhotoImage(name='config',   image=Image.open('./media/icon/setting.png').resize([30,30])),
            'import'    : ImageTk.PhotoImage(name='import',   image=Image.open('./media/icon/import.png').resize([30,30])),
            'export'    : ImageTk.PhotoImage(name='export',   image=Image.open('./media/icon/export.png').resize([30,30])),
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
        self.project_contene = ttk.Frame(master=self,borderwidth=0,bootstyle='light')
        self.items = {
            'mediadef'  : ttk.Button(master=self.project_contene,text='媒体库',bootstyle='success-link'),
            'chartab'   : ttk.Button(master=self.project_contene,text='角色配置',bootstyle='success-link'),
            'rplgenlog' : ttk.Button(master=self.project_contene,text='剧本',bootstyle='success-link'),
        }
        # 放置
        self.update_item()
        self.project_contene.pack(fill='both',expand=True,side='top')
    def update_item(self):
        for idx,key in enumerate(self.items):
            fileitem:ttk.Button = self.items[key]
            fileitem.pack(fill='x',pady=3,side='top')
# 项目视图-页面标签
class PageNotes(ttk.Frame):
    def __init__(self,master)->None:
        super().__init__(master,borderwidth=0,bootstyle='light')
        self.master = master
        self.active_page = {
            '1': ttk.Button(master=self,text='媒体库',bootstyle='primary'),
            '2': ttk.Button(master=self,text='角色配置',bootstyle='primary'),
            '3': ttk.Button(master=self,text='剧本',bootstyle='primary'),
        }
        self.update_item()
    def update_item(self):
        for idx,key in enumerate(self.active_page):
            page_label:ttk.Button = self.active_page[key]
            page_label.pack(fill='y',padx=3,side='left',pady=0)
# 脚本视图
class ScriptView(ttk.Frame):
    pass
# 控制台视图
class ConsoleView(ttk.Frame):
    pass
# 首选项视图
class PreferenceView(ttk.Frame):
    pass