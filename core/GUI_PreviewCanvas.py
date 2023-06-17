#!/usr/bin/env python
# coding: utf-8

import numpy as np
import tkinter as tk
import ttkbootstrap as ttk
import pygame
from pygame.draw import line, rect
from PIL import Image, ImageTk

from core.Medias import MediaObj

from .ScriptParser import MediaDef, CharTable, RplGenLog
from .Medias import MediaObj, Animation, Bubble, ChatWindow, Balloon, Background, HitPoint, Dice
from .FreePos import Pos

# 可交互的点线框
class InteractiveDot:
    def __init__(self,p1,p2,color,master:Animation=None) -> None:
        self.master = master
        self.color:str = color
        if self.color == 'green':
            self.p1 = np.array(p1)
            self.p2 = np.array(p2)
        elif self.color == 'blue':
            self.p1 = np.array(p1) + np.array(master.pos.get())
            self.p2 = np.array(p2) + np.array(master.pos.get())
        elif self.color == 'purple':
            self.p1 = np.array(p1) + np.array(master.pos.get())
            self.p2 = np.array(p2) + np.array(master.pos.get())
        else: # red
            self.p1 = np.array([p1,0])
            self.p2 = np.array([-np.inf,-np.inf]) # 无效的占位符
        # 是否被选中
        self.selected = {
            'p1' : False,
            'p2' : False
        }
    def check(self, pos, canvas_zoom:float=1.0)->bool:
        rw = int(5 / canvas_zoom)
        if np.max(np.abs(np.array(pos) - self.p1)) < rw:
            self.selected['p1'] = True
            self.selected['p2'] = False
            return True
        elif np.max(np.abs(np.array(pos) - self.p2)) < rw:
            self.selected['p1'] = False
            self.selected['p2'] = True
            return True
        else:
            self.selected['p1'] = False
            self.selected['p2'] = False
            return False
    def draw(self, surface, canvas_zoom:float=1.0):
        lw = int(1 / canvas_zoom)
        rw = int(5 / canvas_zoom)
        dlw = {True:rw, False:lw}
        if self.color == 'green':
            element_rect = [self.p1[0], self.p1[1], self.p2[0]-self.p1[0], self.p2[1]-self.p1[1]]
            p1_rect = [self.p1[0]-rw, self.p1[1]-rw, 2*rw, 2*rw]
            p2_rect = [self.p2[0]-rw, self.p2[1]-rw, 2*rw, 2*rw]
            rect(surface=surface,color='#00aa00',rect=element_rect,width=lw)
            rect(surface=surface,color='#00aa00',rect=p1_rect,width=dlw[self.selected['p1']])
            rect(surface=surface,color='#00aa00',rect=p2_rect,width=dlw[self.selected['p2']])
        elif self.color == 'blue':
            element_rect = [self.p1[0], self.p1[1], self.p2[0]-self.p1[0], self.p2[1]-self.p1[1]]
            p1_rect = [self.p1[0]-rw, self.p1[1]-rw, 2*rw, 2*rw]
            rect(surface=surface,color='#0000bb',rect=element_rect,width=lw)
            rect(surface=surface,color='#0000bb',rect=p1_rect,width=dlw[self.selected['p1']])
        elif self.color == 'purple':
            element_rect = [self.p1[0], self.p1[1], self.p2[0]-self.p1[0], self.p2[1]-self.p1[1]]
            p1_rect = [self.p1[0]-rw, self.p1[1]-rw, 2*rw, 2*rw]
            p2_rect = [self.p2[0]-rw, self.p2[1]-rw, 2*rw, 2*rw]
            rect(surface=surface,color='#aa00aa',rect=element_rect,width=lw)
            rect(surface=surface,color='#aa00aa',rect=p1_rect,width=dlw[self.selected['p1']])
            rect(surface=surface,color='#aa00aa',rect=p2_rect,width=dlw[self.selected['p2']])
        else:
            center = self.master.pos.get()[1] + int(self.master.size[1]/2)
            p1_rect = [self.p1[0]-rw, center-rw, 2*rw, 2*rw]
            line(
                surface=surface,
                start_pos=(self.p1[0], self.master.pos.get()[1]),
                end_pos=(self.p1[0], self.master.pos.get()[1] + self.master.size[1]),
                width=lw, color='#aa0000'
                )
            rect(surface=surface,color='#aa0000',rect=p1_rect,width=dlw[self.selected['p1']])
    def move(self, new_pos):
        if self.selected['p1'] == True:
            if self.color in ('green','blue'):
                p1_2_p2_vec = self.p2 - self.p1
                self.p1 = np.array(new_pos)
                self.p2 = self.p1 + p1_2_p2_vec
            else:
                self.p1 = np.array(new_pos)
        elif self.selected['p2'] == True:
            # TODO: 只能在对角线上！
            self.p2 = np.array(new_pos)
        else:
            pass
    def get(self):
        if self.color=='green':
            return self.p1.tolist(), self.p2.tolist()
        else:
            master_pos = np.array(self.master.pos.get())
            return self.p1-master_pos, self.p2-master_pos
# 预览窗
class PreviewCanvas(ttk.Frame):
    def __init__(self,master,screenzoom,mediadef):
        # 基类初始化
        self.sz = screenzoom
        SZ_2 = int(self.sz * 2)
        super().__init__(master=master, bootstyle='secondary',border=SZ_2)
        self.blank_size = (0, 0)
        self.canvas_zoom = tk.DoubleVar(master=self,value=0.4)
        # TODO: 待修改，这个位置应该引用项目的尺寸！
        self.canvas_size = (1920, 1080)
        # 媒体定义
        self.mediadef:MediaDef = mediadef
        # 尺寸自适应：
        # 元件
        self.canvas_label = ttk.Label(master=self,image=None,style='preview.TLabel')
        self.canvas_label.bind('<Configure>', self.update_size)
        # 预览图像
        self.empty_canvas = pygame.image.load('./media/canvas.png')
        self.canvas = pygame.Surface(size=self.canvas_size)
        self.canvas.blit(self.empty_canvas,(0,0))
        # 更新
        self.update_canvas()
        self.update_item()
    # 更新尺寸
    def update_size(self, event):
        WW = self.canvas_label.winfo_width()
        WH = self.canvas_label.winfo_height()
        RW = WW/self.canvas_size[0]
        RH = WH/self.canvas_size[1]
        # 根据尺寸，调整缩放率
        if RW > RH:
            # 宽有余量：
            self.canvas_zoom.set(RH)
            self.blank_size = (int((WW/RH - self.canvas_size[0])/2), 0)
        else:
            # 高有余量
            self.canvas_zoom.set(RW)
            self.blank_size = (0, int((WH/RW - self.canvas_size[1])/2))
        # 更新画面
        if self.canvas_zoom.get() > 0.01:
            self.update_canvas()
    # 更新组件
    def update_item(self):
        self.canvas_label.pack(expand=True,fill='both')
    # 更新画布
    def update_canvas(self):
        pil_canvas_iamge = Image.frombytes(mode='RGB',data=pygame.image.tostring(self.canvas,'RGB'),size=self.canvas_size)
        self.image = ImageTk.PhotoImage(
            image=pil_canvas_iamge.resize([
                int(self.canvas_size[0]*self.canvas_zoom.get()),
                int(self.canvas_size[1]*self.canvas_zoom.get()),
                ]),
            )
        self.canvas_label.config(image=self.image)
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
    def __init__(self, master, screenzoom, mediadef):
        # 继承
        super().__init__(master, screenzoom, mediadef)
        # 可交互的预览窗的特性：
        # 预览窗是可输入焦点的
        self.canvas_label.configure(takefocus=True) 
        self.canvas_label.bind('<FocusIn>',self.get_focus)
        self.canvas_label.bind('<FocusOut>',self.lost_focus)
        # 鼠标单击和拖动
        self.canvas_label.bind('<Button-1>',self.get_pressed)
        self.canvas_label.bind('<B1-Motion>',self.get_drag)
        self.canvas_label.bind('<ButtonRelease-1>',self.get_drag_done)
        # ctrl + Z 撤回
    def preview(self, media_name:str):
        super().preview()
        # 需要将这个对象保存下来
        self.object_this = self.get_media(media_name)
        # print(self.object_this)
        if self.object_this:
            self.object_this.preview(self.canvas)
        # 获取
        self.dots = {}
        self.dot_info = self.object_this.get_pos()
        for color in self.dot_info:
            this_color = self.dot_info[color]
            for dot in this_color:
                if color == 'green':
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot]['pos'],
                        p2=this_color[dot]['scale'],
                        color=color,
                        master=self.object_this
                        )
                elif color == 'purple':
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot]['sub_pos'],
                        p2=this_color[dot]['sub_end'],
                        color=color,
                        master=self.object_this
                        )
                elif color == 'red':
                    if 'am_left' in this_color[dot]:
                        keyword = 'am_left'
                    else:
                        keyword = 'am_right'
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot][keyword],
                        p2=None,
                        color=color,
                        master=self.object_this
                        )
                else:
                    if dot == 'b0':
                        p1k = 'mt_pos'
                        p2k = 'mt_end'
                    else:
                        p1k = 'ht_pos'
                        p2k = 'ht_end'
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot][p1k],
                        p2=this_color[dot][p2k],
                        color=color,
                        master=self.object_this
                        )
                self.dots[dot].draw(self.canvas,self.canvas_zoom.get())
        self.update_canvas()
    def update_preview(self,pressed:tuple,refresh:bool=False):
        # 重置背景
        self.canvas.blit(self.empty_canvas,(0,0))
        # 刷新媒体
        self.object_this.preview(self.canvas)
        # 刷新点
        self.selected_dot = None
        self.selected_dot_name = None
        for dot in self.dots:
            this_dot:InteractiveDot = self.dots[dot]
            if this_dot.check(pos=pressed,canvas_zoom=self.canvas_zoom.get()):
                self.selected_dot = this_dot
                self.selected_dot_name = dot
            self.dots[dot].draw(self.canvas,self.canvas_zoom.get())
        # 刷新画布
        self.update_canvas()
    def get_focus(self,event):
        self.configure(bootstyle='primary')
    def lost_focus(self,event):
        self.configure(bootstyle='secondary')
    def get_coordinates(self,event):
        zoom = self.canvas_zoom.get()
        Rx = int(event.x / zoom)
        Ry = int(event.y / zoom)
        return (Rx - self.blank_size[0], Ry - self.blank_size[1])
    def get_pressed(self,event):
        # 被点击的功能：输入焦点、点选一个可拖动点
        self.canvas_label.focus_set()
        pressd = self.get_coordinates(event=event)
        self.update_preview(pressed=pressd,refresh=False)
    def get_drag(self,event):
        # 拖动中的功能：渲染点被拖动中的位置
        pressd = self.get_coordinates(event=event)
        if self.selected_dot:
            self.selected_dot.move(new_pos=pressd)
        self.update_preview(pressed=pressd,refresh=False)
    def get_drag_done(self,event):
        # 释放鼠标的功能：确定最终修改的位置，并重置预览的画面渲染
        pressd = self.get_coordinates(event=event)
        if self.selected_dot:
            if self.selected_dot_name == 'g0':
                new_pos = self.selected_dot.get()[0]
                #TODO: new_end = self.selected_dot.get()[1]
                self.object_this.pos = Pos(*new_pos)
            elif self.selected_dot_name == 'b0':
                new_pos = self.selected_dot.get()[0] 
                self.object_this.mt_pos = tuple([x for x in new_pos])
            elif self.selected_dot_name[0] == 'b':
                header_index = int(self.selected_dot_name[1:])-1
                new_pos = self.selected_dot.get()[0]
                if type(self.object_this) is Balloon:
                    ht_pos:list = self.object_this.ht_pos
                    ht_pos[header_index] = tuple([x for x in new_pos])
                    self.object_this.ht_pos = ht_pos
                else:
                    self.object_this.ht_pos = tuple([x for x in new_pos])
            elif self.selected_dot_name == 'r0':
                pass
            elif self.selected_dot_name == 'r1':
                pass
            elif self.selected_dot_name == 'p0':
                pass
            else:
                pass
        self.update_preview(pressed=pressd,refresh=True)

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
                    bubble_obj:Bubble = self.get_media(bb_obj['bubble'])
                    bubble_obj.display(surface=self.canvas, text=main_text, header=header_text)
            elif section_dict_this['type'] == 'hitpoint':
                self.get_background(line_index).preview(self.canvas) # 背景
                Background('black').display(self.canvas, alpha=80)
                for layer in range(0,3):
                    layer_this = HitPoint(
                        describe   = section_dict_this['content'],
                        heart_max  = section_dict_this['hp_max'],
                        heart_begin= section_dict_this['hp_begin'],
                        heart_end  = section_dict_this['hp_end'],
                        layer= layer
                        )
                    if layer == 2:
                        layer_this.display(surface=self.canvas, alpha=50)
                    else:
                        layer_this.preview(surface=self.canvas)
            elif section_dict_this['type'] == 'dice':
                self.get_background(line_index).preview(self.canvas) # 背景
                Background('black').display(self.canvas, alpha=80)
                for layer in range(0,3):
                    Dice(
                        dice_set=section_dict_this['dice_set'],
                        layer= layer
                        ).preview(surface=self.canvas)
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

