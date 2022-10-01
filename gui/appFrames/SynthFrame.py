"""
语音合成页面
"""
from .AppFrame import AppFrame

import tkinter as tk
from PIL import Image,ImageTk,ImageFont,ImageDraw
import webbrowser
import os
import appFrames as af

class SynthFrame(AppFrame):
    def __init__(self,master,app,*args, **kwargs):
        super().__init__(master,app,*args, **kwargs)
        # self.place(x=10,y=50) # 不需要在这里place，Application.printFrame函数里面已经做了这件事
        self.createWidgets()
        
    def createWidgets(self):
        # synth_frame
        filepath_s = tk.LabelFrame(self,text='文件路径')
        filepath_s.place(x=10,y=10,width=600,height=200)
        # 路径
        tk.Label(filepath_s, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(filepath_s, text="角色配置：",anchor=tk.W).place(x=10,y=50,width=70,height=30)
        tk.Label(filepath_s, text="log文件：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
        tk.Label(filepath_s, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
        tk.Entry(filepath_s, textvariable=self.v["media_define"]).place(x=80,y=5+3,width=430,height=25)
        tk.Entry(filepath_s, textvariable=self.v["characor_table"]).place(x=80,y=50+3,width=430,height=25)
        tk.Entry(filepath_s, textvariable=self.v["stdin_logfile"]).place(x=80,y=95+3,width=430,height=25)
        tk.Entry(filepath_s, textvariable=self.v["output_path"]).place(x=80,y=140+3,width=430,height=25)
        tk.Button(filepath_s, command=lambda:self.call_browse_file(self.v["media_define"]),text="浏览").place(x=520,y=5,width=70,height=30)
        tk.Button(filepath_s, command=lambda:self.call_browse_file(self.v["characor_table"]),text="浏览").place(x=520,y=50,width=70,height=30)
        tk.Button(filepath_s, command=lambda:self.call_browse_file(self.v["stdin_logfile"]),text="浏览").place(x=520,y=95,width=70,height=30)
        tk.Button(filepath_s, command=lambda:self.call_browse_file(self.v["output_path"],'path'),text="浏览").place(x=520,y=140,width=70,height=30)

        # 选项
        def change_service(now):
            if now == optional_s:
                optional_s.place_forget()
                flag_s.place_forget()
                optional_azs.place(x=10,y=210,width=600,height=110)
                flag_azs.place(x=10,y=320,width=600,height=110)
            elif now == optional_azs:
                optional_azs.place_forget()
                flag_azs.place_forget()
                optional_s.place(x=10,y=210,width=600,height=110)
                flag_s.place(x=10,y=320,width=600,height=110)
            else:
                pass
        
        optional_s = tk.LabelFrame(self,text='选项')
        optional_s.place(x=10,y=210,width=600,height=110)

        self.label_AP = tk.Label(optional_s, text="Appkey：",anchor=tk.W)
        self.label_AP.place(x=10,y=0,width=110,height=25)
        self.label_AK = tk.Label(optional_s, text="AccessKey：",anchor=tk.W)
        self.label_AK.place(x=10,y=30,width=110,height=25)
        self.label_AS = tk.Label(optional_s, text="AccessKeySecret：",anchor=tk.W)
        self.label_AS.place(x=10,y=60,width=110,height=25)

        tk.Entry(optional_s, textvariable=self.v["Appkey"]).place(x=120,y=0,width=390,height=25)
        tk.Entry(optional_s, textvariable=self.v["AccessKey"]).place(x=120,y=30,width=390,height=25)
        tk.Entry(optional_s, textvariable=self.v["AccessKeySecret"]).place(x=120,y=60,width=390,height=25)
        tk.Button(optional_s,text="⇵",command=lambda: change_service(optional_s)).place(x=565,y=0,width=25,height=25)

        optional_azs = tk.LabelFrame(self,text='选项')
        #optional_azs.place(x=10,y=210,width=600,height=110)

        self.label_AZ = tk.Label(optional_azs, text="AzureKey：",anchor=tk.W)
        self.label_AZ.place(x=10,y=10,width=110,height=25)
        self.label_SR = tk.Label(optional_azs, text="服务区域：",anchor=tk.W)
        self.label_SR.place(x=10,y=50,width=110,height=25)

        tk.Entry(optional_azs, textvariable=self.v["AzureKey"]).place(x=120,y=10,width=390,height=25)
        tk.Entry(optional_azs, textvariable=self.v["ServiceRegion"]).place(x=120,y=50,width=390,height=25)
        tk.Button(optional_azs,text="⇵",command=lambda: change_service(optional_azs)).place(x=565,y=0,width=25,height=25)

        flag_s = tk.LabelFrame(self,text='标志')
        flag_s.place(x=10,y=320,width=600,height=110)
        aliyun_logo = ImageTk.PhotoImage(Image.open('./media/aliyun.png'))
        tk.Label(flag_s,image = aliyun_logo).place(x=20,y=13)
        tk.Label(flag_s,text='本项功能由阿里云语音合成支持，了解更多：').place(x=300,y=15)
        tk.Button(flag_s,text='https://ai.aliyun.com/nls/',command=lambda: webbrowser.open('https://ai.aliyun.com/nls/'),fg='blue',relief='flat').place(x=300,y=40)
        tk.Button(flag_s,text='试听',command=lambda:self.run_command_synth_preview('Aliyun')).place(x=540,y=55,width=50,height=25)

        flag_azs = tk.LabelFrame(self,text='标志')
        #flag_azs.place(x=10,y=320,width=600,height=110)
        azure_logo = ImageTk.PhotoImage(Image.open('./media/Azure.png'))
        tk.Label(flag_azs,image = azure_logo).place(x=20,y=8)
        tk.Label(flag_azs,text='本项功能由Azure认知语音服务支持，了解更多：').place(x=300,y=15)
        tk.Button(flag_azs,text='https://docs.microsoft.com/azure/',command=lambda: webbrowser.open('https://docs.microsoft.com/zh-cn/azure/cognitive-services'),fg='blue',relief='flat').place(x=300,y=40)
        tk.Button(flag_azs,text='试听',command=lambda:self.run_command_synth_preview('Azure')).place(x=540,y=55,width=50,height=25)

        tk.Button(self, command=self.run_command_synth,text="开始",font=self.v["big_text"]).place(x=260,y=435,width=100,height=50)

    def run_command_synth_preview(self,init_type='Aliyun'):
        #TODO
        pass
    def run_command_synth(self):
        #TODO
        pass