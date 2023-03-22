#!/usr/bin/env python
# coding: utf-8

import sys

import numpy as np
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from PIL import Image, ImageTk

from .ProjConfig import Preference
from .ScriptParser import RplGenLog,CharTable,MediaDef
from .Utils import EDITION
from .FilePaths import Filepath
from .Medias import MediaObj

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
        # 样式
        SZ_3 = int(3 * self.sz)
        SZ_5 = int(5 * self.sz)
        text_label_pad = (SZ_5,0,SZ_5,0)
        # 导航栏的按钮
        self.style.configure('secondary.TButton',anchor='w',font="-family 微软雅黑 -size 20 -weight bold",compound='left',padding=(SZ_3,0,0,0))
        self.style.configure('output.TButton',compound='left',font="-family 微软雅黑 -size 14 -weight bold")
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
        # 导航栏
        self.navigate_bar = NavigateBar(master=self,screenzoom=self.sz)
        self.navigate_bar.place(x=0,y=0,width=100*self.sz,relheight=1)
        # event
        self.navigate_bar.bind('<ButtonRelease-1>', self.navigateBar_get_click)
        # 视图
        self.view = {
            'project': ProjectView(master=self,screenzoom=self.sz)
            }
        self.view_show('project')
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

# 导航栏，最右
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

# 项目视图
class ProjectView(ttk.Frame):
    """
    各个元件的尺寸：以100%缩放为准
    -----
    1. 资源管理器：宽300，高无限
    2. 页标签：高30，宽无限-30
    3. 页内容：高无限-30，宽无限-30
    """
    def __init__(self,master,screenzoom)->None:
        # 缩放比例
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 子元件
        self.file_manager  = FileManager(master=self, screenzoom=self.sz)
        self.page_notebook = PageNotes(master=self, screenzoom=self.sz)
        self.page_view     = RGLPage(master=self, screenzoom=self.sz, rgl = RplGenLog(file_input=r"./toy/LogFile.rgl"))
        # elf.page_view = MDFPage(master=self, screenzoom=self.sz ,mdf=MediaDef(file_input=r"E:\Data\20220419_星尘的研究\project\Research-of-Stardust\medef.txt"),media_type='Animation')
        # self.page_view = MDFPage(master=self, screenzoom=self.sz ,mdf=MediaDef(file_input="./toy/MediaObject.txt"),media_type='Bubble')
        # 摆放子元件
        self.update_item()
    def update_item(self):
        SZ_300 = int(self.sz * 300)
        SZ_30 = int(self.sz * 30)
        self.file_manager.place(x=0,y=0,width=SZ_300,relheight=1)
        self.page_notebook.place(x=SZ_300,y=0,height=SZ_30,relwidth=1,width=-SZ_300)
        self.page_view.place(x=SZ_300,y=SZ_30,relheight=1,height=-SZ_30,relwidth=1,width=-SZ_300)

# 项目视图-文件管理器
class FileManager(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        self.master = master
        # 图形
        SZ_30 = int(self.sz * 30)
        SZ_300 = int(self.sz * 300)
        SZ_180 = int(self.sz * 180)
        icon_size = [SZ_30,SZ_30]
        self.image = {
            'title'     : ImageTk.PhotoImage(name='title',   image=Image.open('./toy/media/bg1.jpg').resize([SZ_300,SZ_180])),
            'save'      : ImageTk.PhotoImage(name='save' ,   image=Image.open('./media/icon/save.png').resize(icon_size)),
            'config'    : ImageTk.PhotoImage(name='config',   image=Image.open('./media/icon/setting.png').resize(icon_size)),
            'import'    : ImageTk.PhotoImage(name='import',   image=Image.open('./media/icon/import.png').resize(icon_size)),
            'export'    : ImageTk.PhotoImage(name='export',   image=Image.open('./media/icon/export.png').resize(icon_size)),
        }
        # 标题
        self.project_title = ttk.Frame(master=self,borderwidth=0,bootstyle='light')
        self.title_pic = ttk.Label(master=self.project_title,image='title',borderwidth=0)
        self.buttons = {
            'save'      : ttk.Button(master=self.project_title,image='save'  ),
            'config'    : ttk.Button(master=self.project_title,image='config'),
            'import'    : ttk.Button(master=self.project_title,image='import'),
            'export'    : ttk.Button(master=self.project_title,image='export'),
        }
        # 放置
        self.title_pic.pack(fill='none',side='top')
        for idx,key in enumerate(self.buttons):
            buttons:ttk.Button = self.buttons[key]
            buttons.pack(expand=True,fill='x',side='left',anchor='se',padx=0,pady=0)
        self.project_title.pack(fill='x',side='top',padx=0,pady=0,ipadx=0,ipady=0)
        # 文件内容
        self.project_contene = ScrolledFrame(master=self,borderwidth=0,bootstyle='light',autohide=True)
        self.project_contene.vscroll.config(bootstyle='warning-round')
        self.items = {
            'mediadef'  : MDFCollapsing(master=self.project_contene,screenzoom=self.sz,content=MediaDef()),
            'chartab'   : CTBCollapsing(master=self.project_contene,screenzoom=self.sz,content=CharTable(file_input = './toy/CharactorTable.tsv')),
            'rplgenlog' : RGLCollapsing(master=self.project_contene,screenzoom=self.sz,content=RplGenLog()),
        }
        # 放置
        self.update_item()
        self.project_contene.pack(fill='both',expand=True,side='top')
    def update_item(self):
        for idx,key in enumerate(self.items):
            fileitem:ttk.Button = self.items[key]
            fileitem.pack(fill='x',pady=0,side='top')
# 项目视图-可折叠类容器
class FileCollapsing(ttk.Frame):
    def __init__(self,master,screenzoom:float,fileclass:str,content):
        self.sz = screenzoom
        SZ_5 = int(self.sz * 5)
        SZ_2 = int(self.sz * 2)
        super().__init__(master=master,borderwidth=0)
        self.class_text = {'mediadef':'媒体库','chartab':'角色配置','rplgenlog':'剧本文件'}[fileclass]
        self.collapbutton = ttk.Button(master=self,text=self.class_text,command=self.update_toggle,bootstyle='warning')
        self.content_frame = ttk.Frame(master=self)
        self.button_padding = (SZ_5,SZ_2,SZ_5,SZ_2)
        self.items = {}
        # self.update_item()
    def update_item(self):
        for idx in self.items:
            this_button = self.items[idx]
            this_button.pack(fill='x',side='top')
        self.collapbutton.pack(fill='x',side='top')
        self.expand:bool = False
        self.update_toggle()
    def update_toggle(self):
        if self.expand:
            self.content_frame.pack_forget()
            self.expand:bool = False
        else:
            self.content_frame.pack(fill='x',side='top')
            self.expand:bool = True
class MDFCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content):
        super().__init__(master, screenzoom, 'mediadef', content)
        self.items = {
            'Pos'       :   ttk.Button(master=self.content_frame,text='位置 (Pos)',bootstyle='light',padding=self.button_padding,compound='left'),
            'Animation' :   ttk.Button(master=self.content_frame,text='立绘 (Animation)',bootstyle='light',padding=self.button_padding,compound='left'),
            'Bubble'    :   ttk.Button(master=self.content_frame,text='气泡 (Bubble)',bootstyle='light',padding=self.button_padding,compound='left'),
            'Background':   ttk.Button(master=self.content_frame,text='背景 (Background)',bootstyle='light',padding=self.button_padding,compound='left'),
            'Audio'     :   ttk.Button(master=self.content_frame,text='音频 (Audio)',bootstyle='light',padding=self.button_padding,compound='left'),
        }
        self.update_item()
class CTBCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:CharTable):
        super().__init__(master, screenzoom, 'chartab', content)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0)
        self.add_button.pack(side='right',padx=SZ_10,pady=SZ_5,ipady=SZ_1,ipadx=SZ_3)
        self.table = content.export()
        self.items = {}
        for name in self.table['Name'].unique():
            self.items[name] = ttk.Button(master=self.content_frame,text=name,bootstyle='light',padding=self.button_padding,compound='left')
        self.update_item()
class RGLCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:RplGenLog):
        super().__init__(master, screenzoom, 'rplgenlog', content)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0)
        self.add_button.pack(side='right',padx=SZ_10,pady=SZ_5,ipady=SZ_1,ipadx=SZ_3)
        self.items = {
            '1'     :   ttk.Button(master=self.content_frame,text='第1集',bootstyle='light',padding=self.button_padding,compound='left'),
            '2'     :   ttk.Button(master=self.content_frame,text='第2集',bootstyle='light',padding=self.button_padding,compound='left'),
            '3'     :   ttk.Button(master=self.content_frame,text='第3集',bootstyle='light',padding=self.button_padding,compound='left'),
        }
        self.update_item()
# 项目视图-页面标签
class PageNotes(ttk.Frame):
    """
    相对布局对象，不考虑缩放比例
    """
    def __init__(self,master,screenzoom)->None:
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='secondary')
        self.master = master
        self.active_page = {
            '1': TabNote(master=self,text='媒体库',bootstyle='primary',screenzoom=self.sz),
            '2': TabNote(master=self,text='角色配置',bootstyle='primary',screenzoom=self.sz),
            '3': TabNote(master=self,text='剧本',bootstyle='primary',screenzoom=self.sz),
        }
        self.update_item()
    def update_item(self):
        SZ_1 = int(self.sz * 1)
        for idx,key in enumerate(self.active_page):
            page_label:ttk.Button = self.active_page[key]
            page_label.pack(fill='y',padx=SZ_1,side='left',pady=0)
# 项目视图-页面标签-标签
class TabNote(ttk.Button):
    def __init__(self,master,screenzoom,text,bootstyle)->None:
        self.sz = screenzoom
        SZ_5 = int(self.sz * 5)
        SZ_21 = int(self.sz * 21)
        SZ_24 = int(self.sz * 24)
        SZ_30 = int(self.sz * 30)
        super().__init__(master,bootstyle=bootstyle,text=text,compound='left',padding=(SZ_5,SZ_5,SZ_30,SZ_5),command=self.get_pressed)
        self.bootstyle = bootstyle
        self.is_change = tk.StringVar(master=self,value='×')
        self.dele = ttk.Button(master=self,textvariable=self.is_change,bootstyle=bootstyle,padding=0,command=self.set_change)
        self.dele.place(x=-SZ_24,relx=1,rely=0.15,width=SZ_21,relheight=0.70)
    def set_change(self):
        if self.is_change.get() == '×':
            self.is_change.set('●')
        else:
            self.is_change.set('×')
    def get_pressed(self):
        # 复原所有已点击
        for key in self.master.active_page:
            this_tab = self.master.active_page[key].recover()
        self.config(bootstyle='light')
        self.dele.config(bootstyle='light')
    def recover(self):
        self.config(bootstyle=self.bootstyle)
        self.dele.config(bootstyle=self.bootstyle)
        
# 页面视图：Log文件
class RGLPage(ttk.Frame):
    def __init__(self,master,screenzoom,rgl:RplGenLog):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        # 元件
        self.searchbar = SearchBar(master=self,screenzoom=self.sz)
        self.container = RGLContainer(master=self,content=rgl,screenzoom=self.sz)
        self.outputcommand = OutPutCommand(master=self,screenzoom=self.sz)
        self.preview = PreviewCanvas(master=self,screenzoom=self.sz)
        self.edit = EditWindow(master=self,screenzoom=self.sz,section=rgl.struct['0'])
        # 放置元件
        SZ_40 = int(self.sz * 40)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-2*SZ_40)
        self.outputcommand.place(x=0,y=-SZ_40,rely=1,relwidth=0.5,height=SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.5)
        self.edit.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.5)
# 页面视图：媒体定义文件
class MDFPage(ttk.Frame):
    categroy_dict = {
        'Pos'       : ['Pos','FreePos','PosGrid'],
        'Animation' : ['Animation'],
        'Bubble'    : ['Bubble','Balloon','DynamicBubble','ChatWindow'],
        'Background': ['Background'],
        'Audio'     : ['Audio','BGM'],
    }
    def __init__(self,master,screenzoom,mdf:MediaDef,media_type='Animation'):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='primary')
        # 元件
        self.searchbar = SearchBar(master=self,screenzoom=self.sz)
        self.container = MDFContainer(master=self,content=mdf,typelist=self.categroy_dict[media_type],screenzoom=self.sz)
        self.preview = PreviewCanvas(master=self,screenzoom=self.sz)
        self.edit = EditWindow(master=self,screenzoom=self.sz,section=mdf.struct['0'])
        # 放置元件
        SZ_40 = int(self.sz * 40)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-SZ_40)
        self.preview.place(relx=0.5,rely=0,relwidth=0.5,relheight=0.5)
        self.edit.place(relx=0.5,rely=0.5,relwidth=0.5,relheight=0.5)
# 搜索窗口
class SearchBar(ttk.Frame):
    def __init__(self,master,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=int(5*self.sz),bootstyle='light')
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
    def click_clear(self):
        self.right['info'].config(text = '(无)')
# 输出指令
class OutPutCommand(ttk.Frame):
    def __init__(self,master,screenzoom):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        icon_size = [int(30*self.sz),int(30*self.sz)]
        self.image = {
            'display'   : ImageTk.PhotoImage(name='display',image=Image.open('./media/icon/display.png').resize(icon_size)),
            'exportpr'    : ImageTk.PhotoImage(name='exportpr', image=Image.open('./media/icon/premiere.png').resize(icon_size)),
            'recode'   : ImageTk.PhotoImage(name='recode',image=Image.open('./media/icon/ffmpeg.png').resize(icon_size)),
        }
        self.buttons = {
            'display' : ttk.Button(master=self,image='display',text='播放预览',compound='left',style='output.TButton'),
            'export'  : ttk.Button(master=self,image='exportpr',text='导出PR工程',compound='left',style='output.TButton'),
            'recode'  : ttk.Button(master=self,image='recode',text='导出视频',compound='left',style='output.TButton'),
        }
        self.update_item()
        
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='left',expand=True,pady=0)
# 容纳内容的滚动Frame
class RGLContainer(ScrolledFrame):
    def __init__(self,master,content:RplGenLog,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master, padding=3, bootstyle='light', autohide=True)
        self.vscroll.config(bootstyle='primary-round')
        self.container.config(bootstyle='light',takefocus=True)
        # 按键绑定
        self.container.bind('<Control-Key-a>',lambda event:self.select_range(event,index=False),"+")
        # 滚动条容器的内容物
        self.content = content
        # 根据内容物，调整容器总高度
        self.config(height=int(60*self.sz)*len(self.content.struct))
        # 容器内的元件
        self.element = {}
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            self.element[key] = RGLSectionElement(
                master=self,
                bootstyle='primary',
                text=key,
                section=this_section,
                screenzoom=self.sz)
        # 当前选中的对象
        self.selected:list = []
        # 将内容物元件显示出来
        self.update_item()
    def update_item(self):
        SZ_60 = int(self.sz * 60)
        SZ_55 = int(self.sz * 55)
        sz_10 = int(self.sz * 10)
        for idx,key in enumerate(self.element):
            this_section_frame:ttk.LabelFrame = self.element[key]
            this_section_frame.place(x=0,y=idx*SZ_60,width=-sz_10,height=SZ_55,relwidth=1)
    def select_item(self,event,index,add=False):
        self.container.focus_set()
        # 根据点击的y，定位本次选中的
        selected_idx = index
        if selected_idx in self.element.keys():
            if add is not True:
                # 先清空选中的列表
                for idx in self.selected:
                    self.element[idx].drop_select()
                self.selected.clear()
            # 添加本次选中的
            self.element[selected_idx].get_select()
            self.selected.append(selected_idx)
    def select_range(self,event,index:str):
        self.container.focus_set()
        if index == False:
            effect_range = self.element.keys()
        else:
            # 上一个选中的，数字序号
            last_selected_idx:int = int(self.selected[-1]) # 最后一个
            # 本次选中的，数字序号
            this_selected_idx:int = int(index)
            # 正序或是倒序
            effect_range = range(this_selected_idx,last_selected_idx,{True:1,False:-1}[last_selected_idx>=this_selected_idx])
        for idx in effect_range:
            self.select_item(event=event,index=str(idx),add=True)
class MDFContainer(ScrolledFrame):
    def __init__(self,master,content:MediaDef,typelist:list,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master, padding=3, bootstyle='light', autohide=True)
        self.vscroll.config(bootstyle='primary-round')
        self.container.config(bootstyle='light',takefocus=True)
        # 按键绑定
        self.container.bind('<Control-Key-a>',lambda event:self.select_range(event,index=False),"+")
        # 滚动条容器的内容物
        self.content = content
        # 根据内容物，调整容器总高度
        # 容器内的元件
        self.element = {}
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            if this_section['type'] not in typelist:
                continue
            self.element[key] = MDFSectionElement(
                master=self,
                bootstyle='secondary',
                text=key,
                section=this_section,
                screenzoom=self.sz)
        self.config(height=int(200*self.sz*np.ceil(len(self.element)/3)))
        # 当前选中的对象
        self.selected:list = []
        # 将内容物元件显示出来
        self.update_item()
    def update_item(self):
        SZ_100 = int(self.sz * 200)
        SZ_95 = int(self.sz * 190)
        sz_10 = int(self.sz * 10)
        for idx,key in enumerate(self.element):
            this_section_frame:ttk.LabelFrame = self.element[key]
            this_section_frame.place(relx=idx%3 * 0.33,y=idx//3*SZ_100,width=-sz_10,height=SZ_95,relwidth=0.33)
    def select_item(self,event,index,add=False):
        self.container.focus_set()
        # 根据点击的y，定位本次选中的
        selected_idx = index
        if selected_idx in self.element.keys():
            if add is not True:
                # 先清空选中的列表
                for idx in self.selected:
                    self.element[idx].drop_select()
                self.selected.clear()
            # 添加本次选中的
            self.element[selected_idx].get_select()
            self.selected.append(selected_idx)
    def select_range(self,event,index:str):
        self.container.focus_set()
        if index == False:
            effect_range = self.element.keys()
        else:
            # 上一个选中的，数字序号
            last_selected_idx:int = int(self.selected[-1]) # 最后一个
            # 本次选中的，数字序号
            this_selected_idx:int = int(index)
            # 正序或是倒序
            effect_range = range(this_selected_idx,last_selected_idx,{True:1,False:-1}[last_selected_idx>=this_selected_idx])
        for idx in effect_range:
            self.select_item(event=event,index=str(idx),add=True)
# 容器中的每个小节
class RGLSectionElement(ttk.LabelFrame):
    RGLscript = RplGenLog()
    def __init__(self,master,bootstyle,text,section:dict,screenzoom):
        self.sz = screenzoom
        self.line_type = section['type']
        self.idx = text # 序号
        super().__init__(master=master,bootstyle=bootstyle,text=text,labelanchor='e')
        # 从小节中获取文本
        self.update_text_from_section(section=section)
        self.items = {
            'head' : ttk.Label(master=self,text=self.header,anchor='w',style=self.hstyle+'.TLabel'),
            'sep'  : ttk.Separator(master=self),
            'main' : ttk.Label(master=self,text=self.main,anchor='w',style=self.mstyle+'.TLabel'),
        }
        self.select_symbol = ttk.Frame(master=self,bootstyle='primary')
        self.update_item()
    def update_text_from_section(self,section):
        # 确认显示内容
        if   self.line_type == 'blank':
            self.header = '空行'
            self.main = ''
            self.hstyle = 'comment'
            self.mstyle = 'ingore'
        elif self.line_type == 'comment':
            self.header = '# 注释'
            self.main = section['content']
            self.hstyle = 'comment'
            self.mstyle = 'ingore'
        elif self.line_type == 'dialog':
            # 如果是默认，那么仅显示名字
            if section['charactor_set']['0']['subtype'] == 'default':
                self.header = '[{}]'.format(
                    section['charactor_set']['0']['name']
                )
            else:
                self.header = '[{}.{}]'.format(
                    section['charactor_set']['0']['name'],
                    section['charactor_set']['0']['subtype']
                    )
            # 主文本
            self.main = section['content']
            self.hstyle = 'dialog'
            self.mstyle = 'main'
            # 显示星标
            if '*' in section['sound_set'].keys():
                self.header = '★ ' + self.header
            elif '{*}' in section['sound_set'].keys():
                self.header = '★ ' + self.header
                self.hstyle = 'invasterisk'
            else:
                self.mstyle = 'main'
        elif self.line_type == 'background':
            self.header = '<放置背景>'
            self.main = section['object']
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'animation':
            self.header = '<放置立绘>'
            self.main = self.RGLscript.anime_export(section['object'])
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'bubble':
            self.header = '<放置气泡>'
            self.main = self.RGLscript.bubble_export(section['object'])
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'set':
            target,unit = {
                #默认切换效果（立绘）
                'am_method_default' : ['默认切换效果-立绘',''],
                #默认切换效果持续时间（立绘）
                'am_dur_default'    : ['默认切换时间-立绘',' 帧'],
                #默认切换效果（文本框）
                'bb_method_default' : ['默认切换效果-气泡',''],
                #默认切换效果持续时间（文本框）
                'bb_dur_default'    : ['默认切换时间-气泡',' 帧'],
                #默认切换效果（背景）
                'bg_method_default' : ['默认切换效果-背景',''],
                #默认切换时间（背景）
                'bg_dur_default'    : ['默认切换时间-背景',' 帧'],
                #默认文本展示方式
                'tx_method_default' : ['默认文本展示效果',''],
                #默认单字展示时间参数
                'tx_dur_default'    : ['默认单字时间',' 帧/字'],
                #语速，单位word per minute
                'speech_speed'      : ['缺省星标时的语速',' 字/分钟'],
                #默认的曲线函数
                'formula'           : ['动画函数的曲线',''],
                # 星标音频的句间间隔 a1.4.3，单位是帧，通过处理delay
                'asterisk_pause'    : ['星标小节的间距时间',' 帧'],
                # a 1.8.8 次要立绘的默认透明度
                'secondary_alpha'   : ['次要角色立绘的默认透明度',' %'],
                # 对话行内指定的方法的应用对象：animation、bubble、both、none
                'inline_method_apply' : ['对话行内效果的应用范围','']
            }[section['target']]
            self.header = '<设置：' + target + '>'
            if section['value_type'] == 'digit':
                value = str(section['value'])
                self.mstyle = 'digit'
            elif section['value_type'] in ['function','enumerate']:
                value = section['value']
                self.mstyle = 'fuction'
            elif section['value_type'] == 'method':
                value = self.RGLscript.method_export(section['value'])
                self.mstyle = 'method'
            else:
                value = '错误'
                self.mstyle = 'exception'
            self.main = value + unit
            # 判断类型
            self.hstyle = 'setdync'
        elif self.line_type == 'move':
            self.header = '<移动：' + section['target'] + '>'
            self.main = self.RGLscript.move_export(section['value'])
            self.hstyle = 'setdync'
            self.mstyle = 'object'
        elif self.line_type == 'table':
            if section['target']['subtype'] is None:
                target = section['target']['name'] +'.'+ section['target']['column']
            else:
                target = section['target']['name'] +'.'+ section['target']['subtype'] +'.'+ section['target']['column']
            self.header = '<表格：' + target + '>'
            self.main = str(section['value'])
            self.hstyle = 'setdync'
            self.mstyle = 'main'
        elif self.line_type == 'music':
            self.header = '<背景音乐>'
            self.main = str(section['value'])
            self.hstyle = 'setdync'
            self.mstyle = 'object'
        elif self.line_type == 'clear':
            self.header = '<清除>'
            self.main = section['object']
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'hitpoint':
            self.header = '<生命动画>'
            self.main = '({},{},{},{})'.format(
                section['content'],
                section['hp_max'],
                section['hp_begin'],
                section['hp_end']
                )
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'dice':
            self.header = '<骰子动画>'
            self.main = self.RGLscript.dice_export(section['dice_set'])
            self.hstyle = 'place'
            self.mstyle = 'object'
        elif self.line_type == 'wait':
            self.header = '<停顿>'
            self.main = str(section['time']) + ' 帧'
            self.hstyle = 'place'
            self.mstyle = 'digit'
    def update_item(self):
        for idx,key in enumerate(self.items):
            this_item:ttk.Label = self.items[key]
            this_item.pack(fill='x',anchor='w',side='top',expand={'head':False,'sep':False,'main':True}[key])
            # 按键点击事件
            this_item.bind('<Button-1>',lambda event:self.master.select_item(event,index=self.idx,add=False))
            this_item.bind('<Control-Button-1>',lambda event:self.master.select_item(event,index=self.idx,add=True))
            this_item.bind('<Shift-Button-1>',lambda event:self.master.select_range(event,index=self.idx))
    def get_select(self):
        SZ_5 = int(self.sz * 5)
        self.select_symbol.place(x=0,y=0,width=SZ_5,relheight=1)
    def drop_select(self):
        self.select_symbol.place_forget()
class MDFSectionElement(ttk.Frame):
    MDFscript = MediaDef()
    thumbnail_image = {}
    thumbnail_name = {}
    thumbnail_idx = 0
    def __init__(self,master,bootstyle,text,section:dict,screenzoom):
        self.sz = screenzoom
        self.line_type = section['type']
        self.name = text # 序号
        super().__init__(master=master,bootstyle=bootstyle,borderwidth=int(1*self.sz))
        # 颜色标签
        if 'label_color' not in section.keys():
            self.labelcolor = 'Lavender'
        elif section['label_color'] is None:
            self.labelcolor = 'Lavender'
        else:
            self.labelcolor = section['label_color']
        # 从小节中获取缩略图
        self.update_image_from_section(section=section)
        self.items = {
            'head' : ttk.Label(master=self,text=self.name,anchor='center',style=self.labelcolor+'.TLabel'),
            'thumbnail' : ttk.Label(master=self,image=self.thumb,anchor='center')
        }
        # 被选中的标志
        self.select_symbol = ttk.Frame(master=self,bootstyle='primary')
        self.update_item()
    def update_image_from_section(self,section):
        icon_size= int(160*self.sz)
        # 确认显示内容:image
        if   self.line_type in ['Animation','Bubble','Balloon','DynamicBubble','ChatWindow','Background']:
            if section['filepath'] in self.thumbnail_name.keys():
                self.thumb = self.thumbnail_name[section['filepath']]
            else:
                # 新建一个缩略图
                if section['filepath'] in [None,'None']:
                    image = Image.new(mode='RGBA',size=(icon_size,icon_size),color=(0,0,0,0))
                elif section['filepath'] in MediaObj.cmap.keys():
                    image = Image.new(mode='RGBA',size=(icon_size,icon_size),color=MediaObj.cmap[filepath])
                else:
                    filepath = Filepath(filepath=section['filepath']).exact()
                    image = Image.open(filepath)
                # 尺寸
                origin_w,origin_h = image.size
                if origin_w > origin_h:
                    icon_width = icon_size
                    icon_height = int(origin_h/origin_w * icon_size)
                else:
                    icon_height = icon_size
                    icon_width = int(origin_w/origin_h * icon_size)
                # 缩略名
                thumbnail_name_this = 'thumbnail%d'%self.thumbnail_idx
                MDFSectionElement.thumbnail_idx += 1
                # 应用
                self.thumbnail_name[section['filepath']] = thumbnail_name_this
                self.thumbnail_image[section['filepath']] = ImageTk.PhotoImage(name=thumbnail_name_this,image=image.resize([icon_width,icon_height]))
                self.thumb = thumbnail_name_this
        elif self.line_type in ['Audio','BGM']:
            if self.line_type not in self.thumbnail_name.keys():
                MDFSectionElement.thumbnail_image['Audio'] = ImageTk.PhotoImage(name='Audio', image=Image.open('./media/icon/audio.png').resize([icon_size,icon_size]))
                MDFSectionElement.thumbnail_image['BGM']   = ImageTk.PhotoImage(name='BGM',   image=Image.open('./media/icon/bgm.png').resize([icon_size,icon_size]))
                self.thumbnail_name['Audio'] = 'Audio'
                self.thumbnail_name['BGM'] = 'BGM'
            self.thumb = self.line_type
    def update_item(self):
        for idx,key in enumerate(self.items):
            this_item:ttk.Label = self.items[key]
            this_item.pack(fill='both',anchor='w',side='top',expand={'head':False,'thumbnail':True}[key])
            # 按键点击事件
            this_item.bind('<Button-1>',lambda event:self.master.select_item(event,index=self.name,add=False))
            this_item.bind('<Control-Button-1>',lambda event:self.master.select_item(event,index=self.name,add=True))
            # this_item.bind('<Shift-Button-1>',lambda event:self.master.select_range(event,index=self.name)) # BUG: 这个现在是不可用的
    def get_select(self):
        SZ_5 = int(self.sz * 5)
        self.select_symbol.place(x=0,y=0,width=SZ_5,relheight=1)
    def drop_select(self):
        self.select_symbol.place_forget()
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
# 编辑窗
class EditWindow(ttk.LabelFrame):
    def __init__(self,master,section,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='编辑区')
        # 小节的数据
        self.section = section
        self.line_type = self.section['type']
        # 组件
        self.elements = {
            'type' : KeyValueDescribe(self,self.sz,key='小节类型',value={'type':'str','style':'combox','value':section['type']},describe={'type':'text','text':'（选择）'})
        }
        self.update_item()
    def update_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.pack(side='top',anchor='n',fill='x')
        # 根据小节类型
        # if self.
        # if self.line_type == 'dialog':
        #     pass
# 一个键、值、描述的最小单位。
class KeyValueDescribe(ttk.Frame):
    def __init__(self,master,screenzoom:float,key:str,value:dict,describe:dict):
        self.sz = screenzoom
        super().__init__(master=master)
        # 关键字
        self.key = ttk.Label(master=self,text=key)
        # 数值类型
        if value['type'] == 'int':
            self.value = tk.IntVar(master=self,value=value['value'])
        elif value['type'] == 'float':
            self.value = tk.DoubleVar(master=self,value=value['value'])
        elif value['type'] == 'bool':
            self.value = tk.BooleanVar(master=self,value=value['value'])
        else:
            self.value = tk.StringVar(master=self,value=value['value'])
        # 容器
        if value['style'] == 'entry':
            self.input = ttk.Entry(master=self,textvariable=self.value,width=30)
        elif value['type'] == 'spine':
            self.input = ttk.Spinbox(master=self,textvariable=self.value,width=30)
        elif value['type'] == 'combox':
            self.input = ttk.Combobox(master=self,textvariable=self.value,width=30)
        else:
            self.input = ttk.Entry(master=self,textvariable=self.value,width=30)
        # 描述
        if describe['type'] == 'text':
            self.describe = ttk.Label(master=self,text=describe['text'])
        else:
            self.describe = ttk.Button(master=self,text=describe['text'])
        # 显示
        self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * 5)
        # 放置
        self.key.pack(fill='none',side='left',padx=SZ_5)
        self.input.pack(fill='x',side='left',padx=SZ_5,expand=True)
        self.describe.pack(fill='none',side='left',padx=SZ_5)
# 脚本视图
class ScriptView(ttk.Frame):
    pass
# 控制台视图
class ConsoleView(ttk.Frame):
    pass
# 首选项视图
class PreferenceView(ttk.Frame):
    pass