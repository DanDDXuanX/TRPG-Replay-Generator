"""
导出xml页面
"""
from .AppFrame import AppFrame

import tkinter as tk
from PIL import Image,ImageTk,ImageFont,ImageDraw
import webbrowser
import os
import appFrames as af

class XmlFrame(AppFrame):
    def __init__(self,master,app,*args, **kwargs):
        super().__init__(master,app,*args, **kwargs)
        self.createWidgets()

    def createWidgets(self):
        # xml_frame
        filepath_x = tk.LabelFrame(self,text='文件路径')
        filepath_x.place(x=10,y=10,width=600,height=200)

        tk.Label(filepath_x, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(filepath_x, text="角色配置：",anchor=tk.W,fg='#909090').place(x=10,y=50,width=70,height=30)
        tk.Label(filepath_x, text="时间轴：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
        tk.Label(filepath_x, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
        tk.Entry(filepath_x, textvariable=self.v["media_define"]).place(x=80,y=5+3,width=430,height=25)
        tk.Entry(filepath_x, textvariable=self.v["characor_table"],state=tk.DISABLED).place(x=80,y=50+3,width=430,height=25)
        tk.Entry(filepath_x, textvariable=self.v["timeline_file"]).place(x=80,y=95+3,width=430,height=25)
        tk.Entry(filepath_x, textvariable=self.v["output_path"]).place(x=80,y=140+3,width=430,height=25)
        tk.Button(filepath_x, command=lambda:self.call_browse_file(self.v["media_define"]),text="浏览").place(x=520,y=5,width=70,height=30)
        tk.Button(filepath_x, command=lambda:self.call_browse_file(self.v["characor_table"]),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
        tk.Button(filepath_x, command=lambda:self.call_browse_file(self.v["timeline_file"]),text="浏览").place(x=520,y=95,width=70,height=30)
        tk.Button(filepath_x, command=lambda:self.call_browse_file(self.v["output_path"],'path'),text="浏览").place(x=520,y=140,width=70,height=30)

        optional_x = tk.LabelFrame(self,text='选项')
        optional_x.place(x=10,y=210,width=600,height=110)

        tk.Label(optional_x,text="分辨率-宽:",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(optional_x,text="分辨率-高:",anchor=tk.W).place(x=160,y=5,width=70,height=30)
        tk.Label(optional_x,text="帧率:",anchor=tk.W).place(x=310,y=5,width=70,height=30)
        tk.Label(optional_x,text="图层顺序:",anchor=tk.W).place(x=10,y=50,width=70,height=30)

        tk.Entry(optional_x,textvariable=self.v["project_W"]).place(x=80,y=5,width=70,height=25)
        tk.Entry(optional_x,textvariable=self.v["project_H"]).place(x=230,y=5,width=70,height=25)
        tk.Entry(optional_x,textvariable=self.v["project_F"]).place(x=380,y=5,width=70,height=25)
        tk.Entry(optional_x,textvariable=self.v["project_Z"]).place(x=80,y=50,width=370,height=25)

        flag_x = tk.LabelFrame(self,text='标志')
        flag_x.place(x=10,y=320,width=600,height=110)

        PR_logo = ImageTk.PhotoImage(Image.open('./media/PR.png'))
        Eta_logo = ImageTk.PhotoImage(Image.open('./media/eta.png'))
        tk.Label(flag_x,image = PR_logo).place(x=20,y=10)
        tk.Label(flag_x,text='通向Premiere Pro世界的通道。').place(x=110,y=30)
        tk.Label(flag_x,text='感谢up主伊塔的Idea，了解更多：').place(x=300,y=30)
        tk.Button(flag_x,image = Eta_logo,command=lambda: webbrowser.open('https://space.bilibili.com/10414609'),relief='flat').place(x=500,y=7)

        tk.Button(self, command=self.run_command_xml,text="开始",font=self.v["big_text"]).place(x=260,y=435,width=100,height=50)

    def run_command_xml(self):
        #TODO
        pass