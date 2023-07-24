#!/usr/bin/env python
# coding: utf-8

# 图形界面的欢迎窗口，显示在主界面之前


import sys
import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk

class RplGenStudioWelcome(ttk.Window):
    # 初始化
    def __init__(self, mulitproc_connect):
        # 获取尺寸
        self.get_screen()
        border = int(self.sz * 0)
        window_width = int(800*self.sz) + 2 * border
        window_height = int(450*self.sz) + 2 * border
        # 多进程的信号
        self.pipe = mulitproc_connect
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
        self.image = ImageTk.PhotoImage(name='welcome',image=Image.open('./media/cover.jpg').resize([window_width-2*border,window_height-2*border]))
        self.image_show = ttk.Label(master=self,image='welcome',borderwidth=border,anchor='center',background='#963fff')
        self.image_show.pack(fill='both',expand=True)
        # 主循环
        self.attributes('-alpha', 0)
        self.fade_in()
        self.mainloop()
    # 获取系统的缩放比例
    def get_screen(self)->float:
        if 'win32' in sys.platform:
            try:
                from ctypes import windll
                self.sz = windll.shcore.GetScaleFactorForDevice(0) / 100
                self.screen_width = int(windll.user32.GetSystemMetrics(0) * self.sz)
                self.screen_height = int(windll.user32.GetSystemMetrics(1) * self.sz)
            except Exception:
                self.sz = 1
                self.screen_width = 1920
                self.screen_height = 1080
        else:
            # macbook pro 13
            self.sz = 2.0
            self.screen_width = 2560
            self.screen_height = 1600
    # 关闭
    def fade_out(self):
        alpha = self.attributes('-alpha')
        if alpha > 0:
            alpha -= 0.04
            self.attributes('-alpha', alpha)
            self.after(20, self.fade_out)
        else:
            self.destroy()
    # 开启
    def fade_in(self):
        alpha = self.attributes('-alpha')
        if alpha < 1:
            alpha += 0.04
            self.attributes('-alpha', alpha)
            self.after(20, self.fade_in)
        else:
            self.check_pipe()
    # 检查信号
    def check_pipe(self):
        # 如果接收到了信号
        if self.pipe.poll():
            msg = self.pipe.recv()
            if msg == 'terminate':
                # 淡出
                self.fade_out()
        self.after(100, self.check_pipe)