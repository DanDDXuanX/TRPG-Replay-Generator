#!/usr/bin/env python
# coding: utf-8

# 粘贴属性的对话框

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox, Dialog
from .GUI_Link import Link
# 框

class PasteAttributes(ttk.Frame):
    def __init__(self,master,screenzoom,close_func,title,clipboard_element:dict={}):
        # 缩放尺度
        self.sz = screenzoom
        super().__init__(master,borderwidth=0)
        # 关闭窗口命令
        self.close_func = close_func
        # 获取属性
        self.list_attr = self.get_available_attr()
        # 建立原件
        self.title = ttk.Label(
            master  = self,
            font    = (Link['system_font_family'], 15, "bold"),
            text    = title
            )
    # TODO: 从剪贴板中获取可用于粘贴的属性
    def get_available_attr(self)->list:
        pass
        
# 对话

class PasteAttributesDialog(Dialog):
    def __init__(self, screenzoom, parent=None, title="粘贴属性",clipboard_element:dict={}):
        super().__init__(parent, title, alert=False)
        self.sz = screenzoom
        self.clipboard_element = clipboard_element
    def close_dialog(self,result=None):
        self._result = result
        self._toplevel.destroy()
    def create_body(self, master):
        self.paste_attr = PasteAttributes(
            master = master,
            screenzoom = self.sz,
            clipboard_element = self.clipboard_element,
            title=self._title,
            close_func = self.close_dialog
            )
        self.paste_attr.pack(fill='both',expand=True)
    def create_buttonbox(self, master):
        pass