#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from .GUI_Util import KeyValueDescribe

# 编辑区

# 编辑窗
class EditWindow(ttk.LabelFrame):
    def __init__(self,master,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='编辑区')
        # 初始化状态
        self.line_type = 'no_selection'
        self.elements = {}
        self.section = None
        # 更新
        self.update_item()
    def update_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.pack(side='top',anchor='n',fill='x')
    def clear_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.destroy()
        self.elements.clear()
    # 从小节中更新窗体内容
    def update_section(self,section:dict):
        self.clear_item()

class CharactorEdit(EditWindow):
    custom_col = []
    table_col = ['Name','Subtype','Animation','Bubble','Voice','SpeechRate','PitchRate']
    def update_section(self,section:dict):
        super().update_section(section)
        self.section = section
        for col in CharactorEdit.table_col:
            self.elements[col] = KeyValueDescribe(
                master=self,
                screenzoom=self.sz,
                key=col,
                value={
                    'type':'str',
                    'style':'entry',
                    'value':self.section[col]},
                describe={
                    'type':'text',
                    'text':'输入'
                }
            )
        self.update_item()