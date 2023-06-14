#!/usr/bin/env python
# coding: utf-8

# 重新定位失效媒体素材的对话框

import os
import pandas as pd
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox, Dialog
from tkinter.filedialog import askdirectory
from .ScriptParser import MediaDef,RplGenLog

# 框
class RelocateFile(ttk.Frame):
    def __init__(self,master,screenzoom,close_func,file_not_found:dict={}):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        SZ_10 = int(10 * self.sz)
        SZ_5 = int(5*self.sz)
        # 关闭窗口命令
        self.close_func = close_func
        # 建立表格
        self.data = pd.DataFrame(columns=['media_name','file_name','invalid_path','relocate_path'])
        # 建立原件
        self.title = ttk.Label(master=self,text='重新定位素材',font='-family 微软雅黑 -size 15 -weight bold')
        # 表格
        self.table = ttk.Treeview(
            master=self,
            show='headings',
            bootstyle='primary',
            columns= ['media_name','file_name','invalid_path','relocate_path']
            )
        self.table.column('#0',anchor='center',width=50,stretch=False)
        self.table.column('media_name',anchor='center',width=150,stretch=True)
        self.table.column('file_name',anchor='center',width=150,stretch=True)
        self.table.column('invalid_path',anchor='center',width=400,stretch=True)
        self.table.column('relocate_path',anchor='center',width=400,stretch=True)
        self.table.heading('#0',text='序号',anchor='center')
        self.table.heading('media_name',text='媒体名',anchor='center')
        self.table.heading('file_name',text='文件名',anchor='center')
        self.table.heading('invalid_path',text='脱机素材',anchor='center')
        self.table.heading('relocate_path',text='新路径',anchor='center')
        # 按钮
        self.button_frame = ttk.Frame(master=self)
        self.buttons = {
            'offall'  :ttk.Button(master=self.button_frame,bootstyle='danger' ,text='全部脱机',width=10,command=self.offline_all_file),
            'offline' :ttk.Button(master=self.button_frame,bootstyle='secondary',text='脱机',width=10,command=self.offline_a_file),
            'browse'  :ttk.Button(master=self.button_frame,bootstyle='secondary',text='搜索',width=10,command=self.search_file_by_browse),
            'comfirm' :ttk.Button(master=self.button_frame,bootstyle='primary',text='确定',width=10,command=self.comfirm),
        }
        for keyword in self.buttons:
            self.buttons[keyword].pack(side='left',padx=SZ_10,ipady=SZ_5,expand=True,fill='x')
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
        # 更新数据
    def get_file_to_search(self,colname):
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
                            new_path = os.path.join(root, file).replace('\\','/')
                            self.update_relocate_path(key,new_path)
        else:
            pass
    def offline_a_file(self):
        print(self.table.selection())
        try:
            select_idx = [self.table.index(x) for x in self.table.selection()]
            for idx in select_idx:
                self.update_relocate_path(idx, '脱机')
        except IndexError:
            return
    def offline_all_file(self):
        for idx in self.data.index:
            self.update_relocate_path(idx, '脱机')
    def comfirm(self):
        # 如不不为空
        if len(self.get_file_to_search('relocate_path'))!=0:
            Messagebox().show_info(message='还有尚未处理的待定位文件！\n请完成搜索，或将设置为脱机。',title='还未完成重定位')
        else:
            self.close_func(result=self.data)
    def update_relocate_path(self,idx,path):
        self.data.loc[idx,'relocate_path'] = path
        self.table.set(idx,'relocate_path',path)
    def update_items(self):
        SZ_10 = int(10 * self.sz)
        SZ_5 = int(5*self.sz)
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