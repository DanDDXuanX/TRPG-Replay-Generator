#!/usr/bin/env python
# coding: utf-8

import tkinter as tk
import ttkbootstrap as ttk
import pygame
from PIL import Image, ImageTk

from .ScriptParser import MediaDef, CharTable, RplGenLog
from .Medias import MediaObj, Animation, Bubble, ChatWindow, Balloon, Background

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
        if media_name in ['black', 'white']:
            return Background(media_name)
        elif media_name not in self.mediadef.struct.keys() or media_name == 'NA':
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

class RGLPreviewCanvas(PreviewCanvas):
    def __init__(self, master, screenzoom,rplgenlog, chartab, mediadef):
        self.rplgenlog:RplGenLog = rplgenlog
        self.chartab:CharTable = chartab
        super().__init__(master, screenzoom, mediadef)
    def get_background(self, line_index:str)->Background:
        index_this = int(line_index)
        while index_this > 0:
            section_this = self.rplgenlog.struct[str(index_this)]
            if section_this['type'] == 'background':
                return self.get_media(section_this['object'])
            else:
                index_this = index_this -1
        else:
            return Background('black')
    def get_header(self, this_bb_obj:Bubble, this_charactor_config:dict, key=None)->str:
        # 头文本
        try:
            if type(this_bb_obj) is ChatWindow:
                # ChatWindow 类：只有一个头文本，头文本不能包含|和#，还需要附上key
                targets:str = this_bb_obj.sub_Bubble[key].target
                # 获取target的文本内容
                if ('|' in this_charactor_config[targets]) | ('#' in this_charactor_config[targets]):
                    # 如果包含了非法字符：| #
                    raise ValueError('inv symbol')
                else:
                    target_text = key+'#'+this_charactor_config[targets]
            elif type(this_bb_obj) is Balloon:
                # Balloon 类：有若干个头文本，targets是一个list,用 | 分隔
                targets:list = this_bb_obj.target
                target_text = []
                for target in targets:
                    target_text.append(this_charactor_config[target])
                target_text = '|'.join(target_text)
            else: # Bubble,DynamicBubble类：只有一个头文本
                targets:str = this_bb_obj.target
                target_text = this_charactor_config[targets]
        except Exception as E:
            target_text = 'Error'
        return target_text
    def preview(self, line_index:str):
        super().preview()
        if line_index not in self.rplgenlog.struct.keys():
            # TODO: Exception
            print(line_index)
        else:
            section_dict_this = self.rplgenlog.struct[line_index]
            # 不预览的行
            if section_dict_this['type'] in ['blank','comment','set','table','music','clear','wait']:
                pass
            elif section_dict_this['type'] == 'background':
                self.get_media(section_dict_this['object']).preview(self.canvas)
            elif section_dict_this['type'] == 'animation':
                self.get_background(line_index).preview(self.canvas) # 背景
                am_obj = section_dict_this['object']
                if am_obj is None:
                    pass
                elif type(am_obj) is dict:
                    for idx in am_obj.keys():
                        self.get_media(am_obj[idx]).preview(self.canvas)
                else:
                    self.get_media(am_obj).preview(self.canvas)
            elif section_dict_this['type'] == 'bubble':
                self.get_background(line_index).preview(self.canvas) # 背景
                bb_obj = section_dict_this['object']
                if bb_obj is None:
                    pass
                else:
                    main_text = bb_obj['main_text']
                    header_text = bb_obj['header_text']
                    bubble_obj:Bubble = self.get_media(am_obj[idx])
                    bubble_obj.display(surface=self.canvas, text=main_text, header=header_text)
            elif section_dict_this['type'] in ['hitpoint','dice']:
                # TODO
                pass
            elif section_dict_this['type'] == 'move':
                # TODO
                pass
            elif section_dict_this['type'] == 'dialog':
                self.get_background(line_index).preview(self.canvas) # 背景
                char_set:dict = section_dict_this['charactor_set']
                main_text = section_dict_this['content']
                # 角色
                main_char = char_set['0']
                main_char_dict = self.chartab.struct[main_char['name']+'.'+main_char['subtype']]
                # 气泡
                if ':' in main_char_dict['Bubble']:
                    bubble_this:ChatWindow = self.get_media(main_char_dict['Bubble'].split(':')[0])
                    cw_key = main_char_dict['Bubble'].split(':')[1]
                else:
                    bubble_this:Bubble = self.get_media(main_char_dict['Bubble'])
                    cw_key = None
                header_text = self.get_header(bubble_this, main_char_dict, key=cw_key)
                if bubble_this:
                    bubble_this.display(surface=self.canvas, text=main_text, header=header_text)
                # 立绘
                for idx in char_set.keys():
                    # TODO: zorder
                    this_char = char_set[idx]
                    this_char_dict = self.chartab.struct[this_char['name']+'.'+this_char['subtype']]
                    # 立绘
                    anime_this:Animation = self.get_media(this_char_dict['Animation'])
                    if anime_this:
                        anime_this.preview(surface=self.canvas)
            else:
                pass
        # 刷新
        self.update_canvas()

