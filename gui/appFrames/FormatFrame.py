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
from tkinter import filedialog
from tkinter import messagebox

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
        self.original_info = ttk.Treeview(original_file,columns=['index','filepath'],show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar_original.set)
        ybar_original.config(command=self.original_info.yview)
        ybar_original.place(x=575,y=0,height=180,width=15)

        self.original_info.column("index",anchor = "center",width=40)
        self.original_info.column("filepath",anchor = "w",width=520)

        self.original_info.heading("index", text = "序号")
        self.original_info.heading("filepath", text = "路径")

        self.original_info.place(x=10,y=0,height=180,width=565)
        # 转换后音频文件
        ybar_convert = ttk.Scrollbar(convert_file,orient='vertical')
        self.convert_info = ttk.Treeview(convert_file,columns=['index','filepath'],show = "headings",selectmode = tk.BROWSE,yscrollcommand=ybar_convert.set)
        ybar_convert.config(command=self.convert_info.yview)
        ybar_convert.place(x=575,y=0,height=180,width=15)

        self.convert_info.column("index",anchor = "center",width=40)
        self.convert_info.column("filepath",anchor = "w",width=520)

        self.convert_info.heading("index", text = "序号")
        self.convert_info.heading("filepath", text = "路径")

        self.convert_info.place(x=10,y=0,height=180,width=565)
        # 按键
        tk.Button(self, command=self.load_au_file,text="载入",font=self.app.big_text).place(x=65,y=440,width=100,height=40)
        tk.Button(self, command=self.clear_au_file,text="清空",font=self.app.big_text).place(x=195,y=440,width=100,height=40)
        tk.Button(self, command=lambda:self.run_convert('wav'),text="转wav",font=self.app.big_text).place(x=325,y=440,width=100,height=40)
        tk.Button(self, command=lambda:self.run_convert('ogg'),text="转ogg",font=self.app.big_text).place(x=455,y=440,width=100,height=40)

    def load_au_file(self): # 载入多个音频文件
        getnames = filedialog.askopenfilenames(filetypes=[('mp3文件','.mp3')])
        for index,filepath in enumerate(getnames):
            self.original_info.insert('','end',values =(index,filepath))

    def clear_au_file(self): # 清空所有音频文件
        for item in self.original_info.get_children():
            self.original_info.delete(item)
        for item in self.convert_info.get_children():
            self.convert_info.delete(item)

    def run_convert(self,target):
        # 检查输出路径
        if self.app.output_path.get() == '':
            messagebox.showerror(title='错误',message='缺少输出路径，去主程序界面填写！')
            return -1
        else:
            opath = self.app.output_path.get()+'/'
        # 检查ffmpeg
        if os.path.isfile('./ffmpeg.exe'):
            ffmpeg_exec = 'ffmpeg.exe'
        else:
            ffmpeg_exec = 'ffmpeg'
        # 确定格式
        if target == 'wav':
            command = ffmpeg_exec+" -i {ifile} -f wav {ofile} -loglevel quiet"
        elif target == 'ogg':
            command = ffmpeg_exec+" -i {ifile} -acodec libvorbis -ab 128k {ofile} -loglevel quiet"
        else:
            return -1
        # 开始载入文件
        for item in self.original_info.get_children():
            index,filepath = self.original_info.item(item,"values")
            # 获取文件名
            try:
                filename = filepath.split('/')[-1][0:-3]
            except IndexError:
                messagebox.showerror(title='错误',message='出现了文件名称异常！'+filename)
                return -1
            # 检查文件路径
            if ' ' in filepath:
                filepath = '"'+filepath+'"'
            # 组装命令
            command_this = command.format(ifile = filepath, ofile = '"'+opath+filename+target+'"')
            # 执行命令
            try:
                print('[32m'+command_this+'[0m')
                exit_status = os.system(command_this)
                if exit_status != 0:
                    raise OSError('Major error occurred in ffmpeg!')
                else:
                    print('[convert_format]: '+opath + filename + target+' :Done!')
                    self.convert_info.insert('','end',values =(index,opath+filename+target))
            except Exception:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
                return -1
        messagebox.showinfo(title='完毕',message='格式格式转换完毕，输出文件在:'+opath)