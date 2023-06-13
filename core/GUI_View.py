#!/usr/bin/env python
# coding: utf-8

# 视图：每个导航栏的按钮对应一个视图。
# 视图包括：

# 项目视图：浏览、编辑、预览、使用RplGenProJect的视图
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from PIL import Image, ImageTk
from .GUI_FileManager import FileManager
from .GUI_TabPage import PageFrame
from .GUI_Terminal import Terminal
from .GUI_TableSet import ScriptExecuter, PreferenceTable
from .GUI_Util import Texture
from .GUI_DialogWindow import browse_file
from .GUI_VoiceChooser import VoiceChooser
# 脚本视图：运行 MDF、CTB、RGL 脚本文件的视图。
# 控制台视图：容纳控制台输出内容的视图。
# 首选项视图：设置整个程序的首选项的视图。

# TODO：空白的项目视图（打开项目、新建空白项目、新建智能工程）（初始化+新建的流程）
# 空白的项目视图
class EmptyView(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
        # 缩放比例
        self.sz = screenzoom
        SZ_150 = int(self.sz * 150)
        SZ_10 = int(self.sz * 10)
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 子原件
        icon_size = (SZ_150, SZ_150)
        self.texture = Texture(master=self, screenzoom=self.sz, file='./media/icon/texture3.png')
        self.content = ttk.Frame(master=self,padding=SZ_10)
        self.image = {
            'open_p' : ImageTk.PhotoImage(name='open_p',  image=Image.open('./media/icon/open.png').resize(icon_size)),
            'new_p'  : ImageTk.PhotoImage(name='new_p',   image=Image.open('./media/icon/new.png').resize(icon_size)),
            'intel_p': ImageTk.PhotoImage(name='intel_p', image=Image.open('./media/icon/intel.png').resize(icon_size)),
        }
        self.open_project_buttons = {
            'open_p' : ttk.Button(master=self.content, text='打开项目',     compound='top', image='open_p' ,bootstyle='info',command=self.open_project),
            'new_p'  : ttk.Button(master=self.content, text='新建空白项目', compound='top', image='new_p'  ,bootstyle='info',command=self.new_project),
            'intel_p': ttk.Button(master=self.content, text='新建智能项目', compound='top', image='intel_p',bootstyle='info',command=self.intel_project),
        }
        self.update_items()
    def update_items(self):
        self.texture.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.content.place(relx=0.25,rely=0.3,relwidth=0.5,relheight=0.3)
        for keyword in self.open_project_buttons:
            SZ_10 = int(self.sz * 10)
            this_button:ttk.Button = self.open_project_buttons[keyword]
            this_button.pack(side='left', fill='both',expand=True,padx=SZ_10,pady=SZ_10)
    def open_project(self):
        get_file:str = browse_file(master=self.winfo_toplevel(),text_obj=tk.StringVar(),method='file',filetype='rplgenproj')
        if get_file != '':
            try:
                PView = ProjectView(master=self.master,screenzoom=self.sz,project_file=get_file)
                self.master.view['project'] = PView
                self.place_forget()
                self.master.view_show('project')
                self.destroy()
            except Exception as E:
                Messagebox().show_error(message='无法读取工程文件，该文件可能已损坏。',title='打开失败',parent=self.winfo_toplevel())
    def new_project(self):
        pass
    def intel_project(self):
        pass
# 项目视图
class ProjectView(ttk.Frame):
    """
    各个元件的尺寸：以100%缩放为准
    -----
    1. 资源管理器：宽300，高无限
    2. 页标签：高30，宽无限-30
    3. 页内容：高无限-30，宽无限-30
    """
    def __init__(self,master,screenzoom,project_file:str)->None:
        # 缩放比例
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 子元件
        self.page_frame    = PageFrame(master=self,screenzoom=self.sz)
        self.file_manager  = FileManager(master=self, screenzoom=self.sz, page_frame=self.page_frame, project_file=project_file)
        # 摆放子元件
        self.update_item()
    def update_item(self):
        SZ_300 = int(self.sz * 300)
        self.file_manager.place(x=0,y=0,width=SZ_300,relheight=1)
        self.page_frame.place(x=SZ_300,y=0,relheight=1,relwidth=1,width=-SZ_300)

# 脚本视图
class ScriptView(ttk.Frame):
    """
    各个元件的尺寸：以100%缩放为准
    -----
    1. ScriptExecuter：宽无线*0.6，高无限-50
    2. 按键：高50，宽无限100
    """
    def __init__(self,master,screenzoom)->None:
        # 初始化
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 子原件
        self.texture = Texture(master=self, screenzoom=self.sz, file='./media/icon/texture2.png')
        self.content = ScriptExecuter(master=self,screenzoom=self.sz)
        # 更新
        self.update_item()
    def update_item(self):
        self.texture.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.content.place(relx=0.2,y=0,relwidth=0.6,relheight=1)
# 控制台视图
class ConsoleView(ttk.Frame):
    """
    各个元件的尺寸：以100%缩放为准
    -----
    1. terminal：宽无线/2，高无限-50
    2. 按键：高50，宽无限100
    """
    def __init__(self,master,screenzoom)->None:
        # 初始化
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 子原件
        self.texture = Texture(master=self, screenzoom=self.sz, file='./media/icon/texture4.png')
        self.terminal = VoiceChooser(master=self,screenzoom=self.sz,voice='Azure::zh-CN-YunxiNeural:assistant:1.0:Boy',speech_rate=30,pitch_rate=-70)
        # self.terminal = Terminal(master=self,screenzoom=self.sz)
        # 更新
        self.update_item()
    def update_item(self):
        self.texture.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.terminal.place(relx=0.2,y=0,relwidth=0.6,relheight=1)
# 首选项视图
class PreferenceView(ttk.Frame):
    """
    各个元件的尺寸：以100%缩放为准
    -----
    1. Preference：宽无线*0.6，高无限-50
    2. 按键：高50，宽无限100
    """
    def __init__(self,master,screenzoom)->None:
        # 初始化
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 子原件
        self.texture = Texture(master=self, screenzoom=self.sz, file='./media/icon/texture1.png')
        self.content = PreferenceTable(master=self,screenzoom=self.sz)
        # 更新
        self.update_item()
    def update_item(self):
        self.texture.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.content.place(relx=0.2,y=0,relwidth=0.6,relheight=1)