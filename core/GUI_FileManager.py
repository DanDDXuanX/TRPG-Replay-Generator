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
from ttkbootstrap.tooltip import ToolTip
from .ScriptParser import MediaDef, CharTable, RplGenLog, Script
from .FilePaths import Filepath
from .ProjConfig import Config
from .Exceptions import MediaError
from .Medias import MediaObj
from .GUI_TabPage import PageFrame, RGLPage, CTBPage, MDFPage
from .GUI_DialogWindow import browse_file, save_file
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
            Filepath.Mediapath = Filepath(json_input).directory()
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
    def __init__(self, master, screenzoom, page_frame:PageFrame, project_file:str=None)->None:
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
            'save'      : ttk.Button(master=self.project_title,image='save'  ,command=self.save_file),
            'config'    : ttk.Button(master=self.project_title,image='config',command=None),
            'import'    : ttk.Button(master=self.project_title,image='import',command=self.import_file),
            'export'    : ttk.Button(master=self.project_title,image='export',command=self.export_file),
        }
        self.buttons_tooltip = {
            'save'      : ToolTip(widget=self.buttons['save']  ,text='保存项目',bootstyle='secondary-inverse'),
            'config'    : ToolTip(widget=self.buttons['config'],text='项目设置',bootstyle='secondary-inverse'),
            'import'    : ToolTip(widget=self.buttons['import'],text='导入文件',bootstyle='secondary-inverse'),
            'export'    : ToolTip(widget=self.buttons['export'],text='导出项目',bootstyle='secondary-inverse'),
        }
        # 放置
        self.title_pic.pack(fill='none',side='top')
        for idx,key in enumerate(self.buttons):
            buttons:ttk.Button = self.buttons[key]
            buttons.pack(expand=True,fill='x',side='left',anchor='se',padx=0,pady=0)
        self.project_title.pack(fill='x',side='top',padx=0,pady=0,ipadx=0,ipady=0)
        # 文件管理器的项目对象
        self.project:RplGenProJect = RplGenProJect(json_input=project_file)
        self.project_file:str = project_file
        # 文件浏览器元件
        self.project_content = ScrolledFrame(master=self,borderwidth=0,bootstyle='light',autohide=True)
        self.project_content.vscroll.config(bootstyle='warning-round')
        # 对应的page_frame对象
        self.page_frame:PageFrame = page_frame
        self.page_frame.ref_medef = self.project.mediadef
        self.page_frame.ref_chartab = self.project.chartab
        self.page_frame.ref_config = self.project.config
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
    # 检查相关文件是否存在
    def check_file_exist(self,filepath:str)->bool:
        if filepath in MediaObj.cmap.keys() or filepath == 'None' or filepath is None:
            return True
        try:
            Filepath(filepath).exact()
            return True
        except MediaError:
            return False
    # 导入文件
    def import_file(self):
        get_file:str = browse_file(master=self.winfo_toplevel(),text_obj=tk.StringVar(),method='file',filetype='rgscripts')
        if get_file != '':
            # 尝试多个解析
            Types = {MediaDef:None,CharTable:None,RplGenLog:None}
            for ScriptType in Types:
                try:
                    this = ScriptType(file_input=get_file)
                    Types[ScriptType] = this
                except:
                    Types[ScriptType] = ScriptType()
            # 获取最优解析结果
            top_parse:Script = max(Types,key=lambda x:len(Types.get(x).struct))
            if Types[top_parse] == 0:
                # 显示一个错误消息框
                Messagebox().show_error(message='无法导入这个文件！',title='错误')
            else:
                # 更新到项目
                if top_parse is RplGenLog:
                    showname = '剧本文件'
                    imported:RplGenLog = Types[top_parse]
                    collapse:RGLCollapsing = self.items['rplgenlog']
                    filename = Filepath(get_file).name().split('.')[0]
                    # 如果重名了，在名字后面加东西
                    while filename in self.project.logfile.keys():
                        filename = filename+'_new'
                    else:
                        # 更新项目内容
                        self.project.logfile[filename] = imported
                        # 更新文件管理器
                        collapse.create_new_button(new_keyword=filename)
                elif top_parse is CharTable:
                    showname = '角色配置'
                    imported:CharTable = Types[top_parse]
                    collapse:CTBCollapsing = self.items['chartab']
                    new_charactor:list = []
                    for keyword in imported.struct:
                        name, subtype = keyword.split('.')
                        # 是不是一个新增的角色？是则新建标签
                        if name not in collapse.get_chara_name():
                            new_charactor.append(name)
                            collapse.create_new_button(new_keyword=name)
                        # 如果重名了，在名字后面加东西
                        keyword_new = keyword
                        while keyword_new in self.project.chartab.struct.keys():
                            keyword_new = keyword_new + '_new'
                            subtype = subtype + '_new'
                        else:
                            # 更新项目内容
                            imported.struct[keyword]['Subtype'] = subtype
                            self.project.chartab.struct[keyword_new] = imported.struct[keyword]
                    # 最后，检查所有新建角色，有没有default，没有则新建
                    for chara in new_charactor:
                        self.project.chartab.add_chara_default(name=chara)
                elif top_parse is MediaDef:
                    showname = '媒体库'
                    imported:MediaDef = Types[top_parse]
                    collapse:MDFCollapsing = self.items['mediadef']
                    file_not_found:list = []
                    for keyword in imported.struct:
                        # 检查是否是无效行
                        if imported.struct[keyword]['type'] in ['comment','blank']:
                            continue
                        # 检查文件可用性
                        if 'filepath' in imported.struct[keyword]:
                            file_path = imported.struct[keyword]['filepath']
                        elif 'fontpath' in imported.struct[keyword]:
                            file_path = imported.struct[keyword]['fontpath']
                        else:
                            file_path = None
                        if not self.check_file_exist(file_path):
                            file_not_found.append(file_path)
                        # 检查文件名是否重复
                        keyword_new = keyword
                        while keyword_new in self.project.mediadef.struct.keys():
                            keyword_new = keyword_new + '_new'
                        else:
                            self.project.mediadef.struct[keyword_new] = imported.struct[keyword]
                    # TODO：检查素材可及性？
                    print(file_not_found)
                    # self.relocation_file(file_not_found)
                else:
                    return
                Messagebox().show_info(title='导入成功',message='成功向{showname}中导入共计{number}个小节/项目。'.format(showname=showname,number=len(imported.struct)))
    # 导出文件
    def export_file(self):
        # 如果导出完整的项目为脚本
        get_file = save_file(master=self.winfo_toplevel(), method='file',filetype='prefix')
        if get_file != '':
            try:
                # 媒体定义
                self.project.mediadef.dump_file(filepath=get_file+'.媒体库.txt')
                # 角色配置
                self.project.chartab.dump_file(filepath=get_file+'.角色配置.tsv')
                # 剧本文件
                for keyword, rgl in self.project.logfile.items():
                    rgl.dump_file(filepath=get_file+'.{}.rgl'.format(keyword))
                # 显示消息
                Messagebox().show_info(title='导出成功',message='成功将工程导出为脚本文件！\n导出路径：{}'.format(get_file))
            except Exception as E:
                Messagebox().show_error(title='导出失败',message='无法将工程导出！\n由于：{}'.format(E))

    # 保存文件
    def save_file(self):
        if self.project_file is None:
            select_path = save_file(master=self.winfo_toplevel(),filetype='rplgenproj')
            if select_path != '':
                self.project.dump_json(filepath=select_path)
                self.project_file = select_path
        else:
            self.project.dump_json(filepath=self.project_file)
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
        menu.add_command(label="删除",command=lambda:self.delete_item(keyword))
        # 显示菜单
        menu.post(event.x_root, event.y_root)
    def add_item(self):
        # 名字
        self.re_name = tk.StringVar(master=self,value='')
        self.in_rename:bool = True
        # 新建输入框
        new_entry:ttk.Entry = ttk.Entry(master=self.content_frame,textvariable=self.re_name,bootstyle='warning',justify='center')
        new_entry.bind("<Return>",lambda event:self.add_item_done(True))
        new_entry.bind("<FocusOut>",lambda event:self.add_item_done(False))
        new_entry.bind("<Escape>",lambda event:self.add_item_done(False))
        # 放置元件
        self.items['new:init'] = new_entry
        self.update_filelist()
        new_entry.focus_set()
    def add_item_failed(self):
        self.items['new:init'].destroy()
        self.items.pop('new:init')
        self.update_filelist()
    def add_item_done(self,enter,filetype='角色')->bool:
        new_keyword = self.re_name.get()
        origin_keyword = 'new:init'
        # 每次rename，done只能触发一次！
        if self.in_rename:
            self.in_rename = False
        else:
            return False
        try:
            if enter is False:
                self.add_item_failed()
                raise Exception('没有按回车键')
            if re.match('^[\w\ ]+$',new_keyword) is None:
                self.add_item_failed()
                Messagebox().show_warning(
                    message = '非法的{type}名：{name}\n{type}名只能包含中文、英文、数字、下划线和空格！'.format(type=filetype, name=new_keyword),
                    title   = '失败的新建'
                    )
                raise Exception('非法名')
            if new_keyword in self.items.keys():
                self.add_item_failed()
                Messagebox().show_warning(
                    message = '重复的{type}名：{name}\n！'.format(type=filetype, name=new_keyword),
                    title   = '失败的新建'
                    )
                raise Exception('重复名')
            # 删除原来的关键字
            self.items[origin_keyword].destroy()
            self.items.pop(origin_keyword)
            # 新建button
            self.create_new_button(new_keyword)
            self.update_filelist()
            # 返回值：是否会变更项目
            return True
        except Exception as E:
            print(E)
            return False
    def create_new_button(self,new_keyword:str):
        # 新建button
        self.items[new_keyword] = ttk.Button(
            master      = self.content_frame,
            text        = new_keyword,
            bootstyle   = 'light',
            padding     = self.button_padding,
            compound    = 'left',
            )
        self.items[new_keyword].bind("<Button-1>",self.open_item_as_page)
        self.items[new_keyword].bind("<Button-3>",self.right_click_menu)
        self.update_filelist()
    def delete_item(self,keyword)->bool:
        # 确定真的要这么做吗？
        choice = Messagebox().show_question(
            message='确定要删除这个项目？\n这项删除将无法复原！',
            title='警告！',
            buttons=["取消:primary","确定:danger"]
            )
        # 返回是否需要删除项目数据
        if choice != '确定':
            return False
        else:
            self.items[keyword].destroy()
            self.items.pop(keyword)
            return True
    def rename_item(self,keyword,filetype='角色'):
        # 如果尝试重命名的是一个已经打开的标签页
        rename_an_active_page:bool = filetype+"-"+keyword in self.page_frame.page_dict.keys()
        if rename_an_active_page:
            choice = Messagebox().show_question(
                message='尝试重命名一个已经启动的{}页面！\n如果这样做，该页面尚未保存的修改将会丢失！'.format(filetype),
                title='警告！',
                buttons=["取消:primary","确定:danger"]
                )
            if choice != '确定':
                return
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
    def rename_item_done(self,enter:bool,filetype='角色'):
        # 关键字
        origin_keyword = self.button_2_rename.cget('text')
        new_keyword = self.re_name.get()
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
            if re.match('^[\w\ ]+$',new_keyword) is None:
                self.rename_item_failed(origin_keyword)
                Messagebox().show_warning(
                    message = '非法的{type}名：{name}\n{type}名只能包含中文、英文、数字、下划线和空格！'.format(type=filetype, name=new_keyword),
                    title   = '失败的重命名'
                    )
                raise Exception('非法名')
            if new_keyword in self.items.keys() and new_keyword != origin_keyword:
                self.rename_item_failed(origin_keyword)
                Messagebox().show_warning(
                    message = '重复的{type}名：{name}\n！'.format(type=filetype, name=new_keyword),
                    title   = '失败的重命名'
                    )
                raise Exception('重复名')
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
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0,command=self.add_item)
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
    def add_item_done(self, enter):
        confirm_add =  super().add_item_done(enter, '角色')
        new_keyword = self.re_name.get()
        if confirm_add:
            self.content.add_chara_default(new_keyword)
    def delete_item(self, keyword):
        confirm_delete:bool = super().delete_item(keyword)
        delete_an_active_page:bool = "角色-"+keyword in self.page_frame.page_dict.keys()
        if confirm_delete:
            # 如果是激活的页面，关闭激活的标签页
            if delete_an_active_page:
                self.page_frame.page_notebook.delete("角色-"+keyword)
            # 执行删除项目
            self.content.delete_chara(name=keyword)
    def rename_item(self, keyword):
        return super().rename_item(keyword,filetype='角色')
    def rename_item_done(self,enter:bool):
        origin_keyword = self.button_2_rename.cget('text')
        new_keyword = self.re_name.get()
        rename_an_active_page:bool = "角色-"+origin_keyword in self.page_frame.page_dict.keys()
        edit_CTB = super().rename_item_done(enter=enter,filetype='角色')
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
    def get_chara_name(self)->list:
        return list(self.items.keys())
# 项目视图-可折叠类容器-剧本类
class RGLCollapsing(FileCollapsing):
    def __init__(self, master, screenzoom: float, content:dict, page_frame:PageFrame):
        super().__init__(master, screenzoom, 'rplgenlog', content, page_frame)
        SZ_10 = int(self.sz * 10)
        SZ_5  = int(self.sz * 5 )
        SZ_3  = int(self.sz * 3 )
        SZ_1  = int(self.sz * 1 )
        # 新建按钮
        self.add_button = ttk.Button(master=self.collapbutton,text='新增+',bootstyle='warning',padding=0,command=self.add_item)
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
    def add_item_done(self, enter):
        confirm_add =  super().add_item_done(enter, '剧本')
        new_keyword = self.re_name.get()
        if confirm_add:
            # 新建一个空白的RGL
            self.content[new_keyword] = RplGenLog()
    def delete_item(self, keyword):
        confirm_delete:bool = super().delete_item(keyword)
        delete_an_active_page:bool = "剧本-"+keyword in self.page_frame.page_dict.keys()
        if confirm_delete:
            # 如果是激活的页面，关闭激活的标签页
            if delete_an_active_page:
                self.page_frame.page_notebook.delete("剧本-"+keyword)
            # 执行删除项目
            self.content.pop(keyword)
    def rename_item(self, keyword):
        return super().rename_item(keyword,filetype='剧本')
    def rename_item_done(self,enter:bool):
        origin_keyword = self.button_2_rename.cget('text')
        new_keyword = self.re_name.get()
        rename_an_active_page:bool = "剧本-"+origin_keyword in self.page_frame.page_dict.keys()
        edit_RGL = super().rename_item_done(enter=enter,filetype='剧本')
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