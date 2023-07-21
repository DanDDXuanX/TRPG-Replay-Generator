#!/usr/bin/env python
# coding: utf-8

# 终端

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.dialogs import Messagebox
from PIL import Image, ImageTk
from .Utils import EDITION
from .Exceptions import MainPrint
from .GUI_Link import Link
import tkinter as tk
import sys
import re


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget:ttk.Text = text_widget
        # colortag
        self.text_widget.tag_configure('normal',foreground='#ffffff')
        self.text_widget.tag_configure('error',foreground='#ff4444')
        self.text_widget.tag_configure('warning',foreground='#ff9944')
        self.text_widget.tag_configure('info',foreground='#44ff44')
        self.text_widget.tag_configure('black',foreground='#000000')
        # 返回标记
        self.return_begin = False
        # from terminal output to colortag
        self.colortag = {
            '0' :'normal',
            '33':'warning',
            '32':'info',
            '31':'error',
            '30':'black'
        }
        # regex
        self.RE_cp = re.compile(r"(\x1B\[\d{1,2}m)")
    def write(self, string):
        # 第一件事：把光标移动到末尾
        self.text_widget.see('end')
        # 如果是返回标记
        if self.return_begin == True:
            line_this = self.text_widget.index('insert').split('.')[0]
            self.text_widget.delete(f"{line_this}.0", "end") # 删除前一行
            self.text_widget.insert(f"{line_this}.0", '\n') # 插入一个空行
            self.return_begin = False # 删除一次，置空
        # 构建index->color的字典
        color_index=[]
        color_tag = []
        start_index = self.text_widget.index('insert')
        color_index.append(start_index)
        color_tag.append('normal')
        for clip in self.RE_cp.split(string):
            if clip == '':
                continue
            elif clip[0] == '\x1B':
                tag = clip[2:-1]
                this_index = self.text_widget.index('insert')
                color_index.append(this_index)
                color_tag.append(self.colortag[tag])
            else:
                self.text_widget.insert('end', clip)
        # 更新颜色显示
        for idx, tag in enumerate(color_tag):
            start = color_index[idx]
            try:
                end = color_index[idx+1]
            except IndexError:
                end = 'end'
            self.text_widget.tag_add(tag,start,end)
        # 如果是返回开头，做好标记
        if string[-1] == '\r':
            self.return_begin = True
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
        self.terminal = ScrolledText(
            master=self,
            bootstyle='dark-round',
            background='#333333',
            foreground='#eeeeee',
            insertbackground='#eeeeee',
            autostyle=False,
            font=('Sarasa Mono SC',14),
            autohide=True
            )
        self.terminal._text.configure(padx=2*SZ_10)
        self.control = ttk.Button(master=self,style='terminal.TButton',text='终止',command=self.send_terminate,state='disable')
        # Link
        Link['terminal_control'] = self.control
        # 测试
        self.bind_stdout()
        self.update_item()
    def update_item(self):
        SZ_50 = int(self.sz * 50)
        SZ_5 = int(self.sz * 5)
        self.terminal.place(relx=0,y=0,relwidth=1,relheight=1,height=-SZ_50-SZ_5)
        self.control.place(relx=0.3,y=-SZ_50,rely=1,height=SZ_50,relwidth=0.4)
    # 发送终止消息
    def send_terminate(self):
        if Link['pipeline']:
            Link['pipeline'].terminate()
            self.after(300,self.check_terminate)
    def check_terminate(self):
        # 等待退出
        Link['runing_thread'].join()
        # 消息
        Messagebox().show_info(message=f'已手动终止流程',title='终止操作',parent=self)
    def bind_stdout(self):
        # sys.stdout = StdoutRedirector(text_widget=self.terminal._text)
        # 欢迎
        print(MainPrint('Welcome',EDITION))
