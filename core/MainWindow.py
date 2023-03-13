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
        self.root = ttk.Frame(master=self,style='TFrame',borderwidth=3)
        self.root.pack(fill=tkinter.BOTH)
        # 导航栏
        self.navigate_bar = NavigateBar(master=self.root,style='TFrame')
        self.navigate_bar.pack(fill=tkinter.Y,expand=True)
        # 文字
        title = ttk.Label(master=self.root, text="litera", font="-size 24 -weight bold")
        title.pack(side=tkinter.LEFT)
        # 主要循环
        self.mainloop()

class NavigateBar(ttk.Frame):
    def __init__(self,master,style) -> None:
        super().__init__(master,padding=(10,10,10,0),style=style)