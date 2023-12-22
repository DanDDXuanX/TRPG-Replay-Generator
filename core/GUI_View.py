#!/usr/bin/env python
# coding: utf-8

# 视图：每个导航栏的按钮对应一个视图。
# 视图包括：

# 项目视图：浏览、编辑、预览、使用RplGenProJect的视图
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from .GUI_Language import tr
from .GUI_FileManager import FileManager
from .GUI_TabPage import PageFrame
from .GUI_Terminal import Terminal
from .GUI_TableEdit import ScriptExecuter, PreferenceTable, ResetConfirm, PortalTable
from .GUI_Util import Texture
from .GUI_DialogWindow import browse_file
from .GUI_CustomDialog import new_project
from .GUI_EmptyHomeView import HomePageElements
from .GUI_TableStruct import key_status_bar
from .GUI_Link import Link
from .ProjConfig import preference
from .Utils import EDITION, PUBLICATION
# 脚本视图：运行 MDF、CTB、RGL 脚本文件的视图。
# 控制台视图：容纳控制台输出内容的视图。
# 首选项视图：设置整个程序的首选项的视图。

# 空白的项目视图
class EmptyView(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
        # 缩放比例
        self.sz = screenzoom
        SZ_10 = int(self.sz * 10)
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 子原件
        self.texture = Texture(master=self, screenzoom=self.sz, file='./assets/texture/texture5.png')
        self.content = HomePageElements(master=self, screenzoom=self.sz)
        self.statusbar = ttk.Frame(master=self,padding=0)
        self.status_text = {
            'version': ttk.Label(master=self.statusbar,text=tr('回声工坊') + f' @{PUBLICATION} {EDITION}' ,padding=(SZ_10,0,SZ_10,0)),
            'keys' : ttk.Label(master=self.statusbar,padding=(SZ_10,0,SZ_10,0)),
            'message' : ttk.Label(master=self.statusbar,padding=(SZ_10,0,SZ_10,0))
        }
        self.update_status_bar()
        Link['update_statusbar'] = self.update_status_bar
        self.update_items()
    def update_items(self):
        SZ_20 = int(self.sz * 20)
        self.texture.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.content.place(relx=0.25,rely=0.15,relwidth=0.5,relheight=0.65)
        self.status_text['version'].pack(side='left',fill='y')
        self.status_text['keys'].pack(side='right',fill='y')
        self.status_text['message'].pack(side='right',fill='y')
        self.statusbar.place(relx=0,rely=1,y=-SZ_20,height=SZ_20,relwidth=1)
    def update_status_bar(self):
        text_style = (lambda x: 'secondary-inverse' if x==-1 else 'primary-inverse' if x==0 else 'danger-inverse')(preference.bulitin_keys_status)
        self.status_text['keys'].configure(text=key_status_bar[preference.bulitin_keys_status],bootstyle=text_style)
        if preference.service_message:
            self.status_text['message'].configure(text=preference.service_message)
        else:
            self.status_text['message'].configure(text='')
    def open_project_file(self,filepath):
        try:
            PView = ProjectView(master=self.master,screenzoom=self.sz,project_file=filepath)
            self.master.view['project'] = PView
            self.place_forget()
            self.master.view_show('project')
            self.destroy()
        except Exception as E:
            Messagebox().show_error(message=tr('无法读取工程文件，该文件可能已损坏。'),title=tr('打开失败'),parent=self.winfo_toplevel())
    def open_project(self):
        get_file:str = browse_file(master=self.winfo_toplevel(),text_obj=tk.StringVar(),method='file',filetype='rplgenproj',related=False)
        if get_file != '':
            self.open_project_file(filepath=get_file)
    def empty_project(self):
        get_file:str = new_project(master=self,ptype='Empty')
        if get_file is not None:
            self.open_project_file(filepath=get_file)
    def intel_project(self):
        # 暂时还不可用的
        get_file:str = new_project(master=self,ptype='Intel')
        if get_file is not None:
            self.open_project_file(filepath=get_file)
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
        # 修改窗口标题
        project_file_name = project_file.split('/')[-1]
        self.winfo_toplevel().title(self.winfo_toplevel().window_title+f' @:{project_file_name}')
        # 摆放子元件
        self.update_item()
    def update_item(self):
        SZ_300 = int(self.sz * 300)
        self.file_manager.place(x=0,y=0,width=SZ_300,relheight=1)
        self.page_frame.place(x=SZ_300,y=0,relheight=1,relwidth=1,width=-SZ_300)
    def close_project_view(self):
        PView = EmptyView(master=self.master,screenzoom=self.sz)
        self.master.view['project'] = PView
        self.place_forget()
        self.master.view_show('project')
        # 修改窗口标题
        self.winfo_toplevel().title(self.winfo_toplevel().window_title)
        self.destroy()

# 脚本视图 
# TODO：首个上线版本不采用这个视图。
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
        self.texture = Texture(master=self, screenzoom=self.sz, file='./assets/texture/texture3.png')
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
        self.texture = Texture(master=self, screenzoom=self.sz, file='./assets/texture/texture4.png')
        # self.terminal = VoiceChooser(master=self,screenzoom=self.sz,voice='Azure::zh-CN-YunxiNeural:assistant:1.0:Boy',speech_rate=30,pitch_rate=-70)
        # self.terminal = RelocateFile(master=self, screenzoom=self.sz, file_not_found={'A':'./assets/texture/texture4.png','B':'./assets/texture/texture2.png','C':'./assets/texture/texture3.png'})
        # self.terminal = CreateEmptyProject(master=self,screenzoom=self.sz)
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
        self.texture = Texture(master=self, screenzoom=self.sz, file='./assets/texture/texture1.png')
        self.content = PreferenceTable(master=self,screenzoom=self.sz)
        self.buttons = ResetConfirm(master=self,screenzoom=self.sz,preferencetable=self.content)
        # 更新
        self.update_item()
    def update_item(self):
        SZ_10 = int(self.sz * 10)
        self.texture.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.content.place(relx=0.2,y=0,relwidth=0.6,relheight=1)
        self.buttons.place(
            relx=0.8,   x=SZ_10,
            rely=1,     y=-SZ_10*11,
            relwidth=0.2, width=-SZ_10*2,
            height=SZ_10*10
            )
# 传送门视图
class PortalView(ttk.Frame):
    def __init__(self,master,screenzoom)->None:
        # 初始化
        self.sz = screenzoom
        super().__init__(master,borderwidth=0,bootstyle='light')
        # 子原件
        self.texture = Texture(master=self, screenzoom=self.sz, file='./assets/texture/texture6.png')
        # self.content = PreferenceTable(master=self,screenzoom=self.sz)
        self.content = PortalTable(master=self, screenzoom=self.sz)
        # 更新
        self.update_item()
    def update_item(self):
        self.texture.place(relx=0,rely=0,relwidth=1,relheight=1)
        self.content.place(relx=0.15,y=0,relwidth=0.7,relheight=1)