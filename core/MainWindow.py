#!/usr/bin/env python
# coding: utf-8

import sys

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from PIL import Image, ImageTk

from .ProjConfig import Preference
from .ScriptParser import RplGenLog,CharTable,MediaDef
from .Utils import EDITION

class RplGenStudioMainWindow(ttk.Window):
    def __init__(
            self,preference:Preference = Preference()
            )->None:
        # 系统缩放比例
        self.sz = self.get_screenzoom()
        super().__init__(
            title       = '回声工坊 ' + EDITION,
            themename   = 'litera',
            iconphoto   = './media/icon.png',
            size        = (int(1500*self.sz),int(800*self.sz)),
            resizable   = (True,True),
        )
        # 样式
        self.style.configure('secondary.TButton',anchor='w',font="-family 微软雅黑 -size 20 -weight bold",compound='left',padding=(3,0,0,0))
        self.style.configure('head.TLabel',anchor='w',font="-family 微软雅黑 -size 14 -weight bold",padding=(5,0,5,0))
        self.style.configure('main.TLabel',anchor='w',font="-family 微软雅黑 -size 10",padding=(5,0,5,0))
        self.style.configure('preview.TLabel',anchor='nw',background='#000000',borderwidth=0)
        self.style.configure('note.TLabel',anchor='w',background='#00000000')
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
        navigate_bar_width = {True:180,False:80}[is_wide] * self.sz
        self.navigate_bar.place_widgets(is_wide)
        self.navigate_bar.place_configure(width=navigate_bar_width)
        self.view[self.show].place_configure(x=navigate_bar_width,width=-navigate_bar_width)
    # 显示指定的视图
    def view_show(self,show:str):
        navigate_bar_width = {True:180,False:80}[self.navigate_bar.is_wide] * self.sz
        self.view[show].place_forget()
        self.view[show].place(x=navigate_bar_width,y=0,relwidth=1,relheight=1,width=-navigate_bar_width*self.sz)
        self.show = show
    # 获取系统的缩放比例
    def get_screenzoom(self)->float:
        if 'win32' in sys.platform:
            from win32.win32gui import GetDC
            from win32.win32print import GetDeviceCaps
            from win32.lib.win32con import DESKTOPHORZRES
            from win32.win32api import GetSystemMetrics
            hDC = GetDC(0)
            W = GetDeviceCaps(hDC,DESKTOPHORZRES)
            w = GetSystemMetrics(0)
            return W / w
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
        self.page_view     = RGLPage(master=self, screenzoom=self.sz, rgl = RplGenLog(file_input='./toy/LogFile.rgl'))
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
        self.project_contene = ttk.Frame(master=self,borderwidth=0,bootstyle='light')
        self.items = {
            'mediadef'  : ttk.Button(master=self.project_contene,text='媒体库',bootstyle='success-link'),
            'chartab'   : ttk.Button(master=self.project_contene,text='角色配置',bootstyle='success-link'),
            'rplgenlog' : ttk.Button(master=self.project_contene,text='剧本',bootstyle='success-link'),
        }
        # 放置
        self.update_item()
        self.project_contene.pack(fill='both',expand=True,side='top')
    def update_item(self):
        for idx,key in enumerate(self.items):
            fileitem:ttk.Button = self.items[key]
            fileitem.pack(fill='x',pady=3,side='top')
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
        # 容器
        self.searchbar = SearchBar(master=self,screenzoom=self.sz)
        self.container = Container(master=self,content=rgl,screenzoom=self.sz)
        self.outputcommand = OutPutCommand(master=self,screenzoom=self.sz)
        self.preview = PreviewCanvas(master=self,screenzoom=self.sz)
        self.edit = EditWindow(master=self,screenzoom=self.sz)
        # 放置元件
        SZ_40 = int(self.sz * 40)
        self.searchbar.place(x=0,y=0,relwidth=0.5,height=SZ_40)
        self.container.place(x=0,y=SZ_40,relwidth=0.5,relheight=1,height=-2*SZ_40)
        self.outputcommand.place(x=0,y=-SZ_40,rely=1,relwidth=0.5,height=SZ_40)
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
        self.buttons = {
            'display' : ttk.Button(master=self,text='播放预览',bootstyle='primary'),
            'export'  : ttk.Button(master=self,text='导出PR工程',bootstyle='info'),
            'recode'  : ttk.Button(master=self,text='导出视频',bootstyle='danger'),
        }
        self.update_item()
    def update_item(self):
        for key in self.buttons:
            item:ttk.Button = self.buttons[key]
            item.pack(fill='both',side='left',expand=True,pady=0)
# 容纳内容的滚动Frame
class Container(ScrolledFrame):
    def __init__(self,master,content:RplGenLog,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master, padding=3, bootstyle='light', autohide=True)
        self.vscroll.config(bootstyle='primary-round')
        # 滚动条容器的内容物
        self.content = content
        # 根据内容物，调整容器总高度
        self.config(height=int(80*self.sz)*len(self.content.struct))
        # 容器内的元件
        self.element = {}
        # 遍历内容物，新建元件
        for key in self.content.struct:
            this_section = self.content.struct[key]
            self.element[key] = SectionElememt(master=self,bootstyle='primary',text=key,section=this_section)
        # 将内容物元件显示出来
        self.update_item()
    def update_item(self):
        SZ_80 = int(self.sz * 80)
        SZ_75 = int(self.sz * 75)
        sz_10 = int(self.sz * 10)
        for idx,key in enumerate(self.element):
            this_section_frame:ttk.LabelFrame = self.element[key]
            this_section_frame.place(x=0,y=idx*SZ_80,width=-sz_10,height=SZ_75,relwidth=1)
# 容器中的每个小节
class SectionElememt(ttk.LabelFrame):
    def __init__(self,master,bootstyle,text,section:dict):
        super().__init__(master=master,bootstyle=bootstyle,text=text)
        if section['type'] == 'blank':
            self.header = '空行'
            self.main = ''
        elif section['type'] == 'comment':
            self.header = '# 注释'
            self.main = section['content']
        elif section['type'] == 'dialog':
            self.header = section['charactor_set']['0']['name'] + '.' + section['charactor_set']['0']['subtype']
            self.main = section['content']
        elif section['type'] == 'background':
            self.header = '放置气泡：'
            self.main = section['object']
        elif section['type'] == 'animation':
            self.header = '放置立绘：'
            self.main = str(section['object']) # TODO
        elif section['type'] == 'bubble':
            self.header = '放置气泡：'
            self.main = str(section['object']) # TODO
        elif section['type'] == 'set':
            self.header = '设置：' + section['target']
            self.main = str(section['value']) # TODO
        elif section['type'] == 'move':
            self.header = '移动：' + section['target']
            self.main = str(section['value'])
        elif section['type'] == 'table':
            self.header = '表格操作：'
            self.main = str(section['value'])
        elif section['type'] == 'music':
            self.header = '背景音乐：'
            self.main = str(section['value'])
        elif section['type'] == 'clear':
            self.header = '清除'
            self.main = section['object']
        elif section['type'] == 'hitpoint':
            self.header = '生命动画：'
            self.main = 'WIP'
        elif section['type'] == 'dice':
            self.header = '骰子动画：'
            self.main = 'WIP'
        elif section['type'] == 'wait':
            self.header = '停顿：'
            self.main = str(section['time']) + '帧'
        
        self.items = {
            'head' : ttk.Label(master=self,text=self.header,anchor='w',style='head.TLabel'),
            'sep'  : ttk.Separator(master=self),
            'main' : ttk.Label(master=self,text=self.main,anchor='w',style='main.TLabel'),
        }
        self.update_item()
    def update_item(self):
        for idx,key in enumerate(self.items):
            this_item:ttk.Label = self.items[key]
            this_item.pack(fill='x',anchor='w',side='top')
# 预览窗
class PreviewCanvas(ttk.LabelFrame):
    def __init__(self,master,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='预览窗')
        # 预览图像
        self.canvas = Image.open('./media/canvas.png')
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
    def __init__(self,master,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='编辑区')
        # 小节的数据
       # self.section = section
       # # 根据小节类型
       # if self.section['type'] == 'dialog':
       #     pass
# 脚本视图
class ScriptView(ttk.Frame):
    pass
# 控制台视图
class ConsoleView(ttk.Frame):
    pass
# 首选项视图
class PreferenceView(ttk.Frame):
    pass