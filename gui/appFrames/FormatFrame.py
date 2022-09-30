"""
转换音频格式
"""
from .AppFrame import AppFrame

import tkinter as tk
from PIL import Image,ImageTk,ImageFont,ImageDraw
import webbrowser
import os
import appFrames as af
from tkinter import ttk

class FormatFrame(AppFrame):
    def __init__(self,master,app,*args, **kwargs):
        super().__init__(master,app,*args, **kwargs)
        self.createWidgets()

    def createWidgets(self):
        # format_frame
        original_file = tk.LabelFrame(self,text='原始音频文件')
        convert_file = tk.LabelFrame(self,text='转换后音频文件')
        original_file.place(x=10,y=10,width=600,height=210)
        convert_file.place(x=10,y=220,width=600,height=210)
        # 原始音频文件
        ybar_original = ttk.Scrollbar(original_file,orient='vertical')
        original_info = ttk.Treeview(original_file,columns=['index','filepath'],show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar_original.set)
        ybar_original.config(command=original_info.yview)
        ybar_original.place(x=575,y=0,height=180,width=15)

        original_info.column("index",anchor = "center",width=40)
        original_info.column("filepath",anchor = "w",width=520)

        original_info.heading("index", text = "序号")
        original_info.heading("filepath", text = "路径")

        original_info.place(x=10,y=0,height=180,width=565)
        # 转换后音频文件
        ybar_convert = ttk.Scrollbar(convert_file,orient='vertical')
        convert_info = ttk.Treeview(convert_file,columns=['index','filepath'],show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar_convert.set)
        ybar_convert.config(command=convert_info.yview)
        ybar_convert.place(x=575,y=0,height=180,width=15)

        convert_info.column("index",anchor = "center",width=40)
        convert_info.column("filepath",anchor = "w",width=520)

        convert_info.heading("index", text = "序号")
        convert_info.heading("filepath", text = "路径")

        convert_info.place(x=10,y=0,height=180,width=565)
        # 按键
        tk.Button(self, command=self.load_au_file,text="载入",font=self.v["big_text"]).place(x=65,y=440,width=100,height=40)
        tk.Button(self, command=self.clear_au_file,text="清空",font=self.v["big_text"]).place(x=195,y=440,width=100,height=40)
        tk.Button(self, command=lambda:self.run_convert('wav'),text="转wav",font=self.v["big_text"]).place(x=325,y=440,width=100,height=40)
        tk.Button(self, command=lambda:self.run_convert('ogg'),text="转ogg",font=self.v["big_text"]).place(x=455,y=440,width=100,height=40)

    def load_au_file(self):
        #TODO
        pass

    def clear_au_file(self):
        pass

    def run_convert(self,target):
        pass