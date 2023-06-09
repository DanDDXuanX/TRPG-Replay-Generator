#!/usr/bin/env python
# coding: utf-8

# 终端

import ttkbootstrap as ttk
import tkinter.font as tkFont
from ttkbootstrap.scrolled import ScrolledText
from PIL import Image, ImageTk
from .Utils import EDITION
from .Exceptions import MainPrint
import tkinter as tk
import sys
import re


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget:ttk.Text = text_widget
        # colortag
        self.text_widget.tag_configure('error',foreground='#ff4444')
        self.text_widget.tag_configure('warning',foreground='#ff9944')
        self.text_widget.tag_configure('info',foreground='#44ff44')
        self.text_widget.tag_configure('black',foreground='#000000')
        # from terminal output to colortag
        self.colortag = {
            '33':'warning',
            '32':'info',
            '31':'error',
            '30':'black'
        }
        # regex
        self.RE_cp = re.compile(r"(\x1B\[\d+m.+\x1B\[0m)")
        self.RE_cp_get = re.compile(r"\x1B\[(\d+)m(.+)\x1B\[0m")
    def write(self, string):
        for clip in self.RE_cp.split(string):
            if clip == '':
                continue
            elif clip[0] == '\x1B':
                tag,text = self.RE_cp_get.findall(clip)[0]
                self.text_widget.insert('end', text, self.colortag[tag])
            else:
                self.text_widget.insert('end', clip)
        self.text_widget.see('end')
    def flush(self):
        pass

class Terminal(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
        # 初始化
        self.sz = screenzoom
        SZ_10 = int(self.sz*10)
        super().__init__(master,borderwidth=0,padding=SZ_10)
        # 子原件
        self.font = tkFont.Font(family='./media/YaHei Consolas Hybrid 1.12.ttf',size=14)
        self.terminal = ScrolledText(
            master=self,
            bootstyle='dark-round',
            background='#333333',
            foreground='#eeeeee',
            insertbackground='#eeeeee',
            autostyle=False,
            font=self.font,
            autohide=True
            )
        self.terminal._text.configure(padx=2*SZ_10,font=self.font)
        # self.control = ttk.Button(master=self,style='terminal.TButton',text='终止')
        self.control = ttk.Button(master=self,style='terminal.TButton',text='终止')
        # 测试
        self.bind_stdout()
        self.update_item()
    def update_item(self):
        SZ_50 = int(self.sz * 50)
        SZ_5 = int(self.sz * 5)
        self.terminal.place(relx=0,y=0,relwidth=1,relheight=1,height=-SZ_50-SZ_5)
        self.control.place(relx=0.3,y=-SZ_50,rely=1,height=SZ_50,relwidth=0.4)
    def bind_stdout(self):
        sys.stdout = StdoutRedirector(text_widget=self.terminal._text)
        # 欢迎
        print(MainPrint('Welcome',EDITION))

class Texture(tk.Frame):
    def __init__(self,master,screenzoom):
        super().__init__(master=master)
        # Label对象
        self.canvas = ttk.Label(master=self,padding=0)
        # 纹理图片
        self.texture = Image.open('./media/icon/texture4.png')
        self.bind('<Configure>', self.update_image)
        self.update_image(None)
        self.update_item()
    def update_item(self):
        self.canvas.pack(fill='both', expand=True)
    def update_image(self, event):
        self.image = ImageTk.PhotoImage(self.fill_texture(self.winfo_width(),self.winfo_height()))
        self.canvas.config(image=self.image)
    def fill_texture(self,width,height):
        new_image = Image.new('RGB',(width,height))
        for x in range(0, width, self.texture.width):
            for y in range(0, height, self.texture.height):
                new_image.paste(self.texture, (x, y))
        return new_image