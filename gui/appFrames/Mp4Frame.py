"""
导出mp4页面
"""
from .AppFrame import AppFrame

import tkinter as tk
from PIL import Image,ImageTk,ImageFont,ImageDraw
import webbrowser
import os
import appFrames as af

class Mp4Frame(AppFrame):
    def __init__(self,master,app,*args, **kwargs):
        super().__init__(master,app,*args, **kwargs)
        self.createWidgets()

    def createWidgets(self):
        # mp4_frame
        filepath_v = tk.LabelFrame(self,text='文件路径')
        filepath_v.place(x=10,y=10,width=600,height=200)

        tk.Label(filepath_v, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(filepath_v, text="角色配置：",anchor=tk.W,fg='#909090').place(x=10,y=50,width=70,height=30)
        tk.Label(filepath_v, text="时间轴：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
        tk.Label(filepath_v, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
        tk.Entry(filepath_v, textvariable=self.app.media_define).place(x=80,y=5+3,width=430,height=25)
        tk.Entry(filepath_v, textvariable=self.app.characor_table,state=tk.DISABLED).place(x=80,y=50+3,width=430,height=25)
        tk.Entry(filepath_v, textvariable=self.app.timeline_file).place(x=80,y=95+3,width=430,height=25)
        tk.Entry(filepath_v, textvariable=self.app.output_path).place(x=80,y=140+3,width=430,height=25)
        tk.Button(filepath_v, command=lambda:self.call_browse_file(self.app.media_define),text="浏览").place(x=520,y=5,width=70,height=30)
        tk.Button(filepath_v, command=lambda:self.call_browse_file(self.app.characor_table),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
        tk.Button(filepath_v, command=lambda:self.call_browse_file(self.app.timeline_file),text="浏览").place(x=520,y=95,width=70,height=30)
        tk.Button(filepath_v, command=lambda:self.call_browse_file(self.app.output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

        optional_v = tk.LabelFrame(self,text='选项')
        optional_v.place(x=10,y=210,width=600,height=110)

        tk.Label(optional_v,text="分辨率-宽:",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(optional_v,text="分辨率-高:",anchor=tk.W).place(x=160,y=5,width=70,height=30)
        tk.Label(optional_v,text="帧率:",anchor=tk.W).place(x=310,y=5,width=70,height=30)
        tk.Label(optional_v,text="图层顺序:",anchor=tk.W).place(x=10,y=50,width=70,height=30)
        self.label_ql = tk.Label(optional_v,text="质量:",anchor=tk.W)
        self.label_ql.place(x=310,y=50,width=70,height=30)

        tk.Entry(optional_v,textvariable=self.app.project_W).place(x=80,y=5,width=70,height=25)
        tk.Entry(optional_v,textvariable=self.app.project_H).place(x=230,y=5,width=70,height=25)
        tk.Entry(optional_v,textvariable=self.app.project_F).place(x=380,y=5,width=70,height=25)
        tk.Entry(optional_v,textvariable=self.app.project_Z).place(x=80,y=50,width=220,height=25)
        tk.Entry(optional_v,textvariable=self.app.project_Q).place(x=380,y=50,width=70,height=25)

        flag_v = tk.LabelFrame(self,text='标志')
        flag_v.place(x=10,y=320,width=600,height=110)

        ffmpeg_logo = ImageTk.PhotoImage(Image.open('./media/ffmpeg.png'))
        tk.Label(flag_v,image = ffmpeg_logo).place(x=20,y=10)
        tk.Label(flag_v,text='本项功能调用ffmpeg实现，了解更多：').place(x=300,y=15)
        tk.Button(flag_v,text='https://ffmpeg.org/',command=lambda: webbrowser.open('https://ffmpeg.org/'),fg='blue',relief='flat').place(x=300,y=40)

        tk.Button(self, command=self.run_command_mp4,text="开始",font=self.app.big_text).place(x=260,y=435,width=100,height=50)

    def run_command_mp4(self):
        #TODO
        pass