#!/usr/bin/env python
# coding: utf-8

# 项目资源管理器，项目视图的元素之一。
# 包含：标题图，项目管理按钮，媒体、角色、剧本的可折叠容器

import json
import re
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.dialogs import Messagebox
from .ScriptParser import MediaDef, CharTable, RplGenLog, Script
from .FilePaths import Filepath
from .ProjConfig import Config
from .GUI_TabPage import PageFrame, RGLPage, CTBPage, MDFPage
# 项目视图-文件管理器-RGPJ
class RplGenProJect(Script):
    def __init__(self, json_input=None) -> None:
        # 新建空白工程
        if json_input is None:
            self.config     = Config()
            self.mediadef   = MediaDef(file_input='./toy/MediaObject.txt')
            # 设置当前路径
            Filepath.Mediapath = './toy/' #self.media_path
            self.chartab    = CharTable(file_input='./toy/CharactorTable.tsv')
            self.logfile    = {
                '示例项目1' : RplGenLog(file_input='./toy/LogFile.rgl'),
                '示例项目2' : RplGenLog(file_input='./toy/LogFile2.rgl')
                }
        # 载入json工程文件
        else:
            super().__init__(None, None, None, json_input)
            # config
            self.config     = Config(dict_input=self.struct['config'])
            # media
            self.mediadef   = MediaDef(dict_input=self.struct['mediadef'])
            # chartab
            self.chartab    = CharTable(dict_input=self.struct['chartab'])
            # logfile
            self.logfile    = {}
            for key in self.struct['logfile'].keys():
                self.logfile[key] = RplGenLog(dict_input=self.struct['logfile'][key])
    def dump_json(self, filepath: str) -> None:
        logfile_dict = {}
        for key in self.logfile.keys():
            logfile_dict[key] = self.logfile[key].struct
        with open(filepath,'w',encoding='utf-8') as of:
            of.write(
                json.dumps(
                    {
                        'config'  : self.config.get_struct(),
                        'mediadef': self.mediadef.struct,
                        'chartab' : self.chartab.struct,
                        'logfile' : logfile_dict,
                    }
                    ,indent=4
                )
            )

# 项目视图-文件管理器
class FileManager(ttk.Frame):
    def __init__(self,master,screenzoom,page_frame:PageFrame)->None:
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
        # 文件管理器的项目对象
        self.project:RplGenProJect = RplGenProJect()
        # 文件浏览器元件
        self.project_content = ScrolledFrame(master=self,borderwidth=0,bootstyle='light',autohide=True)
        self.project_content.vscroll.config(bootstyle='warning-round')
        # 对应的page_frame对象
        self.page_frame:PageFrame = page_frame
        self.page_frame.ref_medef = self.project.mediadef
        self.page_frame.ref_chartab = self.project.mediadef
        # 元件
        self.items = {
            'mediadef'  : MDFCollapsing(master=self.project_content,screenzoom=self.sz,content=self.project.mediadef,page_frame=self.page_frame),
            'chartab'   : CTBCollapsing(master=self.project_content,screenzoom=self.sz,content=self.project.chartab,page_frame=self.page_frame),
            'rplgenlog' : RGLCollapsing(master=self.project_content,screenzoom=self.sz,content=self.project.logfile,page_frame=self.page_frame),
        }
        # 放置
        self.update_item()
        self.project_content.pack(fill='both',expand=True,side='top')
    def update_item(self):
        for idx,key in enumerate(self.items):
            fileitem:ttk.Button = self.items[key]
            fileitem.pack(fill='x',pady=0,side='top')
# 项目视图-可折叠类容器-基类
class FileCollapsing(ttk.Frame):
    def __init__(self,master,screenzoom:float,fileclass:str,content,page_frame:PageFrame):
        self.sz = screenzoom
        self.page_frame = page_frame
        SZ_5 = int(self.sz * 5)
        SZ_2 = int(self.sz * 2)
        super().__init__(master=master,borderwidth=0)
        self.class_text = {'mediadef':'媒体库','chartab':'角色配置','rplgenlog':'剧本文件'}[fileclass]
        self.collapbutton = ttk.Button(master=self,text=self.class_text,command=self.update_toggle,bootstyle='warning')
        self.content_frame = ttk.Frame(master=self)
        self.button_padding = (SZ_5,SZ_2,SZ_5,SZ_2)
        # 内容，正常来说，self.items的key应该正好等于Button的text
        self.content = content
        self.items = {}
    def update_item(self):
        self.update_filelist()
        self.collapbutton.pack(fill='x',side='top')
        self.expand:bool = False
        self.update_toggle()
    def update_filelist(self):
        for idx in self.items:
            this_button:ttk.Button = self.items[idx]
            this_button.pack_forget()
            this_button.pack(fill='x',side='top')
    def update_toggle(self):
        if self.expand:
            self.content_frame.pack_forget()
            self.expand:bool = False
        else:
            self.content_frame.pack(fill='x',side='top')
            self.expand:bool = True
    def right_click_menu(self,event):
        # 获取关键字
        keyword = event.widget.cget('text')
        menu = ttk.Menu(master=self.content_frame,tearoff=0)
        menu.add_command(label="重命名",command=lambda:self.rename_item(keyword))
        menu.add_command(label="删除")
        # 显示菜单
        menu.post(event.x_root, event.y_root)
    def add_item(self):
        pass
    def delete_item(self):
        pass
    def rename_item(self,keyword):
        # 原来的按钮
        self.button_2_rename:ttk.Button = self.items[keyword]
        self.re_name = tk.StringVar(master=self,value=keyword)
        self.in_rename:bool = True
        # 新建输入框
        rename_entry:ttk.Entry = ttk.Entry(master=self.content_frame,textvariable=self.re_name,bootstyle='warning',justify='center',)
        rename_entry.bind("<Return>",lambda event:self.rename_item_done(True))
        rename_entry.bind("<FocusOut>",lambda event:self.rename_item_done(False))
        rename_entry.bind("<Escape>",lambda event:self.rename_item_done(False))
        # 放置元件
        self.items[keyword] = rename_entry
        # 更新
        self.button_2_rename.pack_forget()
        self.update_filelist()
        # 设置焦点
        rename_entry.focus_set()
    def rename_item_failed(self,origin_keyword):
        self.items[origin_keyword].destroy()
        self.items[origin_keyword] = self.button_2_rename
        self.update_filelist()
    def rename_item_done(self,enter:bool):
        origin_keyword = self.button_2_rename.cget('text')
        # 每次rename，done只能触发一次！
        if self.in_rename:
            self.in_rename = False
        else:
            return False
        try:
            if enter is False:
                # 删除Entry，复原Button
                self.rename_item_failed(origin_keyword)
                raise Exception('没有按回车键')
            # 新的关键字
            new_keyword = self.re_name.get()
            if re.match('^[\w\ ]+$',new_keyword) is None:
                self.rename_item_failed(origin_keyword)
                Messagebox().show_warning(
                    message = '非法的角色名：{}\n角色名只能包含中文、英文、数字、下划线和空格！'.format(new_keyword),
                    title   = '失败的重命名'
                    )
                raise Exception('非法的角色名')
            if new_keyword in self.items.keys() and new_keyword != origin_keyword:
                self.rename_item_failed(origin_keyword)
                Messagebox().show_warning(
                    message = '重复的角色名：{}\n！',
                    title   = '失败的重命名'
                    )
                raise Exception('重复的角色名')
            # 删除原来的关键字
            self.items[origin_keyword].destroy()
            self.items.pop(origin_keyword)
            # 修改Button的text
            self.button_2_rename.config(text=self.re_name.get())
            # 更新self.items
            self.items[new_keyword] = self.button_2_rename
            self.update_filelist()
            # 返回值：是否会变更项目
            return True
        except Exception as E:
            return False
    def open_item_as_page(self,keyword,file_type,file_index):
        # 检查是否是Page_frame中的活跃页
        if keyword not in self.page_frame.page_dict.keys():
            # 如果不是活动页，新增活跃页
            self.page_frame.add_active_page(
                name        = keyword,
                file_type   = file_type,
                content_obj = self.content,
                content_type= file_index
                )
        else:
            # 如果是活动页，切换到活跃页
            self.page_frame.goto_page(name=keyword)
# 项目视图-可折叠类容器-媒体类
class MDFCollapsing(FileCollapsing):
    media_type_name = {
        'Pos'       :   '位置',
        'Text'      :   '文本',
        'Bubble'    :   '气泡',
        'Animation' :   '立绘',
        'Background':   '背景',
        'Audio'     :   '音频',
    }
    def __init__(self, master, screenzoom: float, content:MediaDef, page_frame:PageFrame):
        super().__init__(master, screenzoom, 'mediadef', content, page_frame)
        for mediatype in ['Pos', 'Text', 'Bubble', 'Animation', 'Background', 'Audio']:
            filename = self.media_type_name[mediatype]
            showname = "{} ({})".format(filename,mediatype)
            self.items[mediatype] = ttk.Button(
                master      = self.content_frame,
                text        = showname,
                bootstyle   = 'light',
                padding     = self.button_padding,
                compound    = 'left',
                )
            self.items[mediatype].bind("<Button-1>",self.open_item_as_page)
        self.update_item()
    def open_item_as_page(self,event):
        # 获取点击按钮的关键字
        keyword = event.widget.cget('text')
        filename,file_index = keyword.split(' ') # 前两个字
        file_index = file_index[1:-1] # 去除括号
        super().open_item_as_page(
            keyword     = '媒体-' + filename, # '媒体-立绘'
            file_type   = 'MDF',
            file_index  = file_index # 'Animation'
            ) 
# 项目视图-可折叠类容器-角色类
class CTBCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:CharTable, page_frame:PageFrame):
        super().__init__(master, screenzoom, 'chartab', content, page_frame)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0)
        self.add_button.pack(side='right',padx=SZ_10,pady=SZ_5,ipady=SZ_1,ipadx=SZ_3)
        self.table = self.content.export()
        # 内容
        for name in self.table['Name'].unique():
            self.items[name] = ttk.Button(
                master      = self.content_frame,
                text        = name,
                bootstyle   = 'light',
                padding     = self.button_padding,
                compound    = 'left',
                )
            self.items[name].bind("<Button-1>",self.open_item_as_page)
            self.items[name].bind("<Button-3>",self.right_click_menu)
        self.update_item()
    def rename_item(self, keyword):
        # 如果尝试重命名的是一个已经打开的标签页
        rename_an_active_page:bool = "角色-"+keyword in self.page_frame.page_dict.keys()
        if rename_an_active_page:
            choice = Messagebox().show_question(
                message='尝试重命名一个已经启动的角色页面！\n如果这样做，该页面尚未保存的修改将会丢失！',
                title='警告！',
                buttons=["取消:primary","确定:danger"]
                )
            if choice != '确定':
                return
        return super().rename_item(keyword)
    def rename_item_done(self,enter:bool):
        origin_keyword = self.button_2_rename.cget('text')
        new_keyword = self.re_name.get()
        rename_an_active_page:bool = "角色-"+origin_keyword in self.page_frame.page_dict.keys()
        edit_CTB = super().rename_item_done(enter=enter)
        if edit_CTB:
            if rename_an_active_page:
                self.page_frame.page_notebook.delete("角色-"+origin_keyword)
            # 重命名 content
            self.content.rename(origin_keyword,new_keyword)
    def open_item_as_page(self,event):
        # 获取点击按钮的关键字
        keyword = event.widget.cget('text')
        super().open_item_as_page(
            keyword     = '角色-'+keyword,
            file_type   = 'CTB',
            file_index  = keyword
            )
# 项目视图-可折叠类容器-剧本类
class RGLCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:dict, page_frame:PageFrame):
        super().__init__(master, screenzoom, 'rplgenlog', content, page_frame)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0)
        self.add_button.pack(side='right',padx=SZ_10,pady=SZ_5,ipady=SZ_1,ipadx=SZ_3)
        # 内容
        for key in self.content.keys():
            self.items[key] = ttk.Button(
                master      = self.content_frame,
                text        = key,
                bootstyle   = 'light',
                padding     = self.button_padding,
                compound    = 'left',
                )
            self.items[key].bind("<Button-1>",self.open_item_as_page)
            self.items[key].bind("<Button-3>",self.right_click_menu)
        self.update_item()
    def rename_item(self, keyword):
        # 如果尝试重命名的是一个已经打开的标签页
        rename_an_active_page:bool = "剧本-"+keyword in self.page_frame.page_dict.keys()
        if rename_an_active_page:
            choice = Messagebox().show_question(
                message='尝试重命名一个已经启动的剧本页面！\n如果这样做，该页面尚未保存的修改将会丢失！',
                title='警告！',
                buttons=["取消:primary","确定:danger"]
                )
            if choice != '确定':
                return
        return super().rename_item(keyword)
    def rename_item_done(self,enter:bool):
        origin_keyword = self.button_2_rename.cget('text')
        new_keyword = self.re_name.get()
        rename_an_active_page:bool = "剧本-"+origin_keyword in self.page_frame.page_dict.keys()
        edit_RGL = super().rename_item_done(enter=enter)
        if edit_RGL:
            if rename_an_active_page:
                self.page_frame.page_notebook.delete("剧本-"+origin_keyword)
            # 重命名 content
            self.content[new_keyword] = self.content[origin_keyword]
            self.content.pop(origin_keyword)
    def open_item_as_page(self,event):
        # 获取点击按钮的关键字
        keyword = event.widget.cget('text')
        super().open_item_as_page(
            keyword     = '剧本-'+keyword,
            file_type   = 'RGL',
            file_index  = keyword
            )