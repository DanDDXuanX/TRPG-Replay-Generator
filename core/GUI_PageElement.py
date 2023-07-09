#!/usr/bin/env python
# coding: utf-8

# 页面的其他公用元件
# 包含：搜索栏、输出命令按钮

import tkinter as tk
import ttkbootstrap as ttk
import threading
import pygame
from ttkbootstrap.tooltip import ToolTip
from PIL import Image, ImageTk
from .GUI_Container import Container
from .GUI_EditTableStruct import NewElement
from .OutputType import PreviewDisplay, ExportVideo, ExportXML
from .SpeechSynth import SpeechSynthesizer
from .Medias import MediaObj
from .ScriptParser import Script
from .GUI_Link import Link
from .GUI_Util import FreeToolTip

# 搜索窗口
class SearchBar(ttk.Frame):
    def __init__(self,master,container:Container,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=int(5*self.sz))
        # 关联容器
        self.container = container
        # 元件
        self.search_text = tk.StringVar(master=self,value='')
        self.is_regex = tk.BooleanVar(master=self,value=False)
        self.left = {
            'entry' : ttk.Entry(master=self,width=30,textvariable=self.search_text),
            'regex' : ttk.Checkbutton(master=self, text='正则', bootstyle='round-toggle', variable=self.is_regex),
            'search' : ttk.Button(master=self,text='搜索',command=self.click_search,bootstyle='primary')
        }
        self.right = {
            'clear' : ttk.Button(master=self,text='清除',command=self.click_clear),
            'info'  : ttk.Label(master=self,text='(无)'),
        }
        self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * 5)
        for key in self.left:
            item:ttk.Button = self.left[key]
            item.pack(padx=[SZ_5,0], fill='y',side='left')
        for key in self.right:
            item:ttk.Button = self.right[key]
            item.pack(padx=[0,SZ_5], fill='y',side='right')
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
            'synth'     : ImageTk.PhotoImage(name='synth',image=Image.open('./media/icon/synth.png').resize(icon_size)),
            'exportpr'  : ImageTk.PhotoImage(name='exportpr', image=Image.open('./media/icon/premiere.png').resize(icon_size)),
            'recode'    : ImageTk.PhotoImage(name='recode',image=Image.open('./media/icon/ffmpeg.png').resize(icon_size)),
        }
        self.buttons = {
            'display'   : ttk.Button(master=self,image='display',text='播放预览',compound='left',style='output.TButton',command=lambda:self.open_new_thread('display')),
            'synth'     : ttk.Button(master=self,image='synth',text='语音合成',compound='left',style='output.TButton',command=lambda:self.open_new_thread('synth')),
            'exportpr'    : ttk.Button(master=self,image='exportpr',text='导出PR工程',compound='left',style='output.TButton',command=lambda:self.open_new_thread('exportpr')),
            'recode'    : ttk.Button(master=self,image='recode',text='导出视频',compound='left',style='output.TButton',command=lambda:self.open_new_thread('recode')),
        }
        self.runing_thread = None
        self.update_item()
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='left',expand=True,pady=0)
    def load_input(self):
        # 项目配置
        self.pconfig = Link['project_config']
        # 脚本
        self.medef = self.page.ref_medef.copy()
        self.chartab = self.page.ref_chartab.copy()
        self.rplgenlog = self.page.content.copy()
        # 初始化配置项
        self.pconfig.execute()
        # 初始化媒体
        self.medef.execute()
        # 初始化角色表
        self.chartab.execute()
        # 初始化log文件
        self.rplgenlog.execute(media_define=self.medef,char_table=self.chartab,config=self.pconfig)
    def preview_display(self):
        try:
            self.load_input()
            print('X')
            PreviewDisplay(rplgenlog=self.rplgenlog,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            pygame.init()
            pygame.font.init()
            self.winfo_toplevel().navigate_bar.enable_navigate()
    def synth_speech(self):
        # 项目配置
        self.pconfig = Link['project_config']
        # 脚本
        self.medef = self.page.ref_medef.copy()
        self.chartab = self.page.ref_chartab.copy()
        # 注意，log不是copy，是实质上要修改内容的！
        self.rplgenlog = self.page.content
        try:
            SpeechSynthesizer(rplgenlog=self.rplgenlog,chartab=self.chartab,mediadef=self.medef,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            self.winfo_toplevel().navigate_bar.enable_navigate()
    def export_video(self):
        try:
            self.load_input()
            ExportVideo(rplgenlog=self.rplgenlog,config=self.pconfig,output_path='./test_output')
        except Exception as E:
            print(E)
        finally:
            pygame.init()
            pygame.font.init()
            self.winfo_toplevel().navigate_bar.enable_navigate()
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
            self.winfo_toplevel().navigate_bar.enable_navigate()
    def open_new_thread(self,output_type:str):
        # 先切换到终端页
        self.winfo_toplevel().navigate_bar.press_button('console')
        self.winfo_toplevel().navigate_bar.disable_navigate()
        # 检查是否有正在执行的
        if self.runing_thread is None:
            pass
        elif self.runing_thread.is_alive():
            print("正在执行中")
            return
        # 新建线程：FIXME：重复两次开始预览播放，可能导致闪退，考虑改为多进程。
        if output_type == 'display':
            self.runing_thread = threading.Thread(target=self.preview_display)
        elif output_type == 'synth':
            self.runing_thread = threading.Thread(target=self.synth_speech)
        elif output_type == 'exportpr':
            self.runing_thread = threading.Thread(target=self.export_xml)
        elif output_type == 'recode':
            self.runing_thread = threading.Thread(target=self.export_video)
        else:
            self.runing_thread = threading.Thread(target=lambda:print("无效的执行"))
        # 开始执行
        self.runing_thread.start()
class VerticalOutputCommand(OutPutCommand):
    def __init__(self,master,screenzoom):
        # 继承
        super().__init__(master=master,screenzoom=screenzoom)
        self.tooltip = {
            'display'   : FreeToolTip(widget=self.buttons['display'],bootstyle='primary-inverse',text='播放预览',screenzoom=self.sz,side='left'),
            'synth'     : FreeToolTip(widget=self.buttons['synth'],bootstyle='primary-inverse',text='语音合成',screenzoom=self.sz,side='left'),
            'exportpr'  : FreeToolTip(widget=self.buttons['exportpr'],bootstyle='primary-inverse',text='导出PR项目',screenzoom=self.sz,side='left'),
            'recode'    : FreeToolTip(widget=self.buttons['recode'],bootstyle='primary-inverse',text='导出视频',screenzoom=self.sz,side='left'),
        }
        SZ_5 = int(self.sz * 5)
        self.configure(borderwidth=SZ_5,bootstyle='light')
        # 要有边框
        for keyword in self.buttons:
            self.buttons[keyword].configure(text='',compound='center',padding=SZ_5)
    def update_item(self):
        SZ_5 = int(self.sz * 5)
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='x',anchor='n',side='top',pady=(0,SZ_5))
    # TODO: 因为垂直输出命令，涉及的是CodeView，因此在导出前应该添加：将CodeView的内容更新到RGL
    def preview_display(self):
        return super().preview_display()
    def export_video(self):
        return super().export_video()
    def export_xml(self):
        return super().export_xml()
    # TODO：因为语音合成涉及到RGL的改变，因此执行成功之后，应该返回给RGL对象，并更新给CodeView！
    def synth_speech(self):
        return super().synth_speech()
# 新建指令
class NewElementCommand(ttk.Frame):
    struct = NewElement
    def __init__(self,master,screenzoom,pagetype):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 引用
        self.page = self.master
        self.container = self.page.container
        self.pagetype = pagetype
        self.section_struct = self.struct[self.pagetype]
        # 初始化的容器
        self.image = {}
        self.buttons = {}
        self.buttons_tooltip = {}
        # 载入表结构
        self.init_buttons()
        self.update_item()
    def init_buttons(self):
        icon_size = [int(30*self.sz),int(30*self.sz)]
        for keyword in self.section_struct:
            button_this = self.section_struct[keyword]
            # 新建按钮绑定的命令
            new_element = self.create_command(button_this=button_this,keyword=keyword)
            # 按钮
            self.buttons[keyword] = ttk.Button(
                master=self,
                # image='display',
                text=button_this['text'],
                compound='left',
                style='output.TButton',
                width=5,
                command=new_element
            )
            self.buttons_tooltip[keyword] = FreeToolTip(
                widget=self.buttons[keyword],
                text=button_this['tooltip'],
                bootstyle='secondary-inverse',
                screenzoom=self.sz,
                side='up'
            )
    # 生成按钮命令的闭包
    def create_command(self,button_this,keyword):
        def command():
            if self.pagetype == 'charactor':
                name_this = self.container.name
                element_name = self.page.content.new_subtype(name=name_this,subtype='新建差分')
            elif self.pagetype in Script.Media_type:
                element_name = self.page.content.new_element(name='新建'+button_this['text'],element_type=keyword)
            else:
                pass
            # 新建原件
            self.container.new_section(key=element_name)
        return command
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='left',expand=True,pady=0)