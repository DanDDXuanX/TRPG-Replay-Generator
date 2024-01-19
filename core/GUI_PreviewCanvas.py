#!/usr/bin/env python
# coding: utf-8

import numpy as np
import tkinter as tk
import ttkbootstrap as ttk
import pygame
from copy import copy
from pygame.draw import line, rect, circle
from pygame.mixer import Channel
from PIL import Image, ImageTk

from core.Medias import MediaObj

from .ProjConfig import preference
from .ScriptParser import MediaDef, CharTable, RplGenLog
from .Medias import MediaObj, Animation, Bubble, ChatWindow, Balloon, Background, HitPoint, Dice, Audio, BGM
from .Utils import get_vppr
from .GUI_Link import Link

# 可交互的点线框
class InteractiveDot:
    def __init__(self,p1:tuple,p2:tuple,color:str,master:Animation=None,screen_zoom:float=1.0) -> None:
        self.master = master
        self.color:str = color
        self.sz = screen_zoom
        # root: pos-scale 两个联动的可交互点
        if self.color == 'green':
            self.p1 = np.array(p1)
            self.p2 = np.array(p2)
        # tx_pos-tx_end 仅一个可交互点
        elif self.color == 'blue':
            self.p1 = np.array(p1) + np.array(master.pos.get())
            self.p2 = np.array(p2) + np.array(master.pos.get())
        # sub_pos 两个不联动的可交互点
        elif self.color == 'purple':
            self.p1 = np.array(p1) + np.array(master.pos.get())
            self.p2 = np.array(p2) + np.array(master.pos.get())
        # pos / posgrid, 一个孤点
        elif self.color == 'orange':
            self.p1 = np.array(p1)
            self.p2 = np.array([-np.inf,-np.inf]) # 无效的占位符
        # ht_pos/ht_end 自适应气泡的分划线
        elif self.color == 'magenta':
            self.p1 = np.array(p1) + np.array(master.pos.get())
            self.p2 = np.array(p2) + np.array(master.pos.get())
        elif self.color == 'red': # am left / right 一条竖线
            self.p1 = np.array([p1[0], int(self.master.size[1]/2)]) + np.array(master.pos.get())
            self.p2 = np.array([-np.inf,-np.inf]) # 无效的占位符
        elif self.color == 'control': # 锚点和控制点
            self.p1 = np.array(p1) # 控制点
            self.p2 = np.array(p2) # 锚点：无法操作的
        elif self.color == 'anchor': # 锚点本体
            self.p1 = np.array(p1)
            self.p2 = np.array([-np.inf,-np.inf]) # 无效的占位符
        # 是否被选中
        self.selected = {
            'p1' : False,
            'p2' : False
        }
    def check(self, pos, canvas_zoom:float=1.0)->bool:
        rw = int(np.ceil(5 / canvas_zoom * self.sz))
        if np.max(np.abs(np.array(pos) - self.p1)) < rw:
            self.selected['p1'] = True
            self.selected['p2'] = False
            return True
        elif np.max(np.abs(np.array(pos) - self.p2)) < rw:
            if self.color not in ['blue','control']: # 蓝点和控制点是无法被选中P2的
                self.selected['p1'] = False
                self.selected['p2'] = True
                return True
            else:
                self.selected['p1'] = False
                self.selected['p2'] = False
                return False
        else:
            self.selected['p1'] = False
            self.selected['p2'] = False
            return False
    def draw(self, surface, canvas_zoom:float=1.0):
        lw = int(np.ceil(1 / canvas_zoom))
        rw = int(np.ceil(5 / canvas_zoom * self.sz))
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
        elif self.color == 'orange':
            p1_rect = [self.p1[0]-rw, self.p1[1]-rw, 2*rw, 2*rw]
            rect(surface=surface,color='#ddaa00',rect=p1_rect,width=dlw[self.selected['p1']])
        elif self.color == 'magenta':
            color = '#dd00aa'
            element_rect = [self.p1[0], self.p1[1], self.p2[0]-self.p1[0], self.p2[1]-self.p1[1]]
            p1_rect = [self.p1[0]-rw, self.p1[1]-rw, 2*rw, 2*rw]
            p2_rect = [self.p2[0]-rw, self.p2[1]-rw, 2*rw, 2*rw]
            # 点1
            line(
                surface=surface,
                start_pos=(self.p1[0], self.master.pos.get()[1]),
                end_pos=(self.p1[0], self.master.pos.get()[1] + self.master.size[1]),
                width=lw, color=color
                )
            line(
                surface=surface,
                start_pos=(self.master.pos.get()[0], self.p1[1]),
                end_pos=(self.master.pos.get()[0] + self.master.size[0], self.p1[1]),
                width=lw, color=color
                )
            # 点2
            line(
                surface=surface,
                start_pos=(self.p2[0], self.master.pos.get()[1]),
                end_pos=(self.p2[0], self.master.pos.get()[1] + self.master.size[1]),
                width=lw, color=color
                )
            line(
                surface=surface,
                start_pos=(self.master.pos.get()[0], self.p2[1]),
                end_pos=(self.master.pos.get()[0] + self.master.size[0], self.p2[1]),
                width=lw, color=color
                )            
            rect(surface=surface,color=color,rect=p1_rect,width=dlw[self.selected['p1']])
            rect(surface=surface,color=color,rect=p2_rect,width=dlw[self.selected['p2']])
        elif self.color=='red':
            # center = self.master.pos.get()[1] + int(self.master.size[1]/2)
            p1_rect = [self.p1[0]-rw, self.p1[1]-rw, 2*rw, 2*rw]
            line(
                surface=surface,
                start_pos=(self.p1[0], self.master.pos.get()[1]),
                end_pos=(self.p1[0], self.master.pos.get()[1] + self.master.size[1]),
                width=lw, color='#aa0000'
                )
            rect(surface=surface,color='#aa0000',rect=p1_rect,width=dlw[self.selected['p1']])
        elif self.color=='control':
            circle(surface=surface,color='#00aaaa',center=self.p1,radius=rw,width=dlw[self.selected['p1']])
            line(surface=surface,color='#00aaaa',start_pos=self.p1,end_pos=self.p2,width=lw)
        elif self.color=='anchor':
            p1_rect = [self.p1[0]-rw, self.p1[1]-rw, 2*rw, 2*rw]
            rect(surface=surface,color='#00aaaa',rect=p1_rect,width=dlw[self.selected['p1']])
    def move(self, new_pos):
        if self.selected['p1'] == True:
            if self.color in ('green','blue'):
                p1_2_p2_vec = self.p2 - self.p1
                self.p1 = np.array(new_pos)
                self.p2 = self.p1 + p1_2_p2_vec
            else:
                self.p1 = np.array(new_pos)
        elif self.selected['p2'] == True:
            self.p2 = np.array(new_pos)
        else:
            pass
    def get(self):
        if self.color in ('green','orange','control','anchor'):
            return self.p1.tolist(), self.p2.tolist()
        else:
            master_pos = np.array(self.master.pos.get())
            return self.p1-master_pos, self.p2-master_pos
    def get_selected(self):
        if self.selected['p1']:
            return self.p1
        elif self.selected['p2']:
            return self.p2
        else:
            return None
    def force_selected(self,pn):
        if pn == 'p1':
            self.selected['p1'] = True
            self.selected['p2'] = False
        else:
            self.selected['p1'] = False
            self.selected['p2'] = True
        return self.get_selected()
# 预览窗
class PreviewCanvas(ttk.Frame):
    def __init__(self,master,screenzoom,mediadef):
        # 基类初始化
        self.sz = screenzoom
        SZ_2 = int(self.sz * 2)
        super().__init__(master=master, bootstyle='secondary',border=SZ_2)
        self.blank_size = (0, 0)
        self.canvas_zoom = tk.DoubleVar(master=self,value=0.4)
        # 这个位置应该引用项目的尺寸
        self.proj_config = Link['project_config']
        # 媒体定义
        self.mediadef:MediaDef = mediadef
        # 尺寸自适应：
        # 元件
        self.canvas_label = ttk.Label(master=self,image=None,style='preview.TLabel')
        self.canvas_label.bind('<Configure>', self.update_display_size)
        # 预览图像
        self.update_canvas_size(None)
        # 更新
        self.update_canvas()
        self.update_item()
    # 更新画布尺寸
    def update_canvas_size(self, event):
        self.canvas_size = (self.proj_config.Width, self.proj_config.Height)
        self.update_empty_canvas()
        self.canvas = pygame.Surface(size=self.canvas_size)
        self.canvas.blit(self.empty_canvas,(0,0))
    # 更新背景底图
    def update_empty_canvas(self):
        self.empty_canvas = pygame.image.load('./assets/canvas.png').subsurface([0,0,self.proj_config.Width,self.proj_config.Height])
        # 如果是黑暗模式，做反相
        if preference.theme == 'rplgendark':
            self.empty_canvas = pygame.surfarray.make_surface(270-pygame.surfarray.array3d(self.empty_canvas))
    # 更新显示尺寸
    def update_display_size(self, event):
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
        # 如果尺寸发生变化：
        if self.proj_config.Width != self.canvas_size[0] or self.proj_config.Height != self.canvas_size[1]:
            self.update_canvas_size(None)
            self.update_display_size(None)
        # 重置背景
        else:
            self.canvas.blit(self.empty_canvas,(0,0))
        # 待重载
    def show_error(self):
        # 错误背景
        RGB = pygame.surfarray.array3d(self.empty_canvas)
        RGB[...,1] = 0
        RGB[...,2] = 0
        error_canvas = pygame.surfarray.make_surface(RGB)
        self.canvas.blit(error_canvas,(0,0))
    # 保存
    def save_command(self,event):
        # 保存
        mainwindow = self.winfo_toplevel()
        # 找到保存项目的命令
        mainwindow.view['project'].file_manager.save_file()
class MDFPreviewCanvas(PreviewCanvas):
    fixed_media = None
    def __init__(self, master, screenzoom, mediadef):
        # 继承
        super().__init__(master, screenzoom, mediadef)
        # 固定
        self.current_fix = None
        # 可交互的预览窗的特性：
        # 预览窗是可输入焦点的
        self.canvas_label.configure(takefocus=True) 
        self.canvas_label.bind('<FocusIn>',self.get_focus)
        self.canvas_label.bind('<FocusOut>',self.lost_focus)
        # 鼠标单击和拖动
        self.canvas_label.bind('<Button-1>',self.get_pressed)
        self.canvas_label.bind('<B1-Motion>',self.get_drag)
        self.canvas_label.bind('<ButtonRelease-1>',self.get_drag_done)
        self.canvas_label.bind('<Control-Button-1>',self.click_move_select_dot)
        # 最大化显示预览窗
        self.canvas_label.bind('<Tab>',self.switch_fullview)
        # 方向控制
        self.canvas_label.bind('<Key-Up>',self.adjust_selected_point)
        self.canvas_label.bind('<Key-Down>',self.adjust_selected_point)
        self.canvas_label.bind('<Key-Left>',self.adjust_selected_point)
        self.canvas_label.bind('<Key-Right>',self.adjust_selected_point)
        # 保存
        self.canvas_label.bind('<Control-Key-s>',self.save_command)
        # 固定和取消固定
        # 按键绑定：暂时不能固定音频类
        self.canvas_label.bind('<Control-Key-q>',lambda event:self.set_fix('NA'),"+")
        self.canvas_label.bind('<Control-Key-e>',lambda event:self.set_fix(),"+")
        # 可以联动编辑区
        self.edit_frame = self.master.edit
        # 初始的鼠标
        self.configure(cursor='hand2')
        # 刷新点
        self.object_this = None
        self.recode = None
        self.dots = {}
        self.selected_dot = None
        self.selected_dot_name = None
        # ctrl + Z 撤回
    # 实例化媒体，生成点视图，并预览一次
    def preview(self, media_name:str):
        # 检查是否需要更新空白画布
        if self.current_fix is not MDFPreviewCanvas.fixed_media:
            self.update_empty_canvas()
            self.current_fix = MDFPreviewCanvas.fixed_media
        # 继承
        super().preview()
        # 需要将这个对象保存下来：如果media_name不是None
        if media_name:
            self.object_this = self.get_media(media_name)
        # print(self.object_this)
        if self.object_this:
            self.object_this.preview(self.canvas)
            self.recode = self.canvas.copy()
        # 获取点视图
        self.update_dotview()
        # 刷新显示
        self.update_canvas()
    # 更新画布尺寸：MDF特性，允许固定媒体
    def update_empty_canvas(self):
        super().update_empty_canvas()
        if MDFPreviewCanvas.fixed_media and type(MDFPreviewCanvas.fixed_media) not in [BGM,Audio]:
            MDFPreviewCanvas.fixed_media.preview(surface=self.empty_canvas)
    # 拖拽中实时刷新点视图的内容
    def update_preview(self,pressed:tuple=None):
        # 没有press（是edit在调用这个方法）则更新媒体画面
        if pressed is None:
            # 重置背景
            self.canvas.blit(self.empty_canvas,(0,0))
            # 刷新媒体
            if self.object_this:
                self.object_this.preview(self.canvas)
                self.recode = self.canvas.copy()
            # 刷新点
            for dot in self.dots:
                self.dots[dot].draw(self.canvas,self.canvas_zoom.get())
        # 有press（是在交互式调用这个方法）则只更新点
        else:
            # 显示底图
            if self.recode:
                self.canvas.blit(self.recode,(0,0))
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
    # 重新生成点视图
    def update_dotview(self):
        # 获取
        if self.object_this:
            self.dot_info = self.object_this.get_pos()
        else:
            return
        self.dots = {}
        for color in self.dot_info:
            this_color = self.dot_info[color]
            for dot in this_color:
                if color == 'green':
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot]['pos'],
                        p2=this_color[dot]['scale'],
                        color=color,
                        master=self.object_this,
                        screen_zoom=self.sz
                        )
                elif color == 'purple':
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot]['sub_pos'],
                        p2=this_color[dot]['sub_end'],
                        color=color,
                        master=self.object_this,
                        screen_zoom=self.sz
                        )
                elif color == 'magenta':
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot]['mt_pos'],
                        p2=this_color[dot]['mt_end'],
                        color=color,
                        master=self.object_this,
                        screen_zoom=self.sz
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
                        master=self.object_this,
                        screen_zoom=self.sz
                        )
                elif color == 'orange':
                    if dot == 'o0':
                        keyword = 'pos'
                    else:
                        keyword = 'end'
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot][keyword],
                        p2=None,
                        color=color,
                        master=self.object_this,
                        screen_zoom=self.sz
                        )
                elif color == 'blue':
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
                        master=self.object_this,
                        screen_zoom=self.sz
                        )
                elif color == 'control':
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot]['control'],
                        p2=this_color[dot]['anchor'],
                        color=color,
                        master=self.object_this,
                        screen_zoom=self.sz
                        )
                elif color == 'anchor':
                    self.dots[dot] = InteractiveDot(
                        p1=this_color[dot]['pos'],
                        p2=None,
                        color=color,
                        master=self.object_this,
                        screen_zoom=self.sz
                        )
                self.dots[dot].draw(self.canvas,self.canvas_zoom.get())
    def get_focus(self,event):
        self.configure(bootstyle='primary',cursor='crosshair')
    def lost_focus(self,event):
        self.update_preview()
        self.configure(bootstyle='secondary',cursor='hand2')
    def get_coordinates(self,event):
        zoom = self.canvas_zoom.get()
        Rx = int(event.x / zoom)
        Ry = int(event.y / zoom)
        return (Rx - self.blank_size[0], Ry - self.blank_size[1])
    # 被点击的功能：输入焦点、点选一个可拖动点
    def get_pressed(self,event):
        self.canvas_label.focus_set()
        pressed = self.get_coordinates(event=event)
        self.update_preview(pressed=pressed)
    def force_dot(self,dotID,pID):
        if dotID in self.dots:
            self.selected_dot_name = dotID
            self.selected_dot = self.dots[dotID]
            dot = self.selected_dot.force_selected(pID)
            # 更新
            self.canvas_label.focus_set()
            self.update_preview()
    # 拖动中的功能：渲染点被拖动中的位置
    def get_drag(self,event):
        pressd = self.get_coordinates(event=event)
        if self.selected_dot:
            self.selected_dot.move(new_pos=pressd)
        self.update_preview(pressed=pressd)
    # 释放鼠标的功能：确定最终修改的位置，并重置预览的画面渲染
    def get_drag_done(self,event):
        pressed = self.get_coordinates(event=event)
        # 根据当前选点，刷新媒体对象
        if self.selected_dot:
            self.update_media_object(pressed=pressed)
    # ctrl点击，直接移动到鼠标点击位置
    def click_move_select_dot(self, event):
        # 先直接把可交互点移动到鼠标点击位置
        self.get_drag(event)
        # 然后根据根据当前点的位置，更新参数
        self.get_drag_done(event)
    # 将变更同步到编辑区和媒体对象的成员，并更新显示
    def update_edit(self):
        # 如果有选中点
        if self.selected_dot:
            # 绿点，影响pos
            if self.selected_dot_name == 'g0':
                # POS
                new_pos = self.selected_dot.get()[0]
                # self.object_this.pos = Pos(*new_pos)
                self.edit_frame.elements['pos'].set( '({},{})'.format(new_pos[0], new_pos[1]) )
                # scale：投影到对角线上
                new_end = self.selected_dot.get()[1]
                NPV = np.array(new_end)-np.array(new_pos)
                Z = get_vppr(new_pos=NPV, master_size=self.object_this.origin_size)
                # 尺寸未改变
                if Z == self.object_this.scale:
                    pass
                # 尺寸改变，但是None
                elif Z != 1 and self.object_this.filepath is None:
                    self.edit_frame.elements['scale'].set(1.0)
                # 尺寸改变
                else:
                    self.edit_frame.elements['scale'].set( round(Z,2) )
            # 蓝点，影响字体位置
            elif self.selected_dot_name == 'b0':
                new_pos = self.selected_dot.get()[0] 
                self.edit_frame.elements['mt_pos'].set( '({},{})'.format(new_pos[0], new_pos[1]) )
            elif self.selected_dot_name[0] == 'b':
                header_index = int(self.selected_dot_name[1:])-1
                new_pos = self.selected_dot.get()[0]
                if type(self.object_this) is Balloon:
                    self.edit_frame.elements['ht_pos_%d'%(header_index+1)].set( '({},{})'.format(new_pos[0], new_pos[1]))
                else:
                    self.edit_frame.elements['ht_pos'].set( '({},{})'.format(new_pos[0], new_pos[1]))
            # 红点，影响am_left_right
            elif self.selected_dot_name == 'r0':
                new_pos = self.selected_dot.get()[0]
                self.edit_frame.elements['am_left'].set(new_pos[0])
            elif self.selected_dot_name == 'r1':
                new_pos = self.selected_dot.get()[0]
                self.edit_frame.elements['am_right'].set(new_pos[0])
            # 紫色点，影响ChatWindow
            elif self.selected_dot_name == 'p0':
                new_pos = self.selected_dot.get()[0]
                new_end = self.selected_dot.get()[1]
                self.edit_frame.elements['sub_pos'].set('({},{})'.format(new_pos[0], new_pos[1]))
                self.edit_frame.elements['sub_end'].set('({},{})'.format(new_end[0], new_end[1]))
            # 品红点，影响DynamicBubble
            elif self.selected_dot_name == 'm0':
                new_pos = self.selected_dot.get()[0]
                new_end = self.selected_dot.get()[1]
                self.edit_frame.elements['mt_pos'].set('({},{})'.format(new_pos[0], new_pos[1]))
                self.edit_frame.elements['mt_end'].set('({},{})'.format(new_end[0], new_end[1]))
            # 橙色点，影响PosGrid
            elif self.selected_dot_name == 'o0':
                new_pos = self.selected_dot.get()[0]
                self.edit_frame.elements['pos'].set('({},{})'.format(new_pos[0], new_pos[1]))
            elif self.selected_dot_name == 'o1':
                new_pos = self.selected_dot.get()[0]
                self.edit_frame.elements['end'].set('({},{})'.format(new_pos[0], new_pos[1]))
            # 控制点和锚点，影响BezierCurve
            elif self.selected_dot_name[0] == 'a':
                header_index = int(self.selected_dot_name[1:])
                new_pos = self.selected_dot.get()[0]
                if header_index == 0:
                    self.edit_frame.elements['pos'].set('({},{})'.format(new_pos[0], new_pos[1]))
                else:
                    self.edit_frame.elements['anchor_%d'%(header_index)].set('({},{})'.format(new_pos[0], new_pos[1]))
            elif self.selected_dot_name[0] == 'c':
                header_index = int(self.selected_dot_name[2:])
                new_pos = self.selected_dot.get()[0]
                if self.selected_dot_name[1] == 'l':
                    anchor = self.object_this.curve_set[header_index-1]['control_points'][0,:]
                    new_vec = np.array(new_pos) - anchor
                    self.edit_frame.elements['control_left_%d'%(header_index)].set('({},{})'.format(new_vec[0], new_vec[1]))
                else:
                    anchor = self.object_this.curve_set[header_index-1]['control_points'][3,:]
                    new_vec = np.array(new_pos) - anchor
                    self.edit_frame.elements['control_right_%d'%(header_index)].set('({},{})'.format(new_vec[0], new_vec[1]))
            else:
                pass
        # 唤起编辑区的输出结果
        # update_dotview, update_preview 在 update_section_from中已经调用过一次了
        self.edit_frame.update_section_from()
    # 刷新媒体对象
    def update_media_object(self,pressed):
        # dot -> edit
        self.update_edit()
        # 需要额外刷新一次带press的
        self.update_preview(pressed=pressed)
    # 切换全屏视图
    def switch_fullview(self,event):
        self.master.set_fullview()
        self.canvas_label.focus_set()
    # 方向键微调位置
    def adjust_selected_point(self,event):
        direction_key = {'Up':(0,-1),'Down':(0,1),'Left':(-1,0),'Right':(1,0)}
        if event.state & 1: # shift
            multi = 100
        elif event.state & 4: # control
            multi = 10
        else:
            multi = 1
        if self.selected_dot:
            r_x, r_y = self.selected_dot.get_selected()
            p_x = r_x+direction_key[event.keysym][0]*multi
            p_y = r_y+direction_key[event.keysym][1]*multi
            self.selected_dot.move(new_pos=(p_x, p_y))
            # 刷新媒体对象
            self.update_media_object(pressed=(p_x, p_y))
        else:
            pass
    # 异常时
    def set_error(self):
        # super().show_error() # 暂时不显示红了
        # 清除当前的显示对象，recode，和全部的dot
        self.object_this = None
        self.recode = self.empty_canvas.copy()
        self.dots.clear()
    # 设置常驻
    def set_fix(self,media_name:str=None):
        if media_name:
            # 更新常驻对象
            MDFPreviewCanvas.fixed_media = self.get_media(media_name=media_name)
        else:
            # 默认，将当前对象设置为常驻对象
            MDFPreviewCanvas.fixed_media = copy(self.object_this)
        # 更新画布
        self.preview(media_name=None)
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
        # 按照图层顺序
        zorder:list = Link['project_config'].zorder
        for layer in zorder:
            if layer == 'Am1':
                if animation_this:
                    animation_this.preview(self.canvas)
            elif layer == 'Bb':
                if bubble_this:
                    bubble_this.preview(self.canvas, key=key)
        self.update_canvas()
class RGLPreviewCanvas(PreviewCanvas):
    def __init__(self, master, screenzoom,rplgenlog, chartab, mediadef):
        self.rplgenlog:RplGenLog = rplgenlog
        self.chartab:CharTable = chartab
        # 预览声道
        self.channel = Channel(3)
        # 重载
        super().__init__(master, screenzoom, mediadef)
    def get_background(self, line_index:str)->Background:
        index_this = int(line_index)
        while index_this >= 0:
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
            #: Exception
            return
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
                        layer_this.display(surface=self.canvas, alpha=50, frame=-1)
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
                # 立绘
                am_dict = {'Am1':None,'Am2':None,'Am3':None}
                for idx in char_set.keys():
                    this_char = char_set[idx]
                    this_char_dict = self.chartab.struct[this_char['name']+'.'+this_char['subtype']]
                    # 立绘
                    layer = 'Am'+str(int(idx)+1)
                    am_dict[layer] = self.get_media(this_char_dict['Animation'])
                # 按照图层顺序
                zorder:list = Link['project_config'].zorder
                for layer in zorder:
                    if layer == 'BG2':
                        self.get_background(line_index).preview(self.canvas) # 背景
                    if layer in ['Am1','Am2','Am3']:
                        if am_dict[layer]:
                            am_dict[layer].preview(self.canvas)
                    elif layer == 'Bb':
                        if bubble_this:
                            bubble_this.display(surface=self.canvas, text=main_text, header=header_text)
                # 音频
                if '*' in section_dict_this['sound_set']:
                    asterisk = section_dict_this['sound_set']['*']
                    # 获取对象
                    sound_object:Audio = self.get_media(asterisk['sound'])
                    if sound_object:
                        sound_object.display(channel=self.channel)
                    else:
                        try:
                            path = asterisk['sound'][1:-1]
                            sound_object = Audio(filepath=path)
                            sound_object.display(channel=self.channel)
                        except Exception:
                            pass        
            else:
                pass
        # 刷新
        self.update_canvas()
    def stop_audio(self):
        self.channel.stop()