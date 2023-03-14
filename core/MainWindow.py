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
        # 导航栏
        self.navigate_bar = NavigateBar(master=self,style='secondary',wide=False)
        self.navigate_bar.place(x=0,y=0,width=100,relheight=1)
        # event
        self.navigate_bar.bind('<ButtonRelease-1>', self.navigateBar_get_click)
        # 文字
        # 主要循环
        self.mainloop()
    def navigateBar_get_click(self,event):
        wide = not self.navigate_bar.wide
        self.navigate_bar.place_forget()
        self.navigate_bar = NavigateBar(master=self,style='secondary',wide=wide)
        self.navigate_bar.place(x=0,y=0,width={True:300,False:100}[wide],relheight=1)
        self.navigate_bar.bind('<ButtonRelease-1>', self.navigateBar_get_click)

class NavigateBar(ttk.Frame):
    def __init__(self,master,style,wide=False) -> None:
        super().__init__(master,borderwidth=10,bootstyle=style)
        icon_size = [70,70]
        self.wide = wide
        self.image = {
            'logo'      : ImageTk.PhotoImage(name='logo',   image=Image.open('./media/icon.png').resize(icon_size)),
            'setting'   : ImageTk.PhotoImage(name='setting',image=Image.open('./media/icon/setting.png').resize(icon_size)),
            'project'   : ImageTk.PhotoImage(name='project',image=Image.open('./media/icon/project.png').resize(icon_size)),
            'script'    : ImageTk.PhotoImage(name='script', image=Image.open('./media/icon/script.png').resize(icon_size)),
            'console'   : ImageTk.PhotoImage(name='console',image=Image.open('./media/icon/console.png').resize(icon_size)),
        }
        self.titles = {
            'logo'      : ttk.Button(master=self,image='logo', bootstyle='secondary-solid',padding=0),
            'set'       : ttk.Button(master=self,image ='setting', bootstyle='secondary-solid',padding=0)
        }
        self.buttons = {
            'project'   : ttk.Button(master=self,image='project', bootstyle='secondary-solid',padding=0),
            'script'    : ttk.Button(master=self,image='script', bootstyle='secondary-solid',padding=0),
            'console'   : ttk.Button(master=self,image='console', bootstyle='secondary-solid',padding=0),
        }
        # self.titles
        for idx,key in enumerate(self.titles.keys()):
            button = self.titles[key]
            button.place(width=80,height=80,x=0, y= idx*100)
        # ----------
        separator = ttk.Separator(master=self,orient='horizontal',bootstyle='light')
        separator.place(width=80,x=0,y= idx*100+100)
        y_this = idx*100 + 120
        # self.buttons
        for idx,key in enumerate(self.buttons.keys()):
            button = self.buttons[key]
            button.place(width=80,height=80,x=0, y= y_this + idx*100)



class ProjectView(ttk.Frame):
    pass

class ScriptView(ttk.Frame):
    pass

class ConsoleView(ttk.Frame):
    pass

class PreferenceView(ttk.Frame):
    pass