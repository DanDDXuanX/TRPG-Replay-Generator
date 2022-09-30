#!/usr/bin/env python
# coding: utf-8
edtion = 'alpha 1.12.7'

"""
这个gui.py是对根目录下的gui.py的实验性重构
"""
import tkinter as tk
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
from PIL import Image,ImageTk,ImageFont,ImageDraw
import webbrowser
import os
import sys
import re
import pickle


class Application(tk.Frame):
    def __init__(self,master=None):
        tk.Frame.__init__(self,master)
        self.pack()


        self.createWidgets()
    def createWidgets(self):
        pass

def close_window():
    #TODO：退出时保存当前参数
    try:
        """之后再想办法处理保存参数的事，先重构其他部分
        o_config = open('./media/save_config','wb')
        if save_config.get() == 1: # 以一个字典的形式把设置保存下来
            pickle.dump({
                'stdin_logfile':stdin_logfile.get(),'characor_table':characor_table.get(),
                'media_define':media_define.get(),'output_path':output_path.get(),
                'timeline_file':timeline_file.get(),'project_W':project_W.get(),
                'project_H':project_H.get(),'project_F':project_F.get(),
                'project_Z':project_Z.get(),'project_Q':project_Q.get(),
                'AccessKey':AccessKey.get(),'Appkey':Appkey.get(),'AccessKeySecret':AccessKeySecret.get(),
                'AzureKey':AzureKey.get(),'ServiceRegion':ServiceRegion.get(),
                'synthanyway':synthanyway.get(),'exportprxml':exportprxml.get(),
                'exportmp4':exportmp4.get(),'fixscrzoom':fixscrzoom.get(),'save_config':save_config.get(),
                'version':edtion
            },o_config) # 把版本信息保存下来
        else: # 如果选择不保存，则抹除保存的参数
            pickle.dump({'save_config':save_config.get()},o_config)
        """
        o_config.close()
    except Exception:
        messagebox.showwarning(title='警告',message='保存设置内容失败!')
    finally: # 关闭主窗口
        Main_windows.destroy()
        Main_windows.quit()

if __name__=='__main__':
    # 初始化
    Main_windows = tk.Tk()
    Main_windows.resizable(0,0)
    Main_windows.geometry("640x550")
    Main_windows.config(background ='#e0e0e0')
    Main_windows.protocol('WM_DELETE_WINDOW',close_window)
    Main_windows.title('回声工坊 ' + edtion)
    # linux:可能无法使用小图标
    try:
        Main_windows.iconbitmap('./media/icon.ico')
    except tk.TclError:
        pass
    # 大号字体
    try:
        big_text = font.Font(font=("微软雅黑",12))
    except Exception:
        big_text = font.Font(font=("System",12))

    app=Application(Main_windows)
    app.mainloop()
