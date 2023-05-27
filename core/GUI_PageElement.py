#!/usr/bin/env python
# coding: utf-8

# 页面的其他公用元件
# 包含：搜索栏、输出命令按钮

import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from core.GUI_Container import Container

# 搜索窗口
class SearchBar(ttk.Frame):
    def __init__(self,master,container:Container,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=int(5*self.sz),bootstyle='light')
        # 关联容器
        self.container = container
        # 元件
        self.search_text = tk.StringVar(master=self,value='')
        self.is_regex = tk.BooleanVar(master=self,value=False)
        self.left = {
            'entry' : ttk.Entry(master=self,width=30,textvariable=self.search_text),
            'regex' : ttk.Checkbutton(master=self,text='正则',variable=self.is_regex),
            'search' : ttk.Button(master=self,text='搜索',command=self.click_search,bootstyle='primary')
        }
        self.right = {
            'clear' : ttk.Button(master=self,text='清除',command=self.click_clear),
            'info'  : ttk.Label(master=self,text='(无)'),
        }
        self.update_item()
    def update_item(self):
        SZ_10 = int(self.sz * 10)
        for key in self.left:
            item:ttk.Button = self.left[key]
            item.pack(padx=SZ_10, fill='y',side='left')
        for key in self.right:
            item:ttk.Button = self.right[key]
            item.pack(padx=SZ_10, fill='y',side='right')
    def click_search(self):
        if self.is_regex.get():
            self.right['info'].config(text = '正则搜索：'+self.search_text.get())
        else:
            self.right['info'].config(text = '搜索：'+self.search_text.get())
        # 搜索与显示过滤
        self.container.search(to_search=self.search_text.get(),regex=self.is_regex.get())
    def click_clear(self):
        self.right['info'].config(text = '(无)')
        self.container.search(to_search='')
# 输出指令
class OutPutCommand(ttk.Frame):
    def __init__(self,master,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        icon_size = [int(30*self.sz),int(30*self.sz)]
        self.image = {
            'display'   : ImageTk.PhotoImage(name='display',image=Image.open('./media/icon/display.png').resize(icon_size)),
            'exportpr'    : ImageTk.PhotoImage(name='exportpr', image=Image.open('./media/icon/premiere.png').resize(icon_size)),
            'recode'   : ImageTk.PhotoImage(name='recode',image=Image.open('./media/icon/ffmpeg.png').resize(icon_size)),
        }
        self.buttons = {
            'display' : ttk.Button(master=self,image='display',text='播放预览',compound='left',style='output.TButton'),
            'export'  : ttk.Button(master=self,image='exportpr',text='导出PR工程',compound='left',style='output.TButton'),
            'recode'  : ttk.Button(master=self,image='recode',text='导出视频',compound='left',style='output.TButton'),
        }
        self.update_item()
        
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='left',expand=True,pady=0)

