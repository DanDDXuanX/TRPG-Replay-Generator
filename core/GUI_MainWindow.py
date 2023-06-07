#!/usr/bin/env python
# coding: utf-8

# 图形界面的主界面

import sys

import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk

from .ProjConfig import Preference
from .Utils import EDITION

# 项目视图
from .GUI_View import ProjectView, ConsoleView

class RplGenStudioMainWindow(ttk.Window):
    def __init__(
            self,preference:Preference = Preference()
            )->None:
        # 系统缩放比例
        self.sz = self.get_screenzoom()
        super().__init__(
            title       = '回声工坊 ' + EDITION,
            themename   = 'lumen',
            iconphoto   = './media/icon.png',
            size        = (int(1500*self.sz),int(800*self.sz)),
            resizable   = (True,True),
        )
        # 关闭
        self.protocol('WM_DELETE_WINDOW',self.on_close)
        # 主题配置
        self.theme_config()
        # 导航栏
        self.navigate_bar = NavigateBar(master=self,screenzoom=self.sz)
        self.navigate_bar.place(x=0,y=0,width=100*self.sz,relheight=1)
        # event
        self.navigate_bar.bind('<ButtonRelease-1>', self.navigateBar_get_click)
        self.bind('<F11>', self.switch_fullscreen)
        # 视图
        self.view = {
            'project': ProjectView(master=self,screenzoom=self.sz),
            'console': ConsoleView(master=self,screenzoom=self.sz)
            }
        self.view_show('project')
    # 初始化主题
    def theme_config(self):
        # 样式
        SZ_3 = int(3 * self.sz)
        SZ_5 = int(5 * self.sz)
        text_label_pad = (SZ_5,0,SZ_5,0)
        # 导航栏的按钮
        self.style.configure('secondary.TButton',anchor='w',font="-family 微软雅黑 -size 20 -weight bold",compound='left',padding=(SZ_3,0,0,0))
        self.style.configure('danger.TButton',compound='left',font="-family 微软雅黑 -size 14 -weight bold")
        self.style.configure('terminal.TButton',compound='left',font="-family 微软雅黑 -size 14 -weight bold")
        # 媒体定义的颜色标签
        self.style.configure('Violet.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#a690e0')
        self.style.configure('Iris.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#729acc')
        self.style.configure('Caribbean.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#29d698')
        self.style.configure('Lavender.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#e384e3')
        self.style.configure('Cerulean.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#2fbfde')
        self.style.configure('Forest.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#51b858')
        self.style.configure('Rose.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#f76fa4')
        self.style.configure('Mango.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#eda63b')
        self.style.configure('Purple.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#970097')
        self.style.configure('Blue.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#3c3cff')
        self.style.configure('Teal.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#008080')
        self.style.configure('Magenta.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#e732e7')
        self.style.configure('Tan.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#cec195')
        self.style.configure('Green.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#1d7021')
        self.style.configure('Brown.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#8b4513')
        self.style.configure('Yellow.TLabel',anchor='center',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#e2e264')
        # 角色表的表头样式
        self.style.configure('CharHead.TLabel',anchor='left',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#ffffff',background='#51b858')
        # 显示内容的头文本
        self.style.configure('comment.TLabel',anchor='w',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#bfbfbf') # 浅灰色
        self.style.configure('dialog.TLabel',anchor='w',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#0066cc') # 蓝色的
        self.style.configure('setdync.TLabel',anchor='w',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#008000') # 绿色的
        self.style.configure('place.TLabel',anchor='w',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#e60074') # 品红
        self.style.configure('invasterisk.TLabel',anchor='w',font="-family 微软雅黑 -size 12 -weight bold",padding=text_label_pad,foreground='#cc0000') # 红色的
        # 显示内容的主文本
        self.style.configure('main.TLabel',anchor='w',font="-family 微软雅黑 -size 10",padding=text_label_pad) # 黑色的
        self.style.configure('ingore.TLabel',anchor='w',font="-family 微软雅黑 -size 10",padding=text_label_pad,foreground='#bfbfbf') # 浅灰色
        self.style.configure('method.TLabel',anchor='w',font="-family 微软雅黑 -size 10 -weight bold",padding=text_label_pad,foreground='#bf8000') # 橙色的
        self.style.configure('digit.TLabel',anchor='w',font="-family 微软雅黑 -size 10 -weight bold",padding=text_label_pad,foreground='#6600cc') # 紫色的
        self.style.configure('fuction.TLabel',anchor='w',font="-family 微软雅黑 -size 10 -weight bold",padding=text_label_pad,foreground='#009898') # 蓝色的
        self.style.configure('object.TLabel',anchor='w',font="-family 微软雅黑 -size 10 -weight bold",padding=text_label_pad,foreground='#303030') # 深灰色
        self.style.configure('exception.TLabel',anchor='w',font="-family 微软雅黑 -size 10 -weight bold",padding=text_label_pad,foreground='#cc0000') # 红色的
        # 预览窗体
        self.style.configure('preview.TLabel',anchor='center',background='#000000',borderwidth=0)
    # 当关闭窗口时
    def on_close(self):
        project_view:ProjectView = self.view['project']
        project_view.file_manager.project.dump_json('./test_project.json')
        self.destroy()
    # 当导航栏被点击时
    def navigateBar_get_click(self,event):
        is_wide = not self.navigate_bar.is_wide
        navigate_bar_width = int({True:180,False:80}[is_wide] * self.sz)
        self.navigate_bar.place_widgets(is_wide)
        self.navigate_bar.place_configure(width=navigate_bar_width)
        self.view[self.show].place_configure(x=navigate_bar_width,width=-navigate_bar_width)
    # 显示指定的视图
    def view_show(self,show:str):
        navigate_bar_width = int({True:180,False:80}[self.navigate_bar.is_wide] * self.sz)
        self.view[show].place_forget()
        self.view[show].place(x=navigate_bar_width,y=0,relwidth=1,relheight=1,width=-navigate_bar_width)
        self.show = show
    # 获取系统的缩放比例
    def get_screenzoom(self)->float:
        if 'win32' in sys.platform:
            from ctypes import windll
            return windll.shcore.GetScaleFactorForDevice(0) / 100
        else:
            print(sys.platform)
            return 1.0
    # 进入或者取消全屏
    def switch_fullscreen(self,event):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

# 最右导航栏的
class NavigateBar(ttk.Frame):
    """
    各个元件的尺寸：以100%缩放为准
    -----
    1. 图标的尺寸：50，50
    2. 按钮的尺寸：60，60
    3. 宽版按钮的尺寸：160，60
    4. 按钮和按钮之间的距离：80
    5. 按钮和分割线的距离：80 + 20
    6. 选中标志，在按钮中的尺寸：5，60
    """
    def __init__(self,master,screenzoom) -> None:
        self.sz = screenzoom
        super().__init__(master,borderwidth=10*self.sz,bootstyle='secondary')
        icon_size = [int(50*self.sz),int(50*self.sz)]
        self.master = master
        self.is_wide = False
        # 图形
        self.image = {
            'logo'      : ImageTk.PhotoImage(name='logo',   image=Image.open('./media/icon.png').resize(icon_size)),
            'setting'   : ImageTk.PhotoImage(name='setting',image=Image.open('./media/icon/setting.png').resize(icon_size)),
            'project'   : ImageTk.PhotoImage(name='project',image=Image.open('./media/icon/project.png').resize(icon_size)),
            'script'    : ImageTk.PhotoImage(name='script', image=Image.open('./media/icon/script.png').resize(icon_size)),
            'console'   : ImageTk.PhotoImage(name='console',image=Image.open('./media/icon/console.png').resize(icon_size)),
        }
        # 顶部
        self.titles = {
            'logo'      : ttk.Button(master=self,image='logo',bootstyle='secondary-solid'),
            'set'       : ttk.Button(master=self,image ='setting',text=' 首选项',command=lambda :self.press_button('setting'),bootstyle='secondary-solid',compound='left')
        } 
        # 分割线
        self.separator = ttk.Separator(master=self,orient='horizontal',bootstyle='light')
        # 按钮
        self.buttons = {
            'project'   : ttk.Button(master=self,image='project',text=' 项目',command=lambda :self.press_button('project'),bootstyle='secondary-solid',compound='left'),
            'script'    : ttk.Button(master=self,image='script',text=' 脚本',command=lambda :self.press_button('script'),bootstyle='secondary-solid',compound='left'),
            'console'   : ttk.Button(master=self,image='console',text=' 控制台',command=lambda :self.press_button('console'),bootstyle='secondary-solid',compound='left'),
        }
        # 高亮的线
        self.choice = ttk.Frame(master=self,bootstyle='primary')
        # self.titles
        self.place_widgets(self.is_wide)
    # 放置元件
    def place_widgets(self,is_wide:bool):
        self.is_wide = is_wide
        if is_wide:
            width = 160
        else:
            width = 60
        width = int(width*self.sz)
        distance = int(80 * self.sz)
        # self.titles
        for idx,key in enumerate(self.titles.keys()):
            button = self.titles[key]
            if len(button.place_info())==0:
                button.place(width=width,height=width,x=0,y=idx*distance)
            else:
                button.place_configure(width=width)
        # ----------
        if len(self.separator.place_info()) == 0:
            self.separator.place(width=width,x=0,y= (idx+1)*distance)
        else:
            self.separator.place_configure(width=width)
        y_this = idx*distance + int(100 * self.sz)
        # self.buttons
        for idx,key in enumerate(self.buttons.keys()):
            button = self.buttons[key]
            if len(button.place_info())==0:
                button.place(width=width,height=width,x=0, y= y_this + idx*distance)
            else:
                button.place_configure(width=width)
    # 点击按键的绑定事件：标注
    def press_button(self,botton):
        position = {'setting':80,'project':180,'script':260,'console':340}[botton]*self.sz
        SZ_5 = int(self.sz * 5)
        SZ_60 = int(self.sz * 60)
        if len(self.choice.place_info()) == 0:
            self.choice.place(width=SZ_5,height=SZ_60,x=-SZ_5,y= position)
        else:
            self.choice.place_configure(y=position)
        self.master.view_show(botton)
