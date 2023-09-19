#!/usr/bin/env python
# coding: utf-8

# 粘贴属性的对话框

import pandas as pd
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox, Dialog
from .GUI_Link import Link
from .ProjConfig import preference
from .ScriptParser import CharTable, Script
from .GUI_Language import tr
# 框

class PasteAttributes(ttk.Frame):
    attribute_table = pd.read_csv('./assets/attribute_table.tsv', sep='\t', index_col='attr')
    def __init__(self,master,screenzoom,close_func,title,container,clipboard_element:dict={},clipboard_name='',select_element:list=[]):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        # 关闭窗口命令
        self.close_func = close_func
        # 容器和选中的目标
        self.container = container
        self.select_element = select_element
        # 获取属性
        self.paste_attr = self.get_paste_attr(clipboard_element)
        # 建立原件
        self.title = ttk.Label(
            master  = self,
            font    = (Link['system_font_family'], 15, "bold"),
            text    = tr('从[{}]粘贴').format(clipboard_name)
            )
        # 选项们
        self.table = ttk.LabelFrame(master=self,text=tr('选择','属性'),borderwidth=int(self.sz*5))
        self.attr_choice = {}
        self.attr_variables = {}
        for attr in self.paste_attr:
            self.attr_variables[attr] = tk.BooleanVar(master=self,value=False)
            self.attr_choice[attr] = ttk.Checkbutton(
                master=self.table,
                variable=self.attr_variables[attr],
                text=self.attr_name[attr],
                bootstyle='primary',
                width=30,
                state='disable'
                )
        # 全选
        self.sepeartor = ttk.Separator(master=self.table)
        self.is_select_all = ttk.BooleanVar(master=self,value=False)
        self.select_all_button = ttk.Checkbutton(
                master=self.table,
                variable=self.is_select_all,
                text=tr('全选'),
                bootstyle='primary',
                width=30,
                command=self.select_all_attribute,
                )
        # 按钮
        self.button_frame = ttk.Frame(master=self)
        self.button_comfirm = ttk.Button(master=self.button_frame, bootstyle='primary' ,text=tr('确定'), width=10,command=self.comfirm)
        # 获取其中的可粘贴属性
        self.select_attr = self.get_select_attr(self.paste_attr)
        for attr in self.select_attr:
            self.attr_choice[attr].configure(state='normal')
        # 显示
        self.update_items()
    def update_items(self):
        SZ_10 = int(10 * self.sz)
        SZ_5 = int(5*self.sz)
        SZ_3 = int(3*self.sz)
        # 标题
        self.title.pack(side='top',fill='x',padx=SZ_10,pady=[SZ_10,SZ_5])
        # 选项
        for attr in self.attr_choice:
            self.attr_choice[attr].pack(side='top',fill='x',padx=SZ_10,pady=SZ_3)
        self.select_all_button.pack(side='bottom',fill='x' ,padx=SZ_10, pady=SZ_3)
        self.sepeartor.pack(side='bottom',fill='x',pady=SZ_3)
        self.table.pack(side='top',fill='x',expand=False,padx=SZ_10,pady=SZ_5)
        # 按钮
        self.button_comfirm.pack(padx=SZ_10, ipady=SZ_3, expand=True, fill='none')
        self.button_frame.pack(side='top',fill='x',padx=SZ_10,pady=[SZ_5,SZ_10])
    def select_all_attribute(self):
        if self.is_select_all.get():
            for attr in self.select_attr:
                self.attr_variables[attr].set(True)
        else:
            for attr in self.select_attr:
                self.attr_variables[attr].set(False)
        self.update()
    # 从剪贴板中获取可用于粘贴的属性
    def get_paste_attr(self,clipboard_element)->list:
        if 'Name' in clipboard_element:
            # 如果复制的是角色
            self.attr_name = {
                'Animation' :"Animation（立绘）",
                'Bubble'    :"Bubble（气泡）",
                'Voice'     :"Voice（音源）",
                'SpeechRate':"SpeechRate（语速）",
                'PitchRate' :"PitchRate（语调）",
            }
            customize = CharTable(dict_input={'tmp':clipboard_element}).get_customize()
            for item in customize:
                self.attr_name[item] = item
            self.copyed_type = 'CSubtype'
            return ['Animation','Bubble','Voice','SpeechRate','PitchRate'] + customize
        else:
            # 如果复制的是媒体
            self.attr_name = self.attribute_table[preference.lang]
            self.copyed_type = clipboard_element['type']
            return Script.type_keyword_position[self.copyed_type]
    def get_select_attr(self,paste_attr:list)->list:
        if self.copyed_type == 'CSubtype':
            for key in self.select_element:
                item = self.container.content.struct[key]
                if 'type' in item:
                    return [] # 如果尝试向媒体里面粘贴角色属性
            else:
                return paste_attr # 角色不存在参数不兼容问题
        else:
            columns_to_check = set([self.copyed_type])
            for key in self.select_element:
                item = self.container.content.struct[key]
                if 'Name' in item:
                    return [] # 如果尝试向角色里面粘贴媒体属性
                else:
                    columns_to_check.add(item['type'])
            # 拉通检查
            check = self.attribute_table[list(columns_to_check)]
            # 值相等且不为零的行
            return check[(check!=0).all(axis=1) & (check.nunique(axis=1) == 1)].index.to_list()
    def comfirm(self):
        result = []
        # 返回被选中的列表
        for attr in self.attr_variables:
            check_this:tk.BooleanVar = self.attr_variables[attr]
            if check_this.get():
                result.append(attr)
        self.close_func(result=result)
        
# 对话

class PasteAttributesDialog(Dialog):
    def __init__(self, screenzoom, container, select_element, parent=None, title="粘贴属性",clipboard_element:dict={},clipboard_name=''):
        super().__init__(parent, title, alert=False)
        self.sz = screenzoom
        self.clipboard_element = clipboard_element
        self.container = container
        self.select_element = select_element
        self.clipboard_name = clipboard_name
    def close_dialog(self,result=None):
        self._result = result
        self._toplevel.destroy()
    def create_body(self, master):
        self.paste_attr = PasteAttributes(
            master = master,
            screenzoom = self.sz,
            clipboard_element = self.clipboard_element,
            title=self._title,
            close_func = self.close_dialog,
            container = self.container,
            select_element=self.select_element,
            clipboard_name=self.clipboard_name
            )
        self.paste_attr.pack(fill='both',expand=True)
    def create_buttonbox(self, master):
        pass