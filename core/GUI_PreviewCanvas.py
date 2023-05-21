#!/usr/bin/env python
# coding: utf-8

import tkinter as tk
import ttkbootstrap as ttk
import pygame
from PIL import Image, ImageTk

from .ScriptParser import MediaDef, CharTable
from .Medias import MediaObj, Animation, Bubble, ChatWindow

# 预览画布

# 预览窗
class PreviewCanvas(ttk.LabelFrame):
    def __init__(self,master,screenzoom,mediadef):
        # 基类初始化
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='预览窗')
        self.canvas_zoom = tk.DoubleVar(master=self,value=0.4)
        self.canvas_size = (1920,1080)
        # 媒体定义
        self.mediadef:MediaDef = mediadef
        # 元件
        self.items = {
            'canvas': ttk.Label(master=self,image=None,style='preview.TLabel'),
            'zoomlb': ttk.Label(master=self,text='缩放'),
            'zoomcb': ttk.Spinbox(master=self,from_=0.1,to=1.0,increment=0.01,textvariable=self.canvas_zoom,width=5,command=self.update_canvas),
        }
        self.items['zoomcb'].bind('<Return>',lambda event:self.update_canvas())
        # 预览图像
        self.empty_canvas = pygame.image.load('./media/canvas.png')
        self.canvas = pygame.Surface(size=self.canvas_size)
        self.canvas.blit(self.empty_canvas,(0,0))
        # 更新
        self.update_canvas()
        self.update_item()
        # 测试：预览
        # self.preview('气泡主文本')
    # 更新组件
    def update_item(self):
        SZ_40 = int(self.sz * 40)
        SZ_60 = int(self.sz * 60)
        SZ_5 = int(self.sz * 5)
        self.items['canvas'].place(x=0,y=0,relwidth=1,relheight=1,height=-SZ_40-SZ_5)
        self.items['zoomlb'].place(x=0,y=-SZ_40,rely=1,width=SZ_60,height=SZ_40)
        self.items['zoomcb'].place(x=SZ_60,y=-SZ_40,rely=1,width=SZ_60,height=SZ_40)
    # 更新画布
    def update_canvas(self):
        pil_canvas_iamge = Image.frombytes(mode='RGB',data=pygame.image.tostring(self.canvas,'RGB'),size=self.canvas_size)
        self.image = ImageTk.PhotoImage(
            image=pil_canvas_iamge.resize([
                int(self.canvas_size[0]*self.canvas_zoom.get()),
                int(self.canvas_size[1]*self.canvas_zoom.get()),
                ]),
            )
        self.items['canvas'].config(image=self.image)
    # 更新预览
    def get_media(self,media_name)->MediaObj:
        if media_name not in self.mediadef.struct.keys() or media_name == 'NA':
            return None
        else:
            object_dict_this = self.mediadef.struct[media_name]
            object_this:MediaObj = self.mediadef.instance_execute(object_dict_this)
            return object_this
    def preview(self):
        # 重置背景
        self.canvas.blit(self.empty_canvas,(0,0))
        
class MDFPreviewCanvas(PreviewCanvas):
    def preview(self, media_name:str):
        super().preview()
        object_this = self.get_media(media_name)
        if object_this:
            object_this.preview(self.canvas)
        self.update_canvas()

class CTBPreviewCanvas(PreviewCanvas):
    def __init__(self, master, screenzoom, chartab, mediadef):
        self.chartab:CharTable = chartab
        super().__init__(master, screenzoom, mediadef)
    def preview(self, char_name:str):
        super().preview()
        if char_name not in self.chartab.struct.keys():
            # TODO: Exception
            print(char_name)
        else:
            char_dict_this = self.chartab.struct[char_name]
            animation_this:Animation = self.get_media(char_dict_this['Animation'])
            # bubble
            bubble_name = char_dict_this['Bubble']
            if ':' in bubble_name:
                bubble_this:ChatWindow = self.get_media(bubble_name.split(':')[0])
                key = bubble_name.split(':')[1]
            else:
                bubble_this:Bubble = self.get_media(bubble_name)
                key = None
        # update canvas # TODO：check zorder!
        if animation_this:
            animation_this.preview(self.canvas)
        if bubble_this:
            bubble_this.preview(self.canvas, key=key)
        self.update_canvas()
