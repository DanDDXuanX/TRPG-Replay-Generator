"""
媒体定义文件编辑器
"""
import tkinter as tk
from tkinter import messagebox
class EditorFrame(tk.Toplevel):
    def __init__(self,master,Edit_filepath='',fig_W=960,fig_H=540,*args, **kwargs):
        super().__init__(master,*args, **kwargs)
        self.master = master
        self.Edit_filepath = Edit_filepath
        self.fig_W = fig_W
        self.fig_H = fig_H
        
    def createWidgets(self):
        pass

    

    def openEditorWindows(self):
        """
        打开编辑器
        TODO
        """
        
        return ""
