#!/usr/bin/env python
# coding: utf-8

import sys

import tkinter
import ttkbootstrap as ttk

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
            # position,
            # minsize,
            # maxsize,
            resizable   = (True,True),
            # hdpi,
            # scaling,
            # transient,
            # overrideredirect,
            alpha=1)
        self.style.configure("TFrame", foreground="black", background="gray")
        # 导航栏
        self.navigate_bar = NavigateBar(master=self,style='TFrame')
        self.navigate_bar.pack(fill=tkinter.Y,expand=True,anchor='w')
        # 文字
        # 主要循环
        self.mainloop()

class NavigateBar(ttk.Frame):
    def __init__(self,master,style) -> None:
        super().__init__(master,padding=(10,10,10,0),style=style,width=100)