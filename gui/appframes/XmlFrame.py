import os
import tkinter as tk
import webbrowser
from tkinter import messagebox

from PIL import Image, ImageTk

from .AppFrame import AppFrame


class XmlFrame(AppFrame):
    """
    导出xml的页面
    """
    def __init__(self,master,app,*args, **kwargs):
        super().__init__(master,app,*args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        # xml_frame
        filepath_x = tk.LabelFrame(self,text='文件路径')
        filepath_x.place(x=10,y=10,width=600,height=200)

        tk.Label(filepath_x, text="媒体定义：",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(filepath_x, text="角色配置：",anchor=tk.W,fg='#909090').place(x=10,y=50,width=70,height=30)
        tk.Label(filepath_x, text="时间轴：",anchor=tk.W).place(x=10,y=95,width=70,height=30)
        tk.Label(filepath_x, text="输出路径：",anchor=tk.W).place(x=10,y=140,width=70,height=30)
        tk.Entry(filepath_x, textvariable=self.app.media_define).place(x=80,y=5+3,width=430,height=25)
        tk.Entry(filepath_x, textvariable=self.app.characor_table,state=tk.DISABLED).place(x=80,y=50+3,width=430,height=25)
        tk.Entry(filepath_x, textvariable=self.app.timeline_file).place(x=80,y=95+3,width=430,height=25)
        tk.Entry(filepath_x, textvariable=self.app.output_path).place(x=80,y=140+3,width=430,height=25)
        tk.Button(filepath_x, command=lambda:self.call_browse_file(self.app.media_define,'file',filetype='mediadef'),text="浏览").place(x=520,y=5,width=70,height=30)
        tk.Button(filepath_x, command=lambda:self.call_browse_file(self.app.characor_table,'file',filetype='chartab'),text="浏览",state=tk.DISABLED).place(x=520,y=50,width=70,height=30)
        tk.Button(filepath_x, command=lambda:self.call_browse_file(self.app.timeline_file,'file',filetype='timeline'),text="浏览").place(x=520,y=95,width=70,height=30)
        tk.Button(filepath_x, command=lambda:self.call_browse_file(self.app.output_path,'path'),text="浏览").place(x=520,y=140,width=70,height=30)

        optional_x = tk.LabelFrame(self,text='选项')
        optional_x.place(x=10,y=210,width=600,height=110)

        tk.Label(optional_x,text="分辨率-宽:",anchor=tk.W).place(x=10,y=5,width=70,height=30)
        tk.Label(optional_x,text="分辨率-高:",anchor=tk.W).place(x=160,y=5,width=70,height=30)
        tk.Label(optional_x,text="帧率:",anchor=tk.W).place(x=310,y=5,width=70,height=30)
        tk.Label(optional_x,text="图层顺序:",anchor=tk.W).place(x=10,y=50,width=70,height=30)

        tk.Entry(optional_x,textvariable=self.app.project_W).place(x=80,y=5,width=70,height=25)
        tk.Entry(optional_x,textvariable=self.app.project_H).place(x=230,y=5,width=70,height=25)
        tk.Entry(optional_x,textvariable=self.app.project_F).place(x=380,y=5,width=70,height=25)
        tk.Entry(optional_x,textvariable=self.app.project_Z).place(x=80,y=50,width=370,height=25)

        flag_x = tk.LabelFrame(self,text='标志')
        flag_x.place(x=10,y=320,width=600,height=110)

        self.PR_logo = ImageTk.PhotoImage(Image.open('./media/PR.png'))
        self.Eta_logo = ImageTk.PhotoImage(Image.open('./media/eta.png'))
        tk.Label(flag_x,image = self.PR_logo).place(x=20,y=10)
        tk.Label(flag_x,text='通向Premiere Pro世界的通道。').place(x=110,y=30)
        tk.Label(flag_x,text='感谢up主伊塔的Idea，了解更多：').place(x=300,y=30)
        tk.Button(flag_x,image = self.Eta_logo,command=lambda: webbrowser.open('https://space.bilibili.com/10414609'),relief='flat').place(x=500,y=7)

        tk.Button(self, command=self.run_command_xml,text="开始",font=self.app.big_text).place(x=260,y=435,width=100,height=50)

    def run_command_xml(self):
        """执行导出xml的命令"""
        command = self.app.python3 + ' ./export_xml.py --TimeLine {tm} --MediaObjDefine {md} --OutputPath {of} --FramePerSecond {fps} --Width {wd} --Height {he} --Zorder {zd}'
        if '' in [self.app.timeline_file.get(),self.app.media_define.get(),self.app.output_path.get(),
                  self.app.project_W.get(),self.app.project_H.get(),self.app.project_F.get(),self.app.project_Z.get()]:
            messagebox.showerror(title='错误',message='缺少必要的参数！')
        else:
            command = command.format(tm = self.app.timeline_file.get().replace('\\','/'),
                                     md = self.app.media_define.get().replace('\\','/'), of = self.app.output_path.get().replace('\\','/'), 
                                     fps = self.app.project_F.get(), wd = self.app.project_W.get(),
                                     he = self.app.project_H.get(), zd = self.app.project_Z.get())
            try:
                print('[32m'+command+'[0m')
                exit_status = os.system(command)
                if exit_status != 0:
                    raise OSError('Major error occurred in export_xml!')
                else:
                    messagebox.showinfo(title='完毕',message='导出XML程序执行完毕！')
            except Exception:
                messagebox.showwarning(title='警告',message='似乎有啥不对劲的事情发生了，检视控制台输出获取详细信息！')
