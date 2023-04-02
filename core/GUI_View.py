#!/usr/bin/env python
# coding: utf-8

# 视图：每个导航栏的按钮对应一个视图。
# 视图包括：

# 项目视图：浏览、编辑、预览、使用RplGenProJect的视图
from .GUI_FileManager import FileManager
from .GUI_TabPage import PageFrame
from .ScriptParser import RplGenLog, MediaDef, CharTable
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
    pass
# 控制台视图
class ConsoleView(ttk.Frame):
    pass
# 首选项视图
class PreferenceView(ttk.Frame):
    pass