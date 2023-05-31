#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
import tkinter as tk
from PIL import Image, ImageTk

# 公用小元件
# 包含：最小键值对

# 一个键、值、描述的最小单位。
class KeyValueDescribe(ttk.Frame):
    def __init__(self,master,screenzoom:float,key:str,value:dict,describe:dict):
        self.sz = screenzoom
        super().__init__(master=master)
        SZ_5 = int(self.sz * 5)
        padding = (0,SZ_5,0,SZ_5)
        # 数值类型
        if value['type'] == 'int':
            self.value = tk.IntVar(master=self,value=value['value'])
        elif value['type'] == 'float':
            self.value = tk.DoubleVar(master=self,value=value['value'])
        elif value['type'] == 'bool':
            self.value = tk.BooleanVar(master=self,value=value['value'])
        elif value['type'] == 'str':
            self.value = tk.StringVar(master=self,value=value['value'])
        else:
            self.value = tk.StringVar(master=self,value=value['value'])
        # 关键字
        self.key = ttk.Label(master=self,text=key,width=8,anchor='e',padding=padding)
        # 容器
        if value['style'] == 'entry':
            self.input = ttk.Entry(master=self,textvariable=self.value,width=30)
        elif value['style'] == 'spine':
            self.input = ttk.Spinbox(master=self,textvariable=self.value,width=30)
        elif value['style'] == 'combox':
            self.input = ttk.Combobox(master=self,textvariable=self.value,width=30)
        elif value['style'] == 'label':
            self.input = ttk.Label(master=self,textvariable=self.value,width=30)
        else:
            self.input = ttk.Label(master=self,textvariable=self.value,width=30)
        # 描述
        if describe['type'] == 'text':
            self.describe = ttk.Label(master=self,text=describe['text'],width=8,anchor='center',padding=padding)
        elif describe['type'] == 'button':
            self.describe = ttk.Button(master=self,text=describe['text'],width=8,padding=padding)
        else:
            self.describe = ttk.Label(master=self,text=describe['text'],width=8,anchor='center',padding=padding)
        # 显示
        self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * 5)
        # 放置
        self.key.pack(fill='none',side='left',padx=SZ_5)
        self.input.pack(fill='x',side='left',padx=SZ_5,expand=True)
        self.describe.pack(fill='none',side='left',padx=SZ_5)
    def get(self):
        return self.value.get()
    
class TextSeparator(ttk.Frame):
    def __init__(self,master,screenzoom:float,describe:dict):
        self.sz = screenzoom
        super().__init__(master=master)
        # 文字：
        self.label = ttk.Label(master=self,text=describe,style='dialog.TLabel')
        # 分割线
        self.sep = ttk.Separator(
                    master=self,
                    orient='horizontal',
                    bootstyle='primary'
                    )
        # 显示
        self.update_item()
    def update_item(self):
        # 放置
        self.label.pack(fill='x',side='top',expand=True)
        self.sep.pack(fill='x',side='top',expand=True)

# 将一个图片处理为指定的icon大小（方形）
def thumbnail(image:Image.Image,icon_size:int)->Image.Image:
    origin_w,origin_h = image.size
    if origin_w > origin_h:
        icon_width = icon_size
        icon_height = int(origin_h/origin_w * icon_size)
    else:
        icon_height = icon_size
        icon_width = int(origin_w/origin_h * icon_size)
    return image.resize([icon_width,icon_height])