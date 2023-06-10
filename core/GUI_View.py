#!/usr/bin/env python
# coding: utf-8

# 视图：每个导航栏的按钮对应一个视图。
# 视图包括：

# 项目视图：浏览、编辑、预览、使用RplGenProJect的视图
from .GUI_FileManager import FileManager
from .GUI_TabPage import PageFrame
from .GUI_Terminal import Terminal
from .GUI_TableSet import ScriptExecuter, PreferenceTable
from .GUI_Util import Texture
# 脚本视图：运行 MDF、CTB、RGL 脚本文件的视图。
# 控制台视图：容纳控制台输出内容的视图。
# 首选项视图：设置整个程序的首选项的视图。

import ttkbootstrap as ttk

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
        self.page_frame    = PageFrame(master=self,screenzoom=self.sz)
        self.file_manager  = FileManager(master=self, screenzoom=self.sz, page_frame=self.page_frame)
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
        self.terminal = Terminal(master=self,screenzoom=self.sz)
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