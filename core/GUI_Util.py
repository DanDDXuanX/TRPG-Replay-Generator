#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
import tkinter as tk
from PIL import Image, ImageTk

# 公用小元件
# 包含：最小键值对

# 加上值的映射关系的Combobox\
class DictCombobox(ttk.Combobox):
    def __init__(self, master,textvariable,**kw):
        self.dictionary = {}
        # 实际的值
        self.var = textvariable
        # 显示的
        self.text = tk.StringVar(master=master,value=self.var.get())
        # 初始化
        super().__init__(master, textvariable=self.text, **kw)
        self.bind('<<ComboboxSelected>>', self.update_var)
    def update_dict(self, dict:dict):
        # 显示的内容：实际的内容
        self.dictionary = dict
        self.configure(values=list(self.dictionary.keys()))
        # 修改目前text
        keys = [key for key,value in self.dictionary.items() if tk.StringVar(value=value).get() == self.text.get()]
        if len(keys) > 0:
            self.text.set(keys[0])
    def update_var(self, event):
        text = self.text.get()
        if text in self.dictionary:
            self.var.set(self.dictionary[text])
        else:
            self.var.set(text)
        print(self.var.get())


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
            self.input = DictCombobox(master=self,textvariable=self.value,width=30)
        elif value['style'] == 'label':
            self.input = ttk.Label(master=self,textvariable=self.value,width=30)
        else:
            self.input = ttk.Label(master=self,textvariable=self.value,width=30)
        # 描述
        if describe['type'] == 'label':
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
# 文本分割线，包含若干个KVD，可以折叠
class TextSeparator(ttk.Frame):
    def __init__(self,master,screenzoom:float,describe:dict):
        self.sz = screenzoom
        super().__init__(master=master)
        # 标题栏
        self.title = ttk.Frame(master=self)
        ## 文字：
        self.label = ttk.Label(master=self.title,text=describe,style='dialog.TLabel')
        self.label.bind("<Button-1>",self.update_toggle)
        ## 分割线
        self.sep = ttk.Separator(
                    master=self.title,
                    orient='horizontal',
                    bootstyle='primary'
                    )
        # 容器
        self.content = {}
        self.content_index = []
        self.content_frame = ttk.Frame(master=self)
        # 显示
        self.update_item()
    # 刷新显示
    def update_item(self):
        # 是否扩展
        self.update_title()
        self.expand = True
        self.title.pack(fill='x',side='top')
        self.content_frame.pack(fill='x',side='top')
    # 放置标题
    def update_title(self):
        self.label.pack(fill='x',side='top',expand=True)
        self.sep.pack(fill='x',side='top',expand=True)
    # 切换收缩
    def update_toggle(self,event):
        if self.expand:
            self.content_frame.pack_forget()
            self.expand:bool = False
        else:
            self.content_frame.pack(fill='x',side='top')
            self.expand:bool = True
    # 添加KVD
    def add_element(self,key:str,value:str,kvd:dict)->KeyValueDescribe:
        SZ_5 = int(self.sz * 5)
        this_kvd = KeyValueDescribe(
            master = self.content_frame,
            screenzoom = self.sz,
            key=kvd['ktext'],
            value={
                'type':kvd['vtype'],
                'style':kvd['vitem'],
                'value':value},
            describe={
                'type':kvd['ditem'],
                'text':kvd['dtext']
            }
        )
        self.content_index.append(key)
        self.content[key] = this_kvd
        # 摆放
        this_kvd.pack(side='top',anchor='n',fill='x',pady=(SZ_5,0))
        return this_kvd
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