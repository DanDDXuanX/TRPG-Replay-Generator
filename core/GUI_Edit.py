#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from .GUI_Util import KeyValueDescribe

# 编辑区

# 编辑窗
class EditWindow(ttk.LabelFrame):
    def __init__(self,master,section,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='编辑区')
        # 小节的数据
        self.section = section
        # 组件
        if self.section == None:
            self.line_type = 'no_selection'
            self.elements = {}
        else:
            self.line_type = self.section['type']
            self.elements = {
                'type' : KeyValueDescribe(self,self.sz,key='小节类型',value={'type':'str','style':'combox','value':section['type']},describe={'type':'text','text':'（选择）'})
            }
        self.update_item()
    def update_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.pack(side='top',anchor='n',fill='x')
        # 根据小节类型
        # if self.
        # if self.line_type == 'dialog':
        #     pass
