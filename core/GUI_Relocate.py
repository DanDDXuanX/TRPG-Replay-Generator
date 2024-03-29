#!/usr/bin/env python
# coding: utf-8

# 重新定位失效媒体素材的对话框

import os
import pandas as pd
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox, Dialog
from tkinter.filedialog import askdirectory
from .GUI_Link import Link
from .FilePaths import Filepath
from .GUI_Language import Localize, tr
from .ProjConfig import preference

# 框
class RelocateFile(ttk.Frame, Localize):
    language = {
        'en': {
            '序号': 'Index',
            '媒体名': 'Media Name',
            '文件名': 'File Name',
            '脱机路径': 'Offline Path',
            '新路径': 'New Path',
            '全部脱机': 'Offline All',
            '脱机': 'Offline',
            '搜索': 'Search',
            '确定': 'OK',
            '还有尚未处理的待定位文件！\n请完成搜索，或将设置为脱机。': 'There are unprocessed files!\nPlease finish all relinks, or set it to offline.',
            '还未完成重定位': 'Relink not finish',
        }
    }
    localize = preference.lang
    def __init__(self,master,screenzoom,close_func,file_not_found:dict={}):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        SZ_10 = int(10 * self.sz)
        SZ_3 = int(3*self.sz)
        SZ_150 = int(150*self.sz)
        SZ_400 = int(400*self.sz)
        # 关闭窗口命令
        self.close_func = close_func
        # 建立表格
        self.data = pd.DataFrame(columns=['media_name','file_name','invalid_path','relocate_path'])
        # 建立原件
        self.title = ttk.Label(master=self,font=(Link['system_font_family'], 15, "bold"))
        # 表格
        self.table = ttk.Treeview(
            master=self,
            show='headings',
            bootstyle='primary',
            columns= ['media_name','file_name','invalid_path','relocate_path'],
            height=20
            )
        self.table.column('#0',anchor='center',width=SZ_10,stretch=False)
        self.table.column('media_name',anchor='center',width=SZ_150,stretch=True)
        self.table.column('file_name',anchor='center',width=SZ_150,stretch=True)
        self.table.column('invalid_path',anchor='center',width=SZ_400,stretch=True)
        self.table.column('relocate_path',anchor='center',width=SZ_400,stretch=True)
        self.table.heading('#0',text=self.tr('序号'),anchor='center')
        self.table.heading('media_name',text=self.tr('媒体名'),anchor='center')
        self.table.heading('file_name',text=self.tr('文件名'),anchor='center')
        self.table.heading('invalid_path',text=self.tr('脱机路径'),anchor='center')
        self.table.heading('relocate_path',text=self.tr('新路径'),anchor='center')
        # 按钮
        self.button_frame = ttk.Frame(master=self)
        self.buttons = {
            'offall'  :ttk.Button(master=self.button_frame,bootstyle='danger' ,text=self.tr('全部脱机'),width=10,command=self.offline_all_file),
            'offline' :ttk.Button(master=self.button_frame,bootstyle='secondary',text=self.tr('脱机'),width=10,command=self.offline_a_file),
            'browse'  :ttk.Button(master=self.button_frame,bootstyle='secondary',text=self.tr('搜索'),width=10,command=self.search_file_by_browse),
            'comfirm' :ttk.Button(master=self.button_frame,bootstyle='primary',text=self.tr('确定'),width=10,command=self.comfirm),
        }
        for keyword in self.buttons:
            self.buttons[keyword].pack(side='left',padx=SZ_10,ipady=SZ_3,expand=True,fill='x')
        # 初始化显示
        self.load_missing_path(file_not_found)
        self.update_items()
    def load_missing_path(self,missing_path:dict):
        for idx, name in enumerate(missing_path.keys()):
            path = missing_path[name].replace('\\','/')
            filename = path.split('/')[-1]
            # 更新data
            self.data.loc[idx,'media_name'] = name
            self.data.loc[idx,'file_name'] = filename
            self.data.loc[idx,'invalid_path'] = path
            self.data.loc[idx,'relocate_path'] = 'None'
            # 更新视图
            self.table.insert(
                parent='',
                index=idx,
                iid=idx,
                text=str(idx+1),
                values=(name, filename, path, '')
                )
        # 用于显示的标题
        self.relocate_len = 0
        self.missing_len = len(self.data)
        self.update_title()
        # 更新数据
    def update_title(self):
        self.relocate_len = self.missing_len - len(self.get_file_to_search())
        self.title.config(text=tr('重新定位媒体') + f' [{self.relocate_len}/{self.missing_len}]')
    def get_file_to_search(self,colname='media_name'):
        return self.data.query("relocate_path=='None'")[colname].values
    def search_file_by_browse(self):
        # 选择目录
        search_dir = askdirectory(mustexist=True)
        if search_dir != '':
            for root,dirs,files in os.walk(search_dir):
                for file in files:
                    # 如果文件名待搜索
                    if file in self.get_file_to_search('file_name'):
                        # 在所有文件名等于当前文件名的行，执行替换
                        for key in self.data[self.data['file_name'] == file].index:
                            new_path = Filepath(os.path.join(root, file)).relative()
                            self.update_relocate_path(key,new_path)
            self.update_title()
        else:
            pass
    def offline_a_file(self):
        try:
            select_idx = [self.table.index(x) for x in self.table.selection()]
            for idx in select_idx:
                self.update_relocate_path(idx, self.tr('脱机'))
            self.update_title()
        except IndexError:
            return
    def offline_all_file(self):
        for idx in self.data.index:
            self.update_relocate_path(idx, self.tr('脱机'))
        self.update_title()
    def comfirm(self):
        # 如不不为空
        if len(self.get_file_to_search('relocate_path'))!=0:
            Messagebox().show_info(message=self.tr('还有尚未处理的待定位文件！\n请完成搜索，或将设置为脱机。'),title=self.tr('还未完成重定位'),parent=self)
        else:
            self.close_func(result=self.data)
    def update_relocate_path(self,idx,path):
        self.data.loc[idx,'relocate_path'] = path
        self.table.set(idx,'relocate_path',path)
    def update_items(self):
        SZ_10 = int(10 * self.sz)
        SZ_5 = int(5*self.sz)
        SZ_1 = int(1 * self.sz)
        self.title.pack(side='top',fill='x',padx=SZ_10,pady=[SZ_10,SZ_5])
        self.table.pack(side='top',fill='both',expand=True,padx=SZ_10,pady=SZ_5)
        self.button_frame.pack(side='top',fill='x',padx=SZ_10,pady=[SZ_5,SZ_10])
class RelocateDialog(Dialog):
    def __init__(self, screenzoom, parent=None, title="重新定位媒体",file_not_found:dict={}):
        super().__init__(parent, title, alert=False)
        self.sz = screenzoom
        self.file_not_found = file_not_found
    def close_dialog(self,result=None):
        self._result = result
        self._toplevel.destroy()
    def create_body(self, master):
        self.relocate_file = RelocateFile(
            master = master,
            screenzoom = self.sz,
            file_not_found = self.file_not_found,
            close_func = self.close_dialog
            )
        self.relocate_file.pack(fill='both',expand=True)
    def create_buttonbox(self, master):
        pass