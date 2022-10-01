"""
媒体定义文件编辑器
"""
import tkinter as tk
from tkinter import messagebox
from .SubWindow import SubWindow

class MediaEditorWindow(SubWindow):
    def __init__(self,master,Edit_filepath='',fig_W=960,fig_H=540,*args, **kwargs):
        super().__init__(master,*args, **kwargs)
        self.Edit_filepath = Edit_filepath
        self.fig_W = fig_W
        self.fig_H = fig_H
        
        window_W , window_H = fig_W//2+40,fig_H//2+440
        self.resizable(0,0)
        self.geometry("{W}x{H}".format(W=window_W,H=window_H))
        self.config(background ='#e0e0e0')
        self.title('回声工坊 媒体定义文件编辑器')
        self.protocol('WM_DELETE_WINDOW',self.close_window)
        self.transient(master)
        try:
            self.iconbitmap('./media/icon.ico')
        except tk.TclError:
            pass
        
        
        self.edit_return_value = False
        self.createWidgets()
        
    def createWidgets(self):
        pass

    

    def open(self):
        """
        打开编辑器窗口
        
        返回关闭窗口时媒体定义文件的保存地址
        TODO
        """
        
        self.mainloop()
        return self.edit_return_value

    def close_window(self):
        if messagebox.askyesno(title='确认退出？',message='未保存的改动将会丢失！') == True:
            self.edit_return_value = self.Edit_filepath
            self.destroy()
            self.quit()
        else:
            pass