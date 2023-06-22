#!/usr/bin/env python
# coding: utf-8

# 图形界面的欢迎窗口，显示在主界面之前


import sys
import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk

class RplGenStudioWelcome(ttk.Window):
    # 初始化
    def __init__(self):
        # 获取尺寸
        self.get_screen()
        SZ_5 = int(self.sz * 6)
        window_width = int(800*self.sz) + 2 * SZ_5
        window_height = int(450*self.sz) + 2 * SZ_5
        # 窗口位置为居中
        x = int((self.screen_width/2) - (window_width/2))
        y = int((self.screen_height/2) - (window_height/2))
        # 初始化一个
        super().__init__(
            resizable           = (False,False),
            size                = (window_width, window_height),
            position            = (x, y),
            overrideredirect    = True,
        )
        # 画面
        self.image = ImageTk.PhotoImage(name='welcome',image=Image.open('./toy/toy_cover.jpg').resize([window_width-2*SZ_5,window_height-2*SZ_5]))
        self.image_show = ttk.Label(master=self,image='welcome',borderwidth=SZ_5,anchor='center',background='#963fff')
        self.image_show.pack(fill='both',expand=True)
        # 主循环
        self.after(4000, self.fade_out)
        self.mainloop()
    # 获取系统的缩放比例
    def get_screen(self)->float:
        if 'win32' in sys.platform:
            from ctypes import windll
            self.sz = windll.shcore.GetScaleFactorForDevice(0) / 100
            self.screen_width = int(windll.user32.GetSystemMetrics(0) * self.sz)
            self.screen_height = int(windll.user32.GetSystemMetrics(1) * self.sz)
        else:
            # macbook pro 13
            self.sz = 2.0
            self.screen_width = 2560
            self.screen_height = 1600
    # 关闭
    def fade_out(self):
        alpha = self.attributes('-alpha')
        if alpha > 0:
            alpha -= 0.02
            self.attributes('-alpha', alpha)
            self.after(20, self.fade_out)
        else:
            self.destroy()