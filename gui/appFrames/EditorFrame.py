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
        global image_canvas # 预览的画布
        global available_Text # 所有的可用文本名
        global used_variable_name # 已经被用户占用的命名
        selected_name,selected_type,selected_args = 'None','None','None'
        selected = 0
        edit_return_value = False
        available_Text = ['None','Text()']
        used_variable_name = []
        media_lines = [] # 保存当前所有媒体行，用于筛选时避免丢失原有媒体。有used_variable_name的地方就有它
    
        def close_window():
            nonlocal edit_return_value
            if messagebox.askyesno(title='确认退出？',message='未保存的改动将会丢失！') == True:
                edit_return_value = self.Edit_filepath
                self.destroy()
                self.quit()
            else:
                pass
        window_W , window_H = self.fig_W//2+40,self.fig_H//2+440
        self.resizable(0,0)
        self.geometry("{W}x{H}".format(W=window_W,H=window_H))
        self.config(background ='#e0e0e0')
        self.title('回声工坊 媒体定义文件编辑器')
        self.protocol('WM_DELETE_WINDOW',close_window)
        self.transient(self.master)
        try:
            self.iconbitmap('./media/icon.ico')
        except tk.TclError:
            pass
        return ""
