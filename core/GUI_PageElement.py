#!/usr/bin/env python
# coding: utf-8

# 页面的其他公用元件
# 包含：搜索栏、输出命令按钮

import tkinter as tk
import ttkbootstrap as ttk
import threading
import pygame
from PIL import Image, ImageTk
from .GUI_Container import Container
from .OutputType import PreviewDisplay, ExportVideo, ExportXML
from .Exceptions import MainPrint
from .Utils import EDITION
from .Medias import MediaObj

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
        # 引用
        self.page = self.master
        icon_size = [int(30*self.sz),int(30*self.sz)]
        self.image = {
            'display'   : ImageTk.PhotoImage(name='display',image=Image.open('./media/icon/display.png').resize(icon_size)),
            'exportpr'    : ImageTk.PhotoImage(name='exportpr', image=Image.open('./media/icon/premiere.png').resize(icon_size)),
            'recode'   : ImageTk.PhotoImage(name='recode',image=Image.open('./media/icon/ffmpeg.png').resize(icon_size)),
        }
        self.buttons = {
            'display' : ttk.Button(master=self,image='display',text='播放预览',compound='left',style='output.TButton',command=lambda:self.open_new_thread('display')),
            'export'  : ttk.Button(master=self,image='exportpr',text='导出PR工程',compound='left',style='output.TButton',command=lambda:self.open_new_thread('exportpr')),
            'recode'  : ttk.Button(master=self,image='recode',text='导出视频',compound='left',style='output.TButton',command=lambda:self.open_new_thread('recode')),
        }
        self.runing_thread = None
        self.update_item()
        
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='left',expand=True,pady=0)
    def load_input(self):
        # 项目配置
        self.pconfig = self.page.ref_config
        # 脚本
        self.medef = self.page.ref_medef.copy()
        self.chartab = self.page.ref_chartab.copy()
        self.rplgenlog = self.page.content.copy()
        try:
            # 初始化配置项
            self.pconfig.execute()
            # 初始化媒体
            self.medef.execute()
            # 初始化角色表
            self.chartab.execute()
            # 初始化log文件
            self.rplgenlog.execute(media_define=self.medef,char_table=self.chartab,config=self.pconfig)
        except Exception as E:
            print(E)
    def preview_display(self):
        self.load_input()
        try:
            PreviewDisplay(rplgenlog=self.rplgenlog,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            pygame.init()
            pygame.font.init()
    def export_video(self):
        try:
            self.load_input()
            ExportVideo(rplgenlog=self.rplgenlog,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            pygame.init()
            pygame.font.init()
    def export_xml(self):
        try:
            # 调整全局变量
            MediaObj.export_xml = True
            MediaObj.output_path = './test_output'
            self.load_input()
            ExportXML(rplgenlog=self.rplgenlog,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            # 复原全局变量
            pygame.init()
            pygame.font.init()
            MediaObj.export_xml = False
    def open_new_thread(self,output_type:str):
        # 先切换到终端页
        self.winfo_toplevel().navigate_bar.press_button('console')
        # 检查是否有正在执行的
        if self.runing_thread is None:
            pass
        elif self.runing_thread.is_alive():
            print("正在执行中")
            return
        # 新建线程：FIXME：重复两次开始预览播放，可能导致闪退，考虑改为多进程。
        if output_type == 'display':
            self.runing_thread = threading.Thread(target=self.preview_display)
        elif output_type == 'exportpr':
            self.runing_thread = threading.Thread(target=self.export_xml)
        elif output_type == 'recode':
            self.runing_thread = threading.Thread(target=self.export_video)
        else:
            self.runing_thread = threading.Thread(target=lambda:print("无效的执行"))
        # 开始执行
        self.runing_thread.start()

