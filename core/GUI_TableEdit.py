#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from ttkbootstrap.constants import DEFAULT
from ttkbootstrap.scrolled import ScrolledFrame
from .GUI_PageElement import OutPutCommand
from .GUI_Util import TextSeparator, KeyValueDescribe
from .GUI_TableStruct import PreferenceTableStruct, ExecuteTableStruct

class OutPutCommandAtScriptExecuter(OutPutCommand):
    # 重载
    def load_input(self):
        raise Exception('WIP')

# 脚本执行
class TableEdit(ttk.Frame):
    TableStruct = {}
    def __init__(self,master,screenzoom,title:str)->None:
        # 初始化
        self.sz = screenzoom
        SZ_10 = int(self.sz*10)
        super().__init__(master,borderwidth=0,padding=SZ_10)
        self.title = ttk.Label(master=self,text=title,font='-family 微软雅黑 -size 20 -weight bold',anchor='center')
        self.options = ScrolledFrame(master=self,autohide=True)
        self.options.vscroll.config(bootstyle='primary-round')
        self.outputs = ttk.Frame(master=self)
        # 分隔符和项目
        self.seperator = {}
        self.elements = {}
        # 初始化
        # self.update_from_tablestruct()
        # self.update_item()
    def update_item(self):
        SZ_5 = int(self.sz * 5)
        SZ_10 = 2 * SZ_5
        SZ_20 = 4 * SZ_5
        self.title.pack(fill='x',side='top')
        self.options.pack(fill='both',expand=True,side='top')
        self.outputs.pack(fill='x',side='top')
        # 滚动窗项目下
        for key in self.seperator:
            item:TextSeparator = self.seperator[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(SZ_10,SZ_20))
    def update_from_tablestruct(self, detail=False):
        # 从EditWindow.update_from_section方法中简化而来的
        self.table_struct:dict = self.TableStruct
        for sep in self.table_struct:
            this_sep:dict = self.table_struct[sep]
            if this_sep['Command'] is None:
                self.seperator[sep] = TextSeparator(
                    master=self.options,
                    screenzoom=self.sz,
                    describe=this_sep['Text']
                )
                for key in this_sep['Content']:
                    this_kvd:dict = this_sep['Content'][key]
                    this_value = this_kvd['default']
                    self.elements[key] = self.seperator[sep].add_element(key=key, value=this_value, kvd=this_kvd, detail=detail)
        # 绑定功能
        self.update_element_prop()
    def update_element_prop(self):
        pass

class ScriptExecuter(TableEdit):
    TableStruct = ExecuteTableStruct
    def __init__(self,master,screenzoom)->None:
        # 继承
        super().__init__(master=master,screenzoom=screenzoom,title='运行脚本')
        # 输出选项
        self.outputs = OutPutCommandAtScriptExecuter(master=self,screenzoom=self.sz)
        # 初始化
        self.update_from_tablestruct(detail=False)
        self.update_item()
    def update_element_prop(self):
        self.elements['mediadef'].bind_button(dtype='mediadef-file')
        self.elements['chartab'].bind_button(dtype='chartab-file')
        self.elements['logfile'].bind_button(dtype='logfile-file')

# 首选项
class PreferenceTable(TableEdit):
    TableStruct = PreferenceTableStruct
    def __init__(self,master,screenzoom)->None:
        # 继承
        super().__init__(master=master,screenzoom=screenzoom,title='首选项')
        # 输出选项
        # self.outputs = OutPutCommand(master=self,screenzoom=self.sz)
        # 初始化
        self.update_from_tablestruct(detail=True)
        self.update_item()
    def update_element_prop(self):
        pass