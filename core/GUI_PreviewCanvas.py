#!/usr/bin/env python
# coding: utf-8

import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk

# 预览画布

# 预览窗
class PreviewCanvas(ttk.LabelFrame):
    def __init__(self,master,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='预览窗')
        # 预览图像
        self.canvas = Image.open('./toy/media/bg2.jpg')
        self.canvas_zoom = tk.DoubleVar(master=self,value=0.4)
        self.image = ImageTk.PhotoImage(
            image=self.canvas.resize([
                int(self.canvas.size[0]*self.canvas_zoom.get()),
                int(self.canvas.size[1]*self.canvas_zoom.get()),
                ]),
            )
        # 元件
        self.items = {
            'canvas': ttk.Label(master=self,image=self.image,style='preview.TLabel'),
            'zoomlb': ttk.Label(master=self,text='缩放'),
            'zoomcb': ttk.Spinbox(master=self,from_=0.1,to=1.0,increment=0.01,textvariable=self.canvas_zoom,width=5,command=self.update_zoom),
        }
        self.items['zoomcb'].bind('<Return>',lambda event:self.update_zoom())
        self.update_item()
    def update_item(self):
        SZ_40 = int(self.sz * 40)
        SZ_60 = int(self.sz * 60)
        SZ_5 = int(self.sz * 5)
        self.items['canvas'].place(x=0,y=0,relwidth=1,relheight=1,height=-SZ_40-SZ_5)
        self.items['zoomlb'].place(x=0,y=-SZ_40,rely=1,width=SZ_60,height=SZ_40)
        self.items['zoomcb'].place(x=SZ_60,y=-SZ_40,rely=1,width=SZ_60,height=SZ_40)
    def update_zoom(self):
        self.image = ImageTk.PhotoImage(
            image=self.canvas.resize([
                int(self.canvas.size[0]*self.canvas_zoom.get()),
                int(self.canvas.size[1]*self.canvas_zoom.get()),
                ]),
            )
        self.items['canvas'].config(image=self.image)