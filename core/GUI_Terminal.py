#!/usr/bin/env python
# coding: utf-8

# 终端

import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.toast import ToastNotification
from .ProjConfig import preference
from .Utils import EDITION
from .Exceptions import MainPrint
from .GUI_Link import Link
from .GUI_Language import tr
import tkinter as tk
import sys
import re

class ExportVideoProgressBar(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
        # 初始化
        self.sz = screenzoom
        SZ_10 = int(self.sz*10)
        super().__init__(master,borderwidth=0,padding=SZ_10,bootstyle='success')
        # 内容
        self.text = ttk.Label(
            master=self,
            text=' ',
            anchor='center',
            bootstyle='success-inverse',
            font=(Link['terminal_font_family'],16)
        )
        self.progress = ttk.Progressbar(master=self, maximum=1.0,value=0.0, bootstyle='primary-striped')
        # 正则
        self.regex = re.compile("\[(导出视频|export Video)\]: (.+?) ([\d\.]+)% (\d+)/(\d+) etr: ([\d\:]+)")
        # 显示
        self.update_item()
    def update_item(self):
        self.text.pack(side='top',fill='x',expand=True)
        self.progress.pack(side='top',fill='x',expand=True)
    def update_value(self, string):
        m = self.regex.fullmatch(string)
        if m:
            self.progress.configure(value = float(m.group(3))/100)
            self.text.configure(text = f'进度：{m.group(4)}/{m.group(5)}({m.group(3)}%)  剩余时间：{m.group(6)}')
    def clear_value(self):
        self.progress.configure(value = 0)
        self.text.configure(text = ' ')

class StdoutRedirector:
    def __init__(self, text_widget, master):
        self.master = master
        self.text_widget:ttk.Text = text_widget
        # colortag
        self.text_widget.tag_configure('normal',foreground='#ffffff')
        self.text_widget.tag_configure('error',foreground='#ff4444')
        self.text_widget.tag_configure('warning',foreground='#ff9944')
        self.text_widget.tag_configure('info',foreground='#44ff44')
        self.text_widget.tag_configure('black',foreground='#000000')
        # 返回标记
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
        # 检查string到底有没有东西
        if string == '':
            return
        # 检查是不是导出视频进度条
        if '━' in string:
            self.master.update_progressbar(string)
            return
        elif string == '\r':
            return
        else:
            self.master.clear_progressbar()
        # 第一件事：把光标移动到末尾
        self.text_widget.see('end')
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
            font=(Link['terminal_font_family'],preference.terminal_fontsize),
            autohide=True
            )
        self.terminal._text.configure(padx=2*SZ_10)
        self.control = ttk.Button(master=self,style='terminal.TButton',text=tr('终止'),command=self.send_terminate,state='disable')
        self.progressbar = ExportVideoProgressBar(master=self,screenzoom=self.sz)
        self.show_bar = False
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
    # 进度条
    def update_progressbar(self,string):
        SZ_40 = (self.sz * 40)
        SZ_5 = int(self.sz * 5)
        if not self.show_bar:
            self.show_bar = True
            self.progressbar.place(x=SZ_5,y=-SZ_40,height=2*SZ_40,width=-2*SZ_5,rely=0.45,relwidth=1)
        self.progressbar.update_value(string=string)
    def clear_progressbar(self):
        if self.show_bar:
            self.show_bar = False
            self.progressbar.place_forget()
            self.progressbar.clear_value()
    # 发送终止消息
    def send_terminate(self):
        self.clear_progressbar()
        if Link['pipeline']:
            Link['pipeline'].terminate()
            self.after(300,self.check_terminate)
    def check_terminate(self):
        # 等待退出
        if Link['runing_thread'].is_alive():
            self.after(1000,self.check_terminate)
        else:
            # 消息
            ToastNotification(title='终止流程',message='已手动终止流程！',duration=3000).show_toast()
    def bind_stdout(self):
        sys.stdout = StdoutRedirector(text_widget=self.terminal._text,master=self)
        # 欢迎
        print(MainPrint('Welcome',EDITION))
